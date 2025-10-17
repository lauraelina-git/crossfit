"""Database operations for workouts"""
import sqlite3
import db

def add_workout(workout_date,
                warmup_description,
                wod_description,
                extras_description,
                user_id,
                programming_week,
                workout_image):
    """Insert a new workout into the database."""
    sql = """INSERT INTO workouts (
                workout_date,
                warmup_description,
                wod_description,
                extras_description,
                user_id,
                workout_image
                ) VALUES (?,?,?,?,?,?)"""
    print(f"Workout image filename before saving: {workout_image}")
    db.execute(
        sql,
        [workout_date,
        warmup_description,
        wod_description,
        extras_description,
        user_id,
        workout_image
        ])
    workout_id=db.last_insert_id()

    sql2 = """INSERT INTO programming(
                workout_id,
                programming_week
                ) VALUES (?,?)"""
    db.execute(sql2,[workout_id, programming_week])


def list_workouts(page=1, per_page=10, user_id=None):
    """Return workouts with pagination"""
    offset = (page - 1) * per_page
    if user_id is None:
        sql = """SELECT id, workout_date, user_id
                 FROM workouts
                 ORDER BY workout_date DESC
                 LIMIT ? OFFSET ?"""
        result=db.query(sql, [per_page, offset])

    else:
        sql = """SELECT id, workout_date,user_id
            FROM workouts
            WHERE user_id = ?
            ORDER BY workout_date DESC
            LIMIT ? OFFSET ?"""
        result=db.query(sql, [user_id, per_page, offset])
    return result

def count_workouts(user_id=None):
    """Return the total number of workouts for a specific user or all workouts."""
    if user_id:
        sql = "SELECT COUNT(id) FROM workouts WHERE user_id = ?"
        result = db.query(sql, [user_id])
    else:
        sql = "SELECT COUNT(id) FROM workouts"
        result = db.query(sql)

    return result[0][0] if result else 0

def list_workout(workout_id):
    """Return a single workout including its id, date, creator, descriptions and image."""
    sql = """SELECT workouts.id,
                    workouts.workout_date,
                    workouts.warmup_description,
                    workouts.wod_description,
                    workouts.extras_description,
                    users.username,
                    workouts.workout_image
            FROM workouts, users
            WHERE workouts.user_id=users.id AND
            workouts.id=?"""
    return db.query(sql, [workout_id])[0]

def edit_workout(
        workout_date,
        warmup_description,
        workout_description,
        extras_description,
        workout_image,
        workout_id,
        programming_week
        ):
    """Update an existing workout"""
    sql = """UPDATE workouts
             SET workout_date = ?,
                warmup_description = ?,
                wod_description= ?,
                extras_description = ?,
                workout_image = ?
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
             workout_image,
             workout_id]
             )
        db.execute(sql2, [programming_week, workout_id])
        print(f"workout changed, workout ID: {workout_id}")

        return workout_id
    except sqlite3.Error as e:
        print(f"Error updating workout: {e}")
        return None

def find_workouts(query, page=1, per_page=10):
    """Find workouts that have the query in their content with pagination."""
    offset = (page - 1) * per_page
    sql = """SELECT id, workout_date
             FROM workouts
             WHERE wod_description LIKE ?
             ORDER by workout_date DESC
             LIMIT ? OFFSET ?"""

    result = db.query(sql, ["%" + query + "%", per_page, offset])
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

def list_comments(workout_id, page=1, per_page=10):
    """List the comments for the workout given by users, limited to the last 10."""
    offset = (page - 1) * per_page
    sql = """SELECT c.id, c.comment_text, u.username
             FROM comments c
             JOIN users u ON c.user_id = u.id
             WHERE c.workout_id = ?
             ORDER BY c.id DESC  -- Järjestä kommentit uusimmasta vanhimpaan
             LIMIT ? OFFSET ?"""
    return db.query(sql, [workout_id, per_page, offset])

def get_programming(workout_id):
    """Return the programming week"""
    sql = """SELECT programming_week
            FROM programming 
            WHERE workout_id = ?"""
    result = db.query(sql, [workout_id])
    return result[0] if result else None
