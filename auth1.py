import streamlit as st
import sqlite3
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError
import home, trending, test, your, about ,temp,livedata
# Function to generate a random OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Function to send OTP via email
def send_otp(email, otp):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'mohammedtousif740@gmail.com'
    smtp_password = 'aqlm gzgg dwts zcqc'  # Use the generated App Password

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    server.login(smtp_username, smtp_password)

    msg = MIMEMultipart()
    msg['From'] = 'mohammedtousif740@gmail.com'
    msg['To'] = email
    msg['Subject'] = 'Your OTP for Signup/Login'

    body = f'Your OTP is: {otp}'
    msg.attach(MIMEText(body, 'plain'))

    server.sendmail(smtp_username, email, msg.as_string())

    server.quit()

# Function to create SQLite database and tables
def create_tables():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create Users table with password column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            otp TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

# Function to add a new user to the database
def add_user(email, password, otp):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO Users (email, password, otp) VALUES (?, ?, ?)', (email, password, otp))

    conn.commit()
    conn.close()

# Function to check if the user is registered
def is_user_registered(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Streamlit app
def main():
    create_tables()  # Create database tables on app startup

    st.title("Login and Signup with OTP")

    # Section selection (Login or Signup)
    section = st.sidebar.radio("Select Section", ('Login', 'Signup'))

    # Common fields for both sections
    email = st.text_input("Enter your email:")
    password = st.text_input("Enter your password:", type="password")
    otp = st.text_input("Enter OTP:")

    if section == 'Signup':
        st.header("Signup")

        # Button to send OTP
        send_otp_button = st.button("Send OTP for Signup")

        if send_otp_button and email and password:
            try:
                # Validate email format
                v = validate_email(email)
                email = v.email

                # Check if the user is already registered
                if is_user_registered(email):
                    st.error("User already registered. Please use Login section.")
                else:
                    # Generate and send OTP
                    otp_signup = generate_otp()
                    send_otp(email, otp_signup)

                    # Save email, password, and OTP in the database
                    add_user(email, password, otp_signup)

                    st.success("OTP sent for signup. Please check your email.")

            except EmailNotValidError as e:
                st.error(f"Invalid email format. Please enter a valid email.")

        # Button to complete signup
        signup_button =  st.button("Complete Signup")
        

        if signup_button and email and password and otp:
            # Your signup logic goes here
            st.success("Signup completed successfully!")
            st.experimental_set_query_params(page=main)

    elif section == 'Login':
        st.header("Login")

        # Button to send OTP
        send_otp_button = st.button("Send OTP for Login")

        if send_otp_button and email and password:
            try:
                # Validate email format
                v = validate_email(email)
                email = v.email

                # Check if the user is registered
                if not is_user_registered(email):
                    st.error("User not found. Please sign up first.")
                else:
                    # Validate password (you may want to use a more secure way, like hashing)
                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM Users WHERE email = ? AND password = ?', (email, password))
                    user = cursor.fetchone()
                    conn.close()

                    if user:
                        # Generate and send OTP
                        otp_login = generate_otp()
                        send_otp(email, otp_login)

                        # Update the OTP in the database
                        conn = sqlite3.connect('users.db')
                        cursor = conn.cursor()
                        cursor.execute('UPDATE Users SET otp = ? WHERE email = ?', (otp_login, email))
                        conn.commit()
                        conn.close()

                        st.success("OTP sent for login. Please check your email.")
                    else:
                        st.error("Invalid password. Please try again.")

            except EmailNotValidError as e:
                st.error(f"Invalid email format. Please enter a valid email.")

        # Button to complete login
        login_button = st.button("Complete Login")

        if login_button and email and password and otp:
            # Your login logic goes here
            st.success("Login completed successfully!")
            

    # Separator
    st.markdown("---")

    # OTP Verification
    if otp:
        # Check if the entered OTP is valid
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = ? AND otp = ?', (email, otp))
        user = cursor.fetchone()
        conn.close()

        if user:
            st.success("OTP verified successfully. You are now logged in.")
            page = st.experimental_get_query_params().get("main.py")
        else:
            st.error("Invalid OTP. Please try again.")

if __name__ == "__main__":
    main()
