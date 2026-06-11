from db_connection import connect_db

def add_employee(emp_name, contact, address, email_id, salary, dept_id):
    connection = connect_db()

    if connection:
        cursor = connection.cursor()

        query = """
        INSERT INTO Employee
        (emp_name, contact, emp_address, email_id, salary, dept_id,address)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (emp_name, contact, address, email_id, salary, dept_id, address)

        cursor.execute(query, values)
        connection.commit()

        print("Employee added successfully.")

        cursor.close()
        connection.close()
def view_employees():
    connection = connect_db()

    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM Employee"
        cursor.execute(query)
        employees = cursor.fetchall()

        print("\nEmployee List:")
        for emp in employees:
            print(emp)

        cursor.close()
        connection.close()
def update_employee(emp_id, emp_name=None, contact=None, address=None, email_id=None, salary=None, dept_id=None):
    connection = connect_db()

    if connection:
        cursor = connection.cursor()

        update_fields = []
        values = []

        if emp_name:
            update_fields.append("emp_name = %s")
            values.append(emp_name)
        if contact:
            update_fields.append("contact = %s")
            values.append(contact)
        if address:
            update_fields.append("emp_address = %s")
            values.append(address)
        if email_id:
            update_fields.append("email_id = %s")
            values.append(email_id)
        if salary:
            update_fields.append("salary = %s")
            values.append(salary)
        if dept_id:
            update_fields.append("dept_id = %s")
            values.append(dept_id)

        if update_fields:
            query = f"UPDATE Employee SET {', '.join(update_fields)} WHERE emp_id = %s"
            values.append(emp_id)

            cursor.execute(query, tuple(values))
            connection.commit()

            print("Employee updated successfully.")
        else:
            print("No fields to update.")

        cursor.close()
        connection.close()
def delete_employee(emp_id):
    connection = connect_db()

    if connection:
        cursor = connection.cursor()
        query = "DELETE FROM Employee WHERE emp_id = %s"
        cursor.execute(query, (emp_id,))
        connection.commit()

        print("Employee deleted successfully.")

        cursor.close()
        connection.close()
while True:
    print("\n1. Add Employee")
    print("2. View Employees")
    print("3. Update Employee")
    print("4. Delete Employee")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == '1':
        emp_name = input("Enter employee name: ")
        contact = input("Enter contact number: ")
        address = input("Enter address: ")
        email_id = input("Enter email: ")
        salary = float(input("Enter salary: "))
        dept_id = int(input("Enter department ID: "))

        add_employee(
            emp_name,
            contact,
            address,
            email_id,
            salary,
            dept_id
        )

    elif choice == '2':
        view_employees()
        break
    elif choice == '3':
        update_emp_id = int(input("Enter employee ID to update: "))
        update_emp_name = input("Enter new employee name (leave blank to skip): ")      
        break
    elif choice == '4':
        delete_emp_id = int(input("Enter employee ID to delete: "))
        delete_employee(delete_emp_id)
        break
    elif choice == '5':
        print("Exiting the program.")
        break   
    else:
        print("Invalid choice. Please try again.")