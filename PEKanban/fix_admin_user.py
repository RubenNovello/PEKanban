#!/usr/bin/env python3
# fix_admin_user.py - Script per correggere la situazione admin nel database

import sqlite3
from database import DatabaseManager
from model import User, Admin

def fix_admin_user():
    """Promuove RubenNovello ad admin e rimuove admin fittizi"""
    print("=== CORREZIONE ADMIN UTENTE ===")
    
    db = DatabaseManager("database.db")
    
    # 1. Verifica situazione attuale
    print("1. Situazione attuale:")
    users = db.get_all_users()
    for user in users:
        print(f"   - {user.username} ({user.email}) - Admin: {user.is_admin}")
    
    # 2. Trova RubenNovello
    ruben_user = None
    admin_fittizio = None
    
    for user in users:
        if user.username == "RubenNovello":
            ruben_user = user
        elif user.username == "admin":
            admin_fittizio = user
    
    if not ruben_user:
        print("[ERROR] Utente RubenNovello non trovato!")
        return False
    
    print(f"2. Trovato RubenNovello: {ruben_user.email} (is_admin: {ruben_user.is_admin})")
    
    # 3. Promuovi RubenNovello ad admin se non lo è già
    if not ruben_user.is_admin:
        print("3. Promuovendo RubenNovello ad admin...")
        
        # Crea nuovo oggetto Admin con gli stessi dati
        admin_ruben = Admin(ruben_user.username, ruben_user.email, "")
        admin_ruben.user_id = ruben_user.user_id
        admin_ruben.password_hash = ruben_user.password_hash
        admin_ruben.token = ruben_user.token
        admin_ruben.created_at = ruben_user.created_at
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Rimuovi dalla tabella users
            cursor.execute("DELETE FROM users WHERE user_id = ?", (ruben_user.user_id,))
            
            # Aggiungi alla tabella admin
            cursor.execute('''
                INSERT INTO admin (admin_id, username, email, password_hash, token, created_at, permissions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                admin_ruben.user_id,
                admin_ruben.username,
                admin_ruben.email,
                admin_ruben.password_hash,
                admin_ruben.token,
                admin_ruben.created_at.isoformat(),
                'full'
            ))
            
            conn.commit()
        
        print("   [OK] RubenNovello promosso ad admin!")
    else:
        print("3. RubenNovello è già admin")
    
    # 4. Rimuovi admin fittizio se esiste
    if admin_fittizio:
        print("4. Rimuovendo admin fittizio...")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Rimuovi tutti i task dell'admin fittizio
            cursor.execute("DELETE FROM tasks WHERE user_id = ?", (admin_fittizio.user_id,))
            
            # Rimuovi l'admin fittizio
            if admin_fittizio.is_admin:
                cursor.execute("DELETE FROM admin WHERE admin_id = ?", (admin_fittizio.user_id,))
            else:
                cursor.execute("DELETE FROM users WHERE user_id = ?", (admin_fittizio.user_id,))
            
            conn.commit()
        
        print("   [OK] Admin fittizio rimosso!")
    else:
        print("4. Nessun admin fittizio trovato")
    
    # 5. Verifica situazione finale
    print("\n5. Situazione finale:")
    users = db.get_all_users()
    for user in users:
        print(f"   - {user.username} ({user.email}) - Admin: {user.is_admin}")
    
    # 6. Statistiche
    stats = db.get_database_stats()
    print(f"\n6. Statistiche:")
    print(f"   - Utenti totali: {stats['total_users']}")
    print(f"   - Admin: {stats['admin_users']}")
    print(f"   - Utenti normali: {stats['regular_users']}")
    print(f"   - Task totali: {stats['total_tasks']}")
    
    return True

if __name__ == "__main__":
    fix_admin_user()