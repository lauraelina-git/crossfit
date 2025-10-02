"""Database operations for log handling"""
import sqlite3
import db

def add_log(log_date, log_text, user_id, workout_id):
    """Insert a new log entry into the database and return its ID."""
    sql = """INSERT INTO logs (
                log_date,
                log_text,
                user_id,
                workout_id)
             VALUES (?, ?, ?, ?)"""
    try:
        db.execute(sql, [log_date, log_text, user_id, workout_id])
        last_id = db.last_insert_id()
        print(f"Log added with ID: {last_id}")
        return last_id
    except sqlite3.Error as e:
        print(f"Error adding log: {e}")
        return None

def list_logs(user_id=None):
    """Return all logs or logs for a specific user, ordered by date descending."""
    if user_id is None:
        sql = """SELECT id,
                        log_date,
                        log_text,
                        user_id,
                        workout_id
                 FROM logs
                 ORDER BY log_date DESC"""
        return db.query(sql)

    sql = """SELECT l.id,
                    l.log_date,
                    l.log_text,
                    l.workout_id,
                    w.workout_date
            FROM logs l
            JOIN workouts w ON l.workout_id = w.id
            WHERE l.user_id = ?
            ORDER BY l.log_date DESC
            """
    return db.query(sql, [user_id])

def list_log(log_id):
    """Return a single log entry by ID, including workout and user details."""
    sql = """SELECT l.id,
                    l.log_date,
                    l.log_text,
                    l.user_id,
                    u.username,
                    w.workout_date,
                    w.warmup_description,
                    w.wod_description,
                    w.extras_description,
                    w.id
            FROM logs l
            JOIN users u ON l.user_id = u.id
            JOIN workouts w ON l.workout_id=w.id
            WHERE l.id=?"""
    return db.query(sql, [log_id])[0]

def update_log(log_id, log_date, log_text, user_id):
    """Update an existing log entry if it belongs to the given user."""
    sql = """UPDATE logs
            SET log_date = ?,
                log_text = ?
            WHERE id = ?
            AND user_id = ?"""
    try:
        db.execute(sql, [log_date, log_text, log_id, user_id])
        print(f"Log changed, log ID: {log_id}")
        return log_id
    except sqlite3.Error as e:
        print(f"Error updating log: {e}")
        return None

def remove_log(log_id, user_id):
    """Remove an existing log entry if it belongs to the given user."""
    sql = """DELETE FROM logs
            WHERE id = ?
            AND user_id = ?"""
    try:
        result=db.execute(sql, [log_id, user_id])
        if result.rowcount==0:
            return False
        print("Log removed")
        return True
    except sqlite3.Error as e:
        print(f"Error deleting log: {e}")
        return False
