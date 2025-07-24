"""
MODEL - Livello di gestione dei dati e logica di business
Contiene le classi User e Task che rappresentano le entità del dominio
Implementa la logica di business e le regole di validazione
"""

from datetime import datetime
from typing import Optional, List
import hashlib


class User:
    """
    Classe che rappresenta un utente del sistema
    Gestisce i dati dell'utente e l'autenticazione
    """
    
    def __init__(self, user_id: Optional[int] = None, username: str = "", password_hash: str = ""):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.created_at = datetime.now()
    
    def set_password(self, password: str) -> None:
        """Imposta la password hashata usando SHA-256"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """Verifica se la password fornita corrisponde a quella hashata"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def __str__(self) -> str:
        return f"User(id={self.user_id}, username='{self.username}')"


class Task:
    """
    Classe che rappresenta un task/attività
    Gestisce i dati del task e le transizioni di stato
    """
    
    # Stati possibili per un task
    STATUS_TODO = "ToDo"
    STATUS_DOING = "Doing" 
    STATUS_DONE = "Done"
    
    VALID_STATUSES = [STATUS_TODO, STATUS_DOING, STATUS_DONE]
    
    def __init__(self, task_id: Optional[int] = None, title: str = "", 
                 description: str = "", status: str = STATUS_TODO, user_id: int = 0):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.status = status if status in self.VALID_STATUSES else self.STATUS_TODO
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: str) -> bool:
        """Aggiorna lo stato del task se valido"""
        if new_status in self.VALID_STATUSES:
            self.status = new_status
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_content(self, title: str = None, description: str = None) -> None:
        """Aggiorna il contenuto del task"""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"Task(id={self.task_id}, title='{self.title}', status='{self.status}', user_id={self.user_id})"