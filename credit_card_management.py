import streamlit as st
import bcrypt


users_db = {}  # Dictionary to store user information
transactions_db = [
    {"Transaction ID": "TX001", "Amount": "$50", "Type": "Groceries"},
    {"Transaction ID": "TX002", "Amount": "$200", "Type": "Electronics"},
]
rewards_db = [
    {"Reward ID": "RW001", "Points": 500, "Status": "Available"},
    {"Reward ID": "RW002", "Points": 200, "Status": "Redeemed"},
]

# ----------------------- Helper Functions -----------------------

def hash_password(password):
    """Hash a password for secure storage."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    """Check if a password matches the stored hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# ----------------------- Login & Registration -------------------

def login_page():
    """Render the login page."""
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = users_db.get(username)
        if user and check_password(password, user['password']):
            st.session_state['user'] = username
            st.success("Logged in successfully!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password!")

def register_page():
    """Render the registration page."""
    st.title("Register")
    username = st.text_input("Choose a Username")
    password = st.text_input("Create Password", type="password")
    if st.button("Register"):
        if username in users_db:
            st.error("Username already exists!")
        else:
            hashed_pwd = hash_password(password)
            users_db[username] = {"password": hashed_pwd, "cards": []}
            st.success("Registration successful! Please log in.")

# ----------------------- Functionalities -----------------------

def user_account_management():
    """Manage user account settings."""
    st.title("User Account Management")
    st.write(f"Welcome, {st.session_state['user']}")
    if st.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

def credit_card_management():
    """Manage credit cards."""
    st.title("Credit Card Management")
    user = st.session_state['user']
    cards = users_db[user]["cards"]
    st.write("Your Cards:")
    if cards:
        st.write(", ".join(cards))
    else:
        st.write("No cards available.")
    if st.button("Apply for a New Card"):
        card_id = f"CC{len(cards) + 1:03}"
        users_db[user]["cards"].append(card_id)
        st.success(f"New card {card_id} issued!")

def transaction_details():
    """Display transaction history."""
    st.title("Transaction Details")
    st.write("Your Transaction History:")
    st.table(transactions_db)

def rewards_and_offers():
    """Show rewards and offers."""
    st.title("Rewards and Offers")
    st.write("Your Rewards:")
    st.table(rewards_db)

def payment_and_billing():
    """Handle payments and billing."""
    st.title("Payment and Billing")
    st.write("Pay your bills or view statements here.")
    if st.button("Pay Now"):
        st.success("Payment processed successfully!")

def customer_support():
    """Provide customer support interface."""
    st.title("Customer Support")
    issue = st.text_area("Describe your issue:")
    if st.button("Submit Issue"):
        if issue:
            st.success("Your issue has been submitted. Our team will contact you shortly.")
        else:
            st.error("Please describe your issue before submitting.")

# ----------------------- Main App ------------------------------

def main():
    """Main application function."""
    st.sidebar.title("Navigation")
    if 'user' not in st.session_state:
        st.sidebar.radio("Choose an option:", ["Login", "Register"], key="auth_page")
        if st.session_state.auth_page == "Login":
            login_page()
        elif st.session_state.auth_page == "Register":
            register_page()
    else:
        option = st.sidebar.selectbox(
            "Choose a feature",
            ["User Account Management", "Credit Card Management",
             "Transaction Details", "Rewards and Offers",
             "Payment and Billing", "Customer Support"]
        )
        if option == "User Account Management":
            user_account_management()
        elif option == "Credit Card Management":
            credit_card_management()
        elif option == "Transaction Details":
            transaction_details()
        elif option == "Rewards and Offers":
            rewards_and_offers()
        elif option == "Payment and Billing":
            payment_and_billing()
        elif option == "Customer Support":
            customer_support()

if __name__ == "__main__":
    main()
