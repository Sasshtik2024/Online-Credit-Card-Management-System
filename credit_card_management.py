import streamlit as st
import sqlite3
from hashlib import sha256
import pandas as pd

# Database setup
def init_db():
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY, 
                    username TEXT UNIQUE, 
                    password TEXT,
                    email TEXT, 
                    phone TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS credit_cards (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    card_number TEXT UNIQUE NOT NULL,
                    expiry_date TEXT NOT NULL,
                    credit_score INTEGER,
                    credit_limit REAL,
                    current_balance REAL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    card_number TEXT,
                    amount REAL,
                    transaction_date TEXT,
                    description TEXT,
                    FOREIGN KEY(card_number) REFERENCES credit_cards(card_number))''')
    conn.commit()
    conn.close()

# User Authentication
def register_user(username, password, email, phone):
    try:
        conn = sqlite3.connect('credit_card_system.db')
        c = conn.cursor()
        hashed_password = sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)", 
                  (username, hashed_password, email, phone))
        conn.commit()
        conn.close()
        return "Registration successful."
    except sqlite3.IntegrityError:
        return "Username already exists."

def login_user(username, password):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user

# Credit Card Management
def add_credit_card(user_id, card_number, expiry_date, credit_score, credit_limit):
    try:
        conn = sqlite3.connect('credit_card_system.db')
        c = conn.cursor()
        c.execute("""INSERT INTO credit_cards 
                     (user_id, card_number, expiry_date, credit_score, credit_limit) 
                     VALUES (?, ?, ?, ?, ?)""", 
                  (user_id, card_number, expiry_date, credit_score, credit_limit))
        conn.commit()
        conn.close()
        return "Card added successfully."
    except sqlite3.IntegrityError:
        return "Card number already exists or invalid input."

def get_credit_cards(user_id):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("SELECT id, card_number, expiry_date, credit_score, credit_limit, current_balance FROM credit_cards WHERE user_id = ?", 
              (user_id,))
    cards = c.fetchall()
    conn.close()
    return cards

# Streamlit App
def main():
    st.title("Online Credit Card Management System")
    menu = ["Login", "Register", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user[0]
                st.session_state["username"] = user[1]
                st.success(f"Welcome {st.session_state['username']}!")
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "Register":
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        if st.button("Register"):
            result = register_user(new_user, new_password, email, phone)
            st.success(result)

    elif choice == "Dashboard" and st.session_state["logged_in"]:
        st.subheader(f"Welcome to your Dashboard, {st.session_state['username']}!")
        dashboard_menu = ["Credit Card Management"]
        selected_function = st.sidebar.selectbox("Dashboard Menu", dashboard_menu)

        if selected_function == "Credit Card Management":
            st.write("### Add New Credit Card")
            card_number = st.text_input("Card Number")
            expiry_date = st.text_input("Expiry Date (MM/YY)")
            credit_score = st.number_input("Credit Score", min_value=0, max_value=850, step=1)
            credit_limit = st.number_input("Credit Limit", min_value=0.0, step=0.01)
            if st.button("Add Card"):
                result = add_credit_card(st.session_state["user_id"], card_number, expiry_date, credit_score, credit_limit)
                st.success(result if "successfully" in result else result)

            st.write("### Your Credit Cards")
            cards = get_credit_cards(st.session_state["user_id"])
            if cards:
                df = pd.DataFrame(cards, columns=["ID", "Card Number", "Expiry Date", "Credit Score", "Credit Limit", "Current Balance"])
                st.dataframe(df)
            else:
                st.write("No credit cards added yet.")

    else:
        st.warning("Please login to access the Dashboard.")

if __name__ == "__main__":
    init_db()
    main()
