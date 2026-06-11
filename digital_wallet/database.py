from pymongo import MongoClient

client = MongoClient("mongodb+srv://Aishwarya:Aish123@aishwarya.gk6q14b.mongodb.net/?appName=Aishwarya")

db = client["DIGITAL_WALLET"]

users_collection = db["users"]
wallets_collection = db["wallets"]
transactions_collection = db["transactions"]
payment_requests_collection = db["payment_requests"]
notifications_collection = db["notifications"]