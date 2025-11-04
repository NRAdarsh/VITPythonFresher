import mysql.connector as conn
import re
import os

from info import password
from admininterface import admin_interface
from clientinterface import client_interface

script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(script_dir, 'vaccination_management.sql')
sql_initiate_path = os.path.join(script_dir, 'login_initiation.sql')

mydb = conn.connect(host='localhost', user='root', passwd=password)
mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES LIKE 'login'")
result = mycursor.fetchone()
if not result:
    mycursor.execute("CREATE DATABASE login")
    mycursor.execute("USE login")
    with open(sql_initiate_path, 'r') as f:
        sql_commands = f.read()
    for cmd in sql_commands.split(';'):
        if cmd.strip():
            mycursor.execute(cmd)
    mydb.commit()
else:
    pass

mycursor.execute("SHOW DATABASES LIKE 'healthcare'")
result = mycursor.fetchone()
if not result:
    mycursor.execute("CREATE DATABASE healthcare")
    mycursor.execute("USE healthcare")
    with open(sql_file_path, 'r') as f:
        sql_commands = f.read()
    for cmd in sql_commands.split(';'):
        if cmd.strip():
            mycursor.execute(cmd)
    mydb.commit()
else:
    pass

mycursor.execute("USE login")

def validate_password(pwd):
    if len(pwd) < 8:
        return False
    if not re.search("[a-z]", pwd):
        return False
    if not re.search("[A-Z]", pwd):
        return False
    if not re.search("[0-9]", pwd):
        return False
    if not re.search("[!@_#$%^&*]", pwd):
        return False
    return True

def reset_password_client(email):
    mycursor.execute("SELECT ClientID FROM clients WHERE Email=%s", (email,))
    result = mycursor.fetchone()
    if not result:
        print("Error: Email not found.")
        return
    client_id = result[0]

    print("\nReset Password:")
    new_password = input("Enter new password: ")
    confirm_password = input("Confirm new password: ")

    if new_password != confirm_password:
        print("Error: Passwords do not match.")
        return
    if not validate_password(new_password):
        print("Error: Invalid password format. Include upper, lower, digit, and symbol.")
        return

    mycursor.execute("UPDATE clients SET Password=%s WHERE ClientID=%s", (new_password, client_id))
    mydb.commit()
    print("Success: Password updated successfully!")

def client_login():
    print("\nClient Login")
    email = input("Enter Email: ")
    password_input = input("Enter Password (or type 'forgot' to reset): ")

    if password_input.lower() == 'forgot':
        reset_password_client(email)
        return

    mycursor.execute("SELECT ClientID, Password FROM clients WHERE Email=%s", (email,))
    result = mycursor.fetchone()

    if result:
        client_id, db_password = result
        if db_password is None:
            if not validate_password(password_input):
                print("Error: Weak password. Include upper, lower, digit, and symbol.")
                return
            mycursor.execute("UPDATE clients SET Password=%s WHERE ClientID=%s", (password_input, client_id))
            mydb.commit()
            print("Success: Password set successfully. Please login again.")
            return
        elif password_input != db_password:
            print("Error: Incorrect password.")
            return
        else:
            client_interface(client_id)
    else:
        print("Error: Email not found.")

def admin_login():
    print("\nAdmin Login")
    admin_id = input("Enter Admin ID: ")
    password_input = input("Enter Password: ")

    mycursor.execute("SELECT Password FROM admins WHERE AdminID=%s", (admin_id,))
    result = mycursor.fetchone()

    if result:
        db_password = result[0]
        if password_input == db_password:
            admin_interface(admin_id)
        else:
            print("Error: Incorrect password.")
    else:
        print("Error: Admin ID not found.")

def main_menu():
    while True:
        print("\nMain Menu")
        print("1. Client Login")
        print("2. Admin Login")
        print("3. Exit")
        choice = input("Select an option: ").strip()

        if choice == '1':
            client_login()
        elif choice == '2':
            admin_login()
        elif choice == '3':
            print()
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()