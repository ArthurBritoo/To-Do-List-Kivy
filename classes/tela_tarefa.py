from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from datetime import datetime
from manipulador_json import carregar_tarefas, salvar_tarefas
from kivy.core.window import Window

class TelaTarefa(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.entrada_tarefa = TextInput(hint_text='Digite uma nova tarefa', size_hint_y=None, height=40)
        layout.add_widget(self.entrada_tarefa)

        self.entrada_data = TextInput(hint_text='Escolha uma data', size_hint_y=None, height=40, readonly=True)
        layout.add_widget(self.entrada_data)

        self.entrada_hora = TextInput(hint_text='Escolha um horário', size_hint_y=None, height=40, readonly=True)
        layout.add_widget(self.entrada_hora)

        botao_data = Button(text="Selecionar Data", size_hint_y=None, height=40, background_color=(0, 0, 1, 1))
        botao_data.bind(on_press=self.show_date_picker)
        layout.add_widget(botao_data)

        botao_hora = Button(text="Selecionar Horário", size_hint_y=None, height=40, background_color=(0, 0, 1, 1))
        botao_hora.bind(on_press=self.show_time_picker)
        layout.add_widget(botao_hora)

        botao_adicionar = Button(text='Adicionar', size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_adicionar.bind(on_press=self.adicionar_tarefa)
        layout.add_widget(botao_adicionar)

        botao_voltar = Button(text="Voltar para o Menu", size_hint_y=None, height=40, background_color=(0, 1, 0, 1))
        botao_voltar.bind(on_press=self.voltar)
        layout.add_widget(botao_voltar)

        self.add_widget(layout)

        with self.canvas.before:
            self.bg = Rectangle(source="classes/fundo2.jpg", size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        # Corrigindo a posição e o tamanho da imagem
        if hasattr(self, 'bg'):
            self.bg.pos = self.pos
            self.bg.size = self.size

    def show_date_picker(self, instance):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save_date)
        date_dialog.open()

    def on_save_date(self, instance, value, date_range):
        self.entrada_data.text = value.strftime('%d/%m/%Y')

    def show_time_picker(self, instance):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.on_save_time)
        time_dialog.open()

    def on_save_time(self, instance, time):
        self.entrada_hora.text = time.strftime('%H:%M')

    def adicionar_tarefa(self, instancia):
        texto_tarefa = self.entrada_tarefa.text.strip()
        texto_data = self.entrada_data.text.strip()
        texto_hora = self.entrada_hora.text.strip()

        if texto_tarefa and texto_data and texto_hora:
            try:
                data_vencimento = datetime.strptime(texto_data, '%d/%m/%Y')
                hora_vencimento = datetime.strptime(texto_hora, '%H:%M')
                nova_tarefa = {
                    'texto': texto_tarefa,
                    'concluida': False,
                    'data_vencimento': data_vencimento.strftime('%d/%m/%Y'),
                    'hora_vencimento': hora_vencimento.strftime('%H:%M')
                }
                tarefas = carregar_tarefas()
                tarefas.append(nova_tarefa)
                salvar_tarefas(tarefas)

                self.entrada_tarefa.text = ''
                self.entrada_data.text = ''
                self.entrada_hora.text = ''

                tela_menu = self.manager.get_screen('menu')
                tela_menu.tarefas = carregar_tarefas()
                tela_menu.atualizar_lista_tarefas()

            except ValueError:
                self.entrada_data.text = 'Formato inválido!'

    def voltar(self, instancia):
        self.manager.current = 'menu'
