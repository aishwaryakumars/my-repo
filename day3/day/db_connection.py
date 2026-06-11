import mysql.connector

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aish@123",
            database="EmpMngmt"
        )
        return connection

    except mysql.connector.Error as err:
        print("Error:", err)
        return None