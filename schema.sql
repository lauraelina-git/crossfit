CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE workouts (
    id INTEGER PRIMARY KEY,
    workout_date DATE,
    warmup_description TEXT,
    wod_description TEXT,
    extras_description TEXT,
    user_id INTEGER REFERENCES users
);