CREATE TABLE IF NOT EXISTS habits (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS completions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id       INTEGER NOT NULL,
    completed_date TEXT NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits(id),
    UNIQUE (habit_id, completed_date)
);
