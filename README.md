# Taskboard - Gestione Attività Personali

Un'applicazione Python CLI per la gestione di attività personali in stile Kanban, sviluppata seguendo il pattern architetturale MVC (Model-View-Controller).

## 📋 Caratteristiche

- **Architettura MVC**: Separazione chiara tra logica di business, presentazione e controllo
- **Autenticazione utente**: Sistema di registrazione e login con password hashate (SHA-256)
- **Gestione task**: Creazione, modifica, eliminazione e cambio stato dei task
- **Stati Kanban**: ToDo, Doing, Done
- **Database SQLite3**: Persistenza dei dati con operazioni CRUD complete
- **Interfaccia CLI**: Interfaccia a riga di comando intuitiva e user-friendly
- **Sicurezza**: Ogni utente può accedere solo ai propri task

## 🏗️ Struttura del Progetto

```
PEKanban/
├── model/
│   └── model.py          # Classi User e Task (Model)
├── view/
│   └── view.py           # Interfaccia CLI (View)
├── controller/
│   └── controller.py     # Logica di controllo (Controller)
├── database.py           # Gestione database SQLite3
├── main.py              # Punto di ingresso dell'applicazione
├── README.md            # Documentazione
└── taskboard.db         # Database SQLite (creato automaticamente)
```

## 🚀 Installazione e Avvio

### Prerequisiti
- Python 3.7 o superiore
- Moduli standard Python (sqlite3, hashlib, datetime, typing)

### Versioni disponibili

#### Versione Base (CLI semplice)
```bash
python main.py
```

#### Versione Rich (CLI avanzata) - **BONUS 3 IMPLEMENTATO**
```bash
# Installa Rich se non già presente
pip install rich

# Avvia la versione avanzata
python main_rich.py
```

**Caratteristiche della versione Rich:**
- 🎨 Interfaccia colorata e moderna
- 📊 Tabelle eleganti con bordi
- ⏳ Animazioni di caricamento
- 📈 Progress bar per statistiche
- 🎯 Pannelli colorati per messaggi
- 📋 Bacheca Kanban visivamente migliorata
- 📊 Statistiche avanzate sui task

## 📖 Utilizzo

### 1. Primo Avvio
Al primo avvio, l'applicazione creerà automaticamente il database SQLite3.

### 2. Registrazione
- Scegli l'opzione "2. Registrazione"
- Inserisci username e password
- La password viene automaticamente hashata con SHA-256

### 3. Login
- Scegli l'opzione "1. Login"
- Inserisci le tue credenziali

### 4. Gestione Task
Una volta autenticato, puoi:
- **Visualizzare task**: Lista di tutti i tuoi task
- **Aggiungere task**: Crea nuovi task con titolo e descrizione
- **Modificare task**: Modifica titolo e descrizione
- **Cambiare stato**: Sposta i task tra ToDo, Doing, Done
- **Eliminare task**: Rimuovi task non più necessari
- **Bacheca Kanban**: Visualizza i task organizzati per colonne

## 🏛️ Architettura MVC

### Model (`model/model.py`)
- **Classe User**: Gestisce i dati utente e l'autenticazione
- **Classe Task**: Rappresenta le attività con stati e validazioni
- **Logica di business**: Validazione dati, hashing password, transizioni di stato

### View (`view/view.py`)
- **TaskboardView**: Interfaccia CLI per l'interazione utente
- **Visualizzazione dati**: Menu, liste task, bacheca Kanban
- **Input utente**: Form per login, registrazione, gestione task

### Controller (`controller/controller.py`)
- **TaskboardController**: Coordina Model e View
- **Gestione flusso**: Loop principale, routing delle azioni
- **Autenticazione**: Controllo accessi e sessioni utente

### Database (`database.py`)
- **DatabaseManager**: Pattern Repository per l'accesso ai dati
- **Operazioni CRUD**: Create, Read, Update, Delete per User e Task
- **Gestione connessioni**: SQLite3 con context manager

## 🗄️ Schema Database

### Tabella `users`
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabella `tasks`
```sql
CREATE TABLE tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'ToDo',
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);
```

## 🔒 Sicurezza

- **Password hashing**: SHA-256 per la sicurezza delle password
- **Isolamento utenti**: Ogni utente accede solo ai propri task
- **Validazione input**: Controlli sui dati inseriti
- **Gestione errori**: Handling robusto delle eccezioni

## 🎯 Funzionalità Implementate

### ✅ Requisiti Base (100 punti)
- [x] **Step 1**: Setup MVC (5 punti)
- [x] **Step 2**: Classi OOP (15 punti)
- [x] **Step 3**: SQLite3 (20 punti)
- [x] **Step 3b**: Login (10 punti)
- [x] **Step 4**: Controller (15 punti)
- [x] **Step 5**: CLI (15 punti)
- [x] **Step 6**: Modularità (10 punti)
- [x] **Step 7**: Refactoring (10 punti)

### 🎁 Bonus Implementati - TUTTI COMPLETATI! 🎉
- [x] **Bonus 1**: Interfaccia Web Flask (15 punti) - **✅ IMPLEMENTATO**
- [x] **Bonus 2**: GUI Desktop Kivy (15 punti) - **✅ IMPLEMENTATO**
- [x] **Bonus 3**: CLI avanzata con Rich (15 punti) - **✅ IMPLEMENTATO**

#### Dettagli Bonus 1 - Interfaccia Web Flask
**Applicazione Web (`main_flask.py`):**
- 🌐 **Server Flask**: Interfaccia web completa su http://localhost:5000
- 🎨 **Bootstrap UI**: Design moderno e responsive
- 🔐 **Autenticazione web**: Login e registrazione via form
- 📋 **CRUD completo**: Creazione, modifica, eliminazione task via web
- 📊 **Dashboard**: Statistiche e overview dei task
- 🎯 **Bacheca Kanban**: Vista Kanban interattiva
- 📱 **Responsive**: Compatibile con desktop e mobile

#### Dettagli Bonus 2 - GUI Desktop Kivy
**Applicazione Desktop (`main_kivy.py`):**
- 🖥️ **GUI nativa**: Interfaccia desktop con Kivy
- 🔑 **Login desktop**: Schermata di autenticazione grafica
- 📝 **Gestione task**: Form grafici per CRUD task
- 🎨 **UI moderna**: Layout responsive e user-friendly
- 🔄 **Navigazione**: Screen manager per diverse schermate
- ⚡ **Performance**: Applicazione desktop veloce e fluida

#### Dettagli Bonus 3 - CLI Avanzata
Il **Bonus 3** è stato completamente implementato con le seguenti caratteristiche:

**Interfaccia Rich (`main_rich.py`):**
- 🎨 **Colori e stili**: Interfaccia completamente colorata con temi coerenti
- 📊 **Tabelle eleganti**: Visualizzazione dati in tabelle con bordi e intestazioni colorate
- ⏳ **Animazioni**: Progress bar e spinner per operazioni di caricamento
- 🎯 **Pannelli informativi**: Messaggi di successo, errore e info in pannelli colorati
- 📋 **Bacheca Kanban migliorata**: Layout a colonne con colori per ogni stato
- 📈 **Statistiche avanzate**: Grafici testuali e percentuali di completamento
- 🔄 **Progress bar animate**: Visualizzazione dinamica del progresso

**Funzionalità aggiuntive:**
- Menu interattivi con scelte guidate
- Validazione input migliorata
- Messaggi di feedback visivamente accattivanti
- Compatibilità Windows ottimizzata

**File implementati:**
- [`main_rich.py`](main_rich.py) - Punto di ingresso versione Rich
- [`view/simple_rich_view.py`](view/simple_rich_view.py) - View avanzata con Rich
- [`controller/rich_controller.py`](controller/rich_controller.py) - Controller per versione Rich
- [`config.py`](config.py) - File di configurazione
- [`utils.py`](utils.py) - Funzioni di utilità

## 🛠️ Sviluppo e Test

### Test Manuale
```bash
# Avvia l'applicazione
python main.py

# Testa il flusso completo:
# 1. Registrazione nuovo utente
# 2. Login
# 3. Creazione task
# 4. Modifica stato task
# 5. Visualizzazione bacheca Kanban
```

### Reset Database
Per resettare completamente il database:
```bash
# Elimina il file database
rm taskboard.db

# Riavvia l'applicazione (ricreerà il database)
python main.py
```

## 📝 Note Tecniche

- **Pattern utilizzati**: MVC, Repository, Singleton (DatabaseManager)
- **Gestione errori**: Try-catch con messaggi user-friendly
- **Type hints**: Utilizzo di typing per migliore leggibilità
- **Docstring**: Documentazione completa di classi e metodi
- **Separazione responsabilità**: Ogni modulo ha un compito specifico

## 🤝 Contributi

Questo progetto è stato sviluppato come test d'esame per il corso di Python. 
La struttura è progettata per essere facilmente estendibile con nuove funzionalità.

## 📄 Licenza

Progetto educativo - Libero utilizzo per scopi didattici.

---

**Autore**: Sviluppato seguendo le specifiche del test d'esame  
**Versione**: 1.0.0  
**Data**: 2025