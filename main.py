"""
MAIN - Punto di ingresso dell'applicazione Taskboard
Inizializza i componenti MVC e avvia l'applicazione
"""

import sys
import os
from database import DatabaseManager
from controller.controller import TaskboardController


def main():
    """
    Funzione principale che avvia l'applicazione Taskboard
    """
    try:
        print("Inizializzazione Taskboard...")
        
        # Inizializza il database manager
        db_manager = DatabaseManager("taskboard.db")
        
        # Inizializza il controller con il database
        controller = TaskboardController(db_manager)
        
        # Avvia l'applicazione
        controller.run()
        
    except KeyboardInterrupt:
        print("\n\nApplicazione interrotta dall'utente.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErrore critico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()