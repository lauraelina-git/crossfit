import db

def add_workout(workout_date, warmup_description, wod_description, extras_description, user_id):
    sql= """INSERT INTO workouts (
                workout_date,
                warmup_description,
                wod_description,
                extras_description,
                user_id
                ) VALUES (?,?,?,?,?)"""
    db.execute(sql,[workout_date, warmup_description, wod_description, extras_description, user_id])

def list_workouts(user_id=None):
    if user_id is None:
        sql = """SELECT id, workout_date, user_id
                 FROM workouts
                 ORDER BY workout_date DESC"""
        return db.query(sql)

    sql = """SELECT id, workout_date, user_id
            FROM workouts
            WHERE user_id = ?
            ORDER BY workout_date DESC"""
    return db.query(sql, [user_id])

def list_workout(workout_id):
    sql = """SELECT workouts.id,
                    workouts.workout_date,
                    workouts.warmup_description,
                    workouts.wod_description,
                    workouts.extras_description,
                    users.username
            FROM workouts, users
            WHERE workouts.user_id=users.id AND
            workouts.id=?"""
    return db.query(sql, [workout_id])[0]