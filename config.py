"""
CONFIGURAZIONE - File di configurazione dell'applicazione
Contiene costanti e impostazioni globali
"""

# Configurazione Database
DATABASE_PATH = "taskboard.db"
DATABASE_TIMEOUT = 30.0

# Configurazione Sicurezza
PASSWORD_MIN_LENGTH = 4
USERNAME_MIN_LENGTH = 3
MAX_LOGIN_ATTEMPTS = 3

# Configurazione UI
MENU_SEPARATOR = "=" * 50
SUBMENU_SEPARATOR = "-" * 30
MAX_TITLE_DISPLAY_LENGTH = 25
MAX_DESCRIPTION_DISPLAY_LENGTH = 30

# Messaggi dell'applicazione
MESSAGES = {
    "welcome": "TASKBOARD - Gestione Attività Personali",
    "goodbye": "Arrivederci!",
    "login_success": "Login effettuato con successo!",
    "login_failed": "Credenziali non valide!",
    "register_success": "Registrazione completata! Ora puoi effettuare il login.",
    "register_failed": "Errore durante la registrazione!",
    "task_created": "Task creato con successo!",
    "task_updated": "Task aggiornato con successo!",
    "task_deleted": "Task eliminato con successo!",
    "no_tasks": "Non hai ancora creato nessun task.",
    "invalid_choice": "Opzione non valida!",
    "operation_cancelled": "Operazione annullata.",
    "database_error": "Errore del database. Riprova più tardi.",
    "unexpected_error": "Errore imprevisto. Contatta l'amministratore."
}

# Configurazione Task
TASK_STATUSES = {
    "TODO": "ToDo",
    "DOING": "Doing", 
    "DONE": "Done"
}

# Simboli per l'interfaccia
SYMBOLS = {
    "success": "✓",
    "error": "✗",
    "info": "ℹ",
    "warning": "⚠",
    "task": "📋",
    "user": "👤",
    "arrow": "→"
}