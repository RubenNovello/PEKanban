"""
RICH CONTROLLER - Controller avanzato per interfaccia Rich
Versione migliorata del controller che utilizza RichTaskboardView
"""

from typing import Optional, List
from model.model import User, Task
from view.simple_rich_view import SimpleRichTaskboardView


class RichTaskboardController:
    """
    Controller avanzato che gestisce l'interfaccia Rich
    Estende le funzionalità del controller base con nuove opzioni
    """
    
    def __init__(self, database_manager):
        """
        Inizializza il controller Rich con il database manager
        Args:
            database_manager: Istanza del gestore database
        """
        self.db = database_manager
        self.view = SimpleRichTaskboardView()
        self.current_user: Optional[User] = None
        self.running = True
    
    def run(self) -> None:
        """Avvia l'applicazione Rich e gestisce il loop principale"""
        self.view.show_loading("🚀 Avvio Taskboard...", 1.5)
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
        
        self.view.show_loading("👋 Chiusura applicazione...", 1.0)
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
            # Menu per utenti autenticati (con statistiche aggiuntive)
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
                self._show_statistics()  # Nuova funzionalità
            elif choice == "8":
                self._handle_logout()
            elif choice == "0":
                self.running = False
            else:
                self.view.show_error("Opzione non valida!")
    
    def _handle_login(self) -> None:
        """Gestisce il processo di login con animazioni"""
        username, password = self.view.show_login_form()
        
        if not username or not password:
            self.view.show_error("Username e password sono obbligatori!")
            return
        
        # Animazione di verifica
        self.view.show_loading("🔍 Verifica credenziali...", 1.0)
        
        user = self.db.get_user_by_username(username)
        if user and user.check_password(password):
            self.current_user = user
            self.view.set_current_user(user)
            self.view.show_success(f"Benvenuto, {username}! 🎉")
        else:
            self.view.show_error("Credenziali non valide!")
    
    def _handle_register(self) -> None:
        """Gestisce il processo di registrazione con validazioni"""
        username, password = self.view.show_register_form()
        
        if not username or not password:
            self.view.show_error("Username e password sono obbligatori!")
            return
        
        # Validazioni aggiuntive
        if len(username) < 3:
            self.view.show_error("Username deve essere almeno 3 caratteri!")
            return
        
        if len(password) < 4:
            self.view.show_error("Password deve essere almeno 4 caratteri!")
            return
        
        # Verifica se l'username esiste già
        if self.db.get_user_by_username(username):
            self.view.show_error("Username già esistente!")
            return
        
        # Animazione di creazione
        self.view.show_loading("📝 Creazione account...", 1.5)
        
        # Crea nuovo utente
        new_user = User(username=username)
        new_user.set_password(password)
        
        if self.db.create_user(new_user):
            self.view.show_success("Registrazione completata! Ora puoi effettuare il login. ✅")
        else:
            self.view.show_error("Errore durante la registrazione!")
    
    def _handle_logout(self) -> None:
        """Gestisce il logout con conferma"""
        if self.view.confirm_action("Sei sicuro di voler uscire?"):
            self.view.show_loading("🚪 Logout in corso...", 1.0)
            self.current_user = None
            self.view.set_current_user(None)
            self.view.show_success("Logout effettuato!")
    
    def _show_user_tasks(self) -> None:
        """Mostra tutti i task dell'utente corrente con Rich table"""
        if not self.current_user:
            return
        
        self.view.show_loading("📋 Caricamento task...", 0.8)
        tasks = self.db.get_tasks_by_user(self.current_user.user_id)
        self.view.show_task_list(tasks)
        self.view.pause()
    
    def _add_new_task(self) -> None:
        """Aggiunge un nuovo task con validazioni migliorate"""
        if not self.current_user:
            return
        
        title, description = self.view.show_task_form()
        
        if not title or len(title.strip()) < 3:
            self.view.show_error("Il titolo deve essere almeno 3 caratteri!")
            return
        
        if len(title) > 100:
            self.view.show_error("Il titolo è troppo lungo (max 100 caratteri)!")
            return
        
        if len(description) > 500:
            self.view.show_error("La descrizione è troppo lunga (max 500 caratteri)!")
            return
        
        # Animazione di creazione
        self.view.show_loading("➕ Creazione task...", 1.0)
        
        new_task = Task(
            title=title.strip(),
            description=description.strip(),
            status=Task.STATUS_TODO,
            user_id=self.current_user.user_id
        )
        
        if self.db.create_task(new_task):
            self.view.show_success("Task creato con successo! 🎉")
        else:
            self.view.show_error("Errore durante la creazione del task!")
    
    def _edit_task(self) -> None:
        """Modifica un task esistente con interfaccia migliorata"""
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
        
        if len(title) < 3:
            self.view.show_error("Il titolo deve essere almeno 3 caratteri!")
            return
        
        # Animazione di aggiornamento
        self.view.show_loading("✏️ Aggiornamento task...", 1.0)
        
        task.update_content(title, description)
        
        if self.db.update_task(task):
            self.view.show_success("Task modificato con successo! ✅")
        else:
            self.view.show_error("Errore durante la modifica del task!")
    
    def _change_task_status(self) -> None:
        """Cambia lo stato di un task con interfaccia Rich"""
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
        
        # Animazione di aggiornamento
        self.view.show_loading("🔄 Aggiornamento stato...", 1.0)
        
        if task.update_status(new_status):
            if self.db.update_task(task):
                self.view.show_success(f"Stato cambiato in '{new_status}'! 🎯")
            else:
                self.view.show_error("Errore durante l'aggiornamento!")
        else:
            self.view.show_error("Stato non valido!")
    
    def _delete_task(self) -> None:
        """Elimina un task con conferma"""
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
            self.view.show_loading("🗑️ Eliminazione task...", 1.0)
            
            if self.db.delete_task(task_id):
                self.view.show_success("Task eliminato con successo! 🗑️")
            else:
                self.view.show_error("Errore durante l'eliminazione!")
    
    def _show_kanban_board(self) -> None:
        """Mostra la bacheca Kanban con Rich layout"""
        if not self.current_user:
            return
        
        self.view.show_loading("📊 Caricamento bacheca Kanban...", 1.0)
        tasks = self.db.get_tasks_by_user(self.current_user.user_id)
        self.view.show_kanban_board(tasks)
        self.view.pause()
    
    def _show_statistics(self) -> None:
        """Mostra statistiche dettagliate sui task (nuova funzionalità)"""
        if not self.current_user:
            return
        
        self.view.show_loading("📈 Calcolo statistiche...", 1.5)
        tasks = self.db.get_tasks_by_user(self.current_user.user_id)
        self.view.show_task_statistics(tasks)
        self.view.pause()