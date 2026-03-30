from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os

app = Flask(__name__, template_folder='template', static_folder='static')
app.secret_key = 'dev-secret-key'  # for flash messages

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# Initialize database before starting the server
def initialize():
    init_db()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please enter both username and password', 'error')
            return redirect(url_for('login'))

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM students WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful', 'success')
            return redirect(url_for('index'))

        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not username or not password:
            flash('Please enter both username and password', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('register'))

        conn = get_db_connection()
        c = conn.cursor()

        try:
            c.execute('INSERT INTO students (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists, choose another.', 'error')
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('registration.html')


@app.route('/contact', methods=['POST'])
def contact():
    """Handle contact form submissions"""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    if not name or not email or not message:
        flash('Please fill in all fields', 'error')
        return redirect(url_for('index') + '#contact')

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)', 
            (name, email, message))
        conn.commit()
        conn.close()
        flash('Thank you! Your message has been sent.', 'success')
    except Exception as e:
        flash('Error sending message. Please try again.', 'error')
    
    return redirect(url_for('index') + '#contact')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


@app.route('/main')
def mainweb():
    return render_template('index.html')


if __name__ == '__main__':
    initialize()
    app.run(debug=True)
