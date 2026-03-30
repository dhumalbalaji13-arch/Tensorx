import sqlite3

conn = sqlite3.connect("students.db")
c = conn.cursor()


c.execute("""
CREATE TABLE IF NOT EXISTS students (
    username TEXT,
    password TEXT
)
""")

c.execute("INSERT INTO students (username, password) VALUES (?, ?)", ("balaji", "123"))


conn.commit()

c.execute("SELECT * FROM students")
print(c.fetchall())


username = "balaji"
password = "123"

c.execute("SELECT * FROM students WHERE username=? AND password=?", (username, password))

if user := c.fetchone():
    print("Login successful")
else:
    print("Invalid username or password")


conn.close()