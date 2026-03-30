import sqlite3

conn = sqlite3.connect("contact .db")
c = conn .cursor()


c .execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    message TEXT
)
""")


def save_contact(name, email, message):
    c.execute(
        "INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )
    conn .commit()
    print("Data saved successfully ")


save_contact("Balaji", "dhumalbalaji13@gmail.com", "Hello ")

c .execute("SELECT * FROM contacts")
print(c .fetchall ())


conn .close()    