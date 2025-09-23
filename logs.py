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

def list_log(log_id):
    sql = """SELECT l.id,
                    l.log_date,
                    l.log_text,
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