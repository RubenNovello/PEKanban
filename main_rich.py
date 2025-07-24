"""
MAIN RICH - Punto di ingresso per l'applicazione Taskboard con interfaccia Rich
Versione avanzata con interfaccia colorata, tabelle eleganti e animazioni
"""

import sys
import os
from database import DatabaseManager
from controller.rich_controller import RichTaskboardController


def main():
    """
    Funzione principale che avvia l'applicazione Taskboard Rich
    """
    try:
        # Configura encoding per Windows
        if sys.platform == "win32":
            os.system("chcp 65001 >nul 2>&1")
        
        # Banner di avvio
        print("Inizializzazione Taskboard Rich...")
        
        # Inizializza il database manager
        db_manager = DatabaseManager("taskboard.db")
        
        # Inizializza il controller Rich con il database
        controller = RichTaskboardController(db_manager)
        
        # Avvia l'applicazione Rich
        controller.run()
        
    except KeyboardInterrupt:
        print("\n\nApplicazione interrotta dall'utente.")
        sys.exit(0)
    except ImportError as e:
        print(f"\nErrore: Libreria mancante - {e}")
        print("Installa Rich con: pip install rich")
        sys.exit(1)
    except Exception as e:
        print(f"\nErrore critico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()