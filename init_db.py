import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite')

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        fullname TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        room TEXT NOT NULL,
        date_start TEXT NOT NULL,
        payment TEXT NOT NULL,
        status TEXT DEFAULT 'Новая',
        review TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

conn.commit()
conn.close()
print("База данных создана:", DB_PATH)