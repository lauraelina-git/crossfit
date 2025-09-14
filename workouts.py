import db
def add_workout(workout_date, warmup_description, wod_description, extras_description, user_id):
    sql= """INSERT INTO workouts (workout_date, warmup_description, wod_description, extras_description, user_id)
            VALUES (?,?,?,?,?)"""
    db.execute(sql, [workout_date, warmup_description, wod_description, extras_description, user_id])
