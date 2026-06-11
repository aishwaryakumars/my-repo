from pymongo import MongoClient
import certifi
client = MongoClient("mongodb+srv://Aishwarya:Aish123@aishwarya.gk6q14b.mongodb.net/?appName=Aishwarya"
                     ,tlsCAFile=certifi.where())
db=client["StudentDB"]
students_collection=db["students"] 