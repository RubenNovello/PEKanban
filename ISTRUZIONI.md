# 📋 Istruzioni per l'utilizzo di Taskboard

## 🚀 Avvio dell'applicazione

### Versione Base (CLI semplice)
```bash
python main.py
```

### Versione Rich (CLI avanzata con colori e tabelle)
```bash
# Prima installa Rich se non già presente
pip install rich

# Poi avvia la versione avanzata
python main_rich.py
```

## 👤 Primo utilizzo

### 1. Registrazione
- Avvia l'applicazione
- Scegli opzione "2. Registrazione"
- Inserisci un username (minimo 3 caratteri)
- Inserisci una password (minimo 4 caratteri)
- Conferma la password

### 2. Login
- Scegli opzione "1. Login"
- Inserisci le credenziali create durante la registrazione

## 📝 Gestione Task

Una volta effettuato il login, avrai accesso a tutte le funzionalità:

### Visualizzare i task
- **Opzione 1**: Mostra tutti i tuoi task in formato tabella
- **Opzione 6**: Visualizza la bacheca Kanban con colonne ToDo/Doing/Done
- **Opzione 7** (solo versione Rich): Statistiche dettagliate sui task

### Creare un nuovo task
- **Opzione 2**: Aggiungi nuovo task
- Inserisci titolo (obbligatorio, minimo 3 caratteri)
- Inserisci descrizione (opzionale)
- Il task viene creato automaticamente nello stato "ToDo"

### Modificare un task
- **Opzione 3**: Modifica task esistente
- Visualizza la lista dei tuoi task
- Inserisci l'ID del task da modificare
- Modifica titolo e/o descrizione

### Cambiare stato di un task
- **Opzione 4**: Cambia stato task
- Visualizza la lista dei tuoi task
- Inserisci l'ID del task
- Scegli il nuovo stato:
  - 1 = ToDo (da fare)
  - 2 = Doing (in corso)
  - 3 = Done (completato)

### Eliminare un task
- **Opzione 5**: Elimina task
- Visualizza la lista dei tuoi task
- Inserisci l'ID del task da eliminare
- Conferma l'eliminazione

## 🎨 Differenze tra le versioni

### Versione Base (`main.py`)
- Interfaccia CLI semplice e funzionale
- Compatibile con tutti i terminali
- Nessuna dipendenza esterna

### Versione Rich (`main_rich.py`)
- Interfaccia colorata e moderna
- Tabelle eleganti con bordi
- Animazioni di caricamento
- Progress bar per le statistiche
- Pannelli colorati per messaggi
- Bacheca Kanban visivamente migliorata
- Statistiche avanzate sui task

## 🔒 Sicurezza

- Ogni utente vede solo i propri task
- Le password sono hashate con SHA-256
- Validazione degli input per prevenire errori
- Gestione sicura delle sessioni

## 🗄️ Database

- Il database SQLite (`taskboard.db`) viene creato automaticamente
- Contiene tabelle per utenti e task
- Relazioni con chiavi esterne per integrità dei dati
- Backup automatico tramite SQLite

## 🛠️ Risoluzione problemi

### Errore "Libreria mancante"
```bash
pip install rich
```

### Problemi con caratteri speciali su Windows
- La versione Rich è ottimizzata per Windows
- Usa `main_rich.py` per la migliore esperienza

### Reset completo del database
```bash
# Elimina il file database
del taskboard.db  # Windows
rm taskboard.db   # Linux/Mac

# Riavvia l'applicazione per ricreare il database
python main.py
```

### Task non visualizzati
- Verifica di aver effettuato il login
- Ogni utente vede solo i propri task
- Controlla di aver creato almeno un task

## 📊 Funzionalità avanzate (versione Rich)

### Statistiche dettagliate
- Conteggio task per stato
- Percentuale di completamento
- Progress bar animata
- Grafici testuali

### Bacheca Kanban migliorata
- Colonne colorate per stato
- Layout responsive
- Visualizzazione compatta dei task

### Interfaccia migliorata
- Messaggi colorati (successo=verde, errore=rosso, info=blu)
- Animazioni di caricamento
- Prompt interattivi migliorati
- Tabelle con intestazioni colorate

## 💡 Suggerimenti d'uso

1. **Organizza i task**: Usa descrizioni chiare per ricordare i dettagli
2. **Sfrutta gli stati**: Sposta i task attraverso ToDo → Doing → Done
3. **Monitora il progresso**: Usa le statistiche per vedere i tuoi progressi
4. **Bacheca Kanban**: Visualizza rapidamente lo stato di tutti i task
5. **Backup**: Il database SQLite può essere copiato per backup

## 🎯 Workflow consigliato

1. **Pianificazione**: Crea tutti i task necessari in stato "ToDo"
2. **Esecuzione**: Sposta in "Doing" i task su cui stai lavorando
3. **Completamento**: Sposta in "Done" i task completati
4. **Monitoraggio**: Controlla regolarmente le statistiche
5. **Pulizia**: Elimina periodicamente i task obsoleti

---

**Buon lavoro con Taskboard! 🎉**