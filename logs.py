import db

def add_log(log_date, log_text, user_id, workout_id):
    sql = """INSERT INTO logs (log_date, log_text, user_id, workout_id)
             VALUES (?, ?, ?, ?)"""
    try:
        db.execute(sql, [log_date, log_text, user_id, workout_id])
        last_id = db.last_insert_id()
        print(f"Log added with ID: {last_id}")
        return last_id
    except Exception as e:
        print(f"Error adding log: {e}")
        return None

def list_logs(user_id=None):
    if user_id is None:
        sql = """SELECT id, log_date, log_text, user_id, workout_id
                 FROM logs
                 ORDER BY log_date DESC"""
        return db.query(sql)

    sql = """SELECT id, log_date, log_text, user_id, workout_id
             FROM logs
             WHERE user_id = ?
             ORDER BY log_date DESC"""
    return db.query(sql, [user_id])
