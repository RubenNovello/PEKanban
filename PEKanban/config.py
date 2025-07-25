# config.py - File di configurazione per l'applicazione Taskboard
# Contiene tutte le impostazioni e costanti dell'applicazione

import os
from typing import Dict, Any

class Config:
    """Classe di configurazione principale"""
    
    # Database
    DATABASE_NAME = "database.db"
    DATABASE_BACKUP_DIR = "backups"
    
    # Sicurezza
    MIN_PASSWORD_LENGTH = 6
    RECOMMENDED_PASSWORD_LENGTH = 8
    TOKEN_EXPIRY_HOURS = 1
    
    # Interfaccia utente
    MENU_WIDTH = 60
    TABLE_WIDTH = 70
    MAX_TITLE_DISPLAY_LENGTH = 25
    MAX_DESCRIPTION_DISPLAY_LENGTH = 50
    
    # Task
    VALID_TASK_STATUSES = ["To Do", "Doing", "Done"]
    DEFAULT_TASK_STATUS = "To Do"
    
    # Utenti - Nessun admin predefinito, il primo utente registrato diventa admin
    
    # Logging
    ENABLE_DEBUG_LOGGING = False
    LOG_FILE_PATH = "taskboard.log"
    
    # Backup
    AUTO_BACKUP_ENABLED = True
    MAX_BACKUP_FILES = 5
    
    # Validazione
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 20
    USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'
    
    # Messaggi
    MESSAGES = {
        'welcome': "Benvenuto nel sistema di gestione task in stile Kanban!",
        'goodbye': "Grazie per aver usato Taskboard!",
        'login_success': "Login effettuato con successo!",
        'login_failed': "Credenziali non valide.",
        'registration_success': "Registrazione completata con successo!",
        'task_created': "Task creato con successo!",
        'task_updated': "Task aggiornato con successo!",
        'task_deleted': "Task eliminato con successo!",
        'password_changed': "Password cambiata con successo!",
        'user_not_found': "Utente non trovato.",
        'task_not_found': "Task non trovato.",
        'access_denied': "Accesso negato.",
        'invalid_input': "Input non valido.",
        'operation_cancelled': "Operazione annullata.",
        'database_error': "Errore del database.",
        'unexpected_error': "Errore imprevisto."
    }
    
    # Simboli per l'interfaccia (compatibili con Windows)
    SYMBOLS = {
        'menu': '[*]',
        'user': '[U]',
        'admin': '[A]',
        'task': '[T]',
        'login': '[L]',
        'register': '[R]',
        'password': '[P]',
        'exit': '[X]',
        'add': '[+]',
        'edit': '[E]',
        'delete': '[D]',
        'status': '[S]',
        'change': '[C]',
        'manage': '[M]',
        'remove': '[R]',
        'quit': '[Q]',
        'success': '[OK]',
        'error': '[ERROR]',
        'info': '[INFO]',
        'warning': '[!]',
        'question': '[?]',
        'todo': '[TODO]',
        'doing': '[WORK]',
        'done': '[DONE]'
    }
    
    # Colori ANSI (opzionali, per terminali che li supportano)
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m',
        'underline': '\033[4m'
    }
    
    @classmethod
    def get_database_path(cls) -> str:
        """Restituisce il percorso completo del database"""
        return os.path.join(os.getcwd(), cls.DATABASE_NAME)
    
    @classmethod
    def get_backup_dir(cls) -> str:
        """Restituisce il percorso della directory di backup"""
        backup_dir = os.path.join(os.getcwd(), cls.DATABASE_BACKUP_DIR)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        return backup_dir
    
    @classmethod
    def get_message(cls, key: str, default: str = None) -> str:
        """Restituisce un messaggio dalla configurazione"""
        return cls.MESSAGES.get(key, default or f"Messaggio non trovato: {key}")
    
    @classmethod
    def get_symbol(cls, key: str, default: str = "[?]") -> str:
        """Restituisce un simbolo dalla configurazione"""
        return cls.SYMBOLS.get(key, default)
    
    @classmethod
    def is_valid_task_status(cls, status: str) -> bool:
        """Verifica se uno stato task è valido"""
        return status in cls.VALID_TASK_STATUSES
    
    @classmethod
    def get_color(cls, key: str, enabled: bool = True) -> str:
        """Restituisce un codice colore ANSI se abilitato"""
        if not enabled:
            return ""
        return cls.COLORS.get(key, "")

class DevelopmentConfig(Config):
    """Configurazione per sviluppo"""
    ENABLE_DEBUG_LOGGING = True
    DATABASE_NAME = "database_dev.db"

class ProductionConfig(Config):
    """Configurazione per produzione"""
    ENABLE_DEBUG_LOGGING = False
    AUTO_BACKUP_ENABLED = True

class TestConfig(Config):
    """Configurazione per test"""
    DATABASE_NAME = "database_test.db"
    ENABLE_DEBUG_LOGGING = True
    AUTO_BACKUP_ENABLED = False

# Configurazione attiva (può essere cambiata in base all'ambiente)
ACTIVE_CONFIG = Config

def get_config() -> Config:
    """Restituisce la configurazione attiva"""
    return ACTIVE_CONFIG

def set_config(config_class: type):
    """Imposta la configurazione attiva"""
    global ACTIVE_CONFIG
    ACTIVE_CONFIG = config_class