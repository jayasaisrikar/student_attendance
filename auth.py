from database import get_db_connection, close_db_connection
from datetime import datetime
import sqlite3
from sqlite3 import IntegrityError

def login(email, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
                        (email, password)).fetchone()
    
    if user:
        user_id = user['id']
        conn.execute("INSERT INTO user_logs (user_id, login_time) VALUES (?, ?)", 
                     (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    
    close_db_connection(conn)
    return user if user else None

def signup(email, password):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)", 
                     (email, password, 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        close_db_connection(conn)

def is_admin(email):
    conn = get_db_connection()
    user = conn.execute("SELECT is_admin FROM users WHERE email = ?", (email,)).fetchone()
    close_db_connection(conn)
    return user and user['is_admin'] == 1

def logout(user_id):
    conn = get_db_connection()
    conn.execute("UPDATE user_logs SET logout_time = ? WHERE user_id = ? AND logout_time IS NULL", 
                 (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    conn.commit()
    close_db_connection(conn)