from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
class TelaBoasVindas(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(1, 1, 1, 1)  
            self.rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        rotulo = Label(text="Bem-vindo ao Gerenciador de Tarefas!", font_size=24, size_hint_y=None, height=40,color=(0, 0, 0, 1))
        layout.add_widget(rotulo)

        botao_entrar = Button(text="Entrar", size_hint_y=None, height=40,background_color=(0, 1, 0, 1))
        botao_entrar.bind(on_press=self.ir_para_menu)
        layout.add_widget(botao_entrar)

        self.add_widget(layout)

    def ir_para_menu(self, instancia):
        self.manager.current = 'menu'
