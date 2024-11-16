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

def update_user_details(user_id, email, phone):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("UPDATE users SET email = ?, phone = ? WHERE id = ?", (email, phone, user_id))
    conn.commit()
    conn.close()

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

def update_credit_card(card_id, expiry_date, credit_score, credit_limit):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("""UPDATE credit_cards 
                 SET expiry_date = ?, credit_score = ?, credit_limit = ? 
                 WHERE id = ?""", 
              (expiry_date, credit_score, credit_limit, card_id))
    conn.commit()
    conn.close()

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

def get_last_transactions(card_number, limit=10):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE card_number = ? ORDER BY transaction_date DESC LIMIT ?", 
              (card_number, limit))
    transactions = c.fetchall()
    conn.close()
    return transactions

# Rewards and Offers
def get_rewards(user_id):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("SELECT reward_name, points FROM rewards WHERE user_id = ?", (user_id,))
    rewards = c.fetchall()
    conn.close()
    return rewards

# Analytics and Reports
def get_transaction_data(user_id):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    query = '''
        SELECT t.card_number, t.amount, t.transaction_date, t.description
        FROM transactions t 
        JOIN credit_cards c ON t.card_number = c.card_number 
        WHERE c.user_id = ? 
        ORDER BY t.transaction_date ASC
    '''
    c.execute(query, (user_id,))
    data = c.fetchall()
    conn.close()
    return pd.DataFrame(data, columns=["Card Number", "Amount", "Transaction Date", "Description"])

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
        dashboard_menu = ["User Management", "Credit Card Management", "Transaction Management", 
                          "Rewards and Offers", "Analytics and Reports"]
        selected_function = st.sidebar.selectbox("Dashboard Menu", dashboard_menu)

        if selected_function == "User Management":
            email = st.text_input("New Email")
            phone = st.text_input("New Phone")
            if st.button("Update Details"):
                update_user_details(st.session_state["user_id"], email, phone)
                st.success("Details updated successfully!")

        elif selected_function == "Credit Card Management":
            action = st.radio("Action", ["Add New Card", "View and Edit Cards"])
            if action == "Add New Card":
                card_number = st.text_input("Card Number")
                expiry_date = st.text_input("Expiry Date (MM/YY)")
                credit_score = st.number_input("Credit Score", min_value=0, max_value=850)
                credit_limit = st.number_input("Credit Limit", min_value=0.0)
                if st.button("Add Card"):
                    result = add_credit_card(st.session_state["user_id"], card_number, expiry_date, credit_score, credit_limit)
                    st.success(result if "successfully" in result else result)
            else:
                cards = get_credit_cards(st.session_state["user_id"])
                for card in cards:
                    if st.button(f"Edit {card[2]}"):
                        expiry_date = st.text_input(f"Expiry Date for {card[2]}", value=card[3])
                        credit_score = st.number_input(f"Credit Score for {card[2]}", value=card[4])
                        credit_limit = st.number_input(f"Credit Limit for {card[2]}", value=card[5])
                        if st.button(f"Update {card[2]}"):
                            update_credit_card(card[0], expiry_date, credit_score, credit_limit)
                            st.success(f"Card {card[2]} updated successfully!")

        elif selected_function == "Transaction Management":
            cards = get_credit_cards(st.session_state["user_id"])
            card_numbers = [card[2] for card in cards]
            selected_card = st.selectbox("Select Card", card_numbers)
            amount = st.number_input("Transaction Amount", min_value=0.0)
            description = st.text_input("Description")
            if st.button("Add Transaction"):
                result = add_transaction(selected_card, amount, description)
                st.success(result if "successful" in result else result)
            if st.button("View Last Transactions"):
                transactions = get_last_transactions(selected_card)
                st.write(pd.DataFrame(transactions, columns=["ID", "Card Number", "Amount", "Date", "Description"]))

        elif selected_function == "Rewards and Offers":
            rewards = get_rewards(st.session_state["user_id"])
            st.write(pd.DataFrame(rewards, columns=["Reward Name", "Points"]))

        elif selected_function == "Analytics and Reports":
            transactions = get_transaction_data(st.session_state["user_id"])
            st.write(transactions)

    else:
        st.warning("Please login to access the Dashboard.")

if __name__ == "__main__":
    init_db()
    main()
