# web_app.py - Applicazione Flask Web per Taskboard
# Versione web dell'applicazione con interfaccia drag&drop

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from database import DatabaseManager
from model import User, Task, Admin
from utils import validate_email, validate_password_strength, validate_username
from config import Config

app = Flask(__name__)
app.secret_key = 'taskboard_secret_key_2025'  # In produzione usare una chiave più sicura

# Inizializza il database
db = DatabaseManager()

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
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username e password sono obbligatori.', 'error')
            return render_template('login.html')
        
        user = db.authenticate_user(username, password)
        if user:
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash(f'Benvenuto, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenziali non valide.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Pagina di registrazione"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validazione
        if not all([username, email, password, confirm_password]):
            flash('Tutti i campi sono obbligatori.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Le password non coincidono.', 'error')
            return render_template('register.html')
        
        # Validazione username
        valid_username, msg = validate_username(username)
        if not valid_username:
            flash(msg, 'error')
            return render_template('register.html')
        
        # Validazione email
        if not validate_email(email):
            flash('Formato email non valido.', 'error')
            return render_template('register.html')
        
        # Validazione password
        valid_password, msg = validate_password_strength(password)
        if not valid_password:
            flash(msg, 'error')
            return render_template('register.html')
        
        # Verifica se utente esiste già
        if db.user_exists(username, email):
            flash('Username o email già esistenti.', 'error')
            return render_template('register.html')
        
        # Verifica se è il primo utente (diventa admin automaticamente)
        is_first_user = db.is_first_user()
        
        if is_first_user:
            # Il primo utente diventa admin
            user = Admin(username, email, password)
            success_message = 'Registrazione completata con successo! Sei il primo utente e hai privilegi di amministratore. Puoi ora effettuare il login.'
        else:
            # Utenti successivi sono normali
            user = User(username, email, password)
            success_message = 'Registrazione completata con successo! Puoi ora effettuare il login.'
        
        if db.create_user(user):
            flash(success_message, 'success')
            return redirect(url_for('login'))
        else:
            flash('Errore durante la registrazione.', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout utente"""
    session.clear()
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Dashboard principale con kanban board"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    is_admin = session.get('is_admin', False)
    
    # Recupera task dell'utente o tutti i task se admin
    if is_admin:
        tasks = db.get_all_tasks()
        users = db.get_all_users()
    else:
        tasks = db.get_user_tasks(user_id)
        users = []
    
    # Raggruppa task per stato
    todo_tasks = [t for t in tasks if t.status == Task.STATUS_TODO]
    doing_tasks = [t for t in tasks if t.status == Task.STATUS_DOING]
    done_tasks = [t for t in tasks if t.status == Task.STATUS_DONE]
    
    return render_template('dashboard.html', 
                         todo_tasks=todo_tasks,
                         doing_tasks=doing_tasks,
                         done_tasks=done_tasks,
                         users=users,
                         is_admin=is_admin)

@app.route('/add_task', methods=['POST'])
def add_task():
    """Aggiunge un nuovo task"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Non autenticato'})
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        return jsonify({'success': False, 'message': 'Il titolo è obbligatorio'})
    
    user_id = session['user_id']
    task = Task(title, description, user_id)
    
    if db.create_task(task):
        return jsonify({
            'success': True, 
            'message': 'Task creato con successo!',
            'task': {
                'id': task.task_id,
                'title': task.title,
                'description': task.description,
                'status': task.status
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Errore durante la creazione del task'})

@app.route('/update_task_status', methods=['POST'])
def update_task_status():
    """Aggiorna lo stato di un task (per drag&drop)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Non autenticato'})
    
    task_id = request.form.get('task_id')
    new_status = request.form.get('new_status')
    
    if not task_id or not new_status:
        return jsonify({'success': False, 'message': 'Parametri mancanti'})
    
    # Verifica che lo stato sia valido
    if new_status not in [Task.STATUS_TODO, Task.STATUS_DOING, Task.STATUS_DONE]:
        return jsonify({'success': False, 'message': 'Stato non valido'})
    
    task = db.get_task_by_id(task_id)
    if not task:
        return jsonify({'success': False, 'message': 'Task non trovato'})
    
    # Verifica autorizzazioni (utente può modificare solo i propri task, admin tutti)
    user_id = session['user_id']
    is_admin = session.get('is_admin', False)
    
    if not is_admin and task.user_id != user_id:
        return jsonify({'success': False, 'message': 'Non autorizzato'})
    
    # Aggiorna stato
    if task.update_status(new_status):
        if db.update_task(task):
            return jsonify({'success': True, 'message': 'Stato aggiornato con successo!'})
        else:
            return jsonify({'success': False, 'message': 'Errore durante l\'aggiornamento'})
    else:
        return jsonify({'success': False, 'message': 'Stato non valido'})

@app.route('/edit_task/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Modifica un task"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = db.get_task_by_id(task_id)
    if not task:
        flash('Task non trovato.', 'error')
        return redirect(url_for('dashboard'))
    
    # Verifica autorizzazioni
    user_id = session['user_id']
    is_admin = session.get('is_admin', False)
    
    if not is_admin and task.user_id != user_id:
        flash('Non autorizzato a modificare questo task.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title:
            flash('Il titolo è obbligatorio.', 'error')
            if is_admin:
                return redirect(url_for('admin_panel'))
            return render_template('edit_task.html', task=task)
        
        task.update_details(title, description)
        if db.update_task(task):
            flash('Task aggiornato con successo!', 'success')
            if is_admin:
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        else:
            flash('Errore durante l\'aggiornamento.', 'error')
    
    return render_template('edit_task.html', task=task)

@app.route('/delete_task/<task_id>', methods=['POST'])
def delete_task(task_id):
    """Elimina un task"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Non autenticato'})
    
    task = db.get_task_by_id(task_id)
    if not task:
        return jsonify({'success': False, 'message': 'Task non trovato'})
    
    # Verifica autorizzazioni
    user_id = session['user_id']
    is_admin = session.get('is_admin', False)
    
    if not is_admin and task.user_id != user_id:
        return jsonify({'success': False, 'message': 'Non autorizzato'})
    
    if db.delete_task(task_id):
        return jsonify({'success': True, 'message': 'Task eliminato con successo!'})
    else:
        return jsonify({'success': False, 'message': 'Errore durante l\'eliminazione'})

@app.route('/admin')
def admin_panel():
    """Pannello amministrativo"""
    if 'user_id' not in session or not session.get('is_admin', False):
        flash('Accesso negato. Privilegi amministrativi richiesti.', 'error')
        return redirect(url_for('dashboard'))
    
    users = db.get_all_users()
    tasks_with_users = db.get_all_tasks_with_users()
    stats = db.get_database_stats()
    
    return render_template('admin.html', users=users, tasks_with_users=tasks_with_users, stats=stats)

@app.route('/admin/create_user', methods=['POST'])
def admin_create_user():
    """Crea un nuovo utente (solo admin)"""
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Accesso negato'})
    
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    is_admin = request.form.get('is_admin') == 'true'
    
    # Validazione
    if not all([username, email, password]):
        return jsonify({'success': False, 'message': 'Tutti i campi sono obbligatori'})
    
    # Validazione username
    valid_username, msg = validate_username(username)
    if not valid_username:
        return jsonify({'success': False, 'message': msg})
    
    # Validazione email
    if not validate_email(email):
        return jsonify({'success': False, 'message': 'Formato email non valido'})
    
    # Validazione password
    valid_password, msg = validate_password_strength(password)
    if not valid_password:
        return jsonify({'success': False, 'message': msg})
    
    # Verifica se utente esiste già
    if db.user_exists(username, email):
        return jsonify({'success': False, 'message': 'Username o email già esistenti'})
    
    # Crea utente
    if is_admin:
        user = Admin(username, email, password)
    else:
        user = User(username, email, password)
    
    if db.create_user(user):
        return jsonify({'success': True, 'message': f'Utente {username} creato con successo!'})
    else:
        return jsonify({'success': False, 'message': 'Errore durante la creazione dell\'utente'})

@app.route('/admin/promote_user', methods=['POST'])
def admin_promote_user():
    """Promuove un utente ad admin"""
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Accesso negato'})
    
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'ID utente mancante'})
    
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Utente non trovato'})
    
    if user.is_admin:
        return jsonify({'success': False, 'message': 'L\'utente è già amministratore'})
    
    user.is_admin = True
    if db.update_user(user):
        return jsonify({'success': True, 'message': f'{user.username} promosso ad amministratore!'})
    else:
        return jsonify({'success': False, 'message': 'Errore durante la promozione'})

@app.route('/admin/demote_user', methods=['POST'])
def admin_demote_user():
    """Rimuove privilegi admin da un utente"""
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Accesso negato'})
    
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'ID utente mancante'})
    
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Utente non trovato'})
    
    if not user.is_admin:
        return jsonify({'success': False, 'message': 'L\'utente non è amministratore'})
    
    if user.user_id == session['user_id']:
        return jsonify({'success': False, 'message': 'Non puoi rimuovere i tuoi privilegi'})
    
    user.is_admin = False
    if db.update_user(user):
        return jsonify({'success': True, 'message': f'Privilegi amministratore rimossi da {user.username}!'})
    else:
        return jsonify({'success': False, 'message': 'Errore durante la rimozione privilegi'})

@app.route('/admin/reset_password', methods=['POST'])
def admin_reset_password():
    """Resetta la password di un utente"""
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Accesso negato'})
    
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password', '').strip()
    
    if not user_id or not new_password:
        return jsonify({'success': False, 'message': 'ID utente e nuova password sono obbligatori'})
    
    # Validazione password
    valid_password, msg = validate_password_strength(new_password)
    if not valid_password:
        return jsonify({'success': False, 'message': msg})
    
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Utente non trovato'})
    
    user.change_password(new_password)
    if db.update_user(user):
        return jsonify({'success': True, 'message': f'Password di {user.username} reimpostata!'})
    else:
        return jsonify({'success': False, 'message': 'Errore durante il reset password'})

@app.route('/admin/delete_user', methods=['POST'])
def admin_delete_user():
    """Elimina un utente e tutti i suoi task"""
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Accesso negato'})
    
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'ID utente mancante'})
    
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Utente non trovato'})
    
    if user.user_id == session['user_id']:
        return jsonify({'success': False, 'message': 'Non puoi eliminare te stesso'})
    
    user_tasks = db.get_user_tasks(user_id)
    if db.delete_user_and_tasks(user_id):
        return jsonify({'success': True, 'message': f'Utente {user.username} e {len(user_tasks)} task eliminati!'})
    else:
        return jsonify({'success': False, 'message': 'Errore durante l\'eliminazione'})

@app.route('/admin/assign_task', methods=['POST'])
def admin_assign_task():
    """Assegna un task a un utente (solo admin)"""
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Accesso negato'})
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    assigned_user_id = request.form.get('assigned_user_id', '').strip()
    
    if not title or not assigned_user_id:
        return jsonify({'success': False, 'message': 'Titolo e utente assegnato sono obbligatori'})
    
    # Verifica che l'utente assegnato esista
    assigned_user = db.get_user_by_id(assigned_user_id)
    if not assigned_user:
        return jsonify({'success': False, 'message': 'Utente assegnato non trovato'})
    
    # Crea il task assegnato all'utente specificato
    task = Task(title, description, assigned_user_id)
    
    if db.create_task(task):
        return jsonify({
            'success': True,
            'message': f'Task assegnato a {assigned_user.username} con successo!',
            'task': {
                'id': task.task_id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'assigned_to': assigned_user.username
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Errore durante l\'assegnazione del task'})

@app.route('/profile')
def profile():
    """Profilo utente"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    
    if not user:
        flash('Utente non trovato.', 'error')
        return redirect(url_for('logout'))
    
    user_tasks = db.get_user_tasks(user_id)
    task_stats = {
        'total': len(user_tasks),
        'todo': len([t for t in user_tasks if t.status == Task.STATUS_TODO]),
        'doing': len([t for t in user_tasks if t.status == Task.STATUS_DOING]),
        'done': len([t for t in user_tasks if t.status == Task.STATUS_DONE])
    }
    
    return render_template('profile.html', user=user, task_stats=task_stats)

@app.errorhandler(404)
def not_found(error):
    """Gestione errore 404"""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Pagina non trovata"), 404

@app.errorhandler(500)
def internal_error(error):
    """Gestione errore 500"""
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Errore interno del server"), 500

if __name__ == '__main__':
    # Crea la directory templates se non esiste
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Crea la directory static se non esiste
    if not os.path.exists('static'):
        os.makedirs('static')
        os.makedirs('static/css')
        os.makedirs('static/js')
    
    # Avvia l'applicazione Flask
    app.run(debug=True, host='0.0.0.0', port=5000)