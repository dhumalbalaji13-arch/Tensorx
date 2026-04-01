import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / 'contact .db'


def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL
            )
        ''')
        conn.commit()


def save_contact(name, email, message):
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            'INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)',
            (name, email, message),
        )
        conn.commit()
    print('Data saved successfully')


def list_contacts():
    with sqlite3.connect(DATABASE_PATH) as conn:
        return conn.execute('SELECT * FROM contacts ORDER BY id DESC').fetchall()


if __name__ == '__main__':
    init_db()
    save_contact('Balaji', 'dhumalbalaji13@gmail.com', 'Hello')
    print(list_contacts())
