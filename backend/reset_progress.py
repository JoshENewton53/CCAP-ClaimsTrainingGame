#!/usr/bin/env python3
"""Reset all user progress in the database."""

import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'data.db')

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute('UPDATE users SET score = 0, current_streak = 0, xp = 0, level = 1')
cur.execute('DELETE FROM achievements')
cur.execute('DELETE FROM attempts')

conn.commit()
conn.close()

print('All user progress has been reset.')
