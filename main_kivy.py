"""
MAIN KIVY - Applicazione desktop Taskboard con Kivy
Bonus 2: GUI desktop con login, elenco task, aggiunta, modifica, cancellazione
"""

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.metrics import dp

from database import DatabaseManager
from model.model import User, Task

kivy.require('2.0.0')

class LoginScreen(Screen):
    """Schermata di login"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Titolo
        title = Label(
            text='TASKBOARD\nGestione Attività Personali',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(100),
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        
        # Form di login
        form_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        form_layout.add_widget(Label(text='Username:', size_hint_x=0.3))
        self.username_input = TextInput(multiline=False, size_hint_x=0.7)
        form_layout.add_widget(self.username_input)
        
        form_layout.add_widget(Label(text='Password:', size_hint_x=0.3))
        self.password_input = TextInput(password=True, multiline=False, size_hint_x=0.7)
        form_layout.add_widget(self.password_input)
        
        # Pulsanti
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        login_btn = Button(text='Login', size_hint_x=0.5)
        login_btn.bind(on_press=self.login)
        
        register_btn = Button(text='Registrati', size_hint_x=0.5)
        register_btn.bind(on_press=self.show_register)
        
        button_layout.add_widget(login_btn)
        button_layout.add_widget(register_btn)
        
        # Messaggio di stato
        self.status_label = Label(text='', size_hint_y=None, height=dp(30))
        
        # Assembla il layout
        main_layout.add_widget(title)
        main_layout.add_widget(Label())  # Spacer
        main_layout.add_widget(form_layout)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(self.status_label)
        main_layout.add_widget(Label())  # Spacer
        
        self.add_widget(main_layout)
    
    def set_database(self, db):
        self.db = db
    
    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text
        
        if not username or not password:
            self.show_message('Username e password sono obbligatori!', 'error')
            return
        
        user = self.db.get_user_by_username(username)
        if user and user.check_password(password):
            self.show_message(f'Benvenuto, {username}!', 'success')
            # Passa alla schermata principale
            app = App.get_running_app()
            app.current_user = user
            app.root.current = 'dashboard'
            app.root.get_screen('dashboard').refresh_tasks()
        else:
            self.show_message('Credenziali non valide!', 'error')
    
    def show_register(self, instance):
        self.manager.current = 'register'
    
    def show_message(self, message, msg_type='info'):
        if msg_type == 'error':
            self.status_label.color = (1, 0, 0, 1)  # Rosso
        elif msg_type == 'success':
            self.status_label.color = (0, 1, 0, 1)  # Verde
        else:
            self.status_label.color = (1, 1, 1, 1)  # Bianco
        
        self.status_label.text = message
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', ''), 3)


class RegisterScreen(Screen):
    """Schermata di registrazione"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Titolo
        title = Label(
            text='REGISTRAZIONE\nCrea il tuo account',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(80),
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        
        # Form di registrazione
        form_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(180))
        
        form_layout.add_widget(Label(text='Username:', size_hint_x=0.3))
        self.username_input = TextInput(multiline=False, size_hint_x=0.7)
        form_layout.add_widget(self.username_input)
        
        form_layout.add_widget(Label(text='Password:', size_hint_x=0.3))
        self.password_input = TextInput(password=True, multiline=False, size_hint_x=0.7)
        form_layout.add_widget(self.password_input)
        
        form_layout.add_widget(Label(text='Conferma Password:', size_hint_x=0.3))
        self.password_confirm_input = TextInput(password=True, multiline=False, size_hint_x=0.7)
        form_layout.add_widget(self.password_confirm_input)
        
        # Pulsanti
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        register_btn = Button(text='Registrati', size_hint_x=0.5)
        register_btn.bind(on_press=self.register)
        
        back_btn = Button(text='Torna al Login', size_hint_x=0.5)
        back_btn.bind(on_press=self.back_to_login)
        
        button_layout.add_widget(register_btn)
        button_layout.add_widget(back_btn)
        
        # Messaggio di stato
        self.status_label = Label(text='', size_hint_y=None, height=dp(30))
        
        # Assembla il layout
        main_layout.add_widget(title)
        main_layout.add_widget(Label())  # Spacer
        main_layout.add_widget(form_layout)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(self.status_label)
        main_layout.add_widget(Label())  # Spacer
        
        self.add_widget(main_layout)
    
    def set_database(self, db):
        self.db = db
    
    def register(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text
        password_confirm = self.password_confirm_input.text
        
        # Validazioni
        if not username or not password:
            self.show_message('Username e password sono obbligatori!', 'error')
            return
        
        if len(username) < 3:
            self.show_message('Username deve essere almeno 3 caratteri!', 'error')
            return
        
        if len(password) < 4:
            self.show_message('Password deve essere almeno 4 caratteri!', 'error')
            return
        
        if password != password_confirm:
            self.show_message('Le password non coincidono!', 'error')
            return
        
        # Verifica se l'username esiste già
        if self.db.get_user_by_username(username):
            self.show_message('Username già esistente!', 'error')
            return
        
        # Crea nuovo utente
        new_user = User(username=username)
        new_user.set_password(password)
        
        if self.db.create_user(new_user):
            self.show_message('Registrazione completata! Torna al login.', 'success')
            Clock.schedule_once(lambda dt: self.back_to_login(None), 2)
        else:
            self.show_message('Errore durante la registrazione!', 'error')
    
    def back_to_login(self, instance):
        self.manager.current = 'login'
    
    def show_message(self, message, msg_type='info'):
        if msg_type == 'error':
            self.status_label.color = (1, 0, 0, 1)  # Rosso
        elif msg_type == 'success':
            self.status_label.color = (0, 1, 0, 1)  # Verde
        else:
            self.status_label.color = (1, 1, 1, 1)  # Bianco
        
        self.status_label.text = message
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', ''), 3)


class DashboardScreen(Screen):
    """Schermata principale con lista task"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.current_user = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        self.title_label = Label(text='Dashboard', font_size=dp(18), size_hint_x=0.7)
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_x=0.3, spacing=dp(5))
        
        add_btn = Button(text='Nuovo Task', size_hint_x=0.5)
        add_btn.bind(on_press=self.add_task)
        
        logout_btn = Button(text='Logout', size_hint_x=0.5)
        logout_btn.bind(on_press=self.logout)
        
        button_layout.add_widget(add_btn)
        button_layout.add_widget(logout_btn)
        
        header_layout.add_widget(self.title_label)
        header_layout.add_widget(button_layout)
        
        # Lista task (scrollabile)
        self.task_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.task_layout.bind(minimum_height=self.task_layout.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.task_layout)
        
        # Assembla il layout
        main_layout.add_widget(header_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def set_database(self, db):
        self.db = db
    
    def set_user(self, user):
        self.current_user = user
        self.title_label.text = f'Dashboard - {user.username}'
    
    def refresh_tasks(self):
        if not self.current_user:
            return
        
        # Pulisce la lista
        self.task_layout.clear_widgets()
        
        # Carica i task
        tasks = self.db.get_tasks_by_user(self.current_user.user_id)
        
        if not tasks:
            no_tasks_label = Label(
                text='Nessun task trovato.\nClicca "Nuovo Task" per iniziare!',
                size_hint_y=None,
                height=dp(100),
                halign='center'
            )
            no_tasks_label.bind(size=no_tasks_label.setter('text_size'))
            self.task_layout.add_widget(no_tasks_label)
            return
        
        for task in tasks:
            task_widget = self.create_task_widget(task)
            self.task_layout.add_widget(task_widget)
    
    def create_task_widget(self, task):
        """Crea un widget per visualizzare un task"""
        task_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),
            padding=dp(5),
            spacing=dp(10)
        )
        
        # Informazioni task
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.6)
        
        title_label = Label(
            text=task.title,
            font_size=dp(16),
            size_hint_y=0.6,
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        desc_text = task.description[:50] + "..." if len(task.description) > 50 else task.description
        desc_label = Label(
            text=desc_text,
            font_size=dp(12),
            size_hint_y=0.4,
            halign='left',
            valign='middle',
            color=(0.7, 0.7, 0.7, 1)
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        
        info_layout.add_widget(title_label)
        info_layout.add_widget(desc_label)
        
        # Stato
        status_colors = {
            'ToDo': (1, 1, 0, 1),      # Giallo
            'Doing': (0, 0.5, 1, 1),   # Blu
            'Done': (0, 1, 0, 1)       # Verde
        }
        
        status_label = Label(
            text=task.status,
            size_hint_x=0.2,
            color=status_colors.get(task.status, (1, 1, 1, 1))
        )
        
        # Pulsanti azione
        action_layout = BoxLayout(orientation='vertical', size_hint_x=0.2, spacing=dp(2))
        
        edit_btn = Button(text='Modifica', size_hint_y=0.5)
        edit_btn.bind(on_press=lambda x: self.edit_task(task))
        
        delete_btn = Button(text='Elimina', size_hint_y=0.5)
        delete_btn.bind(on_press=lambda x: self.delete_task(task))
        
        action_layout.add_widget(edit_btn)
        action_layout.add_widget(delete_btn)
        
        # Assembla il widget
        task_layout.add_widget(info_layout)
        task_layout.add_widget(status_label)
        task_layout.add_widget(action_layout)
        
        return task_layout
    
    def add_task(self, instance):
        self.manager.current = 'add_task'
    
    def edit_task(self, task):
        app = App.get_running_app()
        app.current_task = task
        self.manager.current = 'edit_task'
    
    def delete_task(self, task):
        # Popup di conferma
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text=f'Eliminare il task "{task.title}"?'))
        
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        confirm_btn = Button(text='Elimina')
        cancel_btn = Button(text='Annulla')
        
        button_layout.add_widget(confirm_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)
        
        popup = Popup(title='Conferma Eliminazione', content=content, size_hint=(0.8, 0.4))
        
        def confirm_delete(instance):
            if self.db.delete_task(task.task_id):
                self.refresh_tasks()
            popup.dismiss()
        
        def cancel_delete(instance):
            popup.dismiss()
        
        confirm_btn.bind(on_press=confirm_delete)
        cancel_btn.bind(on_press=cancel_delete)
        
        popup.open()
    
    def logout(self, instance):
        app = App.get_running_app()
        app.current_user = None
        self.manager.current = 'login'


class AddTaskScreen(Screen):
    """Schermata per aggiungere un nuovo task"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Titolo
        title = Label(
            text='Nuovo Task',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Form
        form_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(200))
        
        form_layout.add_widget(Label(text='Titolo:', size_hint_x=0.3))
        self.title_input = TextInput(multiline=False, size_hint_x=0.7)
        form_layout.add_widget(self.title_input)
        
        form_layout.add_widget(Label(text='Descrizione:', size_hint_x=0.3))
        self.description_input = TextInput(multiline=True, size_hint_x=0.7)
        form_layout.add_widget(self.description_input)
        
        # Pulsanti
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        save_btn = Button(text='Salva', size_hint_x=0.5)
        save_btn.bind(on_press=self.save_task)
        
        cancel_btn = Button(text='Annulla', size_hint_x=0.5)
        cancel_btn.bind(on_press=self.cancel)
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        
        # Messaggio di stato
        self.status_label = Label(text='', size_hint_y=None, height=dp(30))
        
        # Assembla il layout
        main_layout.add_widget(title)
        main_layout.add_widget(form_layout)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(self.status_label)
        main_layout.add_widget(Label())  # Spacer
        
        self.add_widget(main_layout)
    
    def set_database(self, db):
        self.db = db
    
    def save_task(self, instance):
        title = self.title_input.text.strip()
        description = self.description_input.text.strip()
        
        if not title or len(title) < 3:
            self.show_message('Il titolo deve essere almeno 3 caratteri!', 'error')
            return
        
        app = App.get_running_app()
        if not app.current_user:
            self.show_message('Errore: utente non autenticato!', 'error')
            return
        
        new_task = Task(
            title=title,
            description=description,
            status=Task.STATUS_TODO,
            user_id=app.current_user.user_id
        )
        
        if self.db.create_task(new_task):
            self.show_message('Task creato con successo!', 'success')
            Clock.schedule_once(lambda dt: self.back_to_dashboard(), 1)
        else:
            self.show_message('Errore durante la creazione del task!', 'error')
    
    def cancel(self, instance):
        self.back_to_dashboard()
    
    def back_to_dashboard(self):
        # Pulisce i campi
        self.title_input.text = ''
        self.description_input.text = ''
        self.status_label.text = ''
        
        # Torna alla dashboard
        self.manager.current = 'dashboard'
        self.manager.get_screen('dashboard').refresh_tasks()
    
    def show_message(self, message, msg_type='info'):
        if msg_type == 'error':
            self.status_label.color = (1, 0, 0, 1)  # Rosso
        elif msg_type == 'success':
            self.status_label.color = (0, 1, 0, 1)  # Verde
        else:
            self.status_label.color = (1, 1, 1, 1)  # Bianco
        
        self.status_label.text = message


class EditTaskScreen(Screen):
    """Schermata per modificare un task esistente"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.current_task = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Titolo
        self.title_label = Label(
            text='Modifica Task',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Form
        form_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(240))
        
        form_layout.add_widget(Label(text='Titolo:', size_hint_x=0.3))
        self.title_input = TextInput(multiline=False, size_hint_x=0.7)
        form_layout.add_widget(self.title_input)
        
        form_layout.add_widget(Label(text='Descrizione:', size_hint_x=0.3))
        self.description_input = TextInput(multiline=True, size_hint_x=0.7)
        form_layout.add_widget(self.description_input)
        
        form_layout.add_widget(Label(text='Stato:', size_hint_x=0.3))
        self.status_spinner = Spinner(
            text='ToDo',
            values=['ToDo', 'Doing', 'Done'],
            size_hint_x=0.7
        )
        form_layout.add_widget(self.status_spinner)
        
        # Pulsanti
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        save_btn = Button(text='Salva', size_hint_x=0.5)
        save_btn.bind(on_press=self.save_task)
        
        cancel_btn = Button(text='Annulla', size_hint_x=0.5)
        cancel_btn.bind(on_press=self.cancel)
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        
        # Messaggio di stato
        self.status_label = Label(text='', size_hint_y=None, height=dp(30))
        
        # Assembla il layout
        main_layout.add_widget(self.title_label)
        main_layout.add_widget(form_layout)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(self.status_label)
        main_layout.add_widget(Label())  # Spacer
        
        self.add_widget(main_layout)
    
    def set_database(self, db):
        self.db = db
    
    def set_task(self, task):
        self.current_task = task
        self.title_label.text = f'Modifica Task: {task.title}'
        self.title_input.text = task.title
        self.description_input.text = task.description
        self.status_spinner.text = task.status
    
    def save_task(self, instance):
        if not self.current_task:
            return
        
        title = self.title_input.text.strip()
        description = self.description_input.text.strip()
        status = self.status_spinner.text
        
        if not title or len(title) < 3:
            self.show_message('Il titolo deve essere almeno 3 caratteri!', 'error')
            return
        
        self.current_task.update_content(title, description)
        self.current_task.update_status(status)
        
        if self.db.update_task(self.current_task):
            self.show_message('Task modificato con successo!', 'success')
            Clock.schedule_once(lambda dt: self.back_to_dashboard(), 1)
        else:
            self.show_message('Errore durante la modifica del task!', 'error')
    
    def cancel(self, instance):
        self.back_to_dashboard()
    
    def back_to_dashboard(self):
        self.status_label.text = ''
        self.manager.current = 'dashboard'
        self.manager.get_screen('dashboard').refresh_tasks()
    
    def show_message(self, message, msg_type='info'):
        if msg_type == 'error':
            self.status_label.color = (1, 0, 0, 1)  # Rosso
        elif msg_type == 'success':
            self.status_label.color = (0, 1, 0, 1)  # Verde
        else:
            self.status_label.color = (1, 1, 1, 1)  # Bianco
        
        self.status_label.text = message


class TaskboardApp(App):
    """Applicazione principale Kivy"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager("taskboard.db")
        self.current_user = None
        self.current_task = None
    
    def build(self):
        # Crea il manager delle schermate
        sm = ScreenManager()
        
        # Crea le schermate
        login_screen = LoginScreen(name='login')
        login_screen.set_database(self.db)
        
        register_screen = RegisterScreen(name='register')
        register_screen.set_database(self.db)
        
        dashboard_screen = DashboardScreen(name='dashboard')
        dashboard_screen.set_database(self.db)
        
        add_task_screen = AddTaskScreen(name='add_task')
        add_task_screen.set_database(self.db)
        
        edit_task_screen = EditTaskScreen(name='edit_task')
        edit_task_screen.set_database(self.db)
        
        # Aggiunge le schermate al manager
        sm.add_widget(login_screen)
        sm.add_widget(register_screen)
        sm.add_widget(dashboard_screen)
        sm.add_widget(add_task_screen)
        sm.add_widget(edit_task_screen)
        
        return sm
    
    def on_start(self):
        """Chiamato all'avvio dell'app"""
        # Imposta l'utente corrente nelle schermate che ne hanno bisogno
        dashboard_screen = self.root.get_screen('dashboard')
        if self.current_user:
            dashboard_screen.set_user(self.current_user)
        
        # Imposta il task corrente nella schermata di modifica
        edit_screen = self.root.get_screen('edit_task')
        if self.current_task:
            edit_screen.set_task(self.current_task)


if __name__ == '__main__':
    print("Avvio Taskboard Desktop Kivy...")
    print("GUI: Interfaccia desktop con login, gestione task e Kanban")
    
    TaskboardApp().run()