from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["StudentDB"]
students = db["trial"]

while True:
    print("\n1. Add Student")
    print("2. View Students")
    print("3. Update Student")
    print("4. Delete Student")
    print("5. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        name = input("Enter Name: ")
        age = int(input("Enter Age: "))
        grade = input("Enter Grade: ")

        students.insert_one({
            "name": name,
            "age": age,
            "grade": grade
        })

        print("Student Added")

    elif choice == "2":
        for student in students.find():
            print(student)

    elif choice == "3":
        name = input("Enter Student Name: ")
        new_grade = input("Enter New Grade: ")

        students.update_one(
            {"name": name},
            {"$set": {"grade": new_grade}}
        )

        print("Student Updated")

    elif choice == "4":
        name = input("Enter Student Name: ")

        students.delete_one({"name": name})

        print("Student Deleted")

    elif choice == "5":
        print("Thank You")
        break

    else:
        print("Invalid Choice")