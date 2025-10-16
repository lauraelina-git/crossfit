CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    is_coach INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY,
    workout_date DATE NOT NULL,
    warmup_description TEXT,
    wod_description TEXT,
    extras_description TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workout_image TEXT
);

CREATE INDEX IF NOT EXISTS idx_workout_date ON workouts (workout_date);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY,
    log_date DATE NOT NULL,
    log_text TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workout_id INTEGER NOT NULL REFERENCES workouts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_log_date ON logs (log_date);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY,
    workout_id INTEGER NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    comment_text TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_workout_id ON comments (workout_id);

CREATE TABLE IF NOT EXISTS likes (
    id INTEGER PRIMARY KEY, 
    log_id INTEGER NOT NULL REFERENCES logs(id) ON DELETE CASCADE, 
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS programming (
    id INTEGER PRIMARY KEY,
    workout_id INTEGER NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    programming_week TEXT
);