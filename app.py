from flask import Flask, flash, redirect, render_template, request, session, url_for
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / 'students.db'

app = Flask(
    __name__,
    template_folder=str(BASE_DIR),
    static_folder=str(BASE_DIR),
    static_url_path='',
)
app.secret_key = 'dev-secret-key'


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    current_columns = [
        row['name'] for row in cursor.execute("PRAGMA table_info(students)").fetchall()
    ]
    required_columns = {'id', 'full_name', 'username', 'email', 'phone', 'password'}

    if not current_columns:
        cursor.execute('''
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name
                TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
    elif not required_columns.issubset(set(current_columns)):
        rows = cursor.execute('SELECT * FROM students').fetchall()
        existing_users = []

        for row in rows:
            data = dict(row)
            username = str(data.get('username', '') or '').strip()
            password = str(data.get('password', '') or '').strip()

            if username and password:
                existing_users.append((
                    str(data.get('full_name', username) or username).strip(),
                    username,
                    str(data.get('email', f'{username}@example.com') or f'{username}@example.com').strip(),
                    str(data.get('phone', 'Not provided') or 'Not provided').strip(),
                    password,
                ))

        cursor.execute('ALTER TABLE students RENAME TO students_old')
        cursor.execute('''
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.executemany(
            'INSERT OR IGNORE INTO students (full_name, username, email, phone, password) VALUES (?, ?, ?, ?, ?)',
            existing_users,
        )
        cursor.execute('DROP TABLE IF EXISTS students_old')

    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_students_username ON students(username)')
    conn.commit()
    conn.close()


init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        flash('Please enter both username and password.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute(
        'SELECT id, username, full_name FROM students WHERE username = ? AND password = ?',
        (username, password),
    ).fetchone()
    conn.close()

    if user:
        display_name = user['full_name'] or user['username']
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['display_name'] = display_name
        flash(f"Welcome back, {display_name}!", 'success')
        return redirect(url_for('subjects'))

    flash('Invalid username or password.', 'error')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method != 'POST':
        return render_template('registration.html')

    full_name = request.form.get('full_name', '').strip()
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()

    if not all([full_name, username, email, phone, password, confirm_password]):
        flash('Please complete all required fields.', 'error')
        return redirect(url_for('register'))

    if '@' not in email or '.' not in email.split('@')[-1]:
        flash('Please enter a valid email address.', 'error')
        return redirect(url_for('register'))

    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('register'))

    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        return redirect(url_for('register'))

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO students (full_name, username, email, phone, password) VALUES (?, ?, ?, ?, ?)',
            (full_name, username, email, phone, password),
        )
        conn.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    except sqlite3.IntegrityError:
        flash('Username already exists. Try another one.', 'error')
        return redirect(url_for('register'))
    finally:
        conn.close()


@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    if not name or not email or not message:
        flash('Please fill in all contact fields.', 'error')
        return redirect(url_for('index') + '#contact')

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)',
            (name, email, message),
        )
        conn.commit()
        flash('Thank you! Your message has been sent.', 'success')
    except sqlite3.Error:
        flash('Error sending message. Please try again.', 'error')
    finally:
        conn.close()

    return redirect(url_for('index') + '#contact')


def require_login():
    if 'user_id' not in session:
        flash('Please log in to access the subject pages.', 'error')
        return False
    return True


@app.route('/subjects')
def subjects():
    if not require_login():
        return redirect(url_for('login'))
    return render_template('subject.html')


@app.route('/subjects/chemistry')
def chemistry():
    if not require_login():
        return redirect(url_for('login'))
    return render_template('subjectC.html')


@app.route('/subjects/mathematics')
def mathematics():
    if not require_login():
        return redirect(url_for('login'))
    return render_template('subjectM.html')


@app.route('/subjects/fpl')
def fpl():
    if not require_login():
        return redirect(url_for('login'))
    return render_template('subjectF.html')


@app.route('/main')
def mainweb():
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

