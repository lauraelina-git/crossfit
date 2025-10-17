"""Module to create test database"""
import sqlite3
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import db
from app import app

def create_users(num_users):
    """Create test users."""
    for i in range(num_users):
        username = f"user{i}"
        password_hash = generate_password_hash("Password123!")
        is_coach = random.choice([0, 1])
        try:
            sql = "INSERT INTO users (username, password_hash, is_coach) VALUES (?, ?, ?)"
            db.execute(sql, [username, password_hash, is_coach])
        except sqlite3.IntegrityError:
            pass

def create_workouts(num_workouts):
    """Create test workouts."""
    users = db.query("SELECT id FROM users")
    programming_weeks = ['1', '2', '3', 'deload']
    for i in range(num_workouts):
        user_id = random.choice(users)["id"]
        workout_date = datetime.now() - timedelta(days=random.randint(0, 30))
        warmup_description = f"Warmup for workout {i}"
        wod_description = f"Do {random.randint(5, 20)} reps of everything!"
        extras_description = "Extra work: core and mobility."
        programming_week = random.choice(programming_weeks)

        sql = """INSERT INTO workouts (
                    workout_date,
                    warmup_description,
                    wod_description,
                    extras_description,
                    user_id
                 ) VALUES (?, ?, ?, ?, ?)"""
        db.execute(
            sql,
            [
                workout_date.date(),
                warmup_description,
                wod_description,
                extras_description,
                user_id
            ]
        )
        workout_id = db.last_insert_id()

        sql_programming = """INSERT INTO programming (
                                workout_id,
                                programming_week
                             ) VALUES (?, ?)"""
        db.execute(sql_programming, [workout_id, programming_week])

def create_logs(num_logs):
    """Create test logs."""
    users = db.query("SELECT id FROM users")
    workouts = db.query("SELECT id FROM workouts")
    for i in range(num_logs):
        user_id = random.choice(users)["id"]
        workout_id = random.choice(workouts)["id"]
        log_date = datetime.now() - timedelta(days=random.randint(0, 30))
        log_text = f"This is log entry {i} for workout {workout_id}."

        sql = """INSERT INTO logs (
                    log_date,
                    log_text,
                    user_id,
                    workout_id
                 ) VALUES (?, ?, ?, ?)"""
        db.execute(sql, [log_date.date(), log_text, user_id, workout_id])

def main():
    """Seed the database with test data."""
    with app.app_context():
        db.initialize_db()
        create_users(1000)
        create_workouts(2000)
        create_logs(5000)

if __name__ == "__main__":
    main()
