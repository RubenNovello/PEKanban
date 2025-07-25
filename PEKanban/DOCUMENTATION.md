# Taskboard - Documentazione Tecnica

## Panoramica del Progetto

Taskboard è un'applicazione Python CLI per la gestione di attività personali in stile Kanban, sviluppata seguendo il pattern architetturale MVC (Model-View-Controller).

## Architettura

### Pattern MVC

L'applicazione è strutturata seguendo il pattern MVC:

- **Model** (`model.py`): Contiene le classi di dominio (User, Task, Admin, PasswordRecovery)
- **View** (`view.py`): Gestisce l'interfaccia utente CLI
- **Controller** (`controller.py`): Coordina Model e View, gestisce la logica di business

### Struttura dei File

```
PEKanban/
├── main.py              # Punto di ingresso dell'applicazione
├── model.py             # Classi del dominio
├── view.py              # Interfaccia utente CLI
├── controller.py        # Logica di controllo
├── database.py          # Gestione database SQLite3
├── utils.py             # Funzioni di utilità
├── config.py            # Configurazione dell'applicazione
├── test_taskboard.py    # Test unitari
├── DOCUMENTATION.md     # Questa documentazione
└── README.md            # Documentazione utente
```

## Classi Principali

### User
Rappresenta un utente del sistema con:
- `user_id`: Identificatore univoco
- `username`: Nome utente
- `email`: Indirizzo email
- `password_hash`: Password hashata con SHA256
- `is_admin`: Flag per privilegi amministrativi
- `token`: Token di sicurezza

**Metodi principali:**
- `verify_password()`: Verifica la password
- `change_password()`: Cambia la password
- `generate_token()`: Genera token di sicurezza

### Task
Rappresenta un'attività nel sistema Kanban con:
- `task_id`: Identificatore univoco
- `title`: Titolo del task
- `description`: Descrizione dettagliata
- `status`: Stato (To Do, Doing, Done)
- `user_id`: ID dell'utente assegnato
- `created_at`: Data di creazione
- `updated_at`: Data ultimo aggiornamento

**Metodi principali:**
- `update_status()`: Aggiorna lo stato
- `update_details()`: Modifica titolo e descrizione

### Admin
Estende la classe User con privilegi aggiuntivi:
- Visualizzare tutti gli utenti e task
- Eliminare utenti e task
- Modificare stati dei task di qualsiasi utente
- Gestire password e permessi utenti
- Creare altri admin e utenti

### PasswordRecovery
Gestisce il recupero password con:
- `recovery_id`: ID del recupero
- `user_id`: ID utente
- `email`: Email per il recupero
- `token`: Token univoco
- `is_used`: Flag utilizzo
- `created_at`: Data creazione

## Database

### Schema SQLite3

**Tabella users:**
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    token TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Tabella tasks:**
```sql
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'To Do',
    user_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);
```

**Tabella password_recovery:**
```sql
CREATE TABLE password_recovery (
    recovery_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    token TEXT NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);
```

### Operazioni CRUD

Il `DatabaseManager` implementa tutte le operazioni CRUD:
- **Create**: `create_user()`, `create_task()`, `create_password_recovery()`
- **Read**: `get_user_by_id()`, `get_task_by_id()`, `get_all_users()`, `get_all_tasks()`
- **Update**: `update_user()`, `update_task()`, `update_password_recovery()`
- **Delete**: `delete_user()`, `delete_task()`, `delete_user_and_tasks()`

## Sicurezza

### Autenticazione
- Password hashate con SHA256
- Token univoci per sessioni sicure
- Validazione input per prevenire SQL injection

### Autorizzazione
- Sistema a ruoli (User/Admin)
- Controllo accessi per operazioni sensibili
- Isolamento dati per utente

### Recupero Password
- Token temporanei con scadenza (1 ora)
- Validazione email per recupero
- Token monouso

## Funzionalità

### Utente Standard
- Registrazione e login
- Gestione task personali (CRUD)
- Cambio password
- Visualizzazione task per stato

### Amministratore
- Tutte le funzionalità utente
- Gestione utenti (visualizza, elimina, modifica privilegi)
- Gestione task globale
- Reset password utenti
- Creazione admin e utenti

## Configurazione

Il file `config.py` contiene:
- Impostazioni database
- Parametri sicurezza
- Messaggi interfaccia
- Simboli e colori
- Configurazioni ambiente (dev/prod/test)

## Utilità

Il file `utils.py` fornisce:
- Validazione email, password, username
- Sanitizzazione input
- Formattazione date e testi
- Statistiche task
- Funzioni di logging

## Test

Il file `test_taskboard.py` include test per:
- Classi del modello
- Operazioni database
- Funzioni di utilità
- Configurazione

**Esecuzione test:**
```bash
python test_taskboard.py
```

## Avvio Applicazione

```bash
python main.py
```

### Credenziali Admin Default
- **Username**: admin
- **Password**: admin123
- **Email**: admin@taskboard.com

## Gestione Errori

L'applicazione gestisce:
- Errori di connessione database
- Input non validi
- Operazioni non autorizzate
- Interruzioni utente (Ctrl+C)
- Errori di encoding Unicode

## Estensibilità

L'architettura MVC permette facilmente:
- Aggiunta nuove funzionalità
- Cambio interfaccia (GUI, Web)
- Integrazione API esterne
- Diversi backend database

## Limitazioni Attuali

- Database SQLite locale (non multi-utente concorrente)
- Interfaccia solo CLI
- Nessuna sincronizzazione cloud
- Backup manuali

## Possibili Miglioramenti

1. **Interfaccia Web** (Flask/Django)
2. **GUI Desktop** (Tkinter/Kivy)
3. **API REST** per integrazioni
4. **Database remoto** (PostgreSQL/MySQL)
5. **Autenticazione OAuth**
6. **Notifiche email**
7. **Backup automatici**
8. **Logging avanzato**
9. **Metriche e analytics**
10. **Supporto team/collaborazione**

## Dipendenze

L'applicazione usa solo librerie standard Python:
- `sqlite3`: Database
- `hashlib`: Hashing password
- `uuid`: Generazione ID univoci
- `datetime`: Gestione date
- `os`: Operazioni sistema
- `re`: Espressioni regolari
- `unittest`: Test

## Compatibilità

- **Python**: 3.7+
- **OS**: Windows, Linux, macOS
- **Database**: SQLite 3.x

## Performance

- Ottimizzato per uso singolo utente
- Database indicizzato su campi chiave
- Queries efficienti con prepared statements
- Gestione memoria ottimale

## Manutenzione

### Backup Database
```python
from database import DatabaseManager
db = DatabaseManager()
db.backup_database("backup_path.db")
```

### Pulizia Token Scaduti
```python
db.cleanup_old_recovery_tokens()
```

### Statistiche Sistema
```python
stats = db.get_database_stats()
print(stats)
```

## Supporto

Per problemi o domande:
1. Controllare la documentazione
2. Eseguire i test per verificare l'installazione
3. Verificare i log per errori specifici
4. Consultare il codice sorgente per dettagli implementativi

---

*Documentazione aggiornata al: 24/07/2025*
*Versione applicazione: 1.0.0*