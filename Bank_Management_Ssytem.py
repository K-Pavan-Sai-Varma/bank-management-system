import sqlite3

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('bank.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            accNo INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('C', 'S')),
            deposit INTEGER NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            accNo INTEGER PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ---------- ACCOUNT CREATION ----------
def create_account():
    accNo = int(input("Enter desired account number: "))
    name = input("Enter your name: ")

    while True:
        acc_type = input("Enter account type [C/S]: ").upper()
        if acc_type in ['C', 'S']:
            break
        print("Invalid type! Choose 'C' for Current or 'S' for Saving.")

    while True:
        deposit = int(input("Enter initial deposit: "))
        if (acc_type == 'S' and deposit >= 500) or (acc_type == 'C' and deposit >= 1000):
            break
        print("Minimum ₹500 for Saving and ₹1000 for Current.")

    password = input("Set a password for your account: ")

    conn = sqlite3.connect('bank.db')
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)", (accNo, name, acc_type, deposit))
        cur.execute("INSERT INTO users VALUES (?, ?)", (accNo, password))
        conn.commit()
        print("\n Account created successfully!")
    except sqlite3.IntegrityError:
        print(" Account number already exists.")
        accNo = None

    conn.close()
    return accNo

# ---------- LOGIN ----------
def verify_user(accNo, password):
    conn = sqlite3.connect('bank.db')
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE accNo=?", (accNo,))
    row = cur.fetchone()
    if not accNo:
        conn.close()
        return "no_account"
    cur.execute("SELECT password FROM users WHERE accNo=?", (accNo,))
    row = cur.fetchone()   
    conn.close()
    if row and row[0] == password:
        return "ok"
    return "wrong_pass"

# ---------- ACCOUNT OPERATIONS ----------
def show_balance(accNo):
    conn = sqlite3.connect('bank.db')
    cur = conn.cursor()
    cur.execute("SELECT deposit FROM accounts WHERE accNo=?", (accNo,))
    row = cur.fetchone()
    conn.close()
    if row:
        print(f"Available balance: ₹{row[0]}")
    else:
        print("!Account not found.")

def deposit_or_withdraw(accNo, action):
    conn = sqlite3.connect('bank.db')
    cur = conn.cursor()
    cur.execute("SELECT deposit FROM accounts WHERE accNo=?", (accNo,))
    row = cur.fetchone()
    if not row:
        print("Account not found.")
        conn.close()
        return
    balance = row[0]
    amount = int(input(f"Enter amount to {action}: "))
    if action == "deposit":
        balance += amount
    elif action == "withdraw":
        if amount > balance:
            print("!! Insufficient funds.")
            conn.close()
            return
        balance -= amount
    cur.execute("UPDATE accounts SET deposit=? WHERE accNo=?", (balance, accNo))
    conn.commit()
    conn.close()
    print(f"{action.capitalize()} successful. New balance: ₹{balance}")

def modify_account(accNo):
    conn = sqlite3.connect('bank.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE accNo=?", (accNo,))
    if cur.fetchone():
        name = input("Enter new name: ")
        while True:
            acc_type = input("Enter new type [C/S]: ").upper()
            if acc_type in ['C', 'S']:
                break
            print("Invalid type! Use C or S.")
        deposit = int(input("Enter new balance: "))
        cur.execute("UPDATE accounts SET name=?, type=?, deposit=? WHERE accNo=?",
                    (name, acc_type, deposit, accNo))
        conn.commit()
        print("Account updated.")
    else:
        print("Account not found.")
    conn.close()

def delete_account(accNo):
    conn = sqlite3.connect('bank.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM accounts WHERE accNo=?", (accNo,))
    cur.execute("DELETE FROM users WHERE accNo=?", (accNo,))
    conn.commit()
    if cur.rowcount:
        print("Account deleted.")
    else:
        print(" Account not found.")
    conn.close()

def display_all_accounts():
    conn = sqlite3.connect('bank.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts")
    rows = cur.fetchall()
    conn.close()
    if rows:
        print(f"{'AccNo':<10}{'Name':<20}{'Type':<10}{'Balance':<10}")
        for r in rows:
            print(f"{r[0]:<10}{r[1]:<20}{r[2]:<10}{r[3]:<10}")
    else:
        print("No accounts found.")

# ---------- MENUS ----------
def user_menu(accNo):
    while True:
        print("\n-- USER MENU --")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Balance Enquiry")
        print("4. Logout")
        choice = input("Choose an option: ")

        if choice == '1':
            deposit_or_withdraw(accNo, 'deposit')
        elif choice == '2':
            deposit_or_withdraw(accNo, 'withdraw')
        elif choice == '3':
            show_balance(accNo)
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

def admin_menu():
    while True:
        print("\n-- ADMIN MENU --")
        print("1. View All Account Holders")
        print("2. Modify Account")
        print("3. Close Account")
        print("4. Logout")
        choice = input("Choose an option: ")
        if choice == '1':
            display_all_accounts()
        elif choice == '2':
            accNo=int(input("Enter account number to modify :"))
            modify_account(accNo)
        elif choice == '3':
            accNo=int(input("Enter account number to delete :"))
            delete_account(accNo)
            break
        elif choice =='4':
            break
        else:
            print("Invalid choice.")

# ---------- MAIN PROGRAM ----------
def main():
    init_db()
    while True:
        print("\n========= LOGIN MENU =========")
        print("1. Admin")
        print("2. Existing User")
        print("3. New User")
        print("4. Exit")
        print("===============================")
        choice = input("Choose an option: ")

        if choice == '1':
            password = input("Enter admin password: ")
            if password == 'admin123':
                admin_menu()
            else:
                print("Wrong password.")
        elif choice == '2':
            accNo = int(input("Enter your account number: "))
            password = input("Enter your password: ")
            res=verify_user(accNo, password)
            if res=="ok":
                user_menu(accNo)
            elif res=="wrong_pass":
                print("Incorrect Password")
            elif res=="no_account":
                print("No such account found")
        elif choice == '3':
            accNo = create_account()
            if accNo:
                user_menu(accNo)
        elif choice == '4':
            print("Thank you for using the Bank Management System.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
