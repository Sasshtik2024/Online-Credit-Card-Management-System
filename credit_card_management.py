import streamlit as st
import sqlite3
from hashlib import sha256

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
            dashboard_menu = ["User Management", "Credit Card Management", "Rewards and Offers"]
            selected_function = st.sidebar.selectbox("Dashboard Menu", dashboard_menu)

            if selected_function == "User Management":
                st.subheader("Update Account Details")
                email = st.text_input("New Email")
                phone = st.text_input("New Phone")
                if st.button("Update Details"):
                    update_user_details(st.session_state['user_id'], email, phone)
                    st.success("Account details updated successfully!")

            elif selected_function == "Credit Card Management":
                st.subheader("Manage Your Credit Cards")
                action = st.radio("Select Action", ["Add New Card", "View and Edit Cards"])
                if action == "Add New Card":
                    card_number = st.text_input("Card Number")
                    expiry_date = st.text_input("Expiry Date (MM/YY)")
                    credit_score = st.number_input("Credit Score", min_value=0, max_value=850)
                    if st.button("Add Card"):
                        result = add_credit_card(st.session_state['user_id'], card_number, expiry_date, credit_score)
                        if "successfully" in result:
                            st.success(result)
                        else:
                            st.error(result)
                elif action == "View and Edit Cards":
                    cards = get_credit_cards(st.session_state['user_id'])
                    for card in cards:
                        st.write(f"Card Number: {card[2]}")
                        st.write(f"Expiry Date: {card[3]}")
                        st.write(f"Credit Score: {card[4]}")
                        st.write("---")
                        if st.button(f"Update Card {card[2]}"):
                            new_expiry = st.text_input(f"New Expiry for {card[2]}")
                            new_score = st.number_input(f"New Credit Score for {card[2]}", min_value=0, max_value=850)
                            update_credit_card(card[0], new_expiry, new_score)
                            st.success("Card updated successfully!")

            elif selected_function == "Rewards and Offers":
                st.subheader("View Your Rewards")
                rewards = get_rewards(st.session_state['user_id'])
                for reward in rewards:
                    st.write(f"Reward: {reward[2]}, Points: {reward[3]}")
                    st.write("---")

# Initialize Database and Run App
if __name__ == '__main__':
    init_db()
    main()
