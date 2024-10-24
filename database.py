import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, is_admin INTEGER)''')
    
    # c.execute('''CREATE TABLE IF NOT EXISTS timetable
    #              (id INTEGER PRIMARY KEY, subject TEXT, start_time TEXT, end_time TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY, user_id INTEGER, subject_id INTEGER, date TEXT, 
                  status TEXT, timestamp TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_logs
                 (id INTEGER PRIMARY KEY, user_id INTEGER, login_time TEXT, logout_time TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS timetable
                 (id INTEGER PRIMARY KEY, subject TEXT, start_time TEXT, end_time TEXT, class_year TEXT, day_of_week TEXT)''')

    # Create admin user if not exists
    c.execute("SELECT * FROM users WHERE email=?", ("admin@app.com",))
    if c.fetchone() is None:
        c.execute("INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)", 
                  ("admin@app.com", "1234", 1))
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

def close_db_connection(conn):
    conn.close()

# Add more database operations here (e.g., insert_user, get_user, update_attendance, etc.)