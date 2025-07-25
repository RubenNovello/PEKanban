# rich_cli.py - CLI migliorata con Rich e tqdm per Taskboard
# Interfaccia CLI con colori, tabelle eleganti e barre di progresso

import os
import sys
import time
from datetime import datetime
from typing import List, Optional

# Rich imports
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
from rich.tree import Tree
from rich.syntax import Syntax
from rich import box
from rich.markdown import Markdown

# tqdm imports
#from tqdm import tqdm

# Local imports
from database import DatabaseManager
from model import User, Task, Admin, PasswordRecovery
from utils import validate_email, validate_password_strength, validate_username
from config import Config

class RichTaskboardCLI:
    """CLI migliorata con Rich per Taskboard"""
    
    def __init__(self):
        self.console = Console()
        self.db = DatabaseManager()
        self.current_user = None
        self.is_running = True
        
        # Configurazione stili
        self.styles = {
            'title': 'bold blue',
            'success': 'bold green',
            'error': 'bold red',
            'warning': 'bold yellow',
            'info': 'bold cyan',
            'prompt': 'bold magenta',
            'task_todo': 'red',
            'task_doing': 'yellow',
            'task_done': 'green',
            'admin': 'bold red',
            'user': 'bold blue'
        }
    
    def run(self):
        """Avvia l'applicazione CLI migliorata"""
        self.show_welcome_screen()
        
        while self.is_running:
            try:
                if self.current_user is None:
                    self.handle_main_menu()
                else:
                    self.handle_user_menu()
            except KeyboardInterrupt:
                self.console.print("\n[bold red]Applicazione interrotta dall'utente.[/bold red]")
                self.is_running = False
            except Exception as e:
                self.console.print(f"[bold red]Errore: {str(e)}[/bold red]")
                self.console.print_exception()
    
    def show_welcome_screen(self):
        """Mostra schermata di benvenuto animata"""
        self.console.clear()
        
        # Logo ASCII art
        logo = """
    ████████╗ █████╗ ███████╗██╗  ██╗██████╗  ██████╗  █████╗ ██████╗ ██████╗ 
    ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
       ██║   ███████║███████╗█████╔╝ ██████╔╝██║   ██║███████║██████╔╝██║  ██║
       ██║   ██╔══██║╚════██║██╔═██╗ ██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║
       ██║   ██║  ██║███████║██║  ██╗██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
       ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
        """
        
        # Animazione logo
        for line in logo.split('\n'):
            self.console.print(line, style='bold blue', justify='center')
            time.sleep(0.1)
        
        # Sottotitolo
        subtitle = Panel(
            "[bold cyan]Sistema di Gestione Attività Personali in Stile Kanban[/bold cyan]",
            box=box.DOUBLE,
            padding=(1, 2)
        )
        self.console.print(subtitle, justify='center')
        
        # Statistiche sistema
        stats = self.db.get_database_stats()
        stats_text = f"[green]Utenti: {stats['total_users']}[/green] | [yellow]Task: {stats['total_tasks']}[/yellow] | [blue]Completati: {stats['done_tasks']}[/blue]"
        self.console.print(stats_text, justify='center')
        
        self.console.print("\n" + "="*80, style='dim')
        time.sleep(1)
    
    def handle_main_menu(self):
        """Gestisce il menu principale"""
        self.console.print("\n")
        
        # Menu principale con pannello
        menu_content = """
[bold cyan]1.[/bold cyan] 🔐 Login
[bold cyan]2.[/bold cyan] 📝 Registrazione  
[bold cyan]3.[/bold cyan] 🔑 Recupero Password
[bold cyan]4.[/bold cyan] 📊 Statistiche Sistema
[bold cyan]5.[/bold cyan] ❌ Esci
        """
        
        menu_panel = Panel(
            menu_content,
            title="[bold blue]MENU PRINCIPALE[/bold blue]",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print(menu_panel)
        
        choice = Prompt.ask(
            "[bold magenta]Seleziona un'opzione[/bold magenta]",
            choices=["1", "2", "3", "4", "5"],
            default="1"
        )
        
        if choice == "1":
            self.handle_login()
        elif choice == "2":
            self.handle_registration()
        elif choice == "3":
            self.handle_password_recovery()
        elif choice == "4":
            self.show_system_stats()
        elif choice == "5":
            self.handle_exit()
    
    def handle_user_menu(self):
        """Gestisce il menu utente"""
        self.console.print("\n")
        
        # Header utente
        user_type = "[bold red]ADMIN[/bold red]" if self.current_user.is_admin else "[bold blue]USER[/bold blue]"
        header = f"👤 {user_type} - [bold]{self.current_user.username}[/bold]"
        
        # Menu utente
        menu_content = """
[bold cyan]1.[/bold cyan] 📋 Visualizza i miei task
[bold cyan]2.[/bold cyan] ➕ Aggiungi nuovo task
[bold cyan]3.[/bold cyan] ✏️  Modifica task
[bold cyan]4.[/bold cyan] 🔄 Cambia stato task
[bold cyan]5.[/bold cyan] 🗑️  Elimina task
[bold cyan]6.[/bold cyan] 📊 Statistiche personali
[bold cyan]7.[/bold cyan] 🔒 Cambia password
        """
        
        if self.current_user.is_admin:
            menu_content += """
[bold red]8.[/bold red] 👥 Visualizza tutti gli utenti
[bold red]9.[/bold red] 📊 Visualizza tutti i task
[bold red]10.[/bold red] 👤 Crea nuovo utente
[bold red]11.[/bold red] 📋 Assegna task
[bold red]12.[/bold red] 🔧 Gestisci utenti
[bold red]13.[/bold red] 🗑️ Elimina utente
[bold red]14.[/bold red] 🔧 Gestisci task utenti
            """
        
        menu_content += "\n[bold cyan]0.[/bold cyan] 🚪 Logout"
        
        menu_panel = Panel(
            menu_content,
            title=header,
            box=box.ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print(menu_panel)
        
        max_choice = "14" if self.current_user.is_admin else "7"
        choices = [str(i) for i in range(int(max_choice) + 1)]
        
        choice = Prompt.ask(
            "[bold magenta]Seleziona un'opzione[/bold magenta]",
            choices=choices,
            default="1"
        )
        
        # Gestisci scelte
        if choice == "1":
            self.show_user_tasks()
        elif choice == "2":
            self.add_new_task()
        elif choice == "3":
            self.edit_task()
        elif choice == "4":
            self.change_task_status()
        elif choice == "5":
            self.delete_task()
        elif choice == "6":
            self.show_personal_stats()
        elif choice == "7":
            self.change_password()
        elif choice == "8" and self.current_user.is_admin:
            self.show_all_users()
        elif choice == "9" and self.current_user.is_admin:
            self.show_all_tasks()
        elif choice == "10" and self.current_user.is_admin:
            self.create_user()
        elif choice == "11" and self.current_user.is_admin:
            self.assign_task()
        elif choice == "12" and self.current_user.is_admin:
            self.manage_users()
        elif choice == "13" and self.current_user.is_admin:
            self.delete_user()
        elif choice == "14" and self.current_user.is_admin:
            self.manage_user_tasks()
        elif choice == "0":
            self.handle_logout()
    
    def handle_login(self):
        """Gestisce il processo di login"""
        self.console.print("\n")
        login_panel = Panel(
            "[bold blue]🔐 LOGIN[/bold blue]",
            box=box.DOUBLE
        )
        self.console.print(login_panel)
        
        username = Prompt.ask("[bold cyan]Username[/bold cyan]")
        password = Prompt.ask("[bold cyan]Password[/bold cyan]", password=True)
        
        if not username or not password:
            self.console.print("[bold red]❌ Username e password sono obbligatori.[/bold red]")
            return
        
        # Animazione login
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Autenticazione in corso...", total=None)
            time.sleep(1)  # Simula processo
            
            user = self.db.authenticate_user(username, password)
            
        if user:
            self.current_user = user
            self.console.print(f"[bold green]✅ Benvenuto, {user.username}![/bold green]")
            time.sleep(1)
        else:
            self.console.print("[bold red]❌ Credenziali non valide.[/bold red]")
    
    def handle_registration(self):
        """Gestisce il processo di registrazione"""
        self.console.print("\n")
        reg_panel = Panel(
            "[bold green]📝 REGISTRAZIONE NUOVO UTENTE[/bold green]",
            box=box.DOUBLE
        )
        self.console.print(reg_panel)
        
        username = Prompt.ask("[bold cyan]Username[/bold cyan]")
        email = Prompt.ask("[bold cyan]Email[/bold cyan]")
        password = Prompt.ask("[bold cyan]Password[/bold cyan]", password=True)
        confirm_password = Prompt.ask("[bold cyan]Conferma Password[/bold cyan]", password=True)
        
        # Validazione con progress bar
        with Progress() as progress:
            task = progress.add_task("[cyan]Validazione dati...", total=4)
            
            # Validazione campi
            progress.update(task, advance=1)
            if not all([username, email, password, confirm_password]):
                self.console.print("[bold red]❌ Tutti i campi sono obbligatori.[/bold red]")
                return
            
            # Validazione password
            progress.update(task, advance=1)
            if password != confirm_password:
                self.console.print("[bold red]❌ Le password non coincidono.[/bold red]")
                return
            
            # Validazione username
            progress.update(task, advance=1)
            valid_username, msg = validate_username(username)
            if not valid_username:
                self.console.print(f"[bold red]❌ {msg}[/bold red]")
                return
            
            # Validazione email
            progress.update(task, advance=1)
            if not validate_email(email):
                self.console.print("[bold red]❌ Formato email non valido.[/bold red]")
                return
        
        # Verifica esistenza utente
        if self.db.user_exists(username, email):
            self.console.print("[bold red]❌ Username o email già esistenti.[/bold red]")
            return
        
        # Crea utente con animazione
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Creazione account...", total=None)
            time.sleep(1)
            
            user = User(username, email, password)
            success = self.db.create_user(user)
        
        if success:
            self.console.print("[bold green]✅ Registrazione completata con successo![/bold green]")
        else:
            self.console.print("[bold red]❌ Errore durante la registrazione.[/bold red]")
    
    def show_user_tasks(self):
        """Mostra i task dell'utente con tabella elegante"""
        tasks = self.db.get_user_tasks(self.current_user.user_id)
        
        if not tasks:
            self.console.print("[yellow]📋 Nessun task trovato.[/yellow]")
            return
        
        # Crea tabella
        table = Table(title=f"📋 I MIEI TASK ({len(tasks)})", box=box.ROUNDED)
        table.add_column("ID", style="dim", width=8)
        table.add_column("Titolo", style="bold")
        table.add_column("Stato", justify="center")
        table.add_column("Descrizione", style="dim")
        table.add_column("Creato", style="dim", justify="center")
        
        # Raggruppa per stato
        todo_tasks = [t for t in tasks if t.status == Task.STATUS_TODO]
        doing_tasks = [t for t in tasks if t.status == Task.STATUS_DOING]
        done_tasks = [t for t in tasks if t.status == Task.STATUS_DONE]
        
        # Aggiungi righe per stato
        for status, task_list, style in [
            ("📝 TO DO", todo_tasks, "red"),
            ("⚡ DOING", doing_tasks, "yellow"), 
            ("✅ DONE", done_tasks, "green")
        ]:
            if task_list:
                # Separatore per stato
                table.add_row("", f"[bold {style}]{status}[/bold {style}]", "", "", "")
                
                for task in task_list:
                    task_id_short = task.task_id[:8]
                    title = task.title[:30] + "..." if len(task.title) > 30 else task.title
                    description = task.description[:40] + "..." if task.description and len(task.description) > 40 else task.description or ""
                    created = task.created_at.strftime('%d/%m/%Y')
                    
                    status_text = f"[{style}]{task.status}[/{style}]"
                    
                    table.add_row(
                        task_id_short,
                        title,
                        status_text,
                        description,
                        created
                    )
        
        self.console.print(table)
        
        # Statistiche rapide
        stats_text = f"[red]To Do: {len(todo_tasks)}[/red] | [yellow]Doing: {len(doing_tasks)}[/yellow] | [green]Done: {len(done_tasks)}[/green]"
        self.console.print(f"\n📊 {stats_text}")
    
    def add_new_task(self):
        """Aggiunge un nuovo task"""
        self.console.print("\n")
        task_panel = Panel(
            "[bold green]➕ NUOVO TASK[/bold green]",
            box=box.DOUBLE
        )
        self.console.print(task_panel)
        
        title = Prompt.ask("[bold cyan]Titolo del task[/bold cyan]")
        description = Prompt.ask("[bold cyan]Descrizione[/bold cyan]", default="")
        
        if not title:
            self.console.print("[bold red]❌ Il titolo del task è obbligatorio.[/bold red]")
            return
        
        # Crea task con animazione
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task_progress = progress.add_task("Creazione task...", total=None)
            time.sleep(0.5)
            
            task = Task(title, description, self.current_user.user_id)
            success = self.db.create_task(task)
        
        if success:
            self.console.print("[bold green]✅ Task creato con successo![/bold green]")
        else:
            self.console.print("[bold red]❌ Errore durante la creazione del task.[/bold red]")
    
    def show_personal_stats(self):
        """Mostra statistiche personali con grafici"""
        tasks = self.db.get_user_tasks(self.current_user.user_id)
        
        if not tasks:
            self.console.print("[yellow]📊 Nessuna statistica disponibile.[/yellow]")
            return
        
        # Calcola statistiche
        total = len(tasks)
        todo = len([t for t in tasks if t.status == Task.STATUS_TODO])
        doing = len([t for t in tasks if t.status == Task.STATUS_DOING])
        done = len([t for t in tasks if t.status == Task.STATUS_DONE])
        completion_rate = (done / total * 100) if total > 0 else 0
        
        # Crea layout per statistiche
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        
        # Header
        header_text = f"📊 STATISTICHE PERSONALI - {self.current_user.username}"
        layout["header"].update(Panel(header_text, style="bold blue"))
        
        # Body con statistiche
        stats_table = Table(box=box.ROUNDED)
        stats_table.add_column("Metrica", style="bold cyan")
        stats_table.add_column("Valore", justify="center")
        stats_table.add_column("Grafico", width=30)
        
        # Barre di progresso per ogni stato
        def create_bar(value, total, color):
            if total == 0:
                return "[dim]━━━━━━━━━━[/dim]"
            filled = int((value / total) * 10)
            empty = 10 - filled
            return f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"
        
        stats_table.add_row("Task Totali", str(total), create_bar(total, total, "blue"))
        stats_table.add_row("Da Fare", str(todo), create_bar(todo, total, "red"))
        stats_table.add_row("In Corso", str(doing), create_bar(doing, total, "yellow"))
        stats_table.add_row("Completati", str(done), create_bar(done, total, "green"))
        stats_table.add_row("Completamento", f"{completion_rate:.1f}%", create_bar(done, total, "green"))
        
        layout["body"].update(stats_table)
        
        self.console.print(layout)
        
        # Progress bar animata per completamento
        if total > 0:
            self.console.print("\n[bold]Progresso Completamento:[/bold]")
            with Progress() as progress:
                task = progress.add_task("[green]Completamento", total=100)
                for i in range(int(completion_rate) + 1):
                    progress.update(task, completed=i)
                    time.sleep(0.02)
    
    def show_system_stats(self):
        """Mostra statistiche del sistema"""
        stats = self.db.get_database_stats()
        
        # Crea tree per statistiche
        tree = Tree("🖥️ [bold blue]STATISTICHE SISTEMA[/bold blue]")
        
        users_branch = tree.add("👥 [bold cyan]Utenti[/bold cyan]")
        users_branch.add(f"Totali: [bold]{stats['total_users']}[/bold]")
        users_branch.add(f"Amministratori: [bold red]{stats['admin_users']}[/bold red]")
        users_branch.add(f"Utenti Standard: [bold blue]{stats['regular_users']}[/bold blue]")
        
        tasks_branch = tree.add("📋 [bold cyan]Task[/bold cyan]")
        tasks_branch.add(f"Totali: [bold]{stats['total_tasks']}[/bold]")
        tasks_branch.add(f"Da Fare: [bold red]{stats['todo_tasks']}[/bold red]")
        tasks_branch.add(f"In Corso: [bold yellow]{stats['doing_tasks']}[/bold yellow]")
        tasks_branch.add(f"Completati: [bold green]{stats['done_tasks']}[/bold green]")
        
        self.console.print(tree)
        
        # Grafico a barre per task
        if stats['total_tasks'] > 0:
            self.console.print("\n[bold]Distribuzione Task:[/bold]")
            
            # Simula caricamento dati
            with Progress() as progress:
                task = progress.add_task("[cyan]Caricamento dati...", total=100)
                for i in range(101):
                    progress.update(task, completed=i)
                    time.sleep(0.01)
            
            # Crea grafico
            total = stats['total_tasks']
            todo_bar = "█" * int((stats['todo_tasks'] / total) * 20)
            doing_bar = "█" * int((stats['doing_tasks'] / total) * 20)
            done_bar = "█" * int((stats['done_tasks'] / total) * 20)
            
            self.console.print(f"[red]To Do   [{todo_bar:<20}] {stats['todo_tasks']}[/red]")
            self.console.print(f"[yellow]Doing   [{doing_bar:<20}] {stats['doing_tasks']}[/yellow]")
            self.console.print(f"[green]Done    [{done_bar:<20}] {stats['done_tasks']}[/green]")
    
    def handle_exit(self):
        """Gestisce l'uscita dall'applicazione"""
        if Confirm.ask("[bold yellow]Sei sicuro di voler uscire?[/bold yellow]"):
            self.console.print("\n[bold blue]Grazie per aver usato Taskboard![/bold blue]")
            
            # Animazione di uscita
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task("Chiusura applicazione...", total=None)
                time.sleep(1)
            
            self.is_running = False
    
    def handle_logout(self):
        """Gestisce il logout"""
        self.current_user = None
        self.console.print("[bold green]✅ Logout effettuato con successo.[/bold green]")
        time.sleep(1)
        self.console.clear()
    
    # Metodi aggiuntivi per completezza
    def handle_password_recovery(self):
        """Gestisce il recupero password"""
        self.console.print("\n")
        recovery_panel = Panel(
            "[bold yellow]🔑 RECUPERO PASSWORD[/bold yellow]",
            box=box.DOUBLE
        )
        self.console.print(recovery_panel)
        
        email = Prompt.ask("[bold cyan]Email[/bold cyan]")
        
        if not email:
            self.console.print("[bold red]❌ Email obbligatoria.[/bold red]")
            return
        
        user = self.db.get_user_by_email(email)
        if not user:
            self.console.print("[bold red]❌ Email non trovata nel sistema.[/bold red]")
            return
        
        # Crea token di recupero
        recovery = PasswordRecovery(user.user_id, email)
        if self.db.create_password_recovery(recovery):
            self.console.print(f"[bold green]✅ Token di recupero generato: {recovery.token}[/bold green]")
            self.console.print("[bold cyan]Usa questo token per reimpostare la password.[/bold cyan]")
            
            # Richiedi token e nuova password
            token = Prompt.ask("[bold cyan]Token di recupero[/bold cyan]")
            if token == recovery.token and recovery.is_valid():
                new_password = Prompt.ask("[bold cyan]Nuova password[/bold cyan]", password=True)
                if len(new_password) >= 6:
                    user.change_password(new_password)
                    self.db.update_user(user)
                    recovery.use_token()
                    self.db.update_password_recovery(recovery)
                    self.console.print("[bold green]✅ Password reimpostata con successo![/bold green]")
                else:
                    self.console.print("[bold red]❌ La password deve essere di almeno 6 caratteri.[/bold red]")
            else:
                self.console.print("[bold red]❌ Token non valido o scaduto.[/bold red]")
        else:
            self.console.print("[bold red]❌ Errore durante la generazione del token.[/bold red]")
    
    def edit_task(self):
        """Modifica un task"""
        tasks = self.db.get_user_tasks(self.current_user.user_id)
        if not tasks:
            self.console.print("[bold red]❌ Non hai task da modificare.[/bold red]")
            return
        
        self.show_user_tasks()
        
        task_id = Prompt.ask("[bold cyan]Inserisci l'ID del task da modificare[/bold cyan]")
        task = self.db.get_task_by_id(task_id)
        
        if not task or task.user_id != self.current_user.user_id:
            self.console.print("[bold red]❌ Task non trovato o non autorizzato.[/bold red]")
            return
        
        # Mostra dettagli task corrente
        task_panel = Panel(
            f"[bold]Titolo:[/bold] {task.title}\n[bold]Descrizione:[/bold] {task.description}\n[bold]Stato:[/bold] {task.status}",
            title="📋 Task Corrente",
            box=box.ROUNDED
        )
        self.console.print(task_panel)
        
        new_title = Prompt.ask("[bold cyan]Nuovo titolo (lascia vuoto per non modificare)[/bold cyan]", default="")
        new_description = Prompt.ask("[bold cyan]Nuova descrizione (lascia vuoto per non modificare)[/bold cyan]", default="")
        
        if new_title or new_description:
            task.update_details(new_title, new_description)
            if self.db.update_task(task):
                self.console.print("[bold green]✅ Task aggiornato con successo![/bold green]")
            else:
                self.console.print("[bold red]❌ Errore durante l'aggiornamento.[/bold red]")
        else:
            self.console.print("[bold yellow]ℹ️ Nessuna modifica effettuata.[/bold yellow]")
    
    def change_task_status(self):
        """Cambia stato task"""
        tasks = self.db.get_user_tasks(self.current_user.user_id)
        if not tasks:
            self.console.print("[bold red]❌ Non hai task da modificare.[/bold red]")
            return
        
        self.show_user_tasks()
        
        task_id = Prompt.ask("[bold cyan]Inserisci l'ID del task[/bold cyan]")
        task = self.db.get_task_by_id(task_id)
        
        if not task or task.user_id != self.current_user.user_id:
            self.console.print("[bold red]❌ Task non trovato o non autorizzato.[/bold red]")
            return
        
        # Mostra stati disponibili
        status_panel = Panel(
            "[bold cyan]1.[/bold cyan] 📝 To Do\n[bold cyan]2.[/bold cyan] ⚡ Doing\n[bold cyan]3.[/bold cyan] ✅ Done",
            title="🔄 Seleziona Nuovo Stato",
            box=box.ROUNDED
        )
        self.console.print(status_panel)
        
        status_choice = Prompt.ask(
            "[bold magenta]Seleziona stato[/bold magenta]",
            choices=["1", "2", "3"]
        )
        
        status_map = {
            "1": Task.STATUS_TODO,
            "2": Task.STATUS_DOING,
            "3": Task.STATUS_DONE
        }
        
        new_status = status_map[status_choice]
        if task.update_status(new_status):
            if self.db.update_task(task):
                self.console.print(f"[bold green]✅ Stato cambiato in: {new_status}[/bold green]")
            else:
                self.console.print("[bold red]❌ Errore durante l'aggiornamento.[/bold red]")
        else:
            self.console.print("[bold red]❌ Stato non valido.[/bold red]")
    
    def delete_task(self):
        """Elimina task"""
        tasks = self.db.get_user_tasks(self.current_user.user_id)
        if not tasks:
            self.console.print("[bold red]❌ Non hai task da eliminare.[/bold red]")
            return
        
        self.show_user_tasks()
        
        task_id = Prompt.ask("[bold cyan]Inserisci l'ID del task da eliminare[/bold cyan]")
        task = self.db.get_task_by_id(task_id)
        
        if not task or task.user_id != self.current_user.user_id:
            self.console.print("[bold red]❌ Task non trovato o non autorizzato.[/bold red]")
            return
        
        # Mostra dettagli task
        task_panel = Panel(
            f"[bold]Titolo:[/bold] {task.title}\n[bold]Descrizione:[/bold] {task.description}",
            title="🗑️ Task da Eliminare",
            box=box.ROUNDED
        )
        self.console.print(task_panel)
        
        if Confirm.ask("[bold red]Sei sicuro di voler eliminare questo task?[/bold red]"):
            if self.db.delete_task(task_id):
                self.console.print("[bold green]✅ Task eliminato con successo![/bold green]")
            else:
                self.console.print("[bold red]❌ Errore durante l'eliminazione.[/bold red]")
        else:
            self.console.print("[bold yellow]ℹ️ Eliminazione annullata.[/bold yellow]")
    
    def change_password(self):
        """Cambia password"""
        self.console.print("\n")
        password_panel = Panel(
            "[bold blue]🔒 CAMBIO PASSWORD[/bold blue]",
            box=box.DOUBLE
        )
        self.console.print(password_panel)
        
        new_password = Prompt.ask("[bold cyan]Nuova password[/bold cyan]", password=True)
        
        if len(new_password) < 6:
            self.console.print("[bold red]❌ La password deve essere di almeno 6 caratteri.[/bold red]")
            return
        
        self.current_user.change_password(new_password)
        if self.db.update_user(self.current_user):
            self.console.print("[bold green]✅ Password cambiata con successo![/bold green]")
        else:
            self.console.print("[bold red]❌ Errore durante il cambio password.[/bold red]")
    
    def show_all_users(self):
        """Mostra tutti gli utenti (admin)"""
        users = self.db.get_all_users()
        
        if not users:
            self.console.print("[bold yellow]👥 Nessun utente trovato.[/bold yellow]")
            return
        
        # Crea tabella utenti
        table = Table(title="👥 TUTTI GLI UTENTI", box=box.ROUNDED)
        table.add_column("ID", style="dim", width=8)
        table.add_column("Username", style="bold")
        table.add_column("Email", style="cyan")
        table.add_column("Tipo", justify="center")
        table.add_column("Registrato", style="dim", justify="center")
        
        for user in users:
            user_id_short = user.user_id[:8]
            user_type = "[bold red]ADMIN[/bold red]" if user.is_admin else "[bold blue]USER[/bold blue]"
            registered = user.created_at.strftime('%d/%m/%Y') if hasattr(user, 'created_at') else "N/A"
            
            table.add_row(
                user_id_short,
                user.username,
                user.email,
                user_type,
                registered
            )
        
        self.console.print(table)
    
    def show_all_tasks(self):
        """Mostra tutti i task (admin)"""
        tasks_with_users = self.db.get_all_tasks_with_users()
        
        if not tasks_with_users:
            self.console.print("[bold yellow]📊 Nessun task trovato.[/bold yellow]")
            return
        
        # Crea tabella task con proprietari
        table = Table(title=f"📊 TUTTI I TASK ({len(tasks_with_users)})", box=box.ROUNDED)
        table.add_column("ID", style="dim", width=8)
        table.add_column("Titolo", style="bold")
        table.add_column("Proprietario", style="cyan")
        table.add_column("Stato", justify="center")
        table.add_column("Creato", style="dim", justify="center")
        
        for task_data in tasks_with_users:
            task_id_short = task_data['task_id'][:8]
            title = task_data['title'][:30] + "..." if len(task_data['title']) > 30 else task_data['title']
            owner = task_data['username']
            status = task_data['status']
            created = task_data['created_at'][:10] if task_data['created_at'] else "N/A"
            
            # Colore stato
            if status == Task.STATUS_TODO:
                status_text = f"[red]{status}[/red]"
            elif status == Task.STATUS_DOING:
                status_text = f"[yellow]{status}[/yellow]"
            else:
                status_text = f"[green]{status}[/green]"
            
            table.add_row(
                task_id_short,
                title,
                owner,
                status_text,
                created
            )
        
        self.console.print(table)
    
    def create_user(self):
        """Crea un nuovo utente (admin)"""
        self.console.print("\n")
        create_panel = Panel(
            "[bold green]👤 CREA NUOVO UTENTE[/bold green]",
            box=box.DOUBLE
        )
        self.console.print(create_panel)
        
        # Selezione tipo utente
        user_type_panel = Panel(
            "[bold cyan]1.[/bold cyan] Utente normale\n[bold cyan]2.[/bold cyan] Amministratore",
            title="Tipo Utente",
            box=box.ROUNDED
        )
        self.console.print(user_type_panel)
        
        user_type_choice = Prompt.ask(
            "[bold magenta]Seleziona tipo utente[/bold magenta]",
            choices=["1", "2"],
            default="1"
        )
        
        # Richiedi dati utente
        username = Prompt.ask("[bold cyan]Username[/bold cyan]")
        email = Prompt.ask("[bold cyan]Email[/bold cyan]")
        password = Prompt.ask("[bold cyan]Password[/bold cyan]", password=True)
        confirm_password = Prompt.ask("[bold cyan]Conferma password[/bold cyan]", password=True)
        
        # Validazione
        if not all([username, email, password, confirm_password]):
            self.console.print("[bold red]❌ Tutti i campi sono obbligatori.[/bold red]")
            return
        
        if password != confirm_password:
            self.console.print("[bold red]❌ Le password non coincidono.[/bold red]")
            return
        
        if len(password) < 6:
            self.console.print("[bold red]❌ La password deve essere di almeno 6 caratteri.[/bold red]")
            return
        
        # Verifica se username o email esistono già
        if self.db.user_exists(username, email):
            self.console.print("[bold red]❌ Username o email già esistenti.[/bold red]")
            return
        
        # Crea utente
        if user_type_choice == "2":
            user = Admin(username, email, password)
            user_type = "amministratore"
        else:
            user = User(username, email, password)
            user_type = "utente"
        
        # Animazione creazione
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(f"Creazione {user_type}...", total=None)
            time.sleep(1)
            success = self.db.create_user(user)
        
        if success:
            self.console.print(f"[bold green]✅ Nuovo {user_type} '{username}' creato con successo![/bold green]")
        else:
            self.console.print("[bold red]❌ Errore durante la creazione dell'utente.[/bold red]")
    
    def assign_task(self):
        """Assegna un task a un utente (admin)"""
        # Mostra tutti gli utenti
        users = self.db.get_all_users()
        if not users:
            self.console.print("[bold red]❌ Nessun utente trovato.[/bold red]")
            return
        
        self.show_all_users()
        
        # Seleziona utente
        user_id = Prompt.ask("[bold cyan]Inserisci l'ID dell'utente a cui assegnare il task[/bold cyan]")
        user = self.db.get_user_by_id(user_id)
        
        if not user:
            self.console.print("[bold red]❌ Utente non trovato.[/bold red]")
            return
        
        # Pannello assegnazione
        assign_panel = Panel(
            f"[bold blue]📋 ASSEGNA TASK A: {user.username}[/bold blue]",
            box=box.DOUBLE
        )
        self.console.print(assign_panel)
        
        # Richiedi dati task
        title = Prompt.ask("[bold cyan]Titolo del task[/bold cyan]")
        description = Prompt.ask("[bold cyan]Descrizione del task[/bold cyan]", default="")
        
        if not title:
            self.console.print("[bold red]❌ Il titolo del task è obbligatorio.[/bold red]")
            return
        
        # Crea task assegnato all'utente specificato
        task = Task(title, description, user_id)
        
        # Animazione assegnazione
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task_progress = progress.add_task("Assegnazione task...", total=None)
            time.sleep(0.5)
            success = self.db.create_task(task)
        
        if success:
            self.console.print(f"[bold green]✅ Task '{title}' assegnato a {user.username} con successo![/bold green]")
        else:
            self.console.print("[bold red]❌ Errore durante l'assegnazione del task.[/bold red]")
    
    def manage_users(self):
        """Gestisce utenti (admin)"""
        users = self.db.get_all_users()
        if not users:
            self.console.print("[bold red]❌ Nessun utente trovato.[/bold red]")
            return
        
        self.show_all_users()
        
        user_id = Prompt.ask("[bold cyan]Inserisci l'ID dell'utente da gestire[/bold cyan]")
        user = self.db.get_user_by_id(user_id)
        
        if not user:
            self.console.print("[bold red]❌ Utente non trovato.[/bold red]")
            return
        
        # Menu gestione utente
        manage_panel = Panel(
            f"[bold cyan]1.[/bold cyan] Promuovi ad Admin\n[bold cyan]2.[/bold cyan] Rimuovi privilegi Admin\n[bold cyan]3.[/bold cyan] Reimposta password",
            title=f"👤 GESTIONE UTENTE: {user.username}",
            box=box.ROUNDED
        )
        self.console.print(manage_panel)
        
        choice = Prompt.ask(
            "[bold magenta]Seleziona azione[/bold magenta]",
            choices=["1", "2", "3"],
            default="1"
        )
        
        if choice == "1":
            user.is_admin = True
            if self.db.update_user(user):
                self.console.print(f"[bold green]✅ {user.username} promosso ad Admin![/bold green]")
            else:
                self.console.print("[bold red]❌ Errore durante la promozione.[/bold red]")
        elif choice == "2":
            user.is_admin = False
            if self.db.update_user(user):
                self.console.print(f"[bold green]✅ Privilegi Admin rimossi da {user.username}![/bold green]")
            else:
                self.console.print("[bold red]❌ Errore durante la rimozione privilegi.[/bold red]")
        elif choice == "3":
            new_password = Prompt.ask("[bold cyan]Nuova password[/bold cyan]", password=True)
            if len(new_password) >= 6:
                user.change_password(new_password)
                if self.db.update_user(user):
                    self.console.print(f"[bold green]✅ Password di {user.username} reimpostata![/bold green]")
                else:
                    self.console.print("[bold red]❌ Errore durante il reset password.[/bold red]")
            else:
                self.console.print("[bold red]❌ Password troppo corta.[/bold red]")
    
    def delete_user(self):
        """Elimina utente (admin)"""
        users = self.db.get_all_users()
        if not users:
            self.console.print("[bold red]❌ Nessun utente trovato.[/bold red]")
            return
        
        self.show_all_users()
        
        user_id = Prompt.ask("[bold cyan]Inserisci l'ID dell'utente da eliminare[/bold cyan]")
        user = self.db.get_user_by_id(user_id)
        
        if not user:
            self.console.print("[bold red]❌ Utente non trovato.[/bold red]")
            return
        
        if user.user_id == self.current_user.user_id:
            self.console.print("[bold red]❌ Non puoi eliminare te stesso.[/bold red]")
            return
        
        user_tasks = self.db.get_user_tasks(user_id)
        
        # Pannello conferma eliminazione
        delete_panel = Panel(
            f"[bold red]⚠️ ATTENZIONE ⚠️[/bold red]\n\nStai per eliminare:\n[bold]Utente:[/bold] {user.username}\n[bold]Task associati:[/bold] {len(user_tasks)}",
            title="🗑️ Conferma Eliminazione",
            box=box.DOUBLE
        )
        self.console.print(delete_panel)
        
        if Confirm.ask(f"[bold red]Eliminare {user.username} e tutti i suoi {len(user_tasks)} task?[/bold red]"):
            # Animazione eliminazione
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task("Eliminazione in corso...", total=None)
                time.sleep(1)
                success = self.db.delete_user_and_tasks(user_id)
            
            if success:
                self.console.print(f"[bold green]✅ Utente {user.username} eliminato![/bold green]")
            else:
                self.console.print("[bold red]❌ Errore durante l'eliminazione.[/bold red]")
        else:
            self.console.print("[bold yellow]ℹ️ Eliminazione annullata.[/bold yellow]")
    
    def manage_user_tasks(self):
        """Gestisce task utenti (admin)"""
        users = self.db.get_all_users()
        if not users:
            self.console.print("[bold red]❌ Nessun utente trovato.[/bold red]")
            return
        
        self.show_all_users()
        
        user_id = Prompt.ask("[bold cyan]Inserisci l'ID dell'utente[/bold cyan]")
        user = self.db.get_user_by_id(user_id)
        
        if not user:
            self.console.print("[bold red]❌ Utente non trovato.[/bold red]")
            return
        
        tasks = self.db.get_user_tasks(user_id)
        if not tasks:
            self.console.print(f"[bold yellow]📋 {user.username} non ha task.[/bold yellow]")
            return
        
        # Mostra task dell'utente
        table = Table(title=f"📋 TASK DI {user.username}", box=box.ROUNDED)
        table.add_column("ID", style="dim", width=8)
        table.add_column("Titolo", style="bold")
        table.add_column("Stato", justify="center")
        table.add_column("Descrizione", style="dim")
        
        for task in tasks:
            task_id_short = task.task_id[:8]
            title = task.title[:30] + "..." if len(task.title) > 30 else task.title
            description = task.description[:40] + "..." if task.description and len(task.description) > 40 else task.description or ""
            
            if task.status == Task.STATUS_TODO:
                status_text = f"[red]{task.status}[/red]"
            elif task.status == Task.STATUS_DOING:
                status_text = f"[yellow]{task.status}[/yellow]"
            else:
                status_text = f"[green]{task.status}[/green]"
            
            table.add_row(task_id_short, title, status_text, description)
        
        self.console.print(table)
        
        # Menu azioni
        action_panel = Panel(
            "[bold cyan]1.[/bold cyan] Modifica task\n[bold cyan]2.[/bold cyan] Modifica stato task\n[bold cyan]3.[/bold cyan] Elimina task",
            title="🔧 Azioni Disponibili",
            box=box.ROUNDED
        )
        self.console.print(action_panel)
        
        choice = Prompt.ask(
            "[bold magenta]Seleziona azione[/bold magenta]",
            choices=["1", "2", "3"],
            default="1"
        )
        
        if choice == "1":
            task_id = Prompt.ask("[bold cyan]Inserisci l'ID del task da modificare[/bold cyan]")
            task = self.db.get_task_by_id(task_id)
            
            if task and task.user_id == user_id:
                # Mostra dettagli task corrente
                task_panel = Panel(
                    f"[bold]Titolo:[/bold] {task.title}\n[bold]Descrizione:[/bold] {task.description}",
                    title="📋 Task Corrente",
                    box=box.ROUNDED
                )
                self.console.print(task_panel)
                
                new_title = Prompt.ask("[bold cyan]Nuovo titolo (lascia vuoto per non modificare)[/bold cyan]", default="")
                new_description = Prompt.ask("[bold cyan]Nuova descrizione (lascia vuoto per non modificare)[/bold cyan]", default="")
                
                if new_title or new_description:
                    task.update_details(new_title, new_description)
                    if self.db.update_task(task):
                        self.console.print("[bold green]✅ Task aggiornato con successo![/bold green]")
                    else:
                        self.console.print("[bold red]❌ Errore durante l'aggiornamento.[/bold red]")
                else:
                    self.console.print("[bold yellow]ℹ️ Nessuna modifica effettuata.[/bold yellow]")
            else:
                self.console.print("[bold red]❌ Task non trovato.[/bold red]")
        
        elif choice == "2":
            task_id = Prompt.ask("[bold cyan]Inserisci l'ID del task[/bold cyan]")
            task = self.db.get_task_by_id(task_id)
            
            if task and task.user_id == user_id:
                # Mostra stati disponibili
                status_panel = Panel(
                    "[bold cyan]1.[/bold cyan] 📝 To Do\n[bold cyan]2.[/bold cyan] ⚡ Doing\n[bold cyan]3.[/bold cyan] ✅ Done",
                    title="🔄 Seleziona Nuovo Stato",
                    box=box.ROUNDED
                )
                self.console.print(status_panel)
                
                status_choice = Prompt.ask(
                    "[bold magenta]Seleziona stato[/bold magenta]",
                    choices=["1", "2", "3"]
                )
                
                status_map = {"1": Task.STATUS_TODO, "2": Task.STATUS_DOING, "3": Task.STATUS_DONE}
                task.update_status(status_map[status_choice])
                
                if self.db.update_task(task):
                    self.console.print("[bold green]✅ Stato task aggiornato![/bold green]")
                else:
                    self.console.print("[bold red]❌ Errore durante l'aggiornamento.[/bold red]")
            else:
                self.console.print("[bold red]❌ Task non trovato.[/bold red]")
        
        elif choice == "3":
            task_id = Prompt.ask("[bold cyan]Inserisci l'ID del task da eliminare[/bold cyan]")
            task = self.db.get_task_by_id(task_id)
            
            if task and task.user_id == user_id:
                if Confirm.ask("[bold red]Eliminare questo task?[/bold red]"):
                    if self.db.delete_task(task_id):
                        self.console.print("[bold green]✅ Task eliminato![/bold green]")
                    else:
                        self.console.print("[bold red]❌ Errore durante l'eliminazione.[/bold red]")
            else:
                self.console.print("[bold red]❌ Task non trovato.[/bold red]")

def main():
    """Funzione principale per avviare la CLI migliorata"""
    try:
        app = RichTaskboardCLI()
        app.run()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[bold red]Applicazione interrotta dall'utente.[/bold red]")
    except Exception as e:
        console = Console()
        console.print(f"[bold red]Errore critico: {str(e)}[/bold red]")
        console.print_exception()

if __name__ == "__main__":
    main()