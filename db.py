"""Database handling"""
import sqlite3
from flask import g

def get_connection():
    con = sqlite3.connect("database.db", timeout=5)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=None):
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
    return g.last_insert_id

def query(sql, params=[]):
    """Execute the read operation"""
    con = get_connection()
    try:
        result = con.execute(sql, params).fetchall()
        return result
    finally:
        con.close()