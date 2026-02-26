#!/usr/bin/env python3
"""Simple DB initialization for CCAP Claims Training Game.

Creates tables:
- users (id, username, password_hash, score)
- scenarios (id, claim_type, difficulty, scenario_json, correct_answer)
- attempts (id, user_id, scenario_id, user_answer, is_correct, feedback_text, points_earned, timestamp)

Run this script to create `data.db` in the backend folder.
"""

import os
import sqlite3
import hashlib

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'data.db')


def create_tables(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        score INTEGER DEFAULT 0,
        current_streak INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_type TEXT,
        difficulty TEXT,
        scenario_json TEXT,
        correct_answer TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        scenario_id INTEGER,
        user_answer TEXT,
        is_correct INTEGER,
        feedback_text TEXT,
        points_earned INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        achievement_key TEXT,
        unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, achievement_key)
    )
    """)
    
    # Add xp and level columns if they don't exist (migration)
    try:
        cur.execute('ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass
    
    try:
        cur.execute('ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1')
    except sqlite3.OperationalError:
        pass
    
    # Create admin account
    admin_hash = hashlib.sha256('Password'.encode()).hexdigest()
    cur.execute('INSERT OR IGNORE INTO users (username, password_hash, score, current_streak) VALUES (?, ?, ?, ?)',
                ('Admin1', admin_hash, 0, 0))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_tables()
    print(f'Initialized SQLite database at: {DB_PATH}')
