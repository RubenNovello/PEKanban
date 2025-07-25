# utils.py - Funzioni di utilità per l'applicazione Taskboard
# Contiene funzioni riutilizzabili e helper per varie operazioni

import re
import hashlib
import uuid
from datetime import datetime
from typing import Optional, List

def validate_email(email: str) -> bool:
    """Valida il formato di un indirizzo email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida la forza di una password
    Restituisce (is_valid, message)
    """
    if len(password) < 6:
        return False, "La password deve essere di almeno 6 caratteri"
    
    if len(password) < 8:
        return True, "Password accettabile (consigliato almeno 8 caratteri)"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    strength_score = sum([has_upper, has_lower, has_digit, has_special])
    
    if strength_score >= 3:
        return True, "Password forte"
    elif strength_score >= 2:
        return True, "Password media"
    else:
        return True, "Password debole (consigliato usare maiuscole, numeri e simboli)"

def validate_username(username: str) -> tuple[bool, str]:
    """
    Valida un username
    Restituisce (is_valid, message)
    """
    if len(username) < 3:
        return False, "L'username deve essere di almeno 3 caratteri"
    
    if len(username) > 20:
        return False, "L'username non può superare i 20 caratteri"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "L'username può contenere solo lettere, numeri e underscore"
    
    return True, "Username valido"

def sanitize_input(text: str) -> str:
    """Pulisce e sanitizza l'input dell'utente"""
    if not text:
        return ""
    
    # Rimuove spazi all'inizio e alla fine
    text = text.strip()
    
    # Rimuove caratteri di controllo
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n')
    
    return text

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Tronca il testo se supera la lunghezza massima"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_datetime(dt: datetime, format_type: str = "default") -> str:
    """Formatta una data/ora in base al tipo richiesto"""
    if format_type == "short":
        return dt.strftime("%d/%m/%Y")
    elif format_type == "time":
        return dt.strftime("%H:%M")
    elif format_type == "full":
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    else:  # default
        return dt.strftime("%d/%m/%Y %H:%M")

def generate_secure_token() -> str:
    """Genera un token sicuro per vari usi"""
    return str(uuid.uuid4()).replace('-', '')

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    Hash di una password con salt
    Restituisce (hash, salt)
    """
    if salt is None:
        salt = str(uuid.uuid4())
    
    # Combina password e salt
    salted_password = password + salt
    
    # Crea hash SHA256
    hash_obj = hashlib.sha256(salted_password.encode())
    password_hash = hash_obj.hexdigest()
    
    return password_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifica una password contro l'hash memorizzato"""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == stored_hash

def calculate_task_stats(tasks: List) -> dict:
    """Calcola statistiche sui task"""
    if not tasks:
        return {
            'total': 0,
            'todo': 0,
            'doing': 0,
            'done': 0,
            'completion_rate': 0.0
        }
    
    total = len(tasks)
    todo = sum(1 for task in tasks if task.status == "To Do")
    doing = sum(1 for task in tasks if task.status == "Doing")
    done = sum(1 for task in tasks if task.status == "Done")
    
    completion_rate = (done / total) * 100 if total > 0 else 0.0
    
    return {
        'total': total,
        'todo': todo,
        'doing': doing,
        'done': done,
        'completion_rate': round(completion_rate, 1)
    }

def format_file_size(size_bytes: int) -> str:
    """Formatta la dimensione di un file in formato leggibile"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def create_backup_filename(base_name: str) -> str:
    """Crea un nome file per backup con timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_backup_{timestamp}.db"

def parse_task_id_input(input_str: str) -> Optional[str]:
    """
    Analizza l'input dell'ID task e restituisce un ID valido
    Accetta sia ID completi che parziali (primi 8 caratteri)
    """
    if not input_str:
        return None
    
    # Rimuove spazi e converte in minuscolo
    clean_input = input_str.strip().lower()
    
    # Se è un UUID completo (36 caratteri con trattini)
    if len(clean_input) == 36 and clean_input.count('-') == 4:
        return clean_input
    
    # Se è un ID parziale (8 caratteri)
    if len(clean_input) == 8 and clean_input.replace('-', '').isalnum():
        return clean_input
    
    return None

def format_task_status_display(status: str) -> str:
    """Formatta lo stato del task per la visualizzazione"""
    status_map = {
        "To Do": "[TODO]",
        "Doing": "[WORK]",
        "Done": "[DONE]"
    }
    return status_map.get(status, f"[{status.upper()}]")

def get_status_color_code(status: str) -> str:
    """Restituisce il codice colore ANSI per lo stato (per terminali che supportano i colori)"""
    color_map = {
        "To Do": "\033[91m",      # Rosso
        "Doing": "\033[93m",      # Giallo
        "Done": "\033[92m",       # Verde
        "reset": "\033[0m"        # Reset
    }
    return color_map.get(status, "")

def create_progress_bar(current: int, total: int, width: int = 20) -> str:
    """Crea una barra di progresso testuale"""
    if total == 0:
        return "[" + " " * width + "] 0%"
    
    percentage = current / total
    filled_width = int(width * percentage)
    
    bar = "[" + "=" * filled_width + " " * (width - filled_width) + "]"
    percent_text = f" {percentage * 100:.1f}%"
    
    return bar + percent_text

def log_action(action: str, user_id: str = None, details: str = None):
    """Log delle azioni per debugging (versione semplificata)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action}"
    
    if user_id:
        log_entry += f" | User: {user_id[:8]}"
    
    if details:
        log_entry += f" | Details: {details}"
    
    # In una versione più avanzata, questo potrebbe scrivere su file
    # Per ora stampa solo se in modalità debug
    # print(f"DEBUG: {log_entry}")

def clean_database_input(text: str) -> str:
    """Pulisce l'input prima di inserirlo nel database"""
    if not text:
        return ""
    
    # Rimuove caratteri potenzialmente pericolosi per SQL injection
    # (anche se usiamo parametri preparati, è una buona pratica)
    text = text.replace("'", "''")  # Escape delle virgolette singole
    text = sanitize_input(text)
    
    return text

def is_valid_uuid(uuid_string: str) -> bool:
    """Verifica se una stringa è un UUID valido"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def get_app_version() -> str:
    """Restituisce la versione dell'applicazione"""
    return "1.0.0"

def get_system_info() -> dict:
    """Restituisce informazioni di sistema base"""
    import platform
    import sys
    
    return {
        'python_version': sys.version,
        'platform': platform.platform(),
        'app_version': get_app_version()
    }