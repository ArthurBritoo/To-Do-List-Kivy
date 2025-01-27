import json
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from datetime import datetime, timedelta
from plyer import notification

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

def send_notification(task_text):
    notification.notify(
        title="Tarefa de To-Do",
        message=f"A tarefa '{task_text}' está prestes a vencer!",
        timeout=10
    )

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
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

        header_layout = BoxLayout(size_hint_y=None, height=60)
        header_label = Label(text="To-Do List", font_size=30, size_hint_y=None, height=40)
        header_checkbox = CheckBox(size_hint_y=None, height=40)
        header_layout.add_widget(header_label)
        header_layout.add_widget(header_checkbox)
        layout.add_widget(header_layout)

        tasks_button = Button(text="Ir para Adicionar Tarefa", size_hint_y=None, height=40)
        tasks_button.bind(on_press=self.go_to_tasks)
        layout.add_widget(tasks_button)

        self.task_list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.task_list_layout.bind(minimum_height=self.task_list_layout.setter('height'))
        scroll_view = ScrollView(size_hint=(1, None), size=(400, 300))
        scroll_view.add_widget(self.task_list_layout)
        layout.add_widget(scroll_view)

        self.update_task_list()

        back_button = Button(text="Voltar para a Tela Inicial", size_hint_y=None, height=40)
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_to_tasks(self, instance):
        self.manager.current = 'tasks'

    def go_back(self, instance):
        self.manager.current = 'welcome'

    def update_task_list(self):
        self.task_list_layout.clear_widgets()

        for index, task in enumerate(self.tasks):
            task_label = Label(text=task['text'], size_hint_y=None, height=40)

            checkbox = CheckBox(active=task['completed'], size_hint_y=None, height=40)
            checkbox.bind(active=lambda instance, value, task_index=index: self.toggle_task(task_index, value))

            task_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            task_layout.add_widget(checkbox)
            task_layout.add_widget(task_label)

            self.task_list_layout.add_widget(task_layout)

            if task.get('due_date') and self.is_task_approaching_due_date(task['due_date']):
                send_notification(task['text'])

    def toggle_task(self, task_index, completed):
        if 0 <= task_index < len(self.tasks):
            if completed:
                del self.tasks[task_index]
            else:
                self.tasks[task_index]['completed'] = False
            
            save_tasks(self.tasks)
            self.update_task_list()

    def is_task_approaching_due_date(self, due_date_str):
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M')
        return due_date - timedelta(days=1) <= datetime.now() <= due_date

class TaskScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.task_input = TextInput(hint_text='Digite uma tarefa', size_hint_y=None, height=40)
        layout.add_widget(self.task_input)

        self.due_date_input = TextInput(hint_text='Digite a data de vencimento (YYYY-MM-DD HH:MM)', size_hint_y=None, height=40)
        layout.add_widget(self.due_date_input)

        add_button = Button(text='Adicionar Tarefa', size_hint_y=None, height=40)
        add_button.bind(on_press=self.add_task)
        layout.add_widget(add_button)

        back_button = Button(text="Voltar para o Menu", size_hint_y=None, height=40)
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def add_task(self, instance):
        task_text = self.task_input.text.strip()
        due_date_text = self.due_date_input.text.strip()

        if task_text and due_date_text:
            try:
                due_date = datetime.strptime(due_date_text, '%Y-%m-%d %H:%M')

                task = {
                    'text': task_text,
                    'completed': False,
                    'due_date': due_date.strftime('%Y-%m-%d %H:%M')
                }
                tasks = load_tasks()
                tasks.append(task)
                save_tasks(tasks)
                self.task_input.text = ''
                self.due_date_input.text = ''

                menu_screen = self.manager.get_screen('menu')
                menu_screen.tasks = load_tasks()
                menu_screen.update_task_list()

            except ValueError:
                self.due_date_input.text = 'Formato de data inválido!'

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
