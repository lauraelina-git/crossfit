"""Database handling"""
import sqlite3
from flask import g

def get_connection():
    """Open a new database connection with foreign keys enabled."""
    con = sqlite3.connect("database.db", timeout=5)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def initialize_db():
    """Initialize the database using the schema.sql file."""
    with open('schema.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()

    con = get_connection()
    cursor = con.cursor()

    cursor.executescript(sql_script)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_workout_date ON workouts (workout_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_date ON logs (log_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_workout_id ON comments (workout_id)")

    con.commit()
    con.close()

def execute(sql, params=None):
    """Execute a write operation (INSERT, UPDATE, DELETE)."""
    if params is None:
        params = []
    con = get_connection()
    try:
        result = con.execute(sql, params)
        con.commit()
        g.last_insert_id = result.lastrowid
        return result
    finally:
        con.close()

def last_insert_id():
    """Return the last inserted row ID from the previous execute()."""
    return g.last_insert_id

def query(sql, params=None):
    """Execute a read operation (SELECT) and return all results."""
    if params is None:
        params = []
    con = get_connection()
    try:
        result = con.execute(sql, params).fetchall()
        return result
    finally:
        con.close()
