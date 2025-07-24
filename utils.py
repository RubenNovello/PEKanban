"""
UTILITIES - Funzioni di utilità riutilizzabili
Contiene helper functions per validazione, formattazione e operazioni comuni
"""

import re
from datetime import datetime
from typing import Optional, List
from config import PASSWORD_MIN_LENGTH, USERNAME_MIN_LENGTH, SYMBOLS


def validate_username(username: str) -> tuple[bool, str]:
    """
    Valida un username
    Args:
        username: Username da validare
    Returns:
        tuple: (is_valid, error_message)
    """
    if not username or not username.strip():
        return False, "Username non può essere vuoto"
    
    username = username.strip()
    
    if len(username) < USERNAME_MIN_LENGTH:
        return False, f"Username deve essere almeno {USERNAME_MIN_LENGTH} caratteri"
    
    if len(username) > 50:
        return False, "Username troppo lungo (max 50 caratteri)"
    
    # Solo caratteri alfanumerici e underscore
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username può contenere solo lettere, numeri e underscore"
    
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """
    Valida una password
    Args:
        password: Password da validare
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Password non può essere vuota"
    
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password deve essere almeno {PASSWORD_MIN_LENGTH} caratteri"
    
    if len(password) > 100:
        return False, "Password troppo lunga (max 100 caratteri)"
    
    return True, ""


def validate_task_title(title: str) -> tuple[bool, str]:
    """
    Valida il titolo di un task
    Args:
        title: Titolo da validare
    Returns:
        tuple: (is_valid, error_message)
    """
    if not title or not title.strip():
        return False, "Titolo non può essere vuoto"
    
    title = title.strip()
    
    if len(title) < 3:
        return False, "Titolo deve essere almeno 3 caratteri"
    
    if len(title) > 100:
        return False, "Titolo troppo lungo (max 100 caratteri)"
    
    return True, ""


def validate_task_description(description: str) -> tuple[bool, str]:
    """
    Valida la descrizione di un task
    Args:
        description: Descrizione da validare
    Returns:
        tuple: (is_valid, error_message)
    """
    if description and len(description) > 500:
        return False, "Descrizione troppo lunga (max 500 caratteri)"
    
    return True, ""


def format_datetime(dt: datetime) -> str:
    """
    Formatta una data/ora per la visualizzazione
    Args:
        dt: Oggetto datetime
    Returns:
        str: Data formattata
    """
    return dt.strftime("%d/%m/%Y %H:%M")


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Tronca un testo se supera la lunghezza massima
    Args:
        text: Testo da troncare
        max_length: Lunghezza massima
        suffix: Suffisso da aggiungere se troncato
    Returns:
        str: Testo troncato
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_success_message(message: str) -> str:
    """
    Formatta un messaggio di successo
    Args:
        message: Messaggio da formattare
    Returns:
        str: Messaggio formattato
    """
    return f"\n{SYMBOLS['success']} {message}"


def format_error_message(message: str) -> str:
    """
    Formatta un messaggio di errore
    Args:
        message: Messaggio da formattare
    Returns:
        str: Messaggio formattato
    """
    return f"\n{SYMBOLS['error']} Errore: {message}"


def format_info_message(message: str) -> str:
    """
    Formatta un messaggio informativo
    Args:
        message: Messaggio da formattare
    Returns:
        str: Messaggio formattato
    """
    return f"\n{SYMBOLS['info']} {message}"


def format_warning_message(message: str) -> str:
    """
    Formatta un messaggio di avviso
    Args:
        message: Messaggio da formattare
    Returns:
        str: Messaggio formattato
    """
    return f"\n{SYMBOLS['warning']} Attenzione: {message}"


def get_user_input(prompt: str, required: bool = True, validator=None) -> Optional[str]:
    """
    Raccoglie input dall'utente con validazione opzionale
    Args:
        prompt: Messaggio di prompt
        required: Se l'input è obbligatorio
        validator: Funzione di validazione opzionale
    Returns:
        str o None: Input dell'utente validato
    """
    while True:
        user_input = input(prompt).strip()
        
        if not user_input and required:
            print(format_error_message("Campo obbligatorio!"))
            continue
        
        if not user_input and not required:
            return None
        
        if validator:
            is_valid, error_msg = validator(user_input)
            if not is_valid:
                print(format_error_message(error_msg))
                continue
        
        return user_input


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Chiede conferma all'utente per un'azione
    Args:
        message: Messaggio di conferma
        default: Valore predefinito se l'utente preme solo INVIO
    Returns:
        bool: True se confermato, False altrimenti
    """
    default_text = "(S/n)" if default else "(s/N)"
    prompt = f"\n{message} {default_text}: "
    
    response = input(prompt).strip().lower()
    
    if not response:
        return default
    
    return response in ['s', 'si', 'y', 'yes', '1']


def clear_screen(lines: int = 3) -> None:
    """
    Simula la pulizia dello schermo stampando righe vuote
    Args:
        lines: Numero di righe vuote da stampare
    """
    print("\n" * lines)


def print_separator(char: str = "=", length: int = 50) -> None:
    """
    Stampa una linea separatrice
    Args:
        char: Carattere da usare per la separazione
        length: Lunghezza della linea
    """
    print(char * length)


def safe_int_input(prompt: str, min_val: int = None, max_val: int = None) -> Optional[int]:
    """
    Raccoglie un input intero con validazione
    Args:
        prompt: Messaggio di prompt
        min_val: Valore minimo accettabile
        max_val: Valore massimo accettabile
    Returns:
        int o None: Numero intero validato o None se non valido
    """
    try:
        value = int(input(prompt).strip())
        
        if min_val is not None and value < min_val:
            print(format_error_message(f"Valore deve essere almeno {min_val}"))
            return None
        
        if max_val is not None and value > max_val:
            print(format_error_message(f"Valore deve essere al massimo {max_val}"))
            return None
        
        return value
    
    except ValueError:
        print(format_error_message("Inserisci un numero valido!"))
        return None


def get_task_status_display(status: str) -> str:
    """
    Restituisce una rappresentazione visiva dello stato del task
    Args:
        status: Stato del task
    Returns:
        str: Stato formattato per la visualizzazione
    """
    status_symbols = {
        "ToDo": "⏳ ToDo",
        "Doing": "🔄 Doing",
        "Done": "✅ Done"
    }
    
    return status_symbols.get(status, status)


def calculate_task_stats(tasks: List) -> dict:
    """
    Calcola statistiche sui task
    Args:
        tasks: Lista di task
    Returns:
        dict: Statistiche calcolate
    """
    if not tasks:
        return {
            "total": 0,
            "todo": 0,
            "doing": 0,
            "done": 0,
            "completion_rate": 0.0
        }
    
    total = len(tasks)
    todo = len([t for t in tasks if t.status == "ToDo"])
    doing = len([t for t in tasks if t.status == "Doing"])
    done = len([t for t in tasks if t.status == "Done"])
    
    completion_rate = (done / total) * 100 if total > 0 else 0.0
    
    return {
        "total": total,
        "todo": todo,
        "doing": doing,
        "done": done,
        "completion_rate": round(completion_rate, 1)
    }