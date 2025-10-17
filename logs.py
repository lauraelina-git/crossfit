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

def list_logs(user_id=None, page=1, per_page=10):
    """Return all logs or logs for a specific user, ordered by date descending."""
    offset = (page - 1) * per_page
    if user_id is None:
        sql = """SELECT id, log_date, log_text, user_id, workout_id
                 FROM logs
                 ORDER BY log_date DESC
                 LIMIT ? OFFSET ?"""
        return db.query(sql, [per_page, offset])

    sql = """SELECT l.id, l.log_date, l.log_text, l.workout_id, w.workout_date
            FROM logs l
            JOIN workouts w ON l.workout_id = w.id
            WHERE l.user_id = ?
            ORDER BY l.log_date DESC
            LIMIT ? OFFSET ?"""
    return db.query(sql, [user_id, per_page, offset])

def count_logs(user_id=None):
    """Return the total number of logs for a specific user or all workouts."""
    if user_id:
        sql = "SELECT COUNT(id) FROM logs WHERE user_id = ?"
        result = db.query(sql, [user_id])
    else:
        sql = "SELECT COUNT(id) FROM logs"
        result = db.query(sql)

    return result[0][0] if result else 0


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

def list_results(workout_id, user_id=None, page=1, per_page=10):
    """List the results of the workout with pagination."""
    offset = (page - 1) * per_page
    sql = """SELECT
                logs.id,
                logs.log_date,
                logs.log_text,
                logs.user_id,
                users.username,
                COUNT(likes.id) AS likes_count
             FROM logs
             LEFT JOIN users ON logs.user_id = users.id
             LEFT JOIN likes ON logs.id = likes.log_id
             WHERE logs.workout_id = ?
             GROUP BY logs.id
             ORDER BY logs.log_date DESC
             LIMIT ? OFFSET ?"""
    results = db.query(sql, [workout_id, per_page, offset])
    results = [dict(r) for r in results]

    if user_id:
        for r in results:
            sql = """SELECT id
                        FROM likes
                        WHERE log_id = ? 
                        AND user_id = ?"""
            liked = db.query(sql, [r["id"], user_id])
            r["user_has_liked"] = bool(liked)
    return results

def count_results(workout_id):
    """Return the total number of results for a specific workout."""
    sql = """
            SELECT COUNT(id) 
            FROM logs 
            WHERE workout_id = ?"""
    result = db.query(sql, [workout_id])
    return result[0][0] if result else 0

def check_likes(log_id, user_id):
    """Check if the user has liked the result"""
    sql = """
            SELECT id
            FROM likes 
            WHERE log_id = ?
            AND user_id = ?"""
    return db.query(sql, [log_id, user_id])

def unlike_log(log_id, user_id):
    """Unlike the result"""
    sql = """
            DELETE FROM likes
            WHERE log_id = ?
            AND user_id = ?"""
    db.execute(sql, [log_id, user_id])


def like_log(log_id, user_id):
    """Like the result"""
    sql = """INSERT INTO likes (log_id, user_id)
             VALUES (?, ?)"""
    db.execute(sql, [log_id, user_id])

def log_summary(user_id):
    """Return total number of logs and date of last training."""
    sql = """SELECT
            COUNT(id) AS wod_count,
            MAX(log_date) AS last_training
            FROM logs
            WHERE user_id = ?"""

    result = db.query(sql, [user_id])[0]
    wod_count = result["wod_count"]
    last_training = result["last_training"]
    return wod_count, last_training
