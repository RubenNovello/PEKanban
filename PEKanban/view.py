# view.py - Vista per l'interfaccia CLI dell'applicazione Taskboard
# Gestisce l'input/output e la presentazione dei dati all'utente

import os
from typing import List, Optional
from model import User, Task, Admin

class TaskboardView:
    """Classe per gestire l'interfaccia utente CLI"""
    
    def __init__(self):
        self.current_user = None
    
    def clear_screen(self):
        """Pulisce lo schermo del terminale"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Stampa un header formattato"""
        print("=" * 60)
        print(f" {title.center(56)} ")
        print("=" * 60)
    
    def print_separator(self):
        """Stampa una linea separatrice"""
        print("-" * 60)
    
    def show_welcome_message(self):
        """Mostra il messaggio di benvenuto"""
        self.clear_screen()
        self.print_header("TASKBOARD - GESTIONE ATTIVITÀ PERSONALI")
        print("\nBenvenuto nel sistema di gestione task in stile Kanban!")
        print("Scegli un'opzione dal menu principale.\n")
    
    def show_main_menu(self) -> str:
        """Mostra il menu principale e restituisce la scelta dell'utente"""
        print("\n[*] MENU PRINCIPALE")
        self.print_separator()
        print("1. [L] Login")
        print("2. [R] Registrazione")
        print("3. [P] Recupero Password")
        print("4. [X] Esci")
        self.print_separator()
        return input("Seleziona un'opzione (1-4): ").strip()
    
    def show_user_menu(self, user: User) -> str:
        """Mostra il menu utente e restituisce la scelta"""
        user_type = "ADMIN" if user.is_admin else "USER"
        print(f"\n[U] MENU {user_type} - {user.username}")
        self.print_separator()
        print("1. [T] Visualizza i miei task")
        print("2. [+] Aggiungi nuovo task")
        print("3. [E] Modifica task")
        print("4. [S] Cambia stato task")
        print("5. [D] Elimina task")
        print("6. [C] Cambia password")
        
        if user.is_admin:
            print("\n[A] FUNZIONI ADMIN:")
            print("7. [U] Visualizza tutti gli utenti")
            print("8. [T] Visualizza tutti i task")
            print("9. [N] Crea nuovo utente")
            print("10. [A] Assegna task a utente")
            print("11. [M] Gestisci utenti")
            print("12. [R] Elimina utente")
            print("13. [G] Gestisci task utenti")
        
        print("0. [Q] Logout")
        self.print_separator()
        return input("Seleziona un'opzione: ").strip()
    
    def get_login_credentials(self) -> tuple:
        """Richiede le credenziali di login"""
        print("\n[L] LOGIN")
        self.print_separator()
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        return username, password
    
    def get_registration_data(self) -> tuple:
        """Richiede i dati per la registrazione"""
        print("\n[R] REGISTRAZIONE NUOVO UTENTE")
        self.print_separator()
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        confirm_password = input("Conferma Password: ").strip()
        return username, email, password, confirm_password
    
    def get_task_data(self) -> tuple:
        """Richiede i dati per un nuovo task"""
        print("\n[+] NUOVO TASK")
        self.print_separator()
        title = input("Titolo del task: ").strip()
        description = input("Descrizione: ").strip()
        return title, description
    
    def get_task_update_data(self) -> tuple:
        """Richiede i dati per aggiornare un task"""
        print("\n[E] MODIFICA TASK")
        self.print_separator()
        title = input("Nuovo titolo (lascia vuoto per non modificare): ").strip()
        description = input("Nuova descrizione (lascia vuoto per non modificare): ").strip()
        return title if title else None, description if description else None
    
    def show_task_statuses(self) -> str:
        """Mostra gli stati disponibili e restituisce la scelta"""
        print("\n[S] STATI DISPONIBILI:")
        print("1. To Do (Da fare)")
        print("2. Doing (In elaborazione)")
        print("3. Done (Completato)")
        return input("Seleziona nuovo stato (1-3): ").strip()
    
    def display_tasks(self, tasks: List[Task], title: str = "TASK"):
        """Visualizza una lista di task in formato tabellare"""
        if not tasks:
            print(f"\n[T] {title}")
            self.print_separator()
            print("Nessun task trovato.")
            return
        
        print(f"\n[T] {title}")
        self.print_separator()
        
        # Header della tabella
        print(f"{'ID':<8} {'Titolo':<25} {'Stato':<15} {'Utente':<15}")
        print("-" * 70)
        
        # Raggruppa task per stato
        todo_tasks = [t for t in tasks if t.status == Task.STATUS_TODO]
        doing_tasks = [t for t in tasks if t.status == Task.STATUS_DOING]
        done_tasks = [t for t in tasks if t.status == Task.STATUS_DONE]
        
        # Visualizza task per stato
        for status, task_list in [("[TODO] TO DO", todo_tasks), ("[DOING] DOING", doing_tasks), ("[DONE] DONE", done_tasks)]:
            if task_list:
                print(f"\n{status}:")
                for task in task_list:
                    task_id_short = task.task_id[:8]
                    title_short = task.title[:23] + "..." if len(task.title) > 23 else task.title
                    user_id_short = task.user_id[:13] + "..." if len(task.user_id) > 13 else task.user_id
                    print(f"{task_id_short:<8} {title_short:<25} {task.status:<15} {user_id_short:<15}")
    
    def display_task_details(self, task: Task):
        """Visualizza i dettagli completi di un task"""
        print(f"\n[T] DETTAGLI TASK")
        self.print_separator()
        print(f"ID: {task.task_id}")
        print(f"Titolo: {task.title}")
        print(f"Descrizione: {task.description}")
        print(f"Stato: {task.status}")
        print(f"Utente: {task.user_id}")
        print(f"Creato: {task.created_at.strftime('%d/%m/%Y %H:%M')}")
        print(f"Aggiornato: {task.updated_at.strftime('%d/%m/%Y %H:%M')}")
    
    def display_users(self, users: List[User]):
        """Visualizza una lista di utenti"""
        if not users:
            print("\n[U] UTENTI REGISTRATI")
            self.print_separator()
            print("Nessun utente trovato.")
            return
        
        print("\n[U] UTENTI REGISTRATI")
        self.print_separator()
        print(f"{'ID':<10} {'Username':<20} {'Email':<25} {'Tipo':<10}")
        print("-" * 70)
        
        for user in users:
            user_id_short = user.user_id[:8]
            user_type = "ADMIN" if user.is_admin else "USER"
            print(f"{user_id_short:<10} {user.username:<20} {user.email:<25} {user_type:<10}")
    
    def get_task_id(self, prompt: str = "Inserisci l'ID del task") -> str:
        """Richiede l'ID di un task"""
        return input(f"{prompt}: ").strip()
    
    def get_user_id(self, prompt: str = "Inserisci l'ID dell'utente") -> str:
        """Richiede l'ID di un utente"""
        return input(f"{prompt}: ").strip()
    
    def get_new_password(self) -> str:
        """Richiede una nuova password"""
        return input("Nuova password: ").strip()
    
    def show_success_message(self, message: str):
        """Mostra un messaggio di successo"""
        print(f"\n[OK] {message}")
    
    def show_error_message(self, message: str):
        """Mostra un messaggio di errore"""
        print(f"\n[ERROR] {message}")
    
    def show_info_message(self, message: str):
        """Mostra un messaggio informativo"""
        print(f"\n[INFO] {message}")
    
    def confirm_action(self, message: str) -> bool:
        """Richiede conferma per un'azione"""
        response = input(f"\n[?] {message} (s/n): ").strip().lower()
        return response in ['s', 'si', 'sì', 'y', 'yes']
    
    def wait_for_input(self, message: str = "Premi INVIO per continuare..."):
        """Aspetta input dall'utente"""
        input(f"\n{message}")
    
    def get_recovery_email(self) -> str:
        """Richiede l'email per il recupero password"""
        print("\n[P] RECUPERO PASSWORD")
        self.print_separator()
        return input("Inserisci la tua email: ").strip()
    
    def get_recovery_token(self) -> str:
        """Richiede il token di recupero"""
        return input("Inserisci il token di recupero: ").strip()
    
    def display_tasks_with_owners(self, tasks_with_users: list, title: str = "TASK CON PROPRIETARI"):
        """Visualizza una lista di task con informazioni sui proprietari"""
        if not tasks_with_users:
            print(f"\n[T] {title}")
            self.print_separator()
            print("Nessun task trovato.")
            return
        
        print(f"\n[T] {title}")
        self.print_separator()
        
        # Header della tabella
        print(f"{'ID':<8} {'Titolo':<25} {'Stato':<15} {'Proprietario':<20} {'Tipo':<8}")
        print("-" * 85)
        
        # Raggruppa task per stato
        todo_tasks = [t for t in tasks_with_users if t['task'].status == Task.STATUS_TODO]
        doing_tasks = [t for t in tasks_with_users if t['task'].status == Task.STATUS_DOING]
        done_tasks = [t for t in tasks_with_users if t['task'].status == Task.STATUS_DONE]
        
        # Visualizza task per stato
        for status, task_list in [("[TODO] TO DO", todo_tasks), ("[DOING] DOING", doing_tasks), ("[DONE] DONE", done_tasks)]:
            if task_list:
                print(f"\n{status}:")
                for item in task_list:
                    task = item['task']
                    task_id_short = task.task_id[:8]
                    title_short = task.title[:23] + "..." if len(task.title) > 23 else task.title
                    owner_name = item['owner_username'][:18] + "..." if len(item['owner_username']) > 18 else item['owner_username']
                    owner_type = "ADMIN" if item['owner_is_admin'] else "USER"
                    print(f"{task_id_short:<8} {title_short:<25} {task.status:<15} {owner_name:<20} {owner_type:<8}")