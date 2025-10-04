CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    is_coach INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE workouts (
    id INTEGER PRIMARY KEY,
    workout_date DATE NOT NULL,
    warmup_description TEXT,
    wod_description TEXT,
    extras_description TEXT,
    user_id INTEGER NOT NULL REFERENCES users
);

CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    log_date DATE NOT NULL,
    log_text TEXT,
    user_id INTEGER NOT NULL REFERENCES users,
    workout_id INTEGER NOT NULL REFERENCES workouts
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    workout_id INTEGER NOT NULL REFERENCES workouts,
    user_id INTEGER NOT NULL REFERENCES users,
    comment_text TEXT NOT NULL
);

CREATE TABLE likes (
    id INTEGER PRIMARY KEY, 
    log_id INTEGER NOT NULL REFERENCES logs, 
    user_id INTEGER NOT NULL REFERENCES users
);
