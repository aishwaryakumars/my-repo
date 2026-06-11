from numpy import e

from db_connection import connect_db
try:    
    connection = connect_db()
    if connection:
        print("Connection established successfully.")   
    connection.close()
except Exception as e:
    print(f"An error occurred: {e}")