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
                    card_number TEXT UNIQUE,
                    expiry_date TEXT,
                    credit_score INTEGER,
                    credit_limit REAL,
                    current_balance REAL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS rewards (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    reward_name TEXT,
                    points INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    card_number TEXT,
                    amount REAL,
                    transaction_date TEXT,
                    description TEXT,
                    FOREIGN KEY(card_number) REFERENCES credit_cards(card_number))''')
    c.execute('''CREATE TABLE IF NOT EXISTS support_queries (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    query TEXT,
                    response TEXT DEFAULT 'Pending',
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
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
    data = c.fetchone()
    conn.close()
    return data

# Credit Card Management
def add_credit_card(user_id, card_number, expiry_date, credit_score, credit_limit):
    try:
        conn = sqlite3.connect('credit_card_system.db')
        c = conn.cursor()
        c.execute("INSERT INTO credit_cards (user_id, card_number, expiry_date, credit_score, credit_limit) VALUES (?, ?, ?, ?, ?)", 
                  (user_id, card_number, expiry_date, credit_score, credit_limit))
        conn.commit()
        conn.close()
        return "Card added successfully."
    except sqlite3.IntegrityError:
        return "Card number already exists."

def get_credit_cards(user_id):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM credit_cards WHERE user_id = ?", (user_id,))
    cards = c.fetchall()
    conn.close()
    return cards

# Transaction Management
def add_transaction(card_number, amount, description):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("SELECT credit_limit, current_balance FROM credit_cards WHERE card_number = ?", (card_number,))
    card = c.fetchone()
    if card:
        credit_limit, current_balance = card
        if current_balance + amount > credit_limit:
            conn.close()
            return "Transaction failed: Credit limit exceeded."
        c.execute("INSERT INTO transactions (card_number, amount, transaction_date, description) VALUES (?, ?, datetime('now'), ?)", 
                  (card_number, amount, description))
        c.execute("UPDATE credit_cards SET current_balance = current_balance + ? WHERE card_number = ?", 
                  (amount, card_number))
        conn.commit()
        conn.close()
        return "Transaction successful!"
    conn.close()
    return "Transaction failed: Invalid card."

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
        cards = get_credit_cards(st.session_state["user_id"])
        st.write("Your Cards:")
        st.write(cards)
        st.write("Add more features as needed.")

    else:
        st.warning("Please login to access the Dashboard.")

if __name__ == "__main__":
    init_db()
    main()
