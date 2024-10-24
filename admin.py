import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from database import get_db_connection, close_db_connection
from datetime import datetime, time
import pytz

conn = sqlite3.connect('attendance.db')
ist = pytz.timezone('Asia/Kolkata')

def admin_interface():
    st.title("Admin Interface")
    
    menu = st.sidebar.selectbox("Admin Menu", ["Timetable", "User Management", "Attendance Analysis", "User Logs"])
    
    if menu == "Timetable":
        st.header('Add Timetable')
        add_timetable()  # Updated to include the day_of_week column
        st.header('Timetable Management')
        manage_timetable()  # Manages timetable and displays data
    elif menu == "User Management":
        manage_users()
    elif menu == "Attendance Analysis":
        attendance_analysis()
    elif menu == "User Logs":
        user_logs()
    

def manage_timetable():
    st.subheader("Manage Timetable")
    
    conn = get_db_connection()

    # Fetch timetable data
    timetable = pd.read_sql_query("SELECT * FROM timetable", conn)
    st.dataframe(timetable)
    
    # Select timetable entry by ID to update or delete
    timetable_id = st.selectbox("Select Timetable ID to Modify", timetable['id'].values)
    
    # Get the selected timetable row
    selected_timetable = timetable[timetable['id'] == timetable_id].iloc[0]
    
    # Get current time in IST
    current_time_ist = datetime.now(ist)
    formatted_time_ist = current_time_ist.strftime("%H:%M:%S")
    st.write(f"**Current Time (IST)**: {formatted_time_ist}")
    
    st.write(f"**Current Subject**: {selected_timetable['subject']}")
    st.write(f"**Current Start Time**: {selected_timetable['start_time']}")
    st.write(f"**Current End Time**: {selected_timetable['end_time']}")
    st.write(f"**Current Day of Week**: {selected_timetable['day_of_week']}")
    st.write(f"**Current Class Year**: {selected_timetable['class_year']}")
    
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    class_years = ['I BTech', 'II BTech', 'III BTech', 'IV BTech', 'I MCA', 'II MCA', 'I MTech', 'II MTech']

    current_day_of_week = selected_timetable['day_of_week'] if selected_timetable['day_of_week'] in days_of_week else days_of_week[0]
    current_class_year = selected_timetable['class_year'] if selected_timetable['class_year'] in class_years else class_years[0]
    
    with st.form("update_timetable"):
        new_subject = st.text_input("Update Subject", selected_timetable['subject'])
        new_start_time = st.time_input("Update Start Time", pd.to_datetime(selected_timetable['start_time']).time())
        new_end_time = st.time_input("Update End Time", pd.to_datetime(selected_timetable['end_time']).time())
        new_day_of_week = st.selectbox("Update Day of Week", days_of_week, index=days_of_week.index(current_day_of_week))
        new_class_year = st.selectbox("Update Class Year", class_years, index=class_years.index(current_class_year))
        
        # Convert new times to IST timezone
        new_start_time_ist = datetime.combine(datetime.today(), new_start_time).astimezone(ist).time()
        new_end_time_ist = datetime.combine(datetime.today(), new_end_time).astimezone(ist).time()
        
        if st.form_submit_button("Update Timetable"):
            conn.execute("""
                UPDATE timetable 
                SET subject = ?, start_time = ?, end_time = ?, class_year = ?, day_of_week = ? 
                WHERE id = ?
            """, (new_subject, new_start_time_ist.strftime("%H:%M"), new_end_time_ist.strftime("%H:%M"), new_class_year, new_day_of_week, timetable_id))
            conn.commit()
            st.success("Timetable updated successfully")
            st.rerun()
    
    if st.button("Delete Timetable Entry"):
        try:
            conn.execute("DELETE FROM timetable WHERE id = ?", (timetable_id,))
            conn.commit()
            st.success("Timetable entry deleted successfully")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting timetable entry: {e}")
    
    close_db_connection(conn)


def manage_users():
    st.subheader("User Management")
    
    conn = get_db_connection()
    users = pd.read_sql_query("SELECT id, email, is_admin FROM users", conn)
    
    st.dataframe(users)
    
    user_id = st.number_input("User ID", min_value=1, step=1)
    action = st.selectbox("Action", ["Delete User", "Toggle Admin Status"])
    
    if st.button("Perform Action"):
        if action == "Delete User":
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        elif action == "Toggle Admin Status":
            conn.execute("UPDATE users SET is_admin = 1 - is_admin WHERE id = ?", (user_id,))
        conn.commit()
        st.success(f"Action '{action}' performed successfully")
        st.rerun()
    
    close_db_connection(conn)

def attendance_analysis():
    st.subheader("Attendance Analysis")
    
    conn = get_db_connection()
    attendance = pd.read_sql_query("""
        SELECT u.email, t.subject, a.date, a.status
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        JOIN timetable t ON a.subject_id = t.id
    """, conn)
    
    subjects = attendance['subject'].unique()
    selected_subject = st.selectbox("Select Subject", subjects)
    
    filtered_attendance = attendance[attendance['subject'] == selected_subject]
    
    fig = px.bar(filtered_attendance, x='email', color='status', title=f"Attendance for {selected_subject}")
    st.plotly_chart(fig)
    
    st.dataframe(filtered_attendance)
    
    close_db_connection(conn)

def user_logs():
    st.subheader("User Logs")
    
    conn = get_db_connection()
    logs = pd.read_sql_query("""
        SELECT u.email, l.login_time, l.logout_time
        FROM user_logs l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.login_time DESC
    """, conn)
    
    st.dataframe(logs)

def add_timetable():
    class_year = st.selectbox(
        'Select Class Year', 
        ['I BTech', 'II BTech', 'III BTech', 'IV BTech', 'I MCA', 'II MCA', 'I MTech', 'II MTech']
    )

    day_of_week = st.selectbox(
        "Select Day of Week", 
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    )
    
    subject = st.text_input('Subject')
    
    # Input time directly without timezone conversion
    start_time = st.time_input("Start Time", time(0, 0))  # Default to 00:00 (midnight)
    end_time = st.time_input("End Time", time(0, 0))
    
    # No need for additional timezone conversion, just store the time directly
    if st.button('Add Timetable'):
        conn = get_db_connection()
        conn.execute("INSERT INTO timetable (subject, start_time, end_time, class_year, day_of_week) VALUES (?, ?, ?, ?, ?)", 
                     (subject, start_time.strftime("%H:%M"), end_time.strftime("%H:%M"), class_year, day_of_week))
        conn.commit()
        st.success(f'Timetable added for {class_year} on {day_of_week}')
        close_db_connection(conn)

