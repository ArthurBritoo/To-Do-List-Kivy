from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')  # Opcional: impede redimensionamento da janela

from kivymd.app import MDApp  
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from classes.tela_boas_vindas import TelaBoasVindas
from classes.tela_menu import TelaMenu
from classes.tela_tarefa import TelaTarefa

class GerenciadorTarefas(MDApp):  
    def build(self):
        gerenciador = ScreenManager(transition=FadeTransition(duration=0.2))
        gerenciador.add_widget(TelaBoasVindas(name='boas_vindas'))
        gerenciador.add_widget(TelaMenu(name='menu'))
        gerenciador.add_widget(TelaTarefa(name='tarefa'))
        gerenciador.current = 'boas_vindas'  # Tela inicial
        return gerenciador

if __name__ == "__main__":
    GerenciadorTarefas().run()
