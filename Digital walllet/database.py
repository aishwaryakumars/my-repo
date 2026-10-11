from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["DIGITAL_WALLET"]

users_collection = db["users"]
wallets_collection = db["wallets"]
transactions_collection = db["transactions"]
payment_requests_collection = db["payment_requests"]
notifications_collection = db["notifications"]