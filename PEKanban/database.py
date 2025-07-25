# database.py - Gestione database SQLite3 per l'applicazione Taskboard
# Implementa i metodi CRUD per User, Task, Admin e PasswordRecovery

import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from model import User, Task, Admin, PasswordRecovery

class DatabaseManager:
    """Classe per gestire tutte le operazioni del database SQLite3"""
    
    def __init__(self, db_name: str = "database.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Crea e restituisce una connessione al database"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Permette accesso per nome colonna
        return conn
    
    def init_database(self):
        """Inizializza il database creando le tabelle necessarie"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabella Users (utenti standard)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabella Admin (amministratori)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin (
                    admin_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    permissions TEXT DEFAULT 'full'
                )
            ''')
            
            # Tabella Tasks
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT 'To Do',
                    user_id TEXT NOT NULL,
                    user_type TEXT NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabella Password Recovery
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_recovery (
                    recovery_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    email TEXT NOT NULL,
                    token TEXT NOT NULL,
                    is_used INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    
    def _row_to_user(self, row, is_admin=False) -> User:
        """Converte una riga del database in oggetto User o Admin"""
        if is_admin:
            user = Admin.__new__(Admin)
            user.user_id = row['admin_id']
        else:
            user = User.__new__(User)
            user.user_id = row['user_id']
        
        user.username = row['username']
        user.email = row['email']
        user.password_hash = row['password_hash']
        user.is_admin = is_admin
        user.token = row['token']
        user.created_at = datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now()
        
        return user
    
    def _row_to_task(self, row) -> Task:
        """Converte una riga del database in oggetto Task"""
        task = Task.__new__(Task)
        task.task_id = row['task_id']
        task.title = row['title']
        task.description = row['description']
        task.status = row['status']
        task.user_id = row['user_id']
        task.created_at = datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now()
        task.updated_at = datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.now()
        
        return task
    
    def _row_to_password_recovery(self, row) -> PasswordRecovery:
        """Converte una riga del database in oggetto PasswordRecovery"""
        recovery = PasswordRecovery.__new__(PasswordRecovery)
        recovery.recovery_id = row['recovery_id']
        recovery.user_id = row['user_id']
        recovery.email = row['email']
        recovery.token = row['token']
        recovery.is_used = bool(row['is_used'])
        recovery.created_at = datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now()
        
        return recovery
    
    # CRUD Operations per Users
    def create_user(self, user: User) -> bool:
        """Crea un nuovo utente nel database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if user.is_admin:
                    # Inserisci nella tabella admin
                    cursor.execute('''
                        INSERT INTO admin (admin_id, username, email, password_hash, token, created_at, permissions)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user.user_id,
                        user.username,
                        user.email,
                        user.password_hash,
                        user.token,
                        user.created_at.isoformat(),
                        'full'
                    ))
                else:
                    # Inserisci nella tabella users
                    cursor.execute('''
                        INSERT INTO users (user_id, username, email, password_hash, token, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        user.user_id,
                        user.username,
                        user.email,
                        user.password_hash,
                        user.token,
                        user.created_at.isoformat()
                    ))
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Recupera un utente per ID (cerca in entrambe le tabelle)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Cerca prima nella tabella users
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row, is_admin=False)
            
            # Cerca nella tabella admin
            cursor.execute("SELECT * FROM admin WHERE admin_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row, is_admin=True)
            
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Recupera un utente per username (cerca in entrambe le tabelle)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Cerca prima nella tabella users
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row, is_admin=False)
            
            # Cerca nella tabella admin
            cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row, is_admin=True)
            
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Recupera un utente per email (cerca in entrambe le tabelle)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Cerca prima nella tabella users
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row, is_admin=False)
            
            # Cerca nella tabella admin
            cursor.execute("SELECT * FROM admin WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row, is_admin=True)
            
            return None
    
    def get_all_users(self) -> List[User]:
        """Recupera tutti gli utenti (da entrambe le tabelle)"""
        users = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Recupera utenti standard
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            user_rows = cursor.fetchall()
            for row in user_rows:
                users.append(self._row_to_user(row, is_admin=False))
            
            # Recupera admin
            cursor.execute("SELECT * FROM admin ORDER BY created_at DESC")
            admin_rows = cursor.fetchall()
            for row in admin_rows:
                users.append(self._row_to_user(row, is_admin=True))
            
            return users
    
    def update_user(self, user: User) -> bool:
        """Aggiorna un utente esistente"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if user.is_admin:
                    # Aggiorna nella tabella admin
                    cursor.execute('''
                        UPDATE admin
                        SET username = ?, email = ?, password_hash = ?, token = ?
                        WHERE admin_id = ?
                    ''', (
                        user.username,
                        user.email,
                        user.password_hash,
                        user.token,
                        user.user_id
                    ))
                else:
                    # Aggiorna nella tabella users
                    cursor.execute('''
                        UPDATE users
                        SET username = ?, email = ?, password_hash = ?, token = ?
                        WHERE user_id = ?
                    ''', (
                        user.username,
                        user.email,
                        user.password_hash,
                        user.token,
                        user.user_id
                    ))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Elimina un utente (cerca in entrambe le tabelle)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prova a eliminare dalla tabella users
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                rows_affected = cursor.rowcount
                
                # Se non trovato, prova nella tabella admin
                if rows_affected == 0:
                    cursor.execute("DELETE FROM admin WHERE admin_id = ?", (user_id,))
                    rows_affected = cursor.rowcount
                
                conn.commit()
                return rows_affected > 0
        except sqlite3.Error:
            return False
    
    def user_exists(self, username: str, email: str) -> bool:
        """Verifica se un utente esiste già (username o email) in entrambe le tabelle"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Controlla nella tabella users
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE username = ? OR email = ?",
                (username, email)
            )
            user_count = cursor.fetchone()[0]
            
            # Controlla nella tabella admin
            cursor.execute(
                "SELECT COUNT(*) FROM admin WHERE username = ? OR email = ?",
                (username, email)
            )
            admin_count = cursor.fetchone()[0]
            
            return (user_count + admin_count) > 0
    
    def is_first_user(self) -> bool:
        """Verifica se questo è il primo utente che si registra"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Conta utenti in entrambe le tabelle
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM admin")
            admin_count = cursor.fetchone()[0]
            
            return (user_count + admin_count) == 0
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autentica un utente con username e password"""
        user = self.get_user_by_username(username)
        if user and user.verify_password(password):
            return user
        return None
    
    # CRUD Operations per Tasks
    def create_task(self, task: Task) -> bool:
        """Crea un nuovo task nel database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tasks (task_id, title, description, status, user_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task.task_id,
                    task.title,
                    task.description,
                    task.status,
                    task.user_id,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat()
                ))
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Recupera un task per ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_task(row)
            return None
    
    def get_user_tasks(self, user_id: str) -> List[Task]:
        """Recupera tutti i task di un utente"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            
            return [self._row_to_task(row) for row in rows]
    
    def get_all_tasks(self) -> List[Task]:
        """Recupera tutti i task"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            return [self._row_to_task(row) for row in rows]
    
    def get_all_tasks_with_users(self) -> List[dict]:
        """Recupera tutti i task con informazioni sui proprietari"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*,
                       COALESCE(u.username, a.username) as owner_username,
                       COALESCE(u.email, a.email) as owner_email,
                       CASE WHEN a.admin_id IS NOT NULL THEN 1 ELSE 0 END as owner_is_admin
                FROM tasks t
                LEFT JOIN users u ON t.user_id = u.user_id
                LEFT JOIN admin a ON t.user_id = a.admin_id
                ORDER BY t.created_at DESC
            ''')
            rows = cursor.fetchall()
            
            tasks_with_users = []
            for row in rows:
                task = self._row_to_task(row)
                task_dict = {
                    'task': task,
                    'owner_username': row['owner_username'],
                    'owner_email': row['owner_email'],
                    'owner_is_admin': bool(row['owner_is_admin'])
                }
                tasks_with_users.append(task_dict)
            
            return tasks_with_users
    
    def get_tasks_by_status(self, status: str, user_id: str = None) -> List[Task]:
        """Recupera task per stato, opzionalmente filtrati per utente"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute(
                    "SELECT * FROM tasks WHERE status = ? AND user_id = ? ORDER BY created_at DESC",
                    (status, user_id)
                )
            else:
                cursor.execute(
                    "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC",
                    (status,)
                )
            
            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]
    
    def update_task(self, task: Task) -> bool:
        """Aggiorna un task esistente"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tasks 
                    SET title = ?, description = ?, status = ?, updated_at = ?
                    WHERE task_id = ?
                ''', (
                    task.title,
                    task.description,
                    task.status,
                    task.updated_at.isoformat(),
                    task.task_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Elimina un task"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def delete_user_tasks(self, user_id: str) -> bool:
        """Elimina tutti i task di un utente"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def delete_user_and_tasks(self, user_id: str) -> bool:
        """Elimina un utente e tutti i suoi task"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Elimina prima i task (per evitare problemi di foreign key)
                cursor.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
                
                # Poi elimina l'utente (cerca in entrambe le tabelle)
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                rows_affected = cursor.rowcount
                
                # Se non trovato nella tabella users, prova in admin
                if rows_affected == 0:
                    cursor.execute("DELETE FROM admin WHERE admin_id = ?", (user_id,))
                
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    # CRUD Operations per Password Recovery
    def create_password_recovery(self, recovery: PasswordRecovery) -> bool:
        """Crea un nuovo record di recupero password"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO password_recovery (recovery_id, user_id, email, token, is_used, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    recovery.recovery_id,
                    recovery.user_id,
                    recovery.email,
                    recovery.token,
                    recovery.is_used,
                    recovery.created_at.isoformat()
                ))
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def get_password_recovery_by_token(self, token: str) -> Optional[PasswordRecovery]:
        """Recupera un record di recupero password per token"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM password_recovery WHERE token = ?", (token,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_password_recovery(row)
            return None
    
    def update_password_recovery(self, recovery: PasswordRecovery) -> bool:
        """Aggiorna un record di recupero password"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE password_recovery 
                    SET is_used = ?
                    WHERE recovery_id = ?
                ''', (
                    recovery.is_used,
                    recovery.recovery_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def cleanup_old_recovery_tokens(self):
        """Elimina i token di recupero vecchi (più di 24 ore)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM password_recovery 
                    WHERE datetime(created_at) < datetime('now', '-1 day')
                ''')
                conn.commit()
        except sqlite3.Error:
            pass
    
    # Metodi di utilità
    def get_database_stats(self) -> dict:
        """Restituisce statistiche del database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Conta utenti standard
            cursor.execute("SELECT COUNT(*) FROM users")
            regular_users = cursor.fetchone()[0]
            
            # Conta admin
            cursor.execute("SELECT COUNT(*) FROM admin")
            admin_users = cursor.fetchone()[0]
            
            total_users = regular_users + admin_users
            
            # Conta task
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'To Do'")
            todo_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Doing'")
            doing_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Done'")
            done_tasks = cursor.fetchone()[0]
            
            return {
                'total_users': total_users,
                'admin_users': admin_users,
                'regular_users': regular_users,
                'total_tasks': total_tasks,
                'todo_tasks': todo_tasks,
                'doing_tasks': doing_tasks,
                'done_tasks': done_tasks
            }
    
    def backup_database(self, backup_path: str) -> bool:
        """Crea un backup del database"""
        try:
            import shutil
            shutil.copy2(self.db_name, backup_path)
            return True
        except Exception:
            return False
    
    def close(self):
        """Chiude la connessione al database (cleanup)"""
        # SQLite gestisce automaticamente le connessioni
        # Questo metodo è qui per compatibilità futura
        pass