"""
VIEW - Livello di presentazione e interfaccia utente
Gestisce l'interazione con l'utente tramite CLI
Visualizza i dati e raccoglie gli input dell'utente
"""

from typing import List, Optional
from model.model import User, Task


class TaskboardView:
    """
    Classe che gestisce l'interfaccia utente CLI
    Fornisce metodi per visualizzare dati e raccogliere input
    """
    
    def __init__(self):
        self.current_user: Optional[User] = None
    
    def show_welcome(self) -> None:
        """Mostra il messaggio di benvenuto"""
        print("\n" + "="*50)
        print("   TASKBOARD - Gestione Attività Personali")
        print("="*50)
    
    def show_main_menu(self) -> str:
        """Mostra il menu principale e restituisce la scelta dell'utente"""
        print("\n--- MENU PRINCIPALE ---")
        if self.current_user:
            print(f"Utente connesso: {self.current_user.username}")
            print("1. Visualizza i miei task")
            print("2. Aggiungi nuovo task")
            print("3. Modifica task")
            print("4. Cambia stato task")
            print("5. Elimina task")
            print("6. Visualizza bacheca Kanban")
            print("7. Logout")
            print("0. Esci")
        else:
            print("1. Login")
            print("2. Registrazione")
            print("0. Esci")
        
        return input("\nScegli un'opzione: ").strip()
    
    def show_login_form(self) -> tuple[str, str]:
        """Raccoglie i dati per il login"""
        print("\n--- LOGIN ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        return username, password
    
    def show_register_form(self) -> tuple[str, str]:
        """Raccoglie i dati per la registrazione"""
        print("\n--- REGISTRAZIONE ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        password_confirm = input("Conferma password: ").strip()
        
        if password != password_confirm:
            self.show_error("Le password non coincidono!")
            return "", ""
        
        return username, password
    
    def show_task_form(self, task: Optional[Task] = None) -> tuple[str, str]:
        """Raccoglie i dati per creare/modificare un task"""
        if task:
            print(f"\n--- MODIFICA TASK: {task.title} ---")
            title = input(f"Titolo [{task.title}]: ").strip() or task.title
            description = input(f"Descrizione [{task.description}]: ").strip() or task.description
        else:
            print("\n--- NUOVO TASK ---")
            title = input("Titolo: ").strip()
            description = input("Descrizione: ").strip()
        
        return title, description
    
    def show_task_list(self, tasks: List[Task]) -> None:
        """Visualizza la lista dei task"""
        if not tasks:
            print("\nNessun task trovato.")
            return
        
        print(f"\n--- I TUOI TASK ({len(tasks)}) ---")
        print(f"{'ID':<4} {'Titolo':<25} {'Stato':<10} {'Descrizione':<30}")
        print("-" * 75)
        
        for task in tasks:
            title = task.title[:24] + "..." if len(task.title) > 24 else task.title
            desc = task.description[:29] + "..." if len(task.description) > 29 else task.description
            print(f"{task.task_id:<4} {title:<25} {task.status:<10} {desc:<30}")
    
    def show_kanban_board(self, tasks: List[Task]) -> None:
        """Visualizza la bacheca Kanban"""
        print("\n" + "="*80)
        print("                           BACHECA KANBAN")
        print("="*80)
        
        # Raggruppa i task per stato
        todo_tasks = [t for t in tasks if t.status == Task.STATUS_TODO]
        doing_tasks = [t for t in tasks if t.status == Task.STATUS_DOING]
        done_tasks = [t for t in tasks if t.status == Task.STATUS_DONE]
        
        # Stampa le colonne
        print(f"{'TODO':<25} {'DOING':<25} {'DONE':<25}")
        print("-" * 75)
        
        max_rows = max(len(todo_tasks), len(doing_tasks), len(done_tasks))
        
        for i in range(max_rows):
            todo_item = todo_tasks[i].title[:22] + "..." if i < len(todo_tasks) and len(todo_tasks[i].title) > 22 else (todo_tasks[i].title if i < len(todo_tasks) else "")
            doing_item = doing_tasks[i].title[:22] + "..." if i < len(doing_tasks) and len(doing_tasks[i].title) > 22 else (doing_tasks[i].title if i < len(doing_tasks) else "")
            done_item = done_tasks[i].title[:22] + "..." if i < len(done_tasks) and len(done_tasks[i].title) > 22 else (done_tasks[i].title if i < len(done_tasks) else "")
            
            print(f"{todo_item:<25} {doing_item:<25} {done_item:<25}")
    
    def show_status_menu(self) -> str:
        """Mostra il menu per la selezione dello stato"""
        print("\n--- CAMBIA STATO ---")
        print("1. ToDo")
        print("2. Doing")
        print("3. Done")
        return input("Scegli nuovo stato: ").strip()
    
    def get_task_id(self, action: str = "selezionare") -> int:
        """Raccoglie l'ID del task dall'utente"""
        try:
            return int(input(f"Inserisci l'ID del task da {action}: "))
        except ValueError:
            self.show_error("ID non valido!")
            return -1
    
    def show_success(self, message: str) -> None:
        """Mostra un messaggio di successo"""
        print(f"\n✓ {message}")
    
    def show_error(self, message: str) -> None:
        """Mostra un messaggio di errore"""
        print(f"\n✗ Errore: {message}")
    
    def show_info(self, message: str) -> None:
        """Mostra un messaggio informativo"""
        print(f"\nℹ {message}")
    
    def confirm_action(self, message: str) -> bool:
        """Chiede conferma per un'azione"""
        response = input(f"\n{message} (s/n): ").strip().lower()
        return response in ['s', 'si', 'y', 'yes']
    
    def pause(self) -> None:
        """Pausa per permettere all'utente di leggere"""
        input("\nPremi INVIO per continuare...")
    
    def clear_screen(self) -> None:
        """Pulisce lo schermo (simulato con righe vuote)"""
        print("\n" * 3)
    
    def set_current_user(self, user: Optional[User]) -> None:
        """Imposta l'utente corrente"""
        self.current_user = user