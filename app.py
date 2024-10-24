import streamlit as st
from database import init_db
from auth import login, signup, is_admin, logout
from admin import admin_interface
from user import user_interface

def main():
    init_db()
    st.title("Student Attendance Tracker")

    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        choice = st.sidebar.selectbox("Login/Signup", ["Login", "Signup"])
        
        if choice == "Login":
            email = st.sidebar.text_input("Email")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                user = login(email, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.sidebar.error("Invalid email or password")
        else:
            email = st.sidebar.text_input("Email")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Signup"):
                if signup(email, password):
                    st.sidebar.success("Account created. Please login.")
                else:
                    st.sidebar.error("Email already exists")
    else:
        st.sidebar.write(f"Welcome, {st.session_state.user['email']}")
        if st.sidebar.button("Logout"):
            logout(st.session_state.user['id'])  # Call the logout function
            st.session_state.user = None
            st.rerun()
        
        if is_admin(st.session_state.user['email']):
            admin_interface()
        else:
            user_interface(st.session_state.user['id'])

if __name__ == "__main__":
    main()