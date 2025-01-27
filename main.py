import json
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen

def load_tasks():
    try:
        with open('tasks.json', 'r') as file:
            tasks = json.load(file)
            if not isinstance(tasks, list):
                tasks = []
            else:
                tasks = [task for task in tasks if isinstance(task, dict) and 'text' in task]
            return tasks
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open('tasks.json', 'w') as file:
        json.dump(tasks, file)

def create_header():
    header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=10, spacing=10)
    label = Label(text="To Do List", font_size=32, halign='left')
    checkbox = CheckBox(size_hint=(None, None), size=(30, 30))
    header.add_widget(label)
    header.add_widget(checkbox)
    return header

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(create_header())
        label = Label(text="Bem-vindo ao To-Do List!", size_hint_y=None, height=40)
        layout.add_widget(label)
        enter_button = Button(text="Entrar", size_hint_y=None, height=40)
        enter_button.bind(on_press=self.go_to_menu)
        layout.add_widget(enter_button)
        self.add_widget(layout)

    def go_to_menu(self, instance):
        self.manager.current = 'menu'

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks = load_tasks()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(create_header())
        tasks_button = Button(text="Ir para Adicionar Tarefa", size_hint_y=None, height=40)
        tasks_button.bind(on_press=self.go_to_tasks)
        layout.add_widget(tasks_button)
        self.task_list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.task_list_layout.bind(minimum_height=self.task_list_layout.setter('height'))
        scroll_view = ScrollView(size_hint=(1, None), size=(400, 300))
        scroll_view.add_widget(self.task_list_layout)
        layout.add_widget(scroll_view)
        back_button = Button(text="Voltar para a Tela Inicial", size_hint_y=None, height=40)
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)
        self.add_widget(layout)
        self.update_task_list()

    def go_to_tasks(self, instance):
        self.manager.current = 'tasks'

    def go_back(self, instance):
        self.manager.current = 'welcome'

    def update_task_list(self):
        self.tasks = load_tasks()
        self.task_list_layout.clear_widgets()
        for index, task in enumerate(self.tasks):
            task_label = Label(text=task['text'], size_hint_y=None, height=40)
            checkbox = CheckBox(active=task.get('completed', False), size_hint_y=None, height=40)
            checkbox.bind(active=lambda instance, value, task_index=index: self.toggle_task(task_index, value))
            task_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            task_layout.add_widget(checkbox)
            task_layout.add_widget(task_label)
            self.task_list_layout.add_widget(task_layout)

    def toggle_task(self, task_index, completed):
        if 0 <= task_index < len(self.tasks):
            if completed:
                del self.tasks[task_index]
            save_tasks(self.tasks)
            self.update_task_list()

class TaskScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(create_header())
        self.task_input = TextInput(hint_text='Digite uma tarefa', size_hint_y=None, height=40)
        layout.add_widget(self.task_input)
        add_button = Button(text='Adicionar Tarefa', size_hint_y=None, height=40)
        add_button.bind(on_press=self.add_task)
        layout.add_widget(add_button)
        back_button = Button(text="Voltar para o Menu", size_hint_y=None, height=40)
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def add_task(self, instance):
        task_text = self.task_input.text.strip()
        if task_text:
            task = {'text': task_text, 'completed': False}
            tasks = load_tasks()
            tasks.append(task)
            save_tasks(tasks)
            menu_screen = self.manager.get_screen('menu')
            menu_screen.update_task_list()
            self.task_input.text = ''

    def go_back(self, instance):
        self.manager.current = 'menu'

class TaskApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(WelcomeScreen(name='welcome'))
        self.screen_manager.add_widget(MenuScreen(name='menu'))
        self.screen_manager.add_widget(TaskScreen(name='tasks'))
        return self.screen_manager

if __name__ == "__main__":
    TaskApp().run()
