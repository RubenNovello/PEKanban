"""
MAIN FLASK - Applicazione web Taskboard con Flask
Bonus 1: Interfaccia web minimale con login, lista task, aggiunta, modifica, cancellazione
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import DatabaseManager
from model.model import User, Task
import os

app = Flask(__name__)
app.secret_key = 'taskboard_secret_key_2025'  # In produzione usare una chiave più sicura

# Inizializza il database
db_manager = DatabaseManager("taskboard.db")

@app.route('/')
def index():
    """Pagina principale - reindirizza al login se non autenticato"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Pagina di login"""
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if not username or not password:
            flash('Username e password sono obbligatori!', 'error')
            return render_template('login.html')
        
        user = db_manager.get_user_by_username(username)
        if user and user.check_password(password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            flash(f'Benvenuto, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenziali non valide!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Pagina di registrazione"""
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        
        # Validazioni
        if not username or not password:
            flash('Username e password sono obbligatori!', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username deve essere almeno 3 caratteri!', 'error')
            return render_template('register.html')
        
        if len(password) < 4:
            flash('Password deve essere almeno 4 caratteri!', 'error')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Le password non coincidono!', 'error')
            return render_template('register.html')
        
        # Verifica se l'username esiste già
        if db_manager.get_user_by_username(username):
            flash('Username già esistente!', 'error')
            return render_template('register.html')
        
        # Crea nuovo utente
        new_user = User(username=username)
        new_user.set_password(password)
        
        if db_manager.create_user(new_user):
            flash('Registrazione completata! Ora puoi effettuare il login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Errore durante la registrazione!', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard principale con lista task"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    tasks = db_manager.get_tasks_by_user(user_id)
    
    # Calcola statistiche
    stats = {
        'total': len(tasks),
        'todo': len([t for t in tasks if t.status == 'ToDo']),
        'doing': len([t for t in tasks if t.status == 'Doing']),
        'done': len([t for t in tasks if t.status == 'Done'])
    }
    
    return render_template('dashboard.html', tasks=tasks, stats=stats)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    """Aggiunge un nuovo task"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        
        if not title or len(title) < 3:
            flash('Il titolo deve essere almeno 3 caratteri!', 'error')
            return render_template('add_task.html')
        
        if len(title) > 100:
            flash('Il titolo è troppo lungo (max 100 caratteri)!', 'error')
            return render_template('add_task.html')
        
        if len(description) > 500:
            flash('La descrizione è troppo lunga (max 500 caratteri)!', 'error')
            return render_template('add_task.html')
        
        new_task = Task(
            title=title,
            description=description,
            status=Task.STATUS_TODO,
            user_id=session['user_id']
        )
        
        if db_manager.create_task(new_task):
            flash('Task creato con successo!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Errore durante la creazione del task!', 'error')
    
    return render_template('add_task.html')

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Modifica un task esistente"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = db_manager.get_task_by_id(task_id)
    if not task or task.user_id != session['user_id']:
        flash('Task non trovato o non autorizzato!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        status = request.form['status']
        
        if not title or len(title) < 3:
            flash('Il titolo deve essere almeno 3 caratteri!', 'error')
            return render_template('edit_task.html', task=task)
        
        if len(title) > 100:
            flash('Il titolo è troppo lungo (max 100 caratteri)!', 'error')
            return render_template('edit_task.html', task=task)
        
        if len(description) > 500:
            flash('La descrizione è troppo lunga (max 500 caratteri)!', 'error')
            return render_template('edit_task.html', task=task)
        
        if status not in [Task.STATUS_TODO, Task.STATUS_DOING, Task.STATUS_DONE]:
            flash('Stato non valido!', 'error')
            return render_template('edit_task.html', task=task)
        
        task.update_content(title, description)
        task.update_status(status)
        
        if db_manager.update_task(task):
            flash('Task modificato con successo!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Errore durante la modifica del task!', 'error')
    
    return render_template('edit_task.html', task=task)

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    """Elimina un task"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = db_manager.get_task_by_id(task_id)
    if not task or task.user_id != session['user_id']:
        flash('Task non trovato o non autorizzato!', 'error')
        return redirect(url_for('dashboard'))
    
    if db_manager.delete_task(task_id):
        flash('Task eliminato con successo!', 'success')
    else:
        flash('Errore durante l\'eliminazione del task!', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/kanban')
def kanban():
    """Visualizza la bacheca Kanban"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    tasks = db_manager.get_tasks_by_user(user_id)
    
    # Raggruppa i task per stato
    kanban_data = {
        'todo': [t for t in tasks if t.status == Task.STATUS_TODO],
        'doing': [t for t in tasks if t.status == Task.STATUS_DOING],
        'done': [t for t in tasks if t.status == Task.STATUS_DONE]
    }
    
    return render_template('kanban.html', kanban=kanban_data)

@app.route('/logout')
def logout():
    """Logout dell'utente"""
    session.clear()
    flash('Logout effettuato con successo!', 'success')
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(error):
    """Gestione errore 404"""
    return render_template('error.html', error="Pagina non trovata"), 404

@app.errorhandler(500)
def internal_error(error):
    """Gestione errore 500"""
    return render_template('error.html', error="Errore interno del server"), 500

if __name__ == '__main__':
    # Crea la cartella templates se non esiste
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Avvio Taskboard Web Flask...")
    print("URL: http://localhost:5000")
    print("Per accedere: registrati o usa credenziali esistenti")
    
    app.run(debug=True, host='0.0.0.0', port=5000)