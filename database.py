"""
DATABASE - Livello di persistenza dei dati
Gestisce la connessione al database SQLite3 e le operazioni CRUD
Implementa il pattern Repository per l'accesso ai dati
"""

import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from model.model import User, Task


class DatabaseManager:
    """
    Classe che gestisce tutte le operazioni sul database SQLite3
    Implementa il pattern Repository per User e Task
    """
    
    def __init__(self, db_path: str = "taskboard.db"):
        """
        Inizializza il database manager
        Args:
            db_path: Percorso del file database SQLite
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Inizializza il database creando le tabelle se non esistono"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Crea tabella users
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Crea tabella tasks
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT,
                        status TEXT NOT NULL DEFAULT 'ToDo',
                        user_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                    )
                ''')
                
                # Crea indici per migliorare le performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
                
                conn.commit()
                print("Database inizializzato con successo!")
                
        except sqlite3.Error as e:
            print(f"Errore durante l'inizializzazione del database: {e}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """Restituisce una connessione al database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permette l'accesso per nome colonna
        return conn
    
    # ==================== OPERAZIONI CRUD PER USER ====================
    
    def create_user(self, user: User) -> bool:
        """
        Crea un nuovo utente nel database
        Args:
            user: Oggetto User da inserire
        Returns:
            bool: True se l'inserimento è riuscito, False altrimenti
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, created_at)
                    VALUES (?, ?, ?)
                ''', (user.username, user.password_hash, user.created_at))
                
                user.user_id = cursor.lastrowid
                conn.commit()
                return True
                
        except sqlite3.IntegrityError:
            print(f"Errore: Username '{user.username}' già esistente!")
            return False
        except sqlite3.Error as e:
            print(f"Errore durante la creazione dell'utente: {e}")
            return False
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Recupera un utente per ID
        Args:
            user_id: ID dell'utente
        Returns:
            User o None se non trovato
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return User(
                        user_id=row['user_id'],
                        username=row['username'],
                        password_hash=row['password_hash']
                    )
                return None
                
        except sqlite3.Error as e:
            print(f"Errore durante il recupero dell'utente: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Recupera un utente per username
        Args:
            username: Username dell'utente
        Returns:
            User o None se non trovato
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                row = cursor.fetchone()
                
                if row:
                    return User(
                        user_id=row['user_id'],
                        username=row['username'],
                        password_hash=row['password_hash']
                    )
                return None
                
        except sqlite3.Error as e:
            print(f"Errore durante il recupero dell'utente: {e}")
            return None
    
    def get_all_users(self) -> List[User]:
        """
        Recupera tutti gli utenti
        Returns:
            Lista di oggetti User
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users ORDER BY username')
                rows = cursor.fetchall()
                
                return [User(
                    user_id=row['user_id'],
                    username=row['username'],
                    password_hash=row['password_hash']
                ) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Errore durante il recupero degli utenti: {e}")
            return []
    
    def update_user(self, user: User) -> bool:
        """
        Aggiorna un utente esistente
        Args:
            user: Oggetto User con i dati aggiornati
        Returns:
            bool: True se l'aggiornamento è riuscito
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET username = ?, password_hash = ?
                    WHERE user_id = ?
                ''', (user.username, user.password_hash, user.user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Errore durante l'aggiornamento dell'utente: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """
        Elimina un utente (e tutti i suoi task)
        Args:
            user_id: ID dell'utente da eliminare
        Returns:
            bool: True se l'eliminazione è riuscita
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Errore durante l'eliminazione dell'utente: {e}")
            return False
    
    # ==================== OPERAZIONI CRUD PER TASK ====================
    
    def create_task(self, task: Task) -> bool:
        """
        Crea un nuovo task nel database
        Args:
            task: Oggetto Task da inserire
        Returns:
            bool: True se l'inserimento è riuscito
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tasks (title, description, status, user_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (task.title, task.description, task.status, task.user_id, 
                      task.created_at, task.updated_at))
                
                task.task_id = cursor.lastrowid
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Errore durante la creazione del task: {e}")
            return False
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Recupera un task per ID
        Args:
            task_id: ID del task
        Returns:
            Task o None se non trovato
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
                row = cursor.fetchone()
                
                if row:
                    return Task(
                        task_id=row['task_id'],
                        title=row['title'],
                        description=row['description'],
                        status=row['status'],
                        user_id=row['user_id']
                    )
                return None
                
        except sqlite3.Error as e:
            print(f"Errore durante il recupero del task: {e}")
            return None
    
    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        """
        Recupera tutti i task di un utente
        Args:
            user_id: ID dell'utente
        Returns:
            Lista di oggetti Task
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM tasks 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC
                ''', (user_id,))
                rows = cursor.fetchall()
                
                return [Task(
                    task_id=row['task_id'],
                    title=row['title'],
                    description=row['description'],
                    status=row['status'],
                    user_id=row['user_id']
                ) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Errore durante il recupero dei task: {e}")
            return []
    
    def get_tasks_by_status(self, user_id: int, status: str) -> List[Task]:
        """
        Recupera i task di un utente filtrati per stato
        Args:
            user_id: ID dell'utente
            status: Stato dei task da recuperare
        Returns:
            Lista di oggetti Task
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM tasks 
                    WHERE user_id = ? AND status = ?
                    ORDER BY created_at DESC
                ''', (user_id, status))
                rows = cursor.fetchall()
                
                return [Task(
                    task_id=row['task_id'],
                    title=row['title'],
                    description=row['description'],
                    status=row['status'],
                    user_id=row['user_id']
                ) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Errore durante il recupero dei task per stato: {e}")
            return []
    
    def update_task(self, task: Task) -> bool:
        """
        Aggiorna un task esistente
        Args:
            task: Oggetto Task con i dati aggiornati
        Returns:
            bool: True se l'aggiornamento è riuscito
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tasks 
                    SET title = ?, description = ?, status = ?, updated_at = ?
                    WHERE task_id = ?
                ''', (task.title, task.description, task.status, 
                      datetime.now(), task.task_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Errore durante l'aggiornamento del task: {e}")
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """
        Elimina un task
        Args:
            task_id: ID del task da eliminare
        Returns:
            bool: True se l'eliminazione è riuscita
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Errore durante l'eliminazione del task: {e}")
            return False
    
    # ==================== METODI UTILITY ====================
    
    def get_task_count_by_status(self, user_id: int) -> dict:
        """
        Restituisce il conteggio dei task per stato
        Args:
            user_id: ID dell'utente
        Returns:
            dict: Dizionario con il conteggio per ogni stato
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT status, COUNT(*) as count
                    FROM tasks 
                    WHERE user_id = ?
                    GROUP BY status
                ''', (user_id,))
                rows = cursor.fetchall()
                
                counts = {Task.STATUS_TODO: 0, Task.STATUS_DOING: 0, Task.STATUS_DONE: 0}
                for row in rows:
                    counts[row['status']] = row['count']
                
                return counts
                
        except sqlite3.Error as e:
            print(f"Errore durante il conteggio dei task: {e}")
            return {Task.STATUS_TODO: 0, Task.STATUS_DOING: 0, Task.STATUS_DONE: 0}
    
    def close_connection(self) -> None:
        """Chiude la connessione al database (se necessario)"""
        # SQLite gestisce automaticamente le connessioni con il context manager
        pass
    
    def reset_database(self) -> bool:
        """
        Resetta il database eliminando tutti i dati (ATTENZIONE!)
        Returns:
            bool: True se il reset è riuscito
        """
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            self.init_database()
            return True
        except Exception as e:
            print(f"Errore durante il reset del database: {e}")
            return False