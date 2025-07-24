"""
SIMPLE RICH VIEW - Interfaccia CLI avanzata con Rich (senza emoji per compatibilità Windows)
Versione semplificata della view Rich compatibile con tutti i sistemi
"""

from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from rich import box
from rich.columns import Columns
import time

from model.model import User, Task
from utils import calculate_task_stats, format_datetime


class SimpleRichTaskboardView:
    """
    Classe che gestisce l'interfaccia utente CLI avanzata con Rich
    Versione semplificata senza emoji per compatibilità Windows
    """
    
    def __init__(self):
        self.console = Console()
        self.current_user: Optional[User] = None
    
    def show_welcome(self) -> None:
        """Mostra il messaggio di benvenuto con stile"""
        self.console.clear()
        
        # Titolo principale con pannello
        title = Text("TASKBOARD", style="bold magenta", justify="center")
        subtitle = Text("Gestione Attivita Personali", style="italic cyan", justify="center")
        
        welcome_panel = Panel(
            Align.center(f"{title}\n{subtitle}"),
            box=box.DOUBLE,
            style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(welcome_panel)
        self.console.print()
    
    def show_main_menu(self) -> str:
        """Mostra il menu principale con stile Rich"""
        if self.current_user:
            # Menu per utenti autenticati
            user_info = f"Utente: [bold green]{self.current_user.username}[/bold green]"
            self.console.print(Panel(user_info, style="green", box=box.ROUNDED))
            
            menu_items = [
                "1. Visualizza i miei task",
                "2. Aggiungi nuovo task", 
                "3. Modifica task",
                "4. Cambia stato task",
                "5. Elimina task",
                "6. Bacheca Kanban",
                "7. Statistiche",
                "8. Logout",
                "0. Esci"
            ]
        else:
            # Menu per utenti non autenticati
            menu_items = [
                "1. Login",
                "2. Registrazione", 
                "0. Esci"
            ]
        
        menu_text = "\n".join(menu_items)
        menu_panel = Panel(
            menu_text,
            title="[bold blue]MENU PRINCIPALE[/bold blue]",
            box=box.ROUNDED,
            style="blue"
        )
        
        self.console.print(menu_panel)
        
        return Prompt.ask(
            "\n[bold yellow]Scegli un'opzione[/bold yellow]",
            choices=[str(i) for i in range(9)] if self.current_user else ["0", "1", "2"],
            show_choices=False
        )
    
    def show_login_form(self) -> tuple[str, str]:
        """Raccoglie i dati per il login con stile"""
        login_panel = Panel(
            "[bold blue]ACCESSO AL SISTEMA[/bold blue]",
            style="blue",
            box=box.DOUBLE
        )
        self.console.print(login_panel)
        
        username = Prompt.ask("[bold]Username[/bold]")
        password = Prompt.ask("[bold]Password[/bold]", password=True)
        
        return username, password
    
    def show_register_form(self) -> tuple[str, str]:
        """Raccoglie i dati per la registrazione con stile"""
        register_panel = Panel(
            "[bold green]REGISTRAZIONE NUOVO UTENTE[/bold green]",
            style="green",
            box=box.DOUBLE
        )
        self.console.print(register_panel)
        
        username = Prompt.ask("[bold]Username[/bold]")
        password = Prompt.ask("[bold]Password[/bold]", password=True)
        password_confirm = Prompt.ask("[bold]Conferma Password[/bold]", password=True)
        
        if password != password_confirm:
            self.show_error("Le password non coincidono!")
            return "", ""
        
        return username, password
    
    def show_task_form(self, task: Optional[Task] = None) -> tuple[str, str]:
        """Raccoglie i dati per creare/modificare un task con stile"""
        if task:
            form_panel = Panel(
                f"[bold yellow]MODIFICA TASK: {task.title}[/bold yellow]",
                style="yellow",
                box=box.DOUBLE
            )
            self.console.print(form_panel)
            
            title = Prompt.ask(
                f"[bold]Titolo[/bold]",
                default=task.title
            )
            description = Prompt.ask(
                f"[bold]Descrizione[/bold]",
                default=task.description
            )
        else:
            form_panel = Panel(
                "[bold green]NUOVO TASK[/bold green]",
                style="green",
                box=box.DOUBLE
            )
            self.console.print(form_panel)
            
            title = Prompt.ask("[bold]Titolo[/bold]")
            description = Prompt.ask("[bold]Descrizione[/bold]", default="")
        
        return title, description
    
    def show_task_list(self, tasks: List[Task]) -> None:
        """Visualizza la lista dei task con tabella elegante"""
        if not tasks:
            self.show_info("Nessun task trovato.")
            return
        
        # Calcola statistiche
        stats = calculate_task_stats(tasks)
        
        # Pannello statistiche
        stats_text = f"Totale: {stats['total']} | ToDo: {stats['todo']} | Doing: {stats['doing']} | Done: {stats['done']} | Completamento: {stats['completion_rate']}%"
        stats_panel = Panel(stats_text, style="cyan", box=box.ROUNDED)
        self.console.print(stats_panel)
        
        # Tabella task
        table = Table(
            title=f"I TUOI TASK ({len(tasks)})",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("ID", style="dim", width=4, justify="center")
        table.add_column("Titolo", style="bold", min_width=20)
        table.add_column("Stato", justify="center", width=12)
        table.add_column("Descrizione", style="dim", min_width=25)
        table.add_column("Creato", style="dim", width=16)
        
        for task in tasks:
            # Colore dello stato
            if task.status == "ToDo":
                status_style = "[yellow]ToDo[/yellow]"
            elif task.status == "Doing":
                status_style = "[blue]Doing[/blue]"
            else:
                status_style = "[green]Done[/green]"
            
            # Tronca descrizione se troppo lunga
            desc = task.description[:30] + "..." if len(task.description) > 30 else task.description
            
            table.add_row(
                str(task.task_id),
                task.title,
                status_style,
                desc,
                format_datetime(task.created_at)
            )
        
        self.console.print(table)
    
    def show_kanban_board(self, tasks: List[Task]) -> None:
        """Visualizza la bacheca Kanban con colonne colorate"""
        # Raggruppa i task per stato
        todo_tasks = [t for t in tasks if t.status == Task.STATUS_TODO]
        doing_tasks = [t for t in tasks if t.status == Task.STATUS_DOING]
        done_tasks = [t for t in tasks if t.status == Task.STATUS_DONE]
        
        # Crea le colonne
        todo_panel = self._create_kanban_column("TODO", todo_tasks, "yellow")
        doing_panel = self._create_kanban_column("DOING", doing_tasks, "blue")
        done_panel = self._create_kanban_column("DONE", done_tasks, "green")
        
        # Layout a colonne
        columns = Columns([todo_panel, doing_panel, done_panel], equal=True, expand=True)
        
        kanban_title = Panel(
            "[bold magenta]BACHECA KANBAN[/bold magenta]",
            style="magenta",
            box=box.DOUBLE
        )
        
        self.console.print(kanban_title)
        self.console.print(columns)
    
    def _create_kanban_column(self, title: str, tasks: List[Task], color: str) -> Panel:
        """Crea una colonna della bacheca Kanban"""
        if not tasks:
            content = "[dim]Nessun task[/dim]"
        else:
            task_items = []
            for task in tasks:
                task_title = task.title[:20] + "..." if len(task.title) > 20 else task.title
                task_items.append(f"- {task_title}")
            content = "\n".join(task_items)
        
        return Panel(
            content,
            title=f"[bold]{title} ({len(tasks)})[/bold]",
            style=color,
            box=box.ROUNDED,
            height=15
        )
    
    def show_status_menu(self) -> str:
        """Mostra il menu per la selezione dello stato"""
        status_panel = Panel(
            "[bold blue]CAMBIA STATO TASK[/bold blue]\n\n1. ToDo\n2. Doing\n3. Done",
            style="blue",
            box=box.DOUBLE
        )
        self.console.print(status_panel)
        
        return Prompt.ask(
            "[bold]Scegli nuovo stato (1-3)[/bold]",
            choices=["1", "2", "3"],
            show_choices=False
        )
    
    def get_task_id(self, action: str = "selezionare") -> int:
        """Raccoglie l'ID del task dall'utente"""
        try:
            return int(Prompt.ask(f"[bold]ID del task da {action}[/bold]"))
        except ValueError:
            self.show_error("ID non valido!")
            return -1
    
    def show_task_statistics(self, tasks: List[Task]) -> None:
        """Mostra statistiche dettagliate sui task"""
        if not tasks:
            self.show_info("Nessun task per le statistiche.")
            return
        
        stats = calculate_task_stats(tasks)
        
        # Tabella statistiche
        stats_table = Table(
            title="STATISTICHE TASK",
            box=box.DOUBLE,
            show_header=True,
            header_style="bold cyan"
        )
        
        stats_table.add_column("Metrica", style="bold", width=20)
        stats_table.add_column("Valore", justify="center", width=10)
        stats_table.add_column("Percentuale", justify="center", width=15)
        
        total = stats['total']
        stats_table.add_row("Totale Task", str(total), "100.0%")
        stats_table.add_row("ToDo", str(stats['todo']), f"{(stats['todo']/total*100):.1f}%" if total > 0 else "0%")
        stats_table.add_row("In Corso", str(stats['doing']), f"{(stats['doing']/total*100):.1f}%" if total > 0 else "0%")
        stats_table.add_row("Completati", str(stats['done']), f"{stats['completion_rate']}%")
        
        self.console.print(stats_table)
        
        # Barra di progresso del completamento
        if total > 0:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task("Caricamento statistiche...", total=100)
                for i in range(int(stats['completion_rate']) + 1):
                    progress.update(task, advance=1)
                    time.sleep(0.02)
            
            completion_text = f"Tasso di completamento: {stats['completion_rate']}%"
            if stats['completion_rate'] >= 80:
                style = "bold green"
            elif stats['completion_rate'] >= 50:
                style = "bold yellow"
            else:
                style = "bold red"
            
            completion_panel = Panel(completion_text, style=style, box=box.ROUNDED)
            self.console.print(completion_panel)
    
    def show_success(self, message: str) -> None:
        """Mostra un messaggio di successo con stile"""
        success_panel = Panel(
            f"SUCCESSO: {message}",
            style="bold green",
            box=box.ROUNDED
        )
        self.console.print(success_panel)
    
    def show_error(self, message: str) -> None:
        """Mostra un messaggio di errore con stile"""
        error_panel = Panel(
            f"ERRORE: {message}",
            style="bold red",
            box=box.ROUNDED
        )
        self.console.print(error_panel)
    
    def show_info(self, message: str) -> None:
        """Mostra un messaggio informativo con stile"""
        info_panel = Panel(
            f"INFO: {message}",
            style="bold blue",
            box=box.ROUNDED
        )
        self.console.print(info_panel)
    
    def show_warning(self, message: str) -> None:
        """Mostra un messaggio di avviso con stile"""
        warning_panel = Panel(
            f"ATTENZIONE: {message}",
            style="bold yellow",
            box=box.ROUNDED
        )
        self.console.print(warning_panel)
    
    def confirm_action(self, message: str) -> bool:
        """Chiede conferma per un'azione con stile"""
        return Confirm.ask(f"{message}")
    
    def pause(self) -> None:
        """Pausa per permettere all'utente di leggere"""
        Prompt.ask("\n[dim]Premi INVIO per continuare...[/dim]", default="")
    
    def clear_screen(self) -> None:
        """Pulisce lo schermo"""
        self.console.clear()
    
    def set_current_user(self, user: Optional[User]) -> None:
        """Imposta l'utente corrente"""
        self.current_user = user
    
    def show_loading(self, message: str, duration: float = 1.0) -> None:
        """Mostra un'animazione di caricamento"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(message, total=100)
            for i in range(100):
                progress.update(task, advance=1)
                time.sleep(duration / 100)