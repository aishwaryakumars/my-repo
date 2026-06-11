from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request
from database import (
    users_collection,
    wallets_collection,
    transactions_collection,
    payment_requests_collection,
    notifications_collection
)
from datetime import datetime
from collections import deque

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


# =========================
# MODELS
# =========================

class User(BaseModel):
    name: str
    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str


class Wallet(BaseModel):
    email: str


class Money(BaseModel):
    email: str
    amount: float


class Transfer(BaseModel):
    sender_email: str
    receiver_email: str
    amount: float


class PaymentRequest(BaseModel):
    requester_email: str
    payer_email: str
    amount: float

# =========================
# BFS FUNCTIONS
# =========================

def build_transaction_graph():

    graph = {}

    transactions = transactions_collection.find()

    for txn in transactions:

        sender = txn.get("sender")
        receiver = txn.get("receiver")

        if sender and receiver:

            if sender not in graph:
                graph[sender] = []

            graph[sender].append(receiver)

    return graph


def bfs(graph, start, target):

    queue = deque([[start]])
    visited = set()

    while queue:

        path = queue.popleft()
        current = path[-1]

        if current == target:
            return path

        if current not in visited:

            visited.add(current)

            for neighbor in graph.get(current, []):

                new_path = path.copy()
                new_path.append(neighbor)

                queue.append(new_path)

    return None


# =========================
# REGISTER
# =========================

@app.post("/register")
def register(user: User):

    existing_user = users_collection.find_one(
        {"email": user.email}
    )

    if existing_user:
        return {"message": "Email already registered"}

    users_collection.insert_one(user.dict())

    return {"message": "User Registered Successfully"}


# =========================
# LOGIN
# =========================

@app.post("/login")
def login(user: Login):

    db_user = users_collection.find_one(
        {"email": user.email}
    )

    if not db_user:
        return {"message": "User not found"}

    if db_user["password"] != user.password:
        return {"message": "Wrong password"}

    return {"message": "Login Successful"}


# =========================
# CREATE WALLET
# =========================

@app.post("/create-wallet")
def create_wallet(wallet: Wallet):

    existing = wallets_collection.find_one(
        {"email": wallet.email}
    )

    if existing:
        return {"message": "Wallet already exists"}

    wallets_collection.insert_one({
        "email": wallet.email,
        "balance": 0
    })

    return {"message": "Wallet created successfully"}


# =========================
# ADD MONEY
# =========================

@app.post("/add-money")
def add_money(data: Money):

    wallet = wallets_collection.find_one(
        {"email": data.email}
    )

    if not wallet:
        return {"message": "Wallet not found"}

    new_balance = wallet["balance"] + data.amount

    wallets_collection.update_one(
        {"email": data.email},
        {"$set": {"balance": new_balance}}
    )

    transactions_collection.insert_one({
        "email": data.email,
        "type": "CREDIT",
        "amount": data.amount,
        "balance_after": new_balance,
        "time": datetime.utcnow()
    })

    return {
        "message": "Money added successfully",
        "balance": new_balance
    }


# =========================
# WITHDRAW
# =========================

@app.post("/withdraw")
def withdraw(data: Money):

    wallet = wallets_collection.find_one(
        {"email": data.email}
    )

    if not wallet:
        return {"message": "Wallet not found"}

    if wallet["balance"] < data.amount:
        return {"message": "Insufficient balance"}

    new_balance = wallet["balance"] - data.amount

    wallets_collection.update_one(
        {"email": data.email},
        {"$set": {"balance": new_balance}}
    )

    transactions_collection.insert_one({
        "email": data.email,
        "type": "DEBIT",
        "amount": data.amount,
        "balance_after": new_balance,
        "time": datetime.utcnow()
    })

    return {
        "message": "Withdrawal successful",
        "balance": new_balance
    }


# =========================
# BALANCE
# =========================

@app.get("/balance/{email}")
def get_balance(email: str):

    wallet = wallets_collection.find_one(
        {"email": email}
    )

    if not wallet:
        return {"message": "Wallet not found"}

    return {
        "email": email,
        "balance": wallet["balance"]
    }


# =========================
# TRANSACTIONS
# =========================

@app.get("/transactions/{email}")
def get_transactions(email: str):

    data = list(
        transactions_collection.find(
            {
                "$or": [
                    {"sender": email},
                    {"receiver": email},
                    {"email": email}
                ]
            },
            {"_id": 0}
        )
    )

    graph = build_transaction_graph()

    connected_users = []

    queue = deque([email])
    visited = set()

    while queue:

        current = queue.popleft()

        if current not in visited:

            visited.add(current)

            for neighbor in graph.get(current, []):

                connected_users.append(neighbor)
                queue.append(neighbor)

    return {
        "email": email,
        "transactions": data,
        "reachable_users_using_bfs": list(set(connected_users))
    }

# =========================
# TRANSFER MONEY
# =========================

@app.post("/transfer")
def transfer_money(data: Transfer):

    sender_wallet = wallets_collection.find_one(
        {"email": data.sender_email}
    )

    receiver_wallet = wallets_collection.find_one(
        {"email": data.receiver_email}
    )

    if not sender_wallet:
        return {"message": "Sender wallet not found"}

    if not receiver_wallet:
        return {"message": "Receiver wallet not found"}

    if sender_wallet["balance"] < data.amount:
        return {"message": "Insufficient balance"}

    wallets_collection.update_one(
        {"email": data.sender_email},
        {"$inc": {"balance": -data.amount}}
    )

    wallets_collection.update_one(
        {"email": data.receiver_email},
        {"$inc": {"balance": data.amount}}
    )

    transactions_collection.insert_one({
        "sender": data.sender_email,
        "receiver": data.receiver_email,
        "amount": data.amount,
        "type": "TRANSFER",
        "time": datetime.utcnow()
    })

    notifications_collection.insert_one({
        "email": data.receiver_email,
        "message": f"You received ₹{data.amount} from {data.sender_email}",
        "time": datetime.utcnow()
    })

    return {"message": "Transfer successful"}


# =========================
# REQUEST MONEY
# =========================

@app.post("/request-money")
def request_money(data: PaymentRequest):

    payment_requests_collection.insert_one({
        "requester_email": data.requester_email,
        "payer_email": data.payer_email,
        "amount": data.amount,
        "status": "PENDING",
        "time": datetime.utcnow()
    })

    notifications_collection.insert_one({
        "email": data.payer_email,
        "message": f"{data.requester_email} requested ₹{data.amount}",
        "time": datetime.utcnow()
    })

    return {"message": "Payment request sent"}


# =========================
# VIEW REQUESTS
# =========================

@app.get("/requests/{email}")
def get_requests(email: str):

    requests = list(
        payment_requests_collection.find(
            {"payer_email": email},
            {"_id": 0}
        )
    )

    return requests


# =========================
# ACCEPT REQUEST
# =========================

@app.post("/accept-request")
def accept_request(data: PaymentRequest):

    payer_wallet = wallets_collection.find_one(
        {"email": data.payer_email}
    )

    requester_wallet = wallets_collection.find_one(
        {"email": data.requester_email}
    )

    if not payer_wallet:
        return {"message": "Payer wallet not found"}

    if not requester_wallet:
        return {"message": "Requester wallet not found"}

    if payer_wallet["balance"] < data.amount:
        return {"message": "Insufficient balance"}

    wallets_collection.update_one(
        {"email": data.payer_email},
        {"$inc": {"balance": -data.amount}}
    )

    wallets_collection.update_one(
        {"email": data.requester_email},
        {"$inc": {"balance": data.amount}}
    )

    payment_requests_collection.update_one(
        {
            "requester_email": data.requester_email,
            "payer_email": data.payer_email,
            "amount": data.amount,
            "status": "PENDING"
        },
        {
            "$set": {"status": "ACCEPTED"}
        }
    )

    transactions_collection.insert_one({
        "sender": data.payer_email,
        "receiver": data.requester_email,
        "amount": data.amount,
        "type": "PAYMENT_REQUEST",
        "time": datetime.utcnow()
    })

    notifications_collection.insert_one({
        "email": data.requester_email,
        "message": f"{data.payer_email} accepted your request of ₹{data.amount}",
        "time": datetime.utcnow()
    })

    return {"message": "Request accepted"}


# =========================
# REJECT REQUEST
# =========================

@app.post("/reject-request")
def reject_request(data: PaymentRequest):

    payment_requests_collection.update_one(
        {
            "requester_email": data.requester_email,
            "payer_email": data.payer_email,
            "amount": data.amount,
            "status": "PENDING"
        },
        {
            "$set": {"status": "REJECTED"}
        }
    )

    notifications_collection.insert_one({
        "email": data.requester_email,
        "message": f"{data.payer_email} rejected your request of ₹{data.amount}",
        "time": datetime.utcnow()
    })

    return {"message": "Request rejected"}


# =========================
# NOTIFICATIONS
# =========================

@app.get("/notifications/{email}")
def get_notifications(email: str):

    notifications = list(
        notifications_collection.find(
            {"email": email},
            {"_id": 0}
        )
    )

    return notifications
@app.get("/transaction-network")
def transaction_network(
    sender_email: str,
    receiver_email: str
):

    graph = build_transaction_graph()

    path = bfs(
        graph,
        sender_email,
        receiver_email
    )

    if path:

        return {
            "path_found": True,
            "transaction_path": path,
            "connections": len(path) - 1
        }

    return {
        "path_found": False,
        "message": "No transaction path found"
    }


# =========================
# FRONTEND
# =========================

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )