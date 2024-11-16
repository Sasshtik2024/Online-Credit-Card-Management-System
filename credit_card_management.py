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
                    description TEXT)''')
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
    except sqlite3.IntegrityError:
        return "Username already exists."
    return "Registration successful."

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
def add_credit_card(user_id, card_number, expiry_date, credit_score):
    try:
        conn = sqlite3.connect('credit_card_system.db')
        c = conn.cursor()
        c.execute("INSERT INTO credit_cards (user_id, card_number, expiry_date, credit_score) VALUES (?, ?, ?, ?)", 
                  (user_id, card_number, expiry_date, credit_score))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return "Card number already exists."
    return "Card added successfully."

def update_credit_card(card_id, expiry_date, credit_score):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("UPDATE credit_cards SET expiry_date = ?, credit_score = ? WHERE id = ?", 
              (expiry_date, credit_score, card_id))
    conn.commit()
    conn.close()

def get_credit_cards(user_id):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM credit_cards WHERE user_id = ?", (user_id,))
    cards = c.fetchall()
    conn.close()
    return cards

# Rewards and Offers
def add_reward(user_id, reward_name, points):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("INSERT INTO rewards (user_id, reward_name, points) VALUES (?, ?, ?)", 
              (user_id, reward_name, points))
    conn.commit()
    conn.close()

def get_rewards(user_id):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rewards WHERE user_id = ?", (user_id,))
    rewards = c.fetchall()
    conn.close()
    return rewards

def check_rewards(user_id):
    # Check if the user has 2 transactions of at least 500
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute('''
        SELECT COUNT(*) 
        FROM transactions t
        JOIN credit_cards c ON t.card_number = c.card_number
        WHERE c.user_id = ? AND t.amount >= 500
    ''', (user_id,))
    count = c.fetchone()[0]
    conn.close()
    if count >= 2:
        add_reward(user_id, "Cashback Reward", 100)
        return "Congratulations! You've earned a cashback reward of 100 points."
    return "Keep shopping to earn rewards!"

# Transaction History
def add_transaction(card_number, amount, description):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("INSERT INTO transactions (card_number, amount, transaction_date, description) VALUES (?, ?, datetime('now'), ?)", 
              (card_number, amount, description))
    conn.commit()
    conn.close()

def get_last_transactions(card_number, limit=10):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE card_number = ? ORDER BY transaction_date DESC LIMIT ?", 
              (card_number, limit))
    transactions = c.fetchall()
    conn.close()
    return transactions

# Analytics and Reports
def get_transaction_data(user_id):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    query = '''
        SELECT t.card_number, t.amount, t.transaction_date 
        FROM transactions t 
        JOIN credit_cards c ON t.card_number = c.card_number 
        WHERE c.user_id = ? 
        ORDER BY t.transaction_date ASC
    '''
    c.execute(query, (user_id,))
    data = c.fetchall()
    conn.close()
    return pd.DataFrame(data, columns=["Card Number", "Amount", "Transaction Date"])

# Customer Support
def submit_support_query(user_id, query):
    conn = sqlite3.connect('credit_card_system.db')
    c = conn.cursor()
    c.execute("INSERT INTO support_queries (user_id, query) VALUES (?, ?)", (user_id, query))
    conn.commit()
    conn.close()

def get_support_faq():
    return [
        "Q1: How do I update my account details?",
        "Q2: How can I add a new credit card?",
        "Q3: Where can I view my transaction history?",
        "Q4: How do I redeem my rewards?"
    ]

# Streamlit App
def main():
    st.title("Online Credit Card Management System")
    st.sidebar.title("Navigation")
    menu = ["Login", "Register", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login Section")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.success(f"Welcome {username}!")
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user[0]
                st.session_state['username'] = username
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "Register":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        if st.button("Register"):
            result = register_user(new_user, new_password, email, phone)
            if "successful" in result:
                st.success(result)
                st.info("Go to Login Menu to login")
            else:
                st.error(result)

    elif choice == "Dashboard":
        if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
            st.warning("Please login first.")
        else:
            st.subheader(f"Welcome to your Dashboard, {st.session_state['username']}!")
            dashboard_menu = [
                "User Management", 
                "Credit Card Management", 
                "Rewards and Offers", 
                "Transaction History", 
                "Perform Transaction", 
                "Customer Support", 
                "Analytics and Reports"
            ]
            selected_function = st.sidebar.selectbox("Dashboard Menu", dashboard_menu)

            if selected_function == "User Management":
                st.subheader("Update Account Details")
                email = st.text_input("New Email")
                phone = st.text_input("New Phone")
                if st.button("Update Details"):
                    update_user_details(st.session_state['user_id'], email, phone)
                    st.success("Account details updated successfully!")

            elif selected_function == "Credit Card Management":
                st.subheader("Credit Card Management")
                card_action = st.selectbox("Select Action", ["Add New Card", "View and Edit Cards"])
                if card_action == "Add New Card":
                    card_number = st.text_input("Card Number")
                    expiry_date = st.text_input("Expiry Date (MM/YY)")
                    credit_score = st.number_input("Credit Score", min_value=0, max_value=850)
                    if st.button("Add Card"):
                        result = add_credit_card(st.session_state['user_id'], card_number, expiry_date, credit_score)
                        if "success" in result:
                            st.success(result)
                        else:
                            st.error(result)
                elif card_action == "View and Edit Cards":
                    cards = get_credit_cards(st.session_state['user_id'])
                    if cards:
                        st.table(cards)
                        card_id = st.number_input("Card ID to Edit", min_value=0)
                        new_expiry_date = st.text_input("New Expiry Date (MM/YY)")
                        new_credit_score = st.number_input("New Credit Score", min_value=0, max_value=850)
                        if st.button("Update Card Details"):
                            update_credit_card(card_id, new_expiry_date, new_credit_score)
                            st.success("Card details updated successfully!")

            elif selected_function == "Rewards and Offers":
                st.subheader("Rewards and Offers")
                if st.button("Check for Rewards"):
                    result = check_rewards(st.session_state['user_id'])
                    st.info(result)
                rewards = get_rewards(st.session_state['user_id'])
                if rewards:
                    st.table(rewards)
                else:
                    st.info("No rewards available. Shop to earn rewards!")

            elif selected_function == "Transaction History":
                st.subheader("Transaction History")
                cards = get_credit_cards(st.session_state['user_id'])
                if cards:
                    card_number = st.selectbox("Select Card", [card[2] for card in cards])
                    if st.button("View Transactions"):
                        transactions = get_last_transactions(card_number)
                        if transactions:
                            st.table(transactions)
                        else:
                            st.info("No transactions available.")
                else:
                    st.warning("No cards found. Add a card first.")

            elif selected_function == "Perform Transaction":
                st.subheader("Perform a Transaction")
                cards = get_credit_cards(st.session_state['user_id'])
                if cards:
                    card_number = st.selectbox("Select Card", [card[2] for card in cards])
                    amount = st.number_input("Transaction Amount", min_value=0.0, format="%.2f")
                    description = st.text_area("Description")
                    if st.button("Complete Transaction"):
                        add_transaction(card_number, amount, description)
                        st.success("Transaction completed successfully!")
                else:
                    st.warning("No cards found. Add a card first.")

            elif selected_function == "Customer Support":
                st.subheader("Customer Support")
                faq = get_support_faq()
                st.markdown("\n".join(faq))
                query = st.text_area("Submit a Query")
                if st.button("Submit Query"):
                    submit_support_query(st.session_state['user_id'], query)
                    st.success("Query submitted. Support team will respond soon.")

            elif selected_function == "Analytics and Reports":
                st.subheader("Transaction Analytics and Reports")
                data = get_transaction_data(st.session_state['user_id'])
                if not data.empty:
                    st.line_chart(data.set_index("Transaction Date")["Amount"])
                    st.table(data)
                else:
                    st.info("No transaction data available.")

if __name__ == "__main__":
    init_db()
    main()
