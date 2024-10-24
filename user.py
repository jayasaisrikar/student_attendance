import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import get_db_connection, close_db_connection

def user_interface(user_id):
    st.title("User Interface")
    
    # Get the current day of the week (Monday = 0, Sunday = 6)
    today = datetime.now().strftime("%A")  # Returns 'Monday', 'Tuesday', etc.
    
    conn = get_db_connection()
    
    # Ask the user to select their class year
    class_year = st.selectbox("Select Your Class Year", 
                              ['I BTech', 'II BTech', 'III BTech', 'IV BTech', 'I MCA', 'II MCA', 'I MTech', 'II MTech'])
    
    # Fetch today's timetable for the selected class year
    timetable = pd.read_sql_query('''SELECT * FROM timetable WHERE class_year = ? AND day_of_week = ?''', 
                                  conn, params=(class_year, today))
    
    st.subheader(f"Today's Timetable for {class_year}")
    st.dataframe(timetable)
    
    st.subheader("Mark Attendance")
    
    for _, subject in timetable.iterrows():
        subject_id = subject['id']
        subject_name = subject['subject']
        start_time = datetime.strptime(subject['start_time'], "%H:%M").time()
        end_time = datetime.strptime(subject['end_time'], "%H:%M").time()
        
        now = datetime.now().time()
        
        if start_time <= now <= end_time:
            attendance = conn.execute('''SELECT * FROM attendance 
                                         WHERE user_id = ? AND subject_id = ? AND date = ?''', 
                                      (user_id, subject_id, today)).fetchone()
            
            if attendance:
                st.info(f"Attendance for {subject_name} already marked as {attendance['status']}")
            else:
                if st.button(f"Mark Attendance for {subject_name}"):
                    conn.execute('''INSERT INTO attendance (user_id, subject_id, date, status, timestamp)
                                    VALUES (?, ?, ?, ?, ?)''', 
                                 (user_id, subject_id, today, "Present", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success(f"Attendance marked for {subject_name}")
        elif now < start_time:
            st.info(f"Attendance for {subject_name} will be available at {start_time}")
        else:
            st.warning(f"Attendance for {subject_name} is closed")
    
    st.subheader("Your Attendance History")
    history = pd.read_sql_query('''SELECT t.subject, a.date, a.status
                                   FROM attendance a
                                   JOIN timetable t ON a.subject_id = t.id
                                   WHERE a.user_id = ?
                                   ORDER BY a.date DESC, t.start_time DESC''', 
                                conn, params=(user_id,))
    
    st.dataframe(history)
    
    close_db_connection(conn)

