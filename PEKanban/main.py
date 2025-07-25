# main.py - Punto di ingresso dell'applicazione Taskboard
# Avvia l'applicazione e gestisce le eccezioni principali

import sys
import traceback
from controller import TaskboardController

def main():
    """Funzione principale dell'applicazione"""
    try:
        # Crea e avvia il controller
        app = TaskboardController()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\n[STOP] Applicazione interrotta dall'utente.")
        print("Arrivederci!")
        
    except Exception as e:
        print(f"\n[ERROR] ERRORE CRITICO: {str(e)}")
        print("\nDettagli tecnici:")
        traceback.print_exc()
        print("\nL'applicazione verrà chiusa.")
        
    finally:
        # Cleanup se necessario
        print("\n[BYE] Grazie per aver usato Taskboard!")
        sys.exit(0)

if __name__ == "__main__":
    main()