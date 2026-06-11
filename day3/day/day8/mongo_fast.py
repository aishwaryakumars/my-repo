from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["StudentDB"]
students = db["trial"]


# Pydantic Model
class Student(BaseModel):
    name: str
    age: int
    grade: str


# Helper Function
def student_serializer(student):
    return {
        "id": str(student["_id"]),
        "name": student["name"],
        "age": student["age"],
        "grade": student["grade"]
    }


# 1. Add Student
@app.post("/students")
def add_student(student: Student):
    result = students.insert_one(student.dict())

    return {
        "message": "Student Added",
        "id": str(result.inserted_id)
    }


# 2. View All Students
@app.get("/students")
def get_students():
    all_students = []

    for student in students.find():
        all_students.append(student_serializer(student))

    return all_students


# 3. View Single Student
@app.get("/students/{name}")
def get_student(name: str):
    student = students.find_one({"name": name})

    if not student:
        raise HTTPException(status_code=404, detail="Student Not Found")

    return student_serializer(student)


# 4. Update Student Grade
@app.put("/students/{name}")
def update_student(name: str, grade: str):
    result = students.update_one(
        {"name": name},
        {"$set": {"grade": grade}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student Not Found")

    return {"message": "Student Updated"}


# 5. Delete Student
@app.delete("/students/{name}")
def delete_student(name: str):
    result = students.delete_one({"name": name})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student Not Found")

    return {"message": "Student Deleted"}