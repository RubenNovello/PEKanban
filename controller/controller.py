"""
CONTROLLER - Livello di controllo e logica applicativa
Gestisce il flusso dell'applicazione e coordina Model e View
Implementa la logica di business e l'autenticazione
"""

from typing import Optional, List
from model.model import User, Task
from view.view import TaskboardView


class TaskboardController:
    """
    Classe che gestisce la logica di controllo dell'applicazione
    Coordina le interazioni tra Model e View
    """
    
    def __init__(self, database_manager):
        """
        Inizializza il controller con il database manager
        Args:
            database_manager: Istanza del gestore database
        """
        self.db = database_manager
        self.view = TaskboardView()
        self.current_user: Optional[User] = None
        self.running = True
    
    def run(self) -> None:
        """Avvia l'applicazione e gestisce il loop principale"""
        self.view.show_welcome()
        
        while self.running:
            try:
                choice = self.view.show_main_menu()
                self._handle_menu_choice(choice)
            except KeyboardInterrupt:
                self.view.show_info("Applicazione interrotta dall'utente.")
                self.running = False
            except Exception as e:
                self.view.show_error(f"Errore imprevisto: {str(e)}")
        
        self.view.show_info("Arrivederci!")
    
    def _handle_menu_choice(self, choice: str) -> None:
        """Gestisce la scelta del menu principale"""
        if not self.current_user:
            # Menu per utenti non autenticati
            if choice == "1":
                self._handle_login()
            elif choice == "2":
                self._handle_register()
            elif choice == "0":
                self.running = False
            else:
                self.view.show_error("Opzione non valida!")
        else:
            # Menu per utenti autenticati
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
                self._show_kanban_board()
            elif choice == "7":
                self._handle_logout()
            elif choice == "0":
                self.running = False
            else:
                self.view.show_error("Opzione non valida!")
    
    def _handle_login(self) -> None:
        """Gestisce il processo di login"""
        username, password = self.view.show_login_form()
        
        if not username or not password:
            self.view.show_error("Username e password sono obbligatori!")
            return
        
        user = self.db.get_user_by_username(username)
        if user and user.check_password(password):
            self.current_user = user
            self.view.set_current_user(user)
            self.view.show_success(f"Benvenuto, {username}!")
        else:
            self.view.show_error("Credenziali non valide!")
    
    def _handle_register(self) -> None:
        """Gestisce il processo di registrazione"""
        username, password = self.view.show_register_form()
        
        if not username or not password:
            self.view.show_error("Username e password sono obbligatori!")
            return
        
        # Verifica se l'username esiste già
        if self.db.get_user_by_username(username):
            self.view.show_error("Username già esistente!")
            return
        
        # Crea nuovo utente
        new_user = User(username=username)
        new_user.set_password(password)
        
        if self.db.create_user(new_user):
            self.view.show_success("Registrazione completata! Ora puoi effettuare il login.")
        else:
            self.view.show_error("Errore durante la registrazione!")
    
    def _handle_logout(self) -> None:
        """Gestisce il logout"""
        if self.view.confirm_action("Sei sicuro di voler uscire?"):
            self.current_user = None
            self.view.set_current_user(None)
            self.view.show_success("Logout effettuato!")
    
    def _show_user_tasks(self) -> None:
        """Mostra tutti i task dell'utente corrente"""
        if not self.current_user:
            return
        
        tasks = self.db.get_tasks_by_user(self.current_user.user_id)
        self.view.show_task_list(tasks)
        self.view.pause()
    
    def _add_new_task(self) -> None:
        """Aggiunge un nuovo task"""
        if not self.current_user:
            return
        
        title, description = self.view.show_task_form()
        
        if not title:
            self.view.show_error("Il titolo è obbligatorio!")
            return
        
        new_task = Task(
            title=title,
            description=description,
            status=Task.STATUS_TODO,
            user_id=self.current_user.user_id
        )
        
        if self.db.create_task(new_task):
            self.view.show_success("Task creato con successo!")
        else:
            self.view.show_error("Errore durante la creazione del task!")
    
    def _edit_task(self) -> None:
        """Modifica un task esistente"""
        if not self.current_user:
            return
        
        # Mostra i task dell'utente
        tasks = self.db.get_tasks_by_user(self.current_user.user_id)
        if not tasks:
            self.view.show_error("Non hai task da modificare!")
            return
        
        self.view.show_task_list(tasks)
        task_id = self.view.get_task_id("modificare")
        
        if task_id == -1:
            return
        
        # Verifica che il task appartenga all'utente
        task = self.db.get_task_by_id(task_id)
        if not task or task.user_id != self.current_user.user_id:
            self.view.show_error("Task non trovato o non autorizzato!")
            return
        
        # Raccoglie i nuovi dati
        title, description = self.view.show_task_form(task)
        task.update_content(title, description)
        
        if self.db.update_task(task):
            self.view.show_success("Task modificato con successo!")
        else:
            self.view.show_error("Errore durante la modifica del task!")
    
    def _change_task_status(self) -> None:
        """Cambia lo stato di un task"""
        if not self.current_user:
            return
        
        # Mostra i task dell'utente
        tasks = self.db.get_tasks_by_user(self.current_user.user_id)
        if not tasks:
            self.view.show_error("Non hai task da modificare!")
            return
        
        self.view.show_task_list(tasks)
        task_id = self.view.get_task_id("modificare")
        
        if task_id == -1:
            return
        
        # Verifica che il task appartenga all'utente
        task = self.db.get_task_by_id(task_id)
        if not task or task.user_id != self.current_user.user_id:
            self.view.show_error("Task non trovato o non autorizzato!")
            return
        
        # Mostra il menu degli stati
        status_choice = self.view.show_status_menu()
        status_map = {
            "1": Task.STATUS_TODO,
            "2": Task.STATUS_DOING,
            "3": Task.STATUS_DONE
        }
        
        new_status = status_map.get(status_choice)
        if not new_status:
            self.view.show_error("Stato non valido!")
            return
        
        if task.update_status(new_status):
            if self.db.update_task(task):
                self.view.show_success(f"Stato cambiato in '{new_status}'!")
            else:
                self.view.show_error("Errore durante l'aggiornamento!")
        else:
            self.view.show_error("Stato non valido!")
    
    def _delete_task(self) -> None:
        """Elimina un task"""
        if not self.current_user:
            return
        
        # Mostra i task dell'utente
        tasks = self.db.get_tasks_by_user(self.current_user.user_id)
        if not tasks:
            self.view.show_error("Non hai task da eliminare!")
            return
        
        self.view.show_task_list(tasks)
        task_id = self.view.get_task_id("eliminare")
        
        if task_id == -1:
            return
        
        # Verifica che il task appartenga all'utente
        task = self.db.get_task_by_id(task_id)
        if not task or task.user_id != self.current_user.user_id:
            self.view.show_error("Task non trovato o non autorizzato!")
            return
        
        # Conferma eliminazione
        if self.view.confirm_action(f"Sei sicuro di voler eliminare il task '{task.title}'?"):
            if self.db.delete_task(task_id):
                self.view.show_success("Task eliminato con successo!")
            else:
                self.view.show_error("Errore durante l'eliminazione!")
    
    def _show_kanban_board(self) -> None:
        """Mostra la bacheca Kanban"""
        if not self.current_user:
            return
        
        tasks = self.db.get_tasks_by_user(self.current_user.user_id)
        self.view.show_kanban_board(tasks)
        self.view.pause()