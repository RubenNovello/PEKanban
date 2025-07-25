# controller.py - Controller per l'applicazione Taskboard
# Gestisce la logica di business e coordina Model e View

from typing import List, Optional, Tuple
from model import User, Task, Admin, PasswordRecovery
from view import TaskboardView
from database import DatabaseManager

class TaskboardController:
    """Controller principale per l'applicazione Taskboard"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.view = TaskboardView()
        self.current_user = None
        self.is_running = True
    
    def run(self):
        """Avvia l'applicazione"""
        self.view.show_welcome_message()
        
        while self.is_running:
            if self.current_user is None:
                self._handle_main_menu()
            else:
                self._handle_user_menu()
    
    def _handle_main_menu(self):
        """Gestisce il menu principale (non autenticato)"""
        choice = self.view.show_main_menu()
        
        if choice == "1":
            self._handle_login()
        elif choice == "2":
            self._handle_registration()
        elif choice == "3":
            self._handle_password_recovery()
        elif choice == "4":
            self._handle_exit()
        else:
            self.view.show_error_message("Opzione non valida. Riprova.")
            self.view.wait_for_input()
    
    def _handle_user_menu(self):
        """Gestisce il menu utente (autenticato)"""
        choice = self.view.show_user_menu(self.current_user)
        
        if choice == "1":
            self._show_user_tasks()
        elif choice == "2":
            self._add_new_task()
        elif choice == "3":
            self._edit_task()
        elif choice == "4":
            self._change_task_status()
        elif choice == "5":
            self._delete_task()
        elif choice == "6":
            self._change_password()
        elif choice == "7" and self.current_user.is_admin:
            self._show_all_users()
        elif choice == "8" and self.current_user.is_admin:
            self._show_all_tasks()
        elif choice == "9" and self.current_user.is_admin:
            self._create_user()
        elif choice == "10" and self.current_user.is_admin:
            self._assign_task()
        elif choice == "11" and self.current_user.is_admin:
            self._manage_users()
        elif choice == "12" and self.current_user.is_admin:
            self._delete_user()
        elif choice == "13" and self.current_user.is_admin:
            self._manage_user_tasks()
        elif choice == "0":
            self._handle_logout()
        else:
            self.view.show_error_message("Opzione non valida. Riprova.")
            self.view.wait_for_input()
    
    def _handle_login(self):
        """Gestisce il processo di login"""
        username, password = self.view.get_login_credentials()
        
        if not username or not password:
            self.view.show_error_message("Username e password sono obbligatori.")
            self.view.wait_for_input()
            return
        
        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user
            self.view.show_success_message(f"Benvenuto, {user.username}!")
            self.view.wait_for_input()
        else:
            self.view.show_error_message("Credenziali non valide.")
            self.view.wait_for_input()
    
    def _handle_registration(self):
        """Gestisce il processo di registrazione"""
        username, email, password, confirm_password = self.view.get_registration_data()
        
        # Validazione input
        if not all([username, email, password, confirm_password]):
            self.view.show_error_message("Tutti i campi sono obbligatori.")
            self.view.wait_for_input()
            return
        
        if password != confirm_password:
            self.view.show_error_message("Le password non coincidono.")
            self.view.wait_for_input()
            return
        
        if len(password) < 6:
            self.view.show_error_message("La password deve essere di almeno 6 caratteri.")
            self.view.wait_for_input()
            return
        
        # Verifica se username o email esistono già
        if self.db.user_exists(username, email):
            self.view.show_error_message("Username o email già esistenti.")
            self.view.wait_for_input()
            return
        
        # Verifica se è il primo utente (diventa admin automaticamente)
        is_first_user = self.db.is_first_user()
        
        if is_first_user:
            # Il primo utente diventa admin
            user = Admin(username, email, password)
            success_message = "Registrazione completata con successo! Sei il primo utente e hai privilegi di amministratore."
        else:
            # Utenti successivi sono normali
            user = User(username, email, password)
            success_message = "Registrazione completata con successo!"
        
        if self.db.create_user(user):
            self.view.show_success_message(success_message)
            self.view.wait_for_input()
        else:
            self.view.show_error_message("Errore durante la registrazione.")
            self.view.wait_for_input()
    
    def _handle_password_recovery(self):
        """Gestisce il recupero password"""
        email = self.view.get_recovery_email()
        
        if not email:
            self.view.show_error_message("Email obbligatoria.")
            self.view.wait_for_input()
            return
        
        user = self.db.get_user_by_email(email)
        if not user:
            self.view.show_error_message("Email non trovata nel sistema.")
            self.view.wait_for_input()
            return
        
        # Crea token di recupero
        recovery = PasswordRecovery(user.user_id, email)
        if self.db.create_password_recovery(recovery):
            self.view.show_success_message(f"Token di recupero generato: {recovery.token}")
            self.view.show_info_message("Usa questo token per reimpostare la password.")
            
            # Richiedi token e nuova password
            token = self.view.get_recovery_token()
            if token == recovery.token and recovery.is_valid():
                new_password = self.view.get_new_password()
                if len(new_password) >= 6:
                    user.change_password(new_password)
                    self.db.update_user(user)
                    recovery.use_token()
                    self.db.update_password_recovery(recovery)
                    self.view.show_success_message("Password reimpostata con successo!")
                else:
                    self.view.show_error_message("La password deve essere di almeno 6 caratteri.")
            else:
                self.view.show_error_message("Token non valido o scaduto.")
        else:
            self.view.show_error_message("Errore durante la generazione del token.")
        
        self.view.wait_for_input()
    
    def _handle_logout(self):
        """Gestisce il logout"""
        self.current_user = None
        self.view.show_success_message("Logout effettuato con successo.")
        self.view.wait_for_input()
        self.view.clear_screen()
    
    def _handle_exit(self):
        """Gestisce l'uscita dall'applicazione"""
        if self.view.confirm_action("Sei sicuro di voler uscire?"):
            self.is_running = False
            self.view.show_success_message("Arrivederci!")
    
    def _show_user_tasks(self):
        """Mostra i task dell'utente corrente"""
        tasks = self.db.get_user_tasks(self.current_user.user_id)
        self.view.display_tasks(tasks, f"I MIEI TASK ({len(tasks)})")
        self.view.wait_for_input()
    
    def _add_new_task(self):
        """Aggiunge un nuovo task"""
        title, description = self.view.get_task_data()
        
        if not title:
            self.view.show_error_message("Il titolo del task è obbligatorio.")
            self.view.wait_for_input()
            return
        
        task = Task(title, description or "", self.current_user.user_id)
        if self.db.create_task(task):
            self.view.show_success_message("Task creato con successo!")
        else:
            self.view.show_error_message("Errore durante la creazione del task.")
        
        self.view.wait_for_input()
    
    def _edit_task(self):
        """Modifica un task esistente"""
        # Mostra i task dell'utente
        tasks = self.db.get_user_tasks(self.current_user.user_id)
        if not tasks:
            self.view.show_error_message("Non hai task da modificare.")
            self.view.wait_for_input()
            return
        
        self.view.display_tasks(tasks, "SELEZIONA TASK DA MODIFICARE")
        task_id = self.view.get_task_id("Inserisci l'ID del task da modificare")
        
        task = self.db.get_task_by_id(task_id)
        if not task or task.user_id != self.current_user.user_id:
            self.view.show_error_message("Task non trovato o non autorizzato.")
            self.view.wait_for_input()
            return
        
        self.view.display_task_details(task)
        title, description = self.view.get_task_update_data()
        
        if title or description:
            task.update_details(title, description)
            if self.db.update_task(task):
                self.view.show_success_message("Task aggiornato con successo!")
            else:
                self.view.show_error_message("Errore durante l'aggiornamento.")
        else:
            self.view.show_info_message("Nessuna modifica effettuata.")
        
        self.view.wait_for_input()
    
    def _change_task_status(self):
        """Cambia lo stato di un task"""
        tasks = self.db.get_user_tasks(self.current_user.user_id)
        if not tasks:
            self.view.show_error_message("Non hai task da modificare.")
            self.view.wait_for_input()
            return
        
        self.view.display_tasks(tasks, "SELEZIONA TASK PER CAMBIARE STATO")
        task_id = self.view.get_task_id("Inserisci l'ID del task")
        
        task = self.db.get_task_by_id(task_id)
        if not task or task.user_id != self.current_user.user_id:
            self.view.show_error_message("Task non trovato o non autorizzato.")
            self.view.wait_for_input()
            return
        
        self.view.display_task_details(task)
        status_choice = self.view.show_task_statuses()
        
        status_map = {
            "1": Task.STATUS_TODO,
            "2": Task.STATUS_DOING,
            "3": Task.STATUS_DONE
        }
        
        if status_choice in status_map:
            new_status = status_map[status_choice]
            if task.update_status(new_status):
                if self.db.update_task(task):
                    self.view.show_success_message(f"Stato cambiato in: {new_status}")
                else:
                    self.view.show_error_message("Errore durante l'aggiornamento.")
            else:
                self.view.show_error_message("Stato non valido.")
        else:
            self.view.show_error_message("Scelta non valida.")
        
        self.view.wait_for_input()
    
    def _delete_task(self):
        """Elimina un task"""
        tasks = self.db.get_user_tasks(self.current_user.user_id)
        if not tasks:
            self.view.show_error_message("Non hai task da eliminare.")
            self.view.wait_for_input()
            return
        
        self.view.display_tasks(tasks, "SELEZIONA TASK DA ELIMINARE")
        task_id = self.view.get_task_id("Inserisci l'ID del task da eliminare")
        
        task = self.db.get_task_by_id(task_id)
        if not task or task.user_id != self.current_user.user_id:
            self.view.show_error_message("Task non trovato o non autorizzato.")
            self.view.wait_for_input()
            return
        
        self.view.display_task_details(task)
        if self.view.confirm_action("Sei sicuro di voler eliminare questo task?"):
            if self.db.delete_task(task_id):
                self.view.show_success_message("Task eliminato con successo!")
            else:
                self.view.show_error_message("Errore durante l'eliminazione.")
        else:
            self.view.show_info_message("Eliminazione annullata.")
        
        self.view.wait_for_input()
    
    def _change_password(self):
        """Cambia la password dell'utente corrente"""
        new_password = self.view.get_new_password()
        
        if len(new_password) < 6:
            self.view.show_error_message("La password deve essere di almeno 6 caratteri.")
            self.view.wait_for_input()
            return
        
        self.current_user.change_password(new_password)
        if self.db.update_user(self.current_user):
            self.view.show_success_message("Password cambiata con successo!")
        else:
            self.view.show_error_message("Errore durante il cambio password.")
        
        self.view.wait_for_input()
    
    # Metodi Admin
    def _show_all_users(self):
        """Mostra tutti gli utenti (solo admin)"""
        users = self.db.get_all_users()
        self.view.display_users(users)
        self.view.wait_for_input()
    
    def _show_all_tasks(self):
        """Mostra tutti i task con proprietari (solo admin)"""
        tasks_with_users = self.db.get_all_tasks_with_users()
        if not tasks_with_users:
            self.view.show_error_message("Nessun task trovato.")
            self.view.wait_for_input()
            return
        
        self.view.display_tasks_with_owners(tasks_with_users, f"TUTTI I TASK ({len(tasks_with_users)})")
        self.view.wait_for_input()
    
    def _manage_users(self):
        """Gestisce gli utenti (solo admin)"""
        users = self.db.get_all_users()
        self.view.display_users(users)
        
        user_id = self.view.get_user_id("Inserisci l'ID dell'utente da gestire")
        user = self.db.get_user_by_id(user_id)
        
        if not user:
            self.view.show_error_message("Utente non trovato.")
            self.view.wait_for_input()
            return
        
        print(f"\n👤 GESTIONE UTENTE: {user.username}")
        print("1. Promuovi ad Admin")
        print("2. Rimuovi privilegi Admin")
        print("3. Reimposta password")
        print("0. Annulla")
        
        choice = input("Seleziona azione: ").strip()
        
        if choice == "1":
            user.is_admin = True
            if self.db.update_user(user):
                self.view.show_success_message(f"{user.username} promosso ad Admin!")
            else:
                self.view.show_error_message("Errore durante la promozione.")
        elif choice == "2":
            user.is_admin = False
            if self.db.update_user(user):
                self.view.show_success_message(f"Privilegi Admin rimossi da {user.username}!")
            else:
                self.view.show_error_message("Errore durante la rimozione privilegi.")
        elif choice == "3":
            new_password = self.view.get_new_password()
            if len(new_password) >= 6:
                user.change_password(new_password)
                if self.db.update_user(user):
                    self.view.show_success_message(f"Password di {user.username} reimpostata!")
                else:
                    self.view.show_error_message("Errore durante il reset password.")
            else:
                self.view.show_error_message("Password troppo corta.")
        
        self.view.wait_for_input()
    
    def _delete_user(self):
        """Elimina un utente e tutti i suoi task (solo admin)"""
        users = self.db.get_all_users()
        self.view.display_users(users)
        
        user_id = self.view.get_user_id("Inserisci l'ID dell'utente da eliminare")
        user = self.db.get_user_by_id(user_id)
        
        if not user:
            self.view.show_error_message("Utente non trovato.")
            self.view.wait_for_input()
            return
        
        if user.user_id == self.current_user.user_id:
            self.view.show_error_message("Non puoi eliminare te stesso.")
            self.view.wait_for_input()
            return
        
        user_tasks = self.db.get_user_tasks(user_id)
        message = f"Eliminare {user.username} e tutti i suoi {len(user_tasks)} task?"
        
        if self.view.confirm_action(message):
            if self.db.delete_user_and_tasks(user_id):
                self.view.show_success_message(f"Utente {user.username} eliminato!")
            else:
                self.view.show_error_message("Errore durante l'eliminazione.")
        else:
            self.view.show_info_message("Eliminazione annullata.")
        
        self.view.wait_for_input()
    
    def _manage_user_tasks(self):
        """Gestisce i task di altri utenti (solo admin)"""
        users = self.db.get_all_users()
        self.view.display_users(users)
        
        user_id = self.view.get_user_id("Inserisci l'ID dell'utente")
        user = self.db.get_user_by_id(user_id)
        
        if not user:
            self.view.show_error_message("Utente non trovato.")
            self.view.wait_for_input()
            return
        
        tasks = self.db.get_user_tasks(user_id)
        if not tasks:
            self.view.show_error_message(f"{user.username} non ha task.")
            self.view.wait_for_input()
            return
        
        self.view.display_tasks(tasks, f"TASK DI {user.username}")
        
        print("\n1. Modifica task")
        print("2. Modifica stato task")
        print("3. Elimina task")
        print("0. Annulla")
        
        choice = input("Seleziona azione: ").strip()
        
        if choice == "1":
            task_id = self.view.get_task_id("Inserisci l'ID del task da modificare")
            task = self.db.get_task_by_id(task_id)
            
            if task and task.user_id == user_id:
                self.view.display_task_details(task)
                title, description = self.view.get_task_update_data()
                
                if title or description:
                    task.update_details(title, description)
                    if self.db.update_task(task):
                        self.view.show_success_message("Task aggiornato con successo!")
                    else:
                        self.view.show_error_message("Errore durante l'aggiornamento.")
                else:
                    self.view.show_info_message("Nessuna modifica effettuata.")
            else:
                self.view.show_error_message("Task non trovato.")
        
        elif choice == "2":
            task_id = self.view.get_task_id("Inserisci l'ID del task")
            task = self.db.get_task_by_id(task_id)
            
            if task and task.user_id == user_id:
                status_choice = self.view.show_task_statuses()
                status_map = {"1": Task.STATUS_TODO, "2": Task.STATUS_DOING, "3": Task.STATUS_DONE}
                
                if status_choice in status_map:
                    task.update_status(status_map[status_choice])
                    if self.db.update_task(task):
                        self.view.show_success_message("Stato task aggiornato!")
                    else:
                        self.view.show_error_message("Errore durante l'aggiornamento.")
                else:
                    self.view.show_error_message("Scelta non valida.")
            else:
                self.view.show_error_message("Task non trovato.")
        
        elif choice == "3":
            task_id = self.view.get_task_id("Inserisci l'ID del task da eliminare")
            task = self.db.get_task_by_id(task_id)
            
            if task and task.user_id == user_id:
                if self.view.confirm_action("Eliminare questo task?"):
                    if self.db.delete_task(task_id):
                        self.view.show_success_message("Task eliminato!")
                    else:
                        self.view.show_error_message("Errore durante l'eliminazione.")
            else:
                self.view.show_error_message("Task non trovato.")
        
        self.view.wait_for_input()
    
    def _create_user(self):
        """Crea un nuovo utente (solo admin)"""
        print("\n👤 CREA NUOVO UTENTE")
        print("1. Crea utente normale")
        print("2. Crea amministratore")
        print("0. Annulla")
        
        choice = input("Seleziona tipo utente: ").strip()
        
        if choice == "0":
            return
        
        if choice not in ["1", "2"]:
            self.view.show_error_message("Scelta non valida.")
            self.view.wait_for_input()
            return
        
        # Richiedi dati utente
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        confirm_password = input("Conferma password: ").strip()
        
        # Validazione
        if not all([username, email, password, confirm_password]):
            self.view.show_error_message("Tutti i campi sono obbligatori.")
            self.view.wait_for_input()
            return
        
        if password != confirm_password:
            self.view.show_error_message("Le password non coincidono.")
            self.view.wait_for_input()
            return
        
        if len(password) < 6:
            self.view.show_error_message("La password deve essere di almeno 6 caratteri.")
            self.view.wait_for_input()
            return
        
        # Verifica se username o email esistono già
        if self.db.user_exists(username, email):
            self.view.show_error_message("Username o email già esistenti.")
            self.view.wait_for_input()
            return
        
        # Crea utente
        if choice == "2":
            user = Admin(username, email, password)
            user_type = "amministratore"
        else:
            user = User(username, email, password)
            user_type = "utente"
        
        if self.db.create_user(user):
            self.view.show_success_message(f"Nuovo {user_type} '{username}' creato con successo!")
        else:
            self.view.show_error_message("Errore durante la creazione dell'utente.")
        
        self.view.wait_for_input()
    
    def _assign_task(self):
        """Assegna un task a un utente (solo admin)"""
        # Mostra tutti gli utenti
        users = self.db.get_all_users()
        if not users:
            self.view.show_error_message("Nessun utente trovato.")
            self.view.wait_for_input()
            return
        
        self.view.display_users(users)
        
        # Seleziona utente
        user_id = self.view.get_user_id("Inserisci l'ID dell'utente a cui assegnare il task")
        user = self.db.get_user_by_id(user_id)
        
        if not user:
            self.view.show_error_message("Utente non trovato.")
            self.view.wait_for_input()
            return
        
        print(f"\n📋 ASSEGNA TASK A: {user.username}")
        print("-" * 40)
        
        # Richiedi dati task
        title = input("Titolo del task: ").strip()
        description = input("Descrizione del task: ").strip()
        
        if not title:
            self.view.show_error_message("Il titolo del task è obbligatorio.")
            self.view.wait_for_input()
            return
        
        # Crea task assegnato all'utente specificato
        task = Task(title, description or "", user_id)
        
        if self.db.create_task(task):
            self.view.show_success_message(f"Task '{title}' assegnato a {user.username} con successo!")
        else:
            self.view.show_error_message("Errore durante l'assegnazione del task.")
        
        self.view.wait_for_input()