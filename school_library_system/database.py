import sqlite3
import os
from datetime import datetime, date

DB_NAME = os.path.join(os.path.dirname(__file__), 'library.db')

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    if not os.path.exists(DB_NAME):
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            script = f.read()
        conn = get_db()
        conn.executescript(script)
        conn.commit()
        conn.close()

def refresh_overdue_status():
    today = date.today().isoformat()
    conn = get_db()
    # Any borrowing without return_date where due_date < today is overdue
    conn.execute("""
        UPDATE borrowings
        SET status = 'overdue'
        WHERE return_date IS NULL AND due_date < ?
    """, (today,))
    # Any borrowing without return_date where due_date >= today is active
    conn.execute("""
        UPDATE borrowings
        SET status = 'active'
        WHERE return_date IS NULL AND due_date >= ?
    """, (today,))
    conn.commit()
    conn.close()
