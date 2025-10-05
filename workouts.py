"""Database operations for workouts"""
import sqlite3
import db

def add_workout(workout_date,
                warmup_description,
                wod_description,
                extras_description,
                user_id,
                programming_week):
    """Insert a new workout into the database."""
    sql = """INSERT INTO workouts (
                workout_date,
                warmup_description,
                wod_description,
                extras_description,
                user_id
                ) VALUES (?,?,?,?,?)"""
    db.execute(sql,[workout_date, warmup_description, wod_description, extras_description, user_id])
    workout_id=db.last_insert_id()

    sql2 = """INSERT INTO programming(
                workout_id,
                programming_week
                ) VALUES (?,?)"""
    db.execute(sql2,[workout_id, programming_week])


def list_workouts(user_id=None):
    """Return all workouts or workouts for a specific user, ordered by date descending."""
    if user_id is None:
        sql = """SELECT id,
                        workout_date,
                        user_id
                 FROM workouts
                 ORDER BY workout_date DESC"""
        return db.query(sql)

    sql = """SELECT id,
                    workout_date,
                    user_id
            FROM workouts
            WHERE user_id = ?
            ORDER BY workout_date DESC"""
    return db.query(sql, [user_id])

def list_workout(workout_id):
    """Return a single workout including its id, date, creator and descriptions."""
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

def edit_workout(
        workout_date,
        warmup_description,
        workout_description,
        extras_description,
        workout_id,
        programming_week
        ):
    """Update an existing workout"""
    sql = """UPDATE workouts
             SET workout_date = ?,
                warmup_description = ?,
                wod_description= ?,
                extras_description = ?
             WHERE id = ?"""
    sql2 = """UPDATE programming
             SET programming_week = ?
             WHERE workout_id = ?"""
    try:
        db.execute(
            sql,
            [workout_date,
             warmup_description,
             workout_description,
             extras_description,
             workout_id]
             )
        db.execute(sql2, [programming_week, workout_id])
        print(f"workout changed, workout ID: {workout_id}")

        return workout_id
    except sqlite3.Error as e:
        print(f"Error updating workout: {e}")
        return None

def find_workouts(query):
    """Find workouts that have the query in their content"""
    sql = """SELECT id, workout_date
             FROM workouts
             WHERE wod_description LIKE ?
             ORDER by workout_date DESC"""

    result=db.query(sql,["%"+query+"%"])
    return result

def add_comment(workout_id, user_id, comment_text):
    """Add a comment to a workout"""
    sql = """INSERT INTO comments (
                workout_id,
                user_id,
                comment_text
                )
             VALUES (?, ?, ?)"""
    return db.execute(sql, [workout_id, user_id, comment_text])

def list_comments(workout_id):
    """List the comments for the workout given by users"""
    sql = """SELECT c.id,
                    c.comment_text,
                    u.username
             FROM comments c
             JOIN users u ON c.user_id = u.id
             WHERE c.workout_id = ?"""
    return db.query(sql, [workout_id])

def get_programming(workout_id):
    """Return the programming week"""
    sql = """SELECT programming_week
            FROM programming 
            WHERE workout_id = ?"""
    result = db.query(sql, [workout_id])
    return result[0] if result else None
