import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / 'students.db'


def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()


def add_user(username, password):
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            'INSERT OR IGNORE INTO students (username, password) VALUES (?, ?)',
            (username, password),
        )
        conn.commit()


def validate_user(username, password):
    with sqlite3.connect(DATABASE_PATH) as conn:
        user = conn.execute(
            'SELECT id, username FROM students WHERE username = ? AND password = ?',
            (username, password),
        ).fetchone()
    return user is not None


if __name__ == '__main__':
    init_db()
    add_user('balaji', '123456')
    print('Login successful' if validate_user('balaji', '123456') else 'Invalid username or password')
