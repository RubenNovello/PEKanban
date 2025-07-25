# kivy_app.py - Interfaccia desktop con Kivy per Taskboard
# Applicazione GUI desktop con supporto navigazione da tastiera

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
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from database import DatabaseManager
from model import User, Task, Admin
from utils import validate_email, validate_password_strength, validate_username

# Imposta dimensioni finestra
Window.size = (1200, 800)
Window.minimum_width = 800
Window.minimum_height = 600

class LoginScreen(Screen):
    """Schermata di login"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        
        # Layout principale
        main_layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # Titolo
        title = Label(
            text='TASKBOARD - LOGIN',
            font_size='24sp',
            size_hint_y=None,
            height=dp(60),
            color=(0.2, 0.4, 0.8, 1)
        )
        main_layout.add_widget(title)
        
        # Form di login
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Username
        form_layout.add_widget(Label(text='Username:', size_hint_y=None, height=dp(40)))
        self.username_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.username_input)
        
        # Password
        form_layout.add_widget(Label(text='Password:', size_hint_y=None, height=dp(40)))
        self.password_input = TextInput(
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.password_input)
        
        main_layout.add_widget(form_layout)
        
        # Pulsanti
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(50))
        
        self.login_btn = Button(text='Login', size_hint_x=0.5)
        self.login_btn.bind(on_press=self.do_login)
        button_layout.add_widget(self.login_btn)
        
        self.register_btn = Button(text='Registrazione', size_hint_x=0.5)
        self.register_btn.bind(on_press=self.go_to_register)
        button_layout.add_widget(self.register_btn)
        
        main_layout.add_widget(button_layout)
        
        # Info primo utente
        demo_info = Label(
            text='Il primo utente registrato diventa automaticamente amministratore',
            font_size='12sp',
            size_hint_y=None,
            height=dp(30),
            color=(0.6, 0.6, 0.6, 1)
        )
        main_layout.add_widget(demo_info)
        
        # Messaggio di stato
        self.status_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30),
            color=(1, 0, 0, 1)
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
        
        # Bind eventi tastiera
        self.username_input.bind(on_text_validate=self.focus_password)
        self.password_input.bind(on_text_validate=self.do_login)
    
    def on_enter(self):
        """Chiamato quando si entra nella schermata - imposta il focus"""
        Clock.schedule_once(self.set_focus, 0.1)
    
    def set_focus(self, dt):
        """Imposta il focus sul campo username"""
        self.username_input.focus = True
    
    def focus_password(self, instance):
        """Sposta focus alla password quando si preme Tab/Enter su username"""
        self.password_input.focus = True
    
    def do_login(self, instance=None):
        """Esegue il login"""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.status_label.text = 'Username e password sono obbligatori'
            return
        
        # Autentica utente
        app = App.get_running_app()
        user = app.db.authenticate_user(username, password)
        
        if user:
            app.current_user = user
            app.root.current = 'dashboard'
            self.status_label.text = ''
            # Pulisci i campi
            self.username_input.text = ''
            self.password_input.text = ''
        else:
            self.status_label.text = 'Credenziali non valide'
    
    def go_to_register(self, instance):
        """Vai alla schermata di registrazione"""
        self.manager.current = 'register'

class RegisterScreen(Screen):
    """Schermata di registrazione"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'register'
        
        # Layout principale
        main_layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # Titolo
        title = Label(
            text='REGISTRAZIONE NUOVO UTENTE',
            font_size='24sp',
            size_hint_y=None,
            height=dp(60),
            color=(0.2, 0.8, 0.4, 1)
        )
        main_layout.add_widget(title)
        
        # Form di registrazione
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Username
        form_layout.add_widget(Label(text='Username:', size_hint_y=None, height=dp(40)))
        self.username_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.username_input)
        
        # Email
        form_layout.add_widget(Label(text='Email:', size_hint_y=None, height=dp(40)))
        self.email_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.email_input)
        
        # Password
        form_layout.add_widget(Label(text='Password:', size_hint_y=None, height=dp(40)))
        self.password_input = TextInput(
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.password_input)
        
        # Conferma Password
        form_layout.add_widget(Label(text='Conferma Password:', size_hint_y=None, height=dp(40)))
        self.confirm_password_input = TextInput(
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.confirm_password_input)
        
        main_layout.add_widget(form_layout)
        
        # Pulsanti
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(50))
        
        self.register_btn = Button(text='Registrati', size_hint_x=0.5)
        self.register_btn.bind(on_press=self.do_register)
        button_layout.add_widget(self.register_btn)
        
        self.back_btn = Button(text='Torna al Login', size_hint_x=0.5)
        self.back_btn.bind(on_press=self.go_to_login)
        button_layout.add_widget(self.back_btn)
        
        main_layout.add_widget(button_layout)
        
        # Messaggio di stato
        self.status_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30),
            color=(1, 0, 0, 1)
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
        
        # Bind eventi tastiera per navigazione con Tab
        self.username_input.bind(on_text_validate=self.focus_email)
        self.email_input.bind(on_text_validate=self.focus_password)
        self.password_input.bind(on_text_validate=self.focus_confirm_password)
        self.confirm_password_input.bind(on_text_validate=self.do_register)
    
    def on_enter(self):
        """Chiamato quando si entra nella schermata - imposta il focus"""
        Clock.schedule_once(self.set_focus, 0.1)
    
    def set_focus(self, dt):
        """Imposta il focus sul campo username"""
        self.username_input.focus = True
    
    def focus_email(self, instance):
        self.email_input.focus = True
    
    def focus_password(self, instance):
        self.password_input.focus = True
    
    def focus_confirm_password(self, instance):
        self.confirm_password_input.focus = True
    
    def do_register(self, instance=None):
        """Esegue la registrazione"""
        username = self.username_input.text.strip()
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()
        
        # Validazione
        if not all([username, email, password, confirm_password]):
            self.status_label.text = 'Tutti i campi sono obbligatori'
            return
        
        if password != confirm_password:
            self.status_label.text = 'Le password non coincidono'
            return
        
        # Validazione username
        valid_username, msg = validate_username(username)
        if not valid_username:
            self.status_label.text = msg
            return
        
        # Validazione email
        if not validate_email(email):
            self.status_label.text = 'Formato email non valido'
            return
        
        # Validazione password
        valid_password, msg = validate_password_strength(password)
        if not valid_password:
            self.status_label.text = msg
            return
        
        # Verifica se utente esiste già
        app = App.get_running_app()
        if app.db.user_exists(username, email):
            self.status_label.text = 'Username o email già esistenti'
            return
        
        # Verifica se è il primo utente (diventa admin automaticamente)
        is_first_user = app.db.is_first_user()
        
        if is_first_user:
            # Il primo utente diventa admin
            user = Admin(username, email, password)
            success_message = 'Registrazione completata! Sei il primo utente e hai privilegi di amministratore. Torna al login.'
        else:
            # Utenti successivi sono normali
            user = User(username, email, password)
            success_message = 'Registrazione completata! Torna al login.'
        
        if app.db.create_user(user):
            self.status_label.text = success_message
            self.status_label.color = (0, 1, 0, 1)  # Verde per successo
            # Pulisci i campi
            self.username_input.text = ''
            self.email_input.text = ''
            self.password_input.text = ''
            self.confirm_password_input.text = ''
        else:
            self.status_label.text = 'Errore durante la registrazione'
    
    def go_to_login(self, instance):
        """Torna alla schermata di login"""
        self.manager.current = 'login'

class DashboardScreen(Screen):
    """Schermata dashboard principale"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'dashboard'
        
        # Layout principale
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header con titolo e logout
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        self.title_label = Label(
            text='DASHBOARD TASKBOARD',
            font_size='20sp',
            color=(0.2, 0.4, 0.8, 1),
            size_hint_x=0.7
        )
        header_layout.add_widget(self.title_label)
        
        self.user_label = Label(
            text='',
            font_size='14sp',
            size_hint_x=0.2
        )
        header_layout.add_widget(self.user_label)
        
        logout_btn = Button(text='Logout', size_hint_x=0.1)
        logout_btn.bind(on_press=self.do_logout)
        header_layout.add_widget(logout_btn)
        
        main_layout.add_widget(header_layout)
        
        # Pannello con tab
        self.tab_panel = TabbedPanel(do_default_tab=False)
        
        # Tab Task
        self.tasks_tab = TabbedPanelItem(text='I Miei Task')
        self.setup_tasks_tab()
        self.tab_panel.add_widget(self.tasks_tab)
        
        # Tab Aggiungi Task
        self.add_task_tab = TabbedPanelItem(text='Nuovo Task')
        self.setup_add_task_tab()
        self.tab_panel.add_widget(self.add_task_tab)
        
        # Tab Admin (se admin)
        self.admin_tab = None
        
        main_layout.add_widget(self.tab_panel)
        
        self.add_widget(main_layout)
    
    def setup_tasks_tab(self):
        """Configura il tab dei task"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Filtri
        filter_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=10)
        
        filter_layout.add_widget(Label(text='Filtro:', size_hint_x=None, width=dp(60)))
        
        self.status_filter = Spinner(
            text='Tutti',
            values=['Tutti', 'To Do', 'Doing', 'Done'],
            size_hint_x=0.3
        )
        self.status_filter.bind(text=self.filter_tasks)
        filter_layout.add_widget(self.status_filter)
        
        refresh_btn = Button(text='Aggiorna', size_hint_x=0.2)
        refresh_btn.bind(on_press=self.refresh_tasks)
        filter_layout.add_widget(refresh_btn)
        
        layout.add_widget(filter_layout)
        
        # Lista task (scrollabile)
        self.tasks_scroll = ScrollView()
        self.tasks_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.tasks_layout.bind(minimum_height=self.tasks_layout.setter('height'))
        self.tasks_scroll.add_widget(self.tasks_layout)
        
        layout.add_widget(self.tasks_scroll)
        
        self.tasks_tab.content = layout
    
    def setup_add_task_tab(self):
        """Configura il tab per aggiungere task"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Form
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Titolo
        form_layout.add_widget(Label(text='Titolo:', size_hint_y=None, height=dp(40)))
        self.new_task_title = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.new_task_title)
        
        # Descrizione
        form_layout.add_widget(Label(text='Descrizione:', size_hint_y=None, height=dp(120)))
        self.new_task_description = TextInput(
            multiline=True,
            size_hint_y=None,
            height=dp(120)
        )
        form_layout.add_widget(self.new_task_description)
        
        layout.add_widget(form_layout)
        
        # Pulsante
        add_btn = Button(text='Crea Task', size_hint_y=None, height=dp(50))
        add_btn.bind(on_press=self.add_task)
        layout.add_widget(add_btn)
        
        # Messaggio di stato
        self.add_task_status = Label(
            text='',
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.add_task_status)
        
        self.add_task_tab.content = layout
    
    def on_enter(self):
        """Chiamato quando si entra nella schermata"""
        app = App.get_running_app()
        if app.current_user:
            user_info = f"Utente: {app.current_user.username}"
            if app.current_user.is_admin:
                user_info += " (Admin)"
                self.setup_admin_tab()
            self.user_label.text = user_info
            self.refresh_tasks()
    
    def setup_admin_tab(self):
        """Configura il tab admin se non esiste"""
        if self.admin_tab is None:
            self.admin_tab = TabbedPanelItem(text='Admin')
            
            layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            # Statistiche
            stats_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=dp(100))
            
            app = App.get_running_app()
            stats = app.db.get_database_stats()
            
            stats_layout.add_widget(Label(text=f"Utenti Totali: {stats['total_users']}"))
            stats_layout.add_widget(Label(text=f"Admin: {stats['admin_users']}"))
            stats_layout.add_widget(Label(text=f"Task Totali: {stats['total_tasks']}"))
            stats_layout.add_widget(Label(text=f"Task Completati: {stats['done_tasks']}"))
            
            layout.add_widget(stats_layout)
            
            # Pulsanti azioni admin
            admin_actions_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=dp(50))
            
            create_user_btn = Button(text='Crea Nuovo Utente')
            create_user_btn.bind(on_press=self.show_create_user_popup)
            admin_actions_layout.add_widget(create_user_btn)
            
            assign_task_btn = Button(text='Assegna Task')
            assign_task_btn.bind(on_press=self.show_assign_task_popup)
            admin_actions_layout.add_widget(assign_task_btn)
            
            view_all_tasks_btn = Button(text='Visualizza Tutti i Task')
            view_all_tasks_btn.bind(on_press=self.show_all_tasks_popup)
            admin_actions_layout.add_widget(view_all_tasks_btn)
            
            manage_user_tasks_btn = Button(text='Gestisci Task Utenti')
            manage_user_tasks_btn.bind(on_press=self.show_manage_user_tasks_popup)
            admin_actions_layout.add_widget(manage_user_tasks_btn)
            
            layout.add_widget(admin_actions_layout)
            
            # Lista utenti
            users_label = Label(text='Gestione Utenti', size_hint_y=None, height=dp(30))
            layout.add_widget(users_label)
            
            users_scroll = ScrollView()
            self.users_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
            self.users_layout.bind(minimum_height=self.users_layout.setter('height'))
            users_scroll.add_widget(self.users_layout)
            
            layout.add_widget(users_scroll)
            
            self.admin_tab.content = layout
            self.tab_panel.add_widget(self.admin_tab)
            
            self.refresh_users()
    
    def refresh_tasks(self, instance=None):
        """Aggiorna la lista dei task"""
        app = App.get_running_app()
        if not app.current_user:
            return
        
        # Ottieni task dell'utente
        if app.current_user.is_admin:
            tasks = app.db.get_all_tasks()
        else:
            tasks = app.db.get_user_tasks(app.current_user.user_id)
        
        # Filtra per stato se necessario
        if hasattr(self, 'status_filter') and self.status_filter.text != 'Tutti':
            tasks = [t for t in tasks if t.status == self.status_filter.text]
        
        # Pulisci layout
        self.tasks_layout.clear_widgets()
        
        # Aggiungi task
        for task in tasks:
            task_widget = self.create_task_widget(task)
            self.tasks_layout.add_widget(task_widget)
        
        if not tasks:
            no_tasks_label = Label(
                text='Nessun task trovato',
                size_hint_y=None,
                height=dp(50),
                color=(0.6, 0.6, 0.6, 1)
            )
            self.tasks_layout.add_widget(no_tasks_label)
    
    def create_task_widget(self, task):
        """Crea widget per un singolo task"""
        # Layout principale del task
        task_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),
            spacing=10,
            padding=5
        )
        
        # Colore di sfondo basato sullo stato
        with task_layout.canvas.before:
            Color(*self.get_status_color(task.status))
            Rectangle(pos=task_layout.pos, size=task_layout.size)
        
        # Informazioni task
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        title_label = Label(
            text=task.title,
            font_size='16sp',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        info_layout.add_widget(title_label)
        
        details_text = f"Stato: {task.status} | Creato: {task.created_at.strftime('%d/%m/%Y')}"
        if task.description:
            details_text += f"\n{task.description[:50]}..."
        
        details_label = Label(
            text=details_text,
            font_size='12sp',
            text_size=(None, None),
            halign='left',
            valign='top',
            color=(0.6, 0.6, 0.6, 1)
        )
        info_layout.add_widget(details_label)
        
        task_layout.add_widget(info_layout)
        
        # Pulsanti azione
        actions_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=5)
        
        # Pulsante cambia stato
        status_btn = Button(text='Cambia Stato', size_hint_y=0.5)
        status_btn.bind(on_press=lambda x: self.change_task_status(task))
        actions_layout.add_widget(status_btn)
        
        # Pulsante elimina
        delete_btn = Button(text='Elimina', size_hint_y=0.5)
        delete_btn.bind(on_press=lambda x: self.delete_task(task))
        actions_layout.add_widget(delete_btn)
        
        task_layout.add_widget(actions_layout)
        
        return task_layout
    
    def get_status_color(self, status):
        """Restituisce il colore per lo stato del task"""
        colors = {
            'To Do': (1, 0.8, 0.8, 0.3),      # Rosso chiaro
            'Doing': (1, 1, 0.8, 0.3),       # Giallo chiaro
            'Done': (0.8, 1, 0.8, 0.3)       # Verde chiaro
        }
        return colors.get(status, (0.9, 0.9, 0.9, 0.3))
    
    def filter_tasks(self, spinner, text):
        """Filtra i task per stato"""
        self.refresh_tasks()
    
    def add_task(self, instance):
        """Aggiunge un nuovo task"""
        title = self.new_task_title.text.strip()
        description = self.new_task_description.text.strip()
        
        if not title:
            self.add_task_status.text = 'Il titolo è obbligatorio'
            self.add_task_status.color = (1, 0, 0, 1)
            return
        
        app = App.get_running_app()
        task = Task(title, description, app.current_user.user_id)
        
        if app.db.create_task(task):
            self.add_task_status.text = 'Task creato con successo!'
            self.add_task_status.color = (0, 1, 0, 1)
            # Pulisci i campi
            self.new_task_title.text = ''
            self.new_task_description.text = ''
            # Aggiorna la lista
            self.refresh_tasks()
        else:
            self.add_task_status.text = 'Errore durante la creazione del task'
            self.add_task_status.color = (1, 0, 0, 1)
    
    def change_task_status(self, task):
        """Cambia lo stato di un task con popup di selezione"""
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=f'Cambia stato del task: "{task.title}"'))
        
        # Spinner per selezione stato
        status_spinner = Spinner(
            text=task.status,
            values=['To Do', 'Doing', 'Done'],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(status_spinner)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        
        confirm_btn = Button(text='Conferma')
        cancel_btn = Button(text='Annulla')
        
        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Cambia Stato Task',
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        def confirm_change(instance):
            new_status = status_spinner.text
            if new_status != task.status:
                task.update_status(new_status)
                app = App.get_running_app()
                if app.db.update_task(task):
                    self.refresh_tasks()
                    self.show_message(f"Stato cambiato in: {new_status}", "success")
                else:
                    self.show_message("Errore durante l'aggiornamento", "error")
            popup.dismiss()
        
        def cancel_change(instance):
            popup.dismiss()
        
        confirm_btn.bind(on_press=confirm_change)
        cancel_btn.bind(on_press=cancel_change)
        
        popup.open()
    
    def delete_task(self, task):
        """Elimina un task"""
        # Conferma eliminazione
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=f'Eliminare il task "{task.title}"?'))
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        
        confirm_btn = Button(text='Sì')
        cancel_btn = Button(text='No')
        
        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Conferma Eliminazione',
            content=content,
            size_hint=(0.6, 0.4)
        )
        
        def confirm_delete(instance):
            app = App.get_running_app()
            if app.db.delete_task(task.task_id):
                self.refresh_tasks()
            popup.dismiss()
        
        def cancel_delete(instance):
            popup.dismiss()
        
        confirm_btn.bind(on_press=confirm_delete)
        cancel_btn.bind(on_press=cancel_delete)
        
        popup.open()
    
    def refresh_users(self):
        """Aggiorna la lista degli utenti (admin)"""
        if not hasattr(self, 'users_layout'):
            return
        
        app = App.get_running_app()
        users = app.db.get_all_users()
        
        self.users_layout.clear_widgets()
        
        for user in users:
            user_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(60),
                spacing=5
            )
            
            user_info = f"{user.username} ({user.email})"
            if user.is_admin:
                user_info += " - ADMIN"
            
            user_label = Label(text=user_info, size_hint_x=0.5)
            user_layout.add_widget(user_label)
            
            if user.user_id != app.current_user.user_id:
                # Pulsante gestisci
                manage_btn = Button(text='Gestisci', size_hint_x=0.2)
                manage_btn.bind(on_press=lambda x, u=user: self.show_manage_user_popup(u))
                user_layout.add_widget(manage_btn)
                
                # Pulsante elimina
                delete_user_btn = Button(text='Elimina', size_hint_x=0.2)
                delete_user_btn.bind(on_press=lambda x, u=user: self.confirm_delete_user(u))
                user_layout.add_widget(delete_user_btn)
            else:
                # Spazio vuoto per l'utente corrente
                user_layout.add_widget(Label(text='(Tu)', size_hint_x=0.4))
            
            self.users_layout.add_widget(user_layout)
    
    def confirm_delete_user(self, user):
        """Conferma eliminazione utente"""
        app = App.get_running_app()
        user_tasks = app.db.get_user_tasks(user.user_id)
        
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=f'Eliminare l\'utente "{user.username}"?'))
        content.add_widget(Label(text=f'Verranno eliminati anche {len(user_tasks)} task associati.'))
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        
        confirm_btn = Button(text='Sì, Elimina')
        cancel_btn = Button(text='Annulla')
        
        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Conferma Eliminazione Utente',
            content=content,
            size_hint=(0.7, 0.5)
        )
        
        def confirm_delete(instance):
            if app.db.delete_user_and_tasks(user.user_id):
                self.refresh_users()
                self.refresh_tasks()
                self.show_message(f"Utente {user.username} eliminato con successo", "success")
            else:
                self.show_message("Errore durante l'eliminazione", "error")
            popup.dismiss()
        
        def cancel_delete(instance):
            popup.dismiss()
        
        confirm_btn.bind(on_press=confirm_delete)
        cancel_btn.bind(on_press=cancel_delete)
        
        popup.open()
    
    def show_create_user_popup(self, instance):
        """Mostra popup per creare nuovo utente"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Form
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Username
        form_layout.add_widget(Label(text='Username:', size_hint_y=None, height=dp(40)))
        username_input = TextInput(multiline=False, size_hint_y=None, height=dp(40))
        form_layout.add_widget(username_input)
        
        # Email
        form_layout.add_widget(Label(text='Email:', size_hint_y=None, height=dp(40)))
        email_input = TextInput(multiline=False, size_hint_y=None, height=dp(40))
        form_layout.add_widget(email_input)
        
        # Password
        form_layout.add_widget(Label(text='Password:', size_hint_y=None, height=dp(40)))
        password_input = TextInput(password=True, multiline=False, size_hint_y=None, height=dp(40))
        form_layout.add_widget(password_input)
        
        # Tipo utente
        form_layout.add_widget(Label(text='Tipo:', size_hint_y=None, height=dp(40)))
        user_type_spinner = Spinner(
            text='Utente Normale',
            values=['Utente Normale', 'Amministratore'],
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(user_type_spinner)
        
        content.add_widget(form_layout)
        
        # Messaggio di stato
        status_label = Label(text='', size_hint_y=None, height=dp(30), color=(1, 0, 0, 1))
        content.add_widget(status_label)
        
        # Pulsanti
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        
        create_btn = Button(text='Crea Utente')
        cancel_btn = Button(text='Annulla')
        
        buttons_layout.add_widget(create_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Crea Nuovo Utente',
            content=content,
            size_hint=(0.8, 0.8)
        )
        
        def create_user(instance):
            username = username_input.text.strip()
            email = email_input.text.strip()
            password = password_input.text.strip()
            is_admin = user_type_spinner.text == 'Amministratore'
            
            # Validazione
            if not all([username, email, password]):
                status_label.text = 'Tutti i campi sono obbligatori'
                return
            
            if len(password) < 6:
                status_label.text = 'La password deve essere di almeno 6 caratteri'
                return
            
            app = App.get_running_app()
            if app.db.user_exists(username, email):
                status_label.text = 'Username o email già esistenti'
                return
            
            # Crea utente
            if is_admin:
                user = Admin(username, email, password)
            else:
                user = User(username, email, password)
            
            if app.db.create_user(user):
                self.refresh_users()
                self.show_message(f"Utente {username} creato con successo", "success")
                popup.dismiss()
            else:
                status_label.text = 'Errore durante la creazione dell\'utente'
        
        def cancel_create(instance):
            popup.dismiss()
        
        create_btn.bind(on_press=create_user)
        cancel_btn.bind(on_press=cancel_create)
        
        popup.open()
    
    def show_assign_task_popup(self, instance):
        """Mostra popup per assegnare task a utente"""
        app = App.get_running_app()
        users = app.db.get_all_users()
        
        if not users:
            self.show_message("Nessun utente trovato", "error")
            return
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Selezione utente
        content.add_widget(Label(text='Seleziona utente:', size_hint_y=None, height=dp(30)))
        user_spinner = Spinner(
            text='Seleziona...',
            values=[f"{u.username} ({u.email})" for u in users],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(user_spinner)
        
        # Form task
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Titolo
        form_layout.add_widget(Label(text='Titolo:', size_hint_y=None, height=dp(40)))
        title_input = TextInput(multiline=False, size_hint_y=None, height=dp(40))
        form_layout.add_widget(title_input)
        
        # Descrizione
        form_layout.add_widget(Label(text='Descrizione:', size_hint_y=None, height=dp(80)))
        description_input = TextInput(multiline=True, size_hint_y=None, height=dp(80))
        form_layout.add_widget(description_input)
        
        content.add_widget(form_layout)
        
        # Messaggio di stato
        status_label = Label(text='', size_hint_y=None, height=dp(30), color=(1, 0, 0, 1))
        content.add_widget(status_label)
        
        # Pulsanti
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        
        assign_btn = Button(text='Assegna Task')
        cancel_btn = Button(text='Annulla')
        
        buttons_layout.add_widget(assign_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Assegna Task a Utente',
            content=content,
            size_hint=(0.8, 0.7)
        )
        
        def assign_task(instance):
            if user_spinner.text == 'Seleziona...':
                status_label.text = 'Seleziona un utente'
                return
            
            title = title_input.text.strip()
            description = description_input.text.strip()
            
            if not title:
                status_label.text = 'Il titolo è obbligatorio'
                return
            
            # Trova utente selezionato
            selected_user = None
            for user in users:
                if f"{user.username} ({user.email})" == user_spinner.text:
                    selected_user = user
                    break
            
            if not selected_user:
                status_label.text = 'Utente non trovato'
                return
            
            # Crea task
            task = Task(title, description, selected_user.user_id)
            
            if app.db.create_task(task):
                self.refresh_tasks()
                self.show_message(f"Task assegnato a {selected_user.username}", "success")
                popup.dismiss()
            else:
                status_label.text = 'Errore durante l\'assegnazione del task'
        
        def cancel_assign(instance):
            popup.dismiss()
        
        assign_btn.bind(on_press=assign_task)
        cancel_btn.bind(on_press=cancel_assign)
        
        popup.open()
    
    def show_manage_user_popup(self, user):
        """Mostra popup per gestire utente"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text=f'Gestione utente: {user.username}', font_size='16sp'))
        
        # Opzioni gestione
        options_layout = BoxLayout(orientation='vertical', spacing=5)
        
        if user.is_admin:
            demote_btn = Button(text='Rimuovi Privilegi Admin', size_hint_y=None, height=dp(40))
            demote_btn.bind(on_press=lambda x: self.toggle_admin_status(user, False, popup))
            options_layout.add_widget(demote_btn)
        else:
            promote_btn = Button(text='Promuovi ad Admin', size_hint_y=None, height=dp(40))
            promote_btn.bind(on_press=lambda x: self.toggle_admin_status(user, True, popup))
            options_layout.add_widget(promote_btn)
        
        reset_password_btn = Button(text='Reimposta Password', size_hint_y=None, height=dp(40))
        reset_password_btn.bind(on_press=lambda x: self.show_reset_password_popup(user, popup))
        options_layout.add_widget(reset_password_btn)
        
        content.add_widget(options_layout)
        
        # Pulsante chiudi
        close_btn = Button(text='Chiudi', size_hint_y=None, height=dp(40))
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Gestione Utente',
            content=content,
            size_hint=(0.6, 0.5)
        )
        
        def close_popup(instance):
            popup.dismiss()
        
        close_btn.bind(on_press=close_popup)
        popup.open()
    
    def toggle_admin_status(self, user, make_admin, parent_popup):
        """Cambia stato admin dell'utente"""
        user.is_admin = make_admin
        app = App.get_running_app()
        
        if app.db.update_user(user):
            action = "promosso ad Admin" if make_admin else "rimosso da Admin"
            self.show_message(f"{user.username} {action}", "success")
            self.refresh_users()
            parent_popup.dismiss()
        else:
            self.show_message("Errore durante l'aggiornamento", "error")
    
    def show_reset_password_popup(self, user, parent_popup):
        """Mostra popup per reset password"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text=f'Reimposta password per: {user.username}'))
        
        # Campo password
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        form_layout.add_widget(Label(text='Nuova Password:', size_hint_y=None, height=dp(40)))
        password_input = TextInput(password=True, multiline=False, size_hint_y=None, height=dp(40))
        form_layout.add_widget(password_input)
        
        content.add_widget(form_layout)
        
        # Messaggio di stato
        status_label = Label(text='', size_hint_y=None, height=dp(30), color=(1, 0, 0, 1))
        content.add_widget(status_label)
        
        # Pulsanti
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        
        reset_btn = Button(text='Reimposta')
        cancel_btn = Button(text='Annulla')
        
        buttons_layout.add_widget(reset_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Reimposta Password',
            content=content,
            size_hint=(0.6, 0.4)
        )
        
        def reset_password(instance):
            new_password = password_input.text.strip()
            
            if len(new_password) < 6:
                status_label.text = 'La password deve essere di almeno 6 caratteri'
                return
            
            user.change_password(new_password)
            app = App.get_running_app()
            
            if app.db.update_user(user):
                self.show_message(f"Password di {user.username} reimpostata", "success")
                popup.dismiss()
                parent_popup.dismiss()
            else:
                status_label.text = 'Errore durante il reset password'
        
        def cancel_reset(instance):
            popup.dismiss()
        
        reset_btn.bind(on_press=reset_password)
        cancel_btn.bind(on_press=cancel_reset)
        
        popup.open()
    
    def show_all_tasks_popup(self, instance):
        """Mostra popup con tutti i task del sistema"""
        app = App.get_running_app()
        tasks_with_users = app.db.get_all_tasks_with_users()
        
        if not tasks_with_users:
            self.show_message("Nessun task trovato nel sistema", "info")
            return
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text=f'Tutti i Task del Sistema ({len(tasks_with_users)})', font_size='16sp'))
        
        # Lista task scrollabile
        scroll = ScrollView()
        tasks_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        tasks_layout.bind(minimum_height=tasks_layout.setter('height'))
        
        for task_data in tasks_with_users:
            task_widget = self.create_all_tasks_widget(task_data)
            tasks_layout.add_widget(task_widget)
        
        scroll.add_widget(tasks_layout)
        content.add_widget(scroll)
        
        # Pulsante chiudi
        close_btn = Button(text='Chiudi', size_hint_y=None, height=dp(40))
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Tutti i Task',
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        def close_popup(instance):
            popup.dismiss()
        
        close_btn.bind(on_press=close_popup)
        popup.open()
    
    def create_all_tasks_widget(self, task_data):
        """Crea widget per task nella vista admin"""
        task_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=10,
            padding=5
        )
        
        # Informazioni task
        info_text = f"[{task_data['task_id'][:8]}] {task_data['title']}\nProprietario: {task_data['username']} | Stato: {task_data['status']}"
        
        info_label = Label(
            text=info_text,
            text_size=(None, None),
            halign='left',
            valign='center',
            size_hint_x=0.8
        )
        task_layout.add_widget(info_label)
        
        return task_layout
    
    def show_manage_user_tasks_popup(self, instance):
        """Mostra popup per gestire task di altri utenti"""
        app = App.get_running_app()
        users = app.db.get_all_users()
        
        if not users:
            self.show_message("Nessun utente trovato", "error")
            return
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Selezione utente
        content.add_widget(Label(text='Seleziona utente:', size_hint_y=None, height=dp(30)))
        user_spinner = Spinner(
            text='Seleziona...',
            values=[f"{u.username} ({u.email})" for u in users],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(user_spinner)
        
        # Area task utente
        self.user_tasks_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.user_tasks_layout.bind(minimum_height=self.user_tasks_layout.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.user_tasks_layout)
        content.add_widget(scroll)
        
        # Pulsante chiudi
        close_btn = Button(text='Chiudi', size_hint_y=None, height=dp(40))
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Gestisci Task Utenti',
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        def on_user_selected(spinner, text):
            if text == 'Seleziona...':
                return
            
            # Trova utente selezionato
            selected_user = None
            for user in users:
                if f"{user.username} ({user.email})" == text:
                    selected_user = user
                    break
            
            if selected_user:
                self.load_user_tasks_for_management(selected_user)
        
        def close_popup(instance):
            popup.dismiss()
        
        user_spinner.bind(text=on_user_selected)
        close_btn.bind(on_press=close_popup)
        
        popup.open()
    
    def load_user_tasks_for_management(self, user):
        """Carica i task dell'utente per la gestione admin"""
        app = App.get_running_app()
        tasks = app.db.get_user_tasks(user.user_id)
        
        self.user_tasks_layout.clear_widgets()
        
        if not tasks:
            no_tasks_label = Label(
                text=f'{user.username} non ha task',
                size_hint_y=None,
                height=dp(40)
            )
            self.user_tasks_layout.add_widget(no_tasks_label)
            return
        
        for task in tasks:
            task_widget = self.create_manageable_task_widget(task, user)
            self.user_tasks_layout.add_widget(task_widget)
    
    def create_manageable_task_widget(self, task, user):
        """Crea widget per task gestibile dall'admin"""
        task_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),
            spacing=10,
            padding=5
        )
        
        # Informazioni task
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.6)
        
        title_label = Label(
            text=task.title,
            font_size='14sp',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        info_layout.add_widget(title_label)
        
        details_text = f"Stato: {task.status} | ID: {task.task_id[:8]}"
        if task.description:
            details_text += f"\n{task.description[:30]}..."
        
        details_label = Label(
            text=details_text,
            font_size='12sp',
            text_size=(None, None),
            halign='left',
            valign='top',
            color=(0.6, 0.6, 0.6, 1)
        )
        info_layout.add_widget(details_label)
        
        task_layout.add_widget(info_layout)
        
        # Pulsanti azione
        actions_layout = BoxLayout(orientation='horizontal', size_hint_x=0.4, spacing=5)
        
        # Pulsante cambia stato
        status_btn = Button(text='Stato', size_hint_x=0.33)
        status_btn.bind(on_press=lambda x: self.admin_change_task_status(task, user))
        actions_layout.add_widget(status_btn)
        
        # Pulsante modifica
        edit_btn = Button(text='Modifica', size_hint_x=0.33)
        edit_btn.bind(on_press=lambda x: self.admin_edit_task(task, user))
        actions_layout.add_widget(edit_btn)
        
        # Pulsante elimina
        delete_btn = Button(text='Elimina', size_hint_x=0.34)
        delete_btn.bind(on_press=lambda x: self.admin_delete_task(task, user))
        actions_layout.add_widget(delete_btn)
        
        task_layout.add_widget(actions_layout)
        
        return task_layout
    
    def admin_change_task_status(self, task, user):
        """Cambia stato task come admin"""
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=f'Cambia stato del task di {user.username}: "{task.title}"'))
        
        status_spinner = Spinner(
            text=task.status,
            values=['To Do', 'Doing', 'Done'],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(status_spinner)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        
        confirm_btn = Button(text='Conferma')
        cancel_btn = Button(text='Annulla')
        
        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Cambia Stato Task',
            content=content,
            size_hint=(0.7, 0.5)
        )
        
        def confirm_change(instance):
            new_status = status_spinner.text
            if new_status != task.status:
                task.update_status(new_status)
                app = App.get_running_app()
                if app.db.update_task(task):
                    self.load_user_tasks_for_management(user)
                    self.show_message(f"Stato cambiato in: {new_status}", "success")
                else:
                    self.show_message("Errore durante l'aggiornamento", "error")
            popup.dismiss()
        
        def cancel_change(instance):
            popup.dismiss()
        
        confirm_btn.bind(on_press=confirm_change)
        cancel_btn.bind(on_press=cancel_change)
        
        popup.open()
    
    def admin_edit_task(self, task, user):
        """Modifica task come admin"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text=f'Modifica task di {user.username}'))
        
        # Form
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Titolo
        form_layout.add_widget(Label(text='Titolo:', size_hint_y=None, height=dp(40)))
        title_input = TextInput(text=task.title, multiline=False, size_hint_y=None, height=dp(40))
        form_layout.add_widget(title_input)
        
        # Descrizione
        form_layout.add_widget(Label(text='Descrizione:', size_hint_y=None, height=dp(80)))
        description_input = TextInput(text=task.description or '', multiline=True, size_hint_y=None, height=dp(80))
        form_layout.add_widget(description_input)
        
        content.add_widget(form_layout)
        
        # Pulsanti
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        
        save_btn = Button(text='Salva')
        cancel_btn = Button(text='Annulla')
        
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Modifica Task',
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        def save_changes(instance):
            new_title = title_input.text.strip()
            new_description = description_input.text.strip()
            
            if not new_title:
                self.show_message("Il titolo è obbligatorio", "error")
                return
            
            task.update_details(new_title, new_description)
            app = App.get_running_app()
            
            if app.db.update_task(task):
                self.load_user_tasks_for_management(user)
                self.show_message("Task aggiornato con successo", "success")
                popup.dismiss()
            else:
                self.show_message("Errore durante l'aggiornamento", "error")
        
        def cancel_edit(instance):
            popup.dismiss()
        
        save_btn.bind(on_press=save_changes)
        cancel_btn.bind(on_press=cancel_edit)
        
        popup.open()
    
    def admin_delete_task(self, task, user):
        """Elimina task come admin"""
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=f'Eliminare il task di {user.username}: "{task.title}"?'))
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        
        confirm_btn = Button(text='Sì')
        cancel_btn = Button(text='No')
        
        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Conferma Eliminazione',
            content=content,
            size_hint=(0.6, 0.4)
        )
        
        def confirm_delete(instance):
            app = App.get_running_app()
            if app.db.delete_task(task.task_id):
                self.load_user_tasks_for_management(user)
                self.show_message("Task eliminato con successo", "success")
            else:
                self.show_message("Errore durante l'eliminazione", "error")
            popup.dismiss()
        
        def cancel_delete(instance):
            popup.dismiss()
        
        confirm_btn.bind(on_press=confirm_delete)
        cancel_btn.bind(on_press=cancel_delete)
        
        popup.open()
    
    def show_message(self, message, msg_type="info"):
        """Mostra un messaggio popup temporaneo"""
        color = (0, 1, 0, 1) if msg_type == "success" else (1, 0, 0, 1) if msg_type == "error" else (0, 0, 1, 1)
        
        content = Label(
            text=message,
            color=color,
            font_size='16sp'
        )
        
        popup = Popup(
            title='Messaggio',
            content=content,
            size_hint=(0.6, 0.3),
            auto_dismiss=True
        )
        
        # Auto-chiudi dopo 2 secondi
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
        popup.open()
    
    def do_logout(self, instance):
        """Esegue il logout"""
        app = App.get_running_app()
        app.current_user = None
        self.manager.current = 'login'

class TaskboardKivyApp(App):
    """Applicazione principale Kivy"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_user = None
    
    def build(self):
        """Costruisce l'interfaccia"""
        # Screen Manager
        sm = ScreenManager()
        
        # Aggiungi schermate
        sm.add_widget(LoginScreen())
        sm.add_widget(RegisterScreen())
        sm.add_widget(DashboardScreen())
        
        # Imposta schermata iniziale
        sm.current = 'login'
        
        return sm
    
    def on_start(self):
        """Chiamato all'avvio dell'app"""
        # Imposta il titolo della finestra
        self.title = 'Taskboard - Gestione Attività Personali'
        
        # Bind eventi tastiera globali
        Window.bind(on_key_down=self.on_key_down)
    
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Gestisce eventi tastiera globali"""
        # F11 per fullscreen
        if key == 292:  # F11
            Window.fullscreen = not Window.fullscreen
            return True
        
        # Escape per uscire da fullscreen
        if key == 27 and Window.fullscreen:  # Escape
            Window.fullscreen = False
            return True
        
        return False

if __name__ == '__main__':
    TaskboardKivyApp().run()