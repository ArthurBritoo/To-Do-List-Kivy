from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from datetime import datetime, timedelta
from manipulador_json import carregar_tarefas, salvar_tarefas
from notificacoes import enviar_notificacao

class TelaMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            # Cor de fundo (branco)
            Color(1, 1, 1, 1)  
            self.rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
        self.tarefas = carregar_tarefas()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        cabecalho_layout = BoxLayout(size_hint_y=None, height=60)
        cabecalho_rotulo = Label(text="Lista de Tarefas", font_size=30, size_hint_y=None, height=40, color=(0, 0, 0, 1))
        cabecalho_layout.add_widget(cabecalho_rotulo)
        layout.add_widget(cabecalho_layout)

        botao_tarefas = Button(text="Adicionar Nova Tarefa", size_hint_y=None, height=40,background_color=(0, 1, 0, 1))
        botao_tarefas.bind(on_press=self.ir_para_tarefas)
        layout.add_widget(botao_tarefas)

        self.lista_tarefas_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.lista_tarefas_layout.bind(minimum_height=self.lista_tarefas_layout.setter('height'))
        area_rolagem = ScrollView(size_hint=(1, None), size=(400, 300))
        area_rolagem.add_widget(self.lista_tarefas_layout)
        layout.add_widget(area_rolagem)

        self.atualizar_lista_tarefas()

        botao_voltar = Button(text="Voltar à Tela Inicial", size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_voltar.bind(on_press=self.voltar)
        layout.add_widget(botao_voltar)

        self.add_widget(layout)

    def ir_para_tarefas(self, instancia):
        self.manager.current = 'tarefa'

    def voltar(self, instancia):
        self.manager.current = 'boas_vindas'

    def atualizar_lista_tarefas(self):
        self.lista_tarefas_layout.clear_widgets()

        for indice, tarefa in enumerate(self.tarefas):
            rotulo_tarefa = Label(text=tarefa['texto'], size_hint_y=None, height=40,font_size='24sp', color=(0, 0, 0, 1))
            checkbox = CheckBox(active=tarefa['concluida'], size_hint_y=None, height=40)
            checkbox.bind(active=lambda instancia, valor, indice_tarefa=indice: self.alternar_tarefa(indice_tarefa, valor))

            layout_tarefa = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            layout_tarefa.add_widget(checkbox)
            layout_tarefa.add_widget(rotulo_tarefa)

            self.lista_tarefas_layout.add_widget(layout_tarefa)

            if tarefa.get('data_vencimento') and self.tarefa_vencendo(tarefa['data_vencimento']):
                enviar_notificacao(tarefa['texto'])

    def alternar_tarefa(self, indice_tarefa, concluida):
        if 0 <= indice_tarefa < len(self.tarefas):
            if concluida:
                del self.tarefas[indice_tarefa]
                
            else:
                self.tarefas[indice_tarefa]['concluida'] = False

            salvar_tarefas(self.tarefas)
            self.atualizar_lista_tarefas()

    def tarefa_vencendo(self, data_vencimento_str):
        data_vencimento = datetime.strptime(data_vencimento_str, '%Y-%m-%d %H:%M')
        return data_vencimento - timedelta(days=1) <= datetime.now() <= data_vencimento

