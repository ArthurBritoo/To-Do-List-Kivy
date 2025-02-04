from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from datetime import datetime, timedelta
from manipulador_json import carregar_tarefas, salvar_tarefas, salvar_tarefas_concluidas, carregar_tarefas_concluidas
from notificacoes import enviar_notificacao
from kivymd.uix.button import MDFlatButton  # Botão com ícone do KivyMD
from kivy.core.text import LabelBase
from kivymd.uix.button import MDIconButton


class TelaMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(1, 1, 1, 1)  # Fundo branco
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        self.mostrando_pendentes = True  # Começa mostrando tarefas pendentes
        self.tarefas = carregar_tarefas()
        self.tarefas_concluidas = carregar_tarefas_concluidas()

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Título da tela
        self.rotulo_titulo = Label(text="Lista de Tarefas Pendentes", font_size=24, size_hint_y=None, height=40, color=(0, 0, 0, 1))
        layout.add_widget(self.rotulo_titulo)

        # Botões para alternar entre tarefas pendentes e concluídas
        botao_pendentes = Button(text="Ver Tarefas Pendentes", size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_pendentes.bind(on_press=self.mostrar_pendentes)
        layout.add_widget(botao_pendentes)

        botao_concluidas = Button(text="Ver Tarefas Concluídas", size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_concluidas.bind(on_press=self.mostrar_concluidas)
        layout.add_widget(botao_concluidas)

        # Área de rolagem para exibir tarefas
        self.lista_tarefas_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.lista_tarefas_layout.bind(minimum_height=self.lista_tarefas_layout.setter('height'))
        area_rolagem = ScrollView(size_hint=(1, None), size=(400, 300))
        area_rolagem.add_widget(self.lista_tarefas_layout)
        layout.add_widget(area_rolagem)

        # Botão para adicionar novas tarefas
        botao_tarefas = Button(text="Adicionar Nova Tarefa", size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_tarefas.bind(on_press=self.ir_para_tarefas)
        layout.add_widget(botao_tarefas)

        # Botão para voltar à tela inicial
        botao_voltar = Button(text="Voltar à Tela Inicial", size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_voltar.bind(on_press=self.voltar)
        layout.add_widget(botao_voltar)

        self.add_widget(layout)

        # Exibir tarefas iniciais
        self.atualizar_lista_tarefas()

        # Verificar vencimento ao carregar a tela
        self.verificar_vencimento_tarefas()

        # Iniciar verificação periódica de vencimento de tarefas
        Clock.schedule_interval(self.verificar_vencimento_tarefas, 60)  # Verifica a cada 60 segundos

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def ir_para_tarefas(self, instancia):
        self.manager.current = 'tarefa'

    def voltar(self, instancia):
        self.manager.current = 'boas_vindas'

    def mostrar_pendentes(self, instancia):
        """ Alterna para exibir tarefas pendentes """
        self.mostrando_pendentes = True
        self.rotulo_titulo.text = "Lista de Tarefas Pendentes"
        self.atualizar_lista_tarefas()

    def mostrar_concluidas(self, instancia):
        """ Alterna para exibir tarefas concluídas """
        self.mostrando_pendentes = False
        self.rotulo_titulo.text = "Lista de Tarefas Concluídas"
        self.atualizar_lista_tarefas()

    def atualizar_lista_tarefas(self):
        """ Atualiza a lista de tarefas exibida no menu """
        self.lista_tarefas_layout.clear_widgets()

        if self.mostrando_pendentes:
            tarefas = carregar_tarefas()
        else:
            tarefas = carregar_tarefas_concluidas()

        for indice, tarefa in enumerate(tarefas):
            layout_tarefa = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

            # Se for lista de tarefas pendentes
            if self.mostrando_pendentes:
                checkbox = CheckBox(active=tarefa.get('concluida', False), size_hint_y=None, height=40)
                checkbox.bind(active=lambda instancia, valor, indice_tarefa=indice: self.alternar_tarefa(indice_tarefa, valor))

                layout_tarefa.add_widget(checkbox)
            else:
                # Caixa de seleção visível e desabilitada para tarefas concluídas
                checkbox = CheckBox(
                    active=True, 
                    size_hint_y=None, 
                    height=40, 
                    disabled=True, 
                    color=(0, 1, 0, 1),  
                )
                layout_tarefa.add_widget(checkbox)

            rotulo_tarefa = Label(text=tarefa['texto'], size_hint_y=None, height=40, font_size='24sp', color=(0, 0, 0, 1))
            layout_tarefa.add_widget(rotulo_tarefa)

            # Adiciona um botão de lixeira para excluir tarefa concluída
            if not self.mostrando_pendentes:
                botao_lixeira = MDIconButton(
                    icon="delete-outline",  # Ícone de lixeira
                    size_hint_x=None,
                    width=50,  # Defina uma largura suficiente
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1),  # Cor vermelha
                    pos_hint={"center_y": 0.5}  # Ajuste a posição vertical
                )
                botao_lixeira.bind(on_press=lambda instancia, indice_tarefa=indice: self.remover_tarefa_concluida(indice_tarefa))
                layout_tarefa.add_widget(botao_lixeira)

            self.lista_tarefas_layout.add_widget(layout_tarefa)

    def alternar_tarefa(self, indice_tarefa, valor):
        if self.mostrando_pendentes:
            tarefa = self.tarefas[indice_tarefa]
            tarefa['concluida'] = valor

            # Só move a tarefa para concluída se foi marcada
            if valor:
                # Atraso de 5 segundos antes de mover para concluídas
                Clock.schedule_once(lambda dt: self.mover_para_concluidas(indice_tarefa), 5)

            salvar_tarefas(self.tarefas)
            self.atualizar_lista_tarefas()

    def mover_para_concluidas(self, indice_tarefa):
        #Move uma tarefa concluída para o arquivo de tarefas concluídas
        if 0 <= indice_tarefa < len(self.tarefas):
            tarefa_concluida = self.tarefas.pop(indice_tarefa)

            tarefas_concluidas = carregar_tarefas_concluidas()
            tarefas_concluidas.append(tarefa_concluida)
            salvar_tarefas_concluidas(tarefas_concluidas)

            salvar_tarefas(self.tarefas)
            self.atualizar_lista_tarefas()

    def remover_tarefa_concluida(self, indice_tarefa):
       #Remove uma tarefa da lista de tarefas concluídas
        tarefas_concluidas = carregar_tarefas_concluidas()
        if 0 <= indice_tarefa < len(tarefas_concluidas):
            del tarefas_concluidas[indice_tarefa]
            salvar_tarefas_concluidas(tarefas_concluidas)
            self.atualizar_lista_tarefas()

    def verificar_vencimento_tarefas(self, dt=None):
        #Verifica se há tarefas vencendo e envia notificações
        tarefas = carregar_tarefas()
        hoje = datetime.now().date()  # Obtém a data atual sem o horário

        for tarefa in tarefas:
            if tarefa.get('data_vencimento'):
                data_vencimento = datetime.strptime(tarefa['data_vencimento'], '%d/%m/%Y').date()

                if hoje == data_vencimento and not tarefa.get('notificacao_enviada', False):
                    enviar_notificacao(tarefa['texto'])
                    tarefa['notificacao_enviada'] = True  # Marca a tarefa como notificada
                    salvar_tarefas(tarefas)  # Salva a alteração no arquivo

    def tarefa_vencendo(self, data_vencimento_str):
        #Verifica se a tarefa está perto do vencimento (um dia antes ou no próprio dia)
        data_vencimento = datetime.strptime(data_vencimento_str, '%d/%m/%Y').date()
        hoje = datetime.now().date()

        return hoje == data_vencimento
