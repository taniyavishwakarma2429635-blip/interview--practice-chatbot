import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("interviews.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            experience TEXT,
            history TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_interview(role, experience, history):
    conn = sqlite3.connect("interviews.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO interviews (role, experience, history, date) VALUES (?, ?, ?, ?)",
        (role, experience, history, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()

def get_all_interviews():
    conn = sqlite3.connect("interviews.db")
    c = conn.cursor()
    c.execute("SELECT * FROM interviews ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data
