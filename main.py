from kivymd.app import MDApp  # Importe MDApp corretamente
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from classes.tela_boas_vindas import TelaBoasVindas
from classes.tela_menu import TelaMenu
from classes.tela_tarefa import TelaTarefa

class GerenciadorTarefas(MDApp):  # Herde de MDApp
    def build(self):
        gerenciador = ScreenManager(transition=FadeTransition(duration=0.5))
        gerenciador.add_widget(TelaBoasVindas(name='boas_vindas'))
        gerenciador.add_widget(TelaMenu(name='menu'))
        gerenciador.add_widget(TelaTarefa(name='tarefa'))
        gerenciador.current = 'boas_vindas'  # Define a tela inicial
        return gerenciador

if __name__ == "__main__":
    GerenciadorTarefas().run()