import mysql.connector as conn
from info import password
import numpy as nps

def client_interface(client_id):
    mydb = conn.connect(host='localhost', user='root', passwd=password)
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("USE healthcare")

    sql = "SELECT * FROM clients WHERE ClientID = %s"
    mycursor.execute(sql, (client_id,))
    client_details = mycursor.fetchone()
    print("\nClient Portal:\n")
    print(f"\n\tWelcome, {client_details['Name']}!")

    if client_details:
        print("\nClient Details:\n")
        header = f"{'Field':20} | {'Value':40}"
        print(header)
        print("-" * len(header))
        for key, value in client_details.items():
            print(f"{key:20} | {str(value):40}")

        while True:
            print("\n1. View Records")
            print("2. Log out")
            choice = input("Select an option: ").strip()

            if choice == '1':
                query = """
                    SELECT v.Name AS VaccineName, v.DosesRequired, vr.DateGiven, vr.NextDueDate FROM Vaccination_Records vr
                    JOIN Vaccines v ON vr.VaccineID = v.VaccineID WHERE vr.ClientID = %s ORDER BY vr.DateGiven DESC"""
                mycursor.execute(query, (client_id,))
                records = mycursor.fetchall()

                if records:
                    print("\nVaccination Records:\n")
                    header = f"{'Vaccine Name':20} | {'Doses Required':15} | {'Date Given':12} | {'Next Due Date':12}"
                    print(header)
                    print("-" * len(header))
                    data = []
                    for rec in records:
                        date_given = rec['DateGiven'].strftime('%Y-%m-%d') if rec['DateGiven'] else 'N/A'
                        next_due = rec['NextDueDate'].strftime('%Y-%m-%d') if rec['NextDueDate'] else 'N/A'
                        data.append([rec['VaccineName'], rec['DosesRequired'], date_given, next_due])
                    np_data = np.array(data)
                    for row in np_data:
                        print(f"{row[0]:20} | {row[1]:<15} | {row[2]:12} | {row[3]:12}")
                else:
                    print("\nNo vaccination records found.")
            elif choice == '2':
                break
            else:
                print("Invalid option. Please try again.")
    else:
        print("No details found for this Client ID.")
    
    mycursor.close()
    mydb.close()
