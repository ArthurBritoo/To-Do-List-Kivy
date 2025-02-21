from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.graphics import Rectangle
from datetime import datetime, timedelta
from manipulador_json import carregar_tarefas, salvar_tarefas, salvar_tarefas_concluidas, carregar_tarefas_concluidas
from notificacoes import enviar_notificacao
from kivymd.uix.button import MDIconButton
from kivy.core.window import Window

class TelaMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            self.bg = Rectangle(source="classes/fundo.jpg", size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Renomeado para "mostrar_pendentes" para evitar conflitos
        self.mostrar_pendentes = True  
        self.tarefas = carregar_tarefas()
        self.tarefas_concluidas = carregar_tarefas_concluidas()

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.rotulo_titulo = Label(text="Lista de Tarefas Pendentes", font_size=24, size_hint_y=None, height=40, color=(0, 0, 0, 1))
        layout.add_widget(self.rotulo_titulo)

        botao_pendentes = Button(text="Ver Tarefas Pendentes", size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_pendentes.bind(on_press=self.mostrar_pendentes_func)
        layout.add_widget(botao_pendentes)

        botao_concluidas = Button(text="Ver Tarefas Concluídas", size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_concluidas.bind(on_press=self.mostrar_concluidas)
        layout.add_widget(botao_concluidas)

        self.lista_tarefas_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.lista_tarefas_layout.bind(minimum_height=self.lista_tarefas_layout.setter('height'))
        area_rolagem = ScrollView(size_hint=(1, None), size=(400, 300))
        area_rolagem.add_widget(self.lista_tarefas_layout)
        layout.add_widget(area_rolagem)

        botao_tarefas = Button(text="Adicionar Nova Tarefa", size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_tarefas.bind(on_press=self.ir_para_tarefas)
        layout.add_widget(botao_tarefas)

        botao_voltar = Button(text="Voltar à Tela Inicial", size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_voltar.bind(on_press=self.voltar)
        layout.add_widget(botao_voltar)

        self.add_widget(layout)
        self.atualizar_lista_tarefas()
        Clock.schedule_interval(self.verificar_vencimento_tarefas, 60)

    def _update_rect(self, *args):
        if hasattr(self, 'bg'):
            self.bg.pos = self.pos
            self.bg.size = self.size

    def ir_para_tarefas(self, instancia):
        self.manager.current = 'tarefa'

    def voltar(self, instancia):
        self.manager.current = 'boas_vindas'

    def mostrar_pendentes_func(self, instancia):
        self.mostrar_pendentes = True
        self.rotulo_titulo.text = "Lista de Tarefas Pendentes"
        self.atualizar_lista_tarefas()

    def mostrar_concluidas(self, instancia):
        self.mostrar_pendentes = False
        self.rotulo_titulo.text = "Lista de Tarefas Concluídas"
        self.atualizar_lista_tarefas()

    def atualizar_lista_tarefas(self):
        self.lista_tarefas_layout.clear_widgets()
        # Usa a lista apropriada conforme o modo de visualização
        tarefas = carregar_tarefas() if self.mostrar_pendentes else carregar_tarefas_concluidas()
        for indice, tarefa in enumerate(tarefas):
            layout_tarefa = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            checkbox = CheckBox(active=tarefa.get('concluida', False),
                                size_hint=(None, None), size=(40, 40))
            checkbox.bind(active=lambda inst, valor, i=indice: self.alternar_tarefa(i, valor))
            layout_tarefa.add_widget(checkbox)
            rotulo_tarefa = Label(
                text=f"{tarefa['texto']} - {tarefa['data_vencimento']} {tarefa.get('hora_vencimento', '')}",
                font_size=18, color=(0, 0, 0, 1))
            layout_tarefa.add_widget(rotulo_tarefa)
            if not self.mostrar_pendentes:
                botao_lixeira = MDIconButton(icon="delete-outline", size_hint_x=None,
                                             width=50, theme_text_color="Custom", text_color=(1, 0, 0, 1))
                botao_lixeira.bind(on_press=lambda inst, i=indice: self.remover_tarefa_concluida(i))
                layout_tarefa.add_widget(botao_lixeira)
            self.lista_tarefas_layout.add_widget(layout_tarefa)

    def alternar_tarefa(self, indice_tarefa, valor):
        # Se o usuário marcar manualmente uma tarefa (opção não relacionada à verificação automática)
        if self.mostrar_pendentes and valor:
            tarefa_concluida = self.tarefas.pop(indice_tarefa)
            self.tarefas_concluidas.append(tarefa_concluida)
            salvar_tarefas(self.tarefas)
            salvar_tarefas_concluidas(self.tarefas_concluidas)
            self.atualizar_lista_tarefas()

    def remover_tarefa_concluida(self, indice_tarefa):
        if 0 <= indice_tarefa < len(self.tarefas_concluidas):
            del self.tarefas_concluidas[indice_tarefa]
            salvar_tarefas_concluidas(self.tarefas_concluidas)
            self.atualizar_lista_tarefas()

    def verificar_vencimento_tarefas(self, dt=None):
        agora = datetime.now()
        # Itera sobre uma cópia da lista para evitar problemas ao modificar a lista original
        for tarefa in self.tarefas.copy():
            if not tarefa.get("data_vencimento"):
                continue
            try:
                # Converte a data de vencimento e, se disponível, combina com a hora de vencimento
                data_vencimento = datetime.strptime(tarefa["data_vencimento"], "%d/%m/%Y")
                if tarefa.get("hora_vencimento"):
                    hora_vencimento = datetime.strptime(tarefa["hora_vencimento"], "%H:%M").time()
                    data_vencimento = datetime.combine(data_vencimento.date(), hora_vencimento)
            except Exception:
                continue
            tempo_restante = data_vencimento - agora

            # Se estiver dentro de 1 hora do vencimento e a notificação pendente não foi enviada
            if timedelta(hours=1) >= tempo_restante > timedelta(seconds=0) and not tarefa.get("notificacao_enviada", False):
                enviar_notificacao(tarefa["texto"], tipo="pendente")
                tarefa["notificacao_enviada"] = True
                salvar_tarefas(self.tarefas)

            # Se o prazo já passou e a tarefa não foi marcada como concluída
            if tempo_restante <= timedelta(seconds=0) and not tarefa.get("concluida", False):
                # Marca a tarefa como concluída e move para a lista de tarefas concluídas
                tarefa["concluida"] = True
                self.tarefas_concluidas.append(tarefa)
                if tarefa in self.tarefas:
                    self.tarefas.remove(tarefa)
                    salvar_tarefas(self.tarefas)
                    salvar_tarefas_concluidas(self.tarefas_concluidas)
                # Envia a notificação de conclusão somente uma vez
                if not tarefa.get("notificacao_concluida_enviada", False):
                    enviar_notificacao(tarefa["texto"], tipo="concluida")
                    tarefa["notificacao_concluida_enviada"] = True
                    salvar_tarefas_concluidas(self.tarefas_concluidas)
        self.atualizar_lista_tarefas()
