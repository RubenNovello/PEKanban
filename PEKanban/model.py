# model.py - Modello dati per l'applicazione Taskboard
# Contiene le classi per User, Task e Admin con la logica di dominio

import hashlib
import uuid
from datetime import datetime
from typing import List, Optional

class User:
    """Classe per rappresentare un utente del sistema"""
    
    def __init__(self, username: str, email: str, password: str, user_id: str = None):
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password)
        self.created_at = datetime.now()
        self.is_admin = False
        self.token = None
    
    def _hash_password(self, password: str) -> str:
        """Hash della password usando SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verifica se la password fornita è corretta"""
        return self._hash_password(password) == self.password_hash
    
    def change_password(self, new_password: str):
        """Cambia la password dell'utente"""
        self.password_hash = self._hash_password(new_password)
    
    def generate_token(self) -> str:
        """Genera un token univoco per la sicurezza"""
        self.token = str(uuid.uuid4())
        return self.token
    
    def __str__(self):
        return f"User(id={self.user_id}, username={self.username}, email={self.email})"


class Task:
    """Classe per rappresentare un task nel sistema Kanban"""
    
    # Stati possibili per i task
    STATUS_TODO = "To Do"
    STATUS_DOING = "Doing"
    STATUS_DONE = "Done"
    
    VALID_STATUSES = [STATUS_TODO, STATUS_DOING, STATUS_DONE]
    
    def __init__(self, title: str, description: str, user_id: str, task_id: str = None, status: str = STATUS_TODO):
        self.task_id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = status if status in self.VALID_STATUSES else self.STATUS_TODO
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: str):
        """Aggiorna lo stato del task"""
        if new_status in self.VALID_STATUSES:
            self.status = new_status
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_details(self, title: str = None, description: str = None):
        """Aggiorna titolo e/o descrizione del task"""
        if title:
            self.title = title
        if description:
            self.description = description
        self.updated_at = datetime.now()
    
    def __str__(self):
        return f"Task(id={self.task_id}, title={self.title}, status={self.status}, user={self.user_id})"


class Admin(User):
    """Classe Admin che estende User con privilegi aggiuntivi"""
    
    def __init__(self, username: str, email: str, password: str, user_id: str = None):
        super().__init__(username, email, password, user_id)
        self.is_admin = True
    
    def create_user(self, username: str, email: str, password: str) -> User:
        """Crea un nuovo utente"""
        return User(username, email, password)
    
    def create_admin(self, username: str, email: str, password: str) -> 'Admin':
        """Crea un nuovo admin"""
        return Admin(username, email, password)
    
    def reset_user_password(self, user: User, new_password: str):
        """Resetta la password di un utente"""
        user.change_password(new_password)
    
    def promote_to_admin(self, user: User):
        """Promuove un utente ad admin"""
        user.is_admin = True
    
    def demote_from_admin(self, user: User):
        """Rimuove i privilegi admin da un utente"""
        user.is_admin = False
    
    def __str__(self):
        return f"Admin(id={self.user_id}, username={self.username}, email={self.email})"


class PasswordRecovery:
    """Classe per gestire il recupero password"""
    
    def __init__(self, user_id: str, email: str):
        self.recovery_id = str(uuid.uuid4())
        self.user_id = user_id
        self.email = email
        self.token = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.is_used = False
    
    def use_token(self):
        """Marca il token come utilizzato"""
        self.is_used = True
    
    def is_valid(self) -> bool:
        """Verifica se il token è ancora valido (non usato e non scaduto)"""
        # Token valido per 1 ora
        time_diff = datetime.now() - self.created_at
        return not self.is_used and time_diff.total_seconds() < 3600
    
    def __str__(self):
        return f"PasswordRecovery(id={self.recovery_id}, user_id={self.user_id}, email={self.email})"