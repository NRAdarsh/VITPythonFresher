import mysql.connector as conn
from info import password
import numpy as np

def admin_interface(admin_id):
    mydb = conn.connect(host='localhost', user='root', passwd=password)
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("USE healthcare")

    sql = "SELECT * FROM admins WHERE AdminID = %s"
    mycursor.execute(sql, (admin_id,))
    admin_details = mycursor.fetchone()
    print("\nAdmin Portal:\n")
    print(f"\n\tGreetings, {admin_details['User']}!")

    if admin_details:
        print("\nAdmin Details:\n")
        header = f"{'Field':20} | {'Value':40}"
        print(header)
        print("-" * len(header))
        for key, value in list(admin_details.items())[:-1]:
            print(f"{key:20} | {str(value):40}")

        while True:
            print("\n1. View Administrated Records")
            print("2. Add/Remove Client")
            print("3. Search Client details")
            print("4. Add/Remove Vaccination Record")
            print("5. Search Vaccine details")
            print("6. View Delivery Reports")
            print("7. Modify Delivery Reports")
            print("8. Log out")
            choice = input("Select an option: ").strip()

            if choice == '1':
                admin_user = admin_details['User']
                records_query = """
                    SELECT RecordID, ClientID, VaccineID, DateGiven, NextDueDate FROM Vaccination_Records
                    WHERE AdministeredBy = %s ORDER BY DateGiven DESC"""
                mycursor.execute(records_query, (admin_user,))
                records = mycursor.fetchall()

                if records:
                    print("\nAdministrated Vaccination Records:\n")
                    header = f"{'RecordID':10} | {'ClientID':12} | {'VaccineID':10} | {'Date Given':12} | {'Next Due Date':12}"
                    print(header)
                    print("-" * len(header))
                    data = []
                    for rec in records:
                        date_given = rec['DateGiven'].strftime('%Y-%m-%d') if rec['DateGiven'] else 'N/A'
                        next_due = rec['NextDueDate'].strftime('%Y-%m-%d') if rec['NextDueDate'] else 'N/A'
                        data.append([str(rec['RecordID']), rec['ClientID'], rec['VaccineID'], date_given, next_due])
                    np_data = np.array(data)
                    for row in np_data:
                        print(f"{row[0]:10} | {row[1]:12} | {row[2]:8} | {row[3]:12} | {row[4]:12}")
                else:
                    print("\nNo administrated vaccination records found.")

            elif choice == '2':
                action = input("\nDo you want to (a)dd or (r)emove a client? (a/r): ").strip().lower()
                if action == 'a':
                    mycursor.execute("SELECT ClientID FROM Clients ORDER BY ClientID DESC LIMIT 1")
                    last_id = mycursor.fetchone()
                    if last_id:
                        last_num = int(last_id['ClientID'][-5:])
                        new_num = last_num + 1
                    else:
                        new_num = 1
                    new_client_id = f"CID00IN{new_num:05d}"

                    print(f"Generated new ClientID: {new_client_id}")
                    name = input("Enter client name: ").strip()
                    dob = input("Enter date of birth (YYYY-MM-DD): ").strip()
                    contact = input("Enter contact number: ").strip()
                    email = input("Enter email address: ").strip()

                    import re
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', dob):
                        print("Invalid date format. Use YYYY-MM-DD.")
                    else:
                        insert_sql = "INSERT INTO Clients (ClientID, Name, DOB, Contact) VALUES (%s, %s, %s, %s)"
                        mycursor.execute(insert_sql, (new_client_id, name, dob, contact))
                        mycursor.execute("INSERT INTO login.Clients (ClientID, Email) VALUES (%s, %s)", (new_client_id, email))
                        mydb.commit()
                        print("Client added successfully.")
                elif action == 'r':
                    remove_id = input("Enter Client ID to remove: ").strip()
                    mycursor.execute("SELECT ClientID FROM Clients WHERE ClientID = %s", (remove_id,))
                    if mycursor.fetchone():
                        confirm = input(f"Are you sure you want to delete client {remove_id}? (y/n): ").strip().lower()
                        if confirm == 'y':
                            mycursor.execute("DELETE FROM Clients WHERE ClientID = %s", (remove_id,))
                            mycursor.execute("DELETE FROM login.Clients WHERE ClientID = %s", (remove_id,))
                            mydb.commit()
                            print("Client removed successfully.")
                        else:
                            print("Deletion cancelled.")
                    else:
                        print("Client ID does not exist.")
                else:
                    print("Invalid option. Please enter 'a' or 'r'.")

            elif choice == '3':
                search_id = input("\nEnter Client ID to search: ").strip()
                query = "SELECT Name, DOB, Contact FROM Clients WHERE ClientID = %s"
                mycursor.execute(query, (search_id,))
                client = mycursor.fetchone()
                if not client:
                    print("No client found with that Client ID.")
                    continue

                while True:
                    action = input("\nDo you want to (v)iew or (u)pdate client details? (v/u): ").strip().lower()
                    if action == 'v':
                        print("\nClient Search Result:")
                        header = f"{'Name':20} | {'DOB':12} | {'Contact':20}"
                        print(header)
                        print("-" * len(header))
                        dob = client['DOB'].strftime('%Y-%m-%d') if client['DOB'] else 'N/A'
                        print(f"{client['Name']:20} | {dob:12} | {client['Contact']:20}")
                        break
                    elif action == 'u':
                        print("\nFields available for update:\n1. Name\n2. DOB\n3. Contact\n4. Email")
                        field_choice = input("Choose field number to update: ").strip()

                        field_map = {'1': 'Name', '2': 'DOB', '3': 'Contact', '4': 'Email'}
                        if field_choice not in field_map:
                            print("Invalid choice. Returning to admin portal...")
                            break
                        if field_choice != '4':
                            field_name = field_map[field_choice]
                            new_value = input(f"Enter new value for {field_name}: ").strip()
                            if field_name == 'DOB':
                                import re
                                if not re.match(r'^\d{4}-\d{2}-\d{2}$', new_value):
                                    print("Invalid date format. Use YYYY-MM-DD.")
                                    continue
                            update_sql = f"UPDATE Clients SET {field_name} = %s WHERE ClientID = %s"
                            mycursor.execute(update_sql, (new_value, search_id))
                            mydb.commit()
                        else:
                            field_name = field_map[field_choice]
                            new_value = input(f"Enter new value for {field_name}: ").strip()
                            mycursor.execute(f"UPDATE login.Clients SET {field_name} = %s WHERE ClientID = %s", (new_value, search_id))
                            mydb.commit()
                        print(f"{field_name} updated successfully.")
                        break
                    else:
                        print("Invalid option. Please enter 'v' to view or 'u' to update.")

            elif choice == '4':
                action = input("\nDo you want to (a)dd or (r)emove a vaccine record? (a/r): ").strip().lower()
                if action == 'a':
                    mycursor.execute("SELECT VaccineID FROM Vaccines ORDER BY VaccineID DESC LIMIT 1")
                    last_id = mycursor.fetchone()
                    if last_id:
                        last_num = int(last_id['VaccineID'][-4:])
                        new_num = last_num + 1
                    else:
                        new_num = 1
                    new_vaccine_id = f"VN{new_num:04d}"

                    print(f"Generated new VaccineID: {new_vaccine_id}")
                    name = input("Enter vaccine name: ").strip()
                    manufacturer = input("Enter manufacturer: ").strip()
                    doses_required = input("Enter doses required (integer): ").strip()

                    if not doses_required.isdigit():
                        print("Doses Required must be an integer.")
                    else:
                        doses_required = int(doses_required)
                        insert_sql = "INSERT INTO Vaccines (VaccineID, Name, Manufacturer, DosesRequired) VALUES (%s, %s, %s, %s)"
                        mycursor.execute(insert_sql, (new_vaccine_id, name, manufacturer, doses_required))
                        mydb.commit()
                        print("Vaccine record added successfully.")

                elif action == 'r':
                    remove_id = input("Enter VaccineID to remove: ").strip()
                    mycursor.execute("SELECT VaccineID FROM Vaccines WHERE VaccineID = %s", (remove_id,))
                    if mycursor.fetchone():
                        confirm = input(f"Confirm deletion of vaccine {remove_id}? (y/n): ").strip().lower()
                        if confirm == 'y':
                            mycursor.execute("DELETE FROM Vaccines WHERE VaccineID = %s", (remove_id,))
                            mydb.commit()
                            print("Vaccine record removed successfully.")
                        else:
                            print("Deletion cancelled.")
                    else:
                        print("VaccineID does not exist.")
                else:
                    print("Invalid option. Enter 'a' or 'r'.")

            elif choice == '5':
                vaccine_id = input("\nEnter Vaccine ID to search: ").strip()
                query = "SELECT Name, Manufacturer, DosesRequired FROM Vaccines WHERE VaccineID = %s"
                mycursor.execute(query, (vaccine_id,))
                vaccine = mycursor.fetchone()
                if not vaccine:
                    print("No vaccine found with that Vaccine ID.")
                    continue

                while True:
                    action = input("\nDo you want to (v)iew or (u)pdate vaccine details? (v/u): ").strip().lower()
                    if action == 'v':
                        print("\nVaccine Search Result:")
                        header = f"{'Name':20} | {'Manufacturer':20} | {'DosesRequired':14}"
                        print(header)
                        print("-" * len(header))
                        print(f"{vaccine['Name']:20} | {vaccine['Manufacturer']:20} | {str(vaccine['DosesRequired']):14}")
                        break
                    elif action == 'u':
                        print("\nFields available for update:\n1. Name\n2. Manufacturer\n3. DosesRequired")
                        field_choice = input("Choose field number to update: ").strip()
                        field_map = {'1': 'Name', '2': 'Manufacturer', '3': 'DosesRequired'}
                        if field_choice not in field_map:
                            print("Invalid choice. Returning to vaccine menu.")
                            break
                        field_name = field_map[field_choice]
                        new_value = input(f"Enter new value for {field_name}: ").strip()
                        if field_name == 'DosesRequired':
                            if not new_value.isdigit():
                                print("DosesRequired must be an integer.")
                                continue
                            new_value = int(new_value)
                        update_sql = f"UPDATE Vaccines SET {field_name} = %s WHERE VaccineID = %s"
                        mycursor.execute(update_sql, (new_value, vaccine_id))
                        mydb.commit()
                        print(f"{field_name} updated successfully.")
                        break
                    else:
                        print("Invalid option. Please enter 'v' to view or 'u' to update.")

            elif choice == '6':
                query = """
                    SELECT DeliverableID, ReportName, CreatedOn FROM Deliverable
                    WHERE CreatedBy = %s ORDER BY CreatedOn DESC"""
                mycursor.execute(query, (admin_id,))
                reports = mycursor.fetchall()

                if reports:
                    print("\nDelivery Reports Created by You:\n")
                    header = f"{'DeliverableID':15} | {'ReportName':30} | {'CreatedOn':12}"
                    print(header)
                    print("-" * len(header))
                    data = []
                    for rep in reports:
                        created_on = rep['CreatedOn'].strftime('%Y-%m-%d') if rep['CreatedOn'] else 'N/A'
                        data.append([rep['DeliverableID'], rep['ReportName'], created_on])
                    np_data = np.array(data)

                    for row in np_data:
                        print(f"{row[0]:15} | {row[1]:30} | {row[2]:12}")
                else:
                    print("\nNo delivery reports found that you created.")

            elif choice == '7':
                deliverable_id = input("\nEnter Deliverable ID to modify: ").strip()

                print("\nSelect the field to modify:")
                print("1. ReportName")
                print("2. CreatedOn")
                field_choice = input("Enter your choice (1/2): ").strip()

                field_map = {'1': 'ReportName', '2': 'CreatedOn'}
                if field_choice not in field_map:
                    print("Invalid choice. Returning to menu.")
                    continue
                field_name = field_map[field_choice]
                new_value = input(f"Enter new value for {field_name}: ").strip()
                if field_name == 'CreatedOn':
                    import re
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', new_value):
                        print("Invalid date format. Use YYYY-MM-DD.")
                        continue

                update_sql = f"UPDATE Deliverable SET {field_name} = %s WHERE DeliverableID = %s"
                mycursor.execute(update_sql, (new_value, deliverable_id))
                mydb.commit()
                print(f"{field_name} updated successfully.")

            elif choice == '8':
                break
            else:
                print('Invalid option. Please try again.')
    else:
        print("No details found for this Admin ID.")
    
    mycursor.close()
    mydb.close()
