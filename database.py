import sqlite3

conn = sqlite3.connect('attendance.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("Database Created Successfully!")