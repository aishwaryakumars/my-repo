from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import fastapi.middleware.cors as corsMiddleware
from database import students_collection
from models import Student

app = FastAPI(
    title="Student CRUD API",
    description="API for managing student records",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    corsMiddleware.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/students")
def create_student(student: Student):
    existing_student = students_collection.find_one({"email": student.email})
    if existing_student:
        raise HTTPException(status_code=400, detail="Email already exists")

    result = students_collection.insert_one(student.dict())
    return {"message": "Student created successfully", "id": str(result.inserted_id)}


@app.get("/students/{email}")
def get_student(email: str):
    student = students_collection.find_one({"email": email})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student["_id"] = str(student["_id"])
    return {
        "id": student["_id"],
        "name": student["name"],
        "email": student["email"],
        "age": student["age"],
        "course": student["course"]
    }


@app.put("/students/{email}")
def update_student(email: str, course: str):
    result = students_collection.update_one(
        {"email": email},
        {"$set": {"course": course}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student course updated successfully"}


@app.delete("/students/{email}")
def delete_student(email: str):
    result = students_collection.delete_one({"email": email})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted successfully"}


# static + frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")