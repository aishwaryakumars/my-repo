import os
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

# =======================================================
# 1. CORE SERVER INITIALIZATION
# =======================================================
app = FastAPI(
    title="DigiWallet Core Backbone Engine",
    description="Production-grade secure ledger routing synchronization system.",
    version="4.0.0"
)

os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# =======================================================
# 2. DATABASE CONFIGURATION (MONGODB)
# =======================================================
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["digital_wallet_db"]

users_collection = db["users"]
wallets_collection = db["wallets"]

# =======================================================
# 3. UNIFIED INPUT VALIDATION SCHEMAS
# =======================================================
class UserRegisterSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=4)

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UnifiedTransactionSchema(BaseModel):
    email: EmailStr
    amount: float
    purpose: str
class Transaction(BaseModel):
    email: str
    amount: float
    purpose: str = "General"
    type: str = "add_money" # 'add_money' or 'spend_money'

# =======================================================
# 4. BROWSER PAGE ROUTING (HTML RENDERING)
# =======================================================
@app.get("/", response_class=HTMLResponse, tags=["UI Pages"])
async def render_login_gateway_view(request: Request): 
    return templates.TemplateResponse(request=request, name="login.html", context={})

@app.get("/register-page", response_class=HTMLResponse, tags=["UI Pages"])
async def render_registration_gateway_view(request: Request): 
    return templates.TemplateResponse(request=request, name="register.html", context={})

@app.get("/dashboard", response_class=HTMLResponse, tags=["UI Pages"])
async def render_dashboard_gateway_view(request: Request): 
    return templates.TemplateResponse(request=request, name="dashboard.html", context={})

@app.get("/analytics-page", response_class=HTMLResponse, tags=["UI Pages"])
async def render_analytics_gateway_view(request: Request): 
    return templates.TemplateResponse(request=request, name="analytics.html", context={})

@app.get("/history-page", response_class=HTMLResponse, tags=["UI Pages"])
async def render_history_log_ledgers_gateway_view(request: Request): 
    return templates.TemplateResponse(request=request, name="history.html", context={})

# =======================================================
# 5. USER AUTHENTICATION ENDPOINTS
# =======================================================
@app.post("/register", status_code=status.HTTP_201_CREATED, tags=["Auth Systems"])
async def register_user_identity_context(user_payload: UserRegisterSchema):
    cleaned_email = user_payload.email.lower().strip()
    existing_user = await users_collection.find_one({"email": cleaned_email})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified email registry node already active."
        )
    
    user_data = {
        "name": user_payload.name.strip(),
        "email": cleaned_email,
        "password": user_payload.password 
    }
    result = await users_collection.insert_one(user_data)
    
    await wallets_collection.update_one(
        {"email": cleaned_email},
        {
            "$setOnInsert": {
                "user_id": result.inserted_id,
                "email": cleaned_email,
                "balance": 0.0,
                "salary": 0.0,
                "ledger_history": []
            }
        },
        upsert=True
    )
    return {"status": "Success", "message": "Identity context instantiated successfully."}

@app.post("/login", tags=["Auth Systems"])
async def process_gateway_authorization(login_payload: UserLoginSchema):
    cleaned_email = login_payload.email.lower().strip()
    db_user = await users_collection.find_one({"email": cleaned_email})
    
    if not db_user or db_user["password"] != login_payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid tracking credentials metadata matched."
        )
        
    return {
        "message": "Authorization verified.", 
        "email": db_user["email"], 
        "name": db_user["name"]
    }

# =======================================================
# 6. LIVE SYNCHRONIZATION DATA FETCHERS (GET DATA)
# =======================================================
# In main.py
@app.get("/balance/{email}")
async def get_wallet_balance(email: str):
    wallet = await wallets_collection.find_one({"email": email.lower().strip()})
    if not wallet: return {"balance": 0.0}
    
    # Summing all amounts in the history (deposits +, withdrawals -)
    total = sum(item.get("amount", 0) for item in wallet.get("ledger_history", []))
    return {"balance": total}

@app.get("/salary/{email}", tags=["Data Sync Engine"])
async def get_wallet_salary(email: str):
    cleaned_email = email.lower().strip()
    wallet = await wallets_collection.find_one({"email": cleaned_email})
    if not wallet:
        return {"salary": 0.0}
    return {"salary": wallet.get("salary", 0.0)}

# =======================================================
# 7. MUTATION TRANSACTIONS & LEGER AUDIT LOGGER (POST DATA)
# =======================================================

# SALARY UPDATE MUTATOR
@app.post("/update-salary", tags=["Ledger Actions"])
async def update_salary_allocation(payload: UnifiedTransactionSchema):
    target_email = payload.email.lower().strip()
    
    audit_entry = {
        "transaction_id": str(ObjectId()),
        "type": "Salary Base Matrix Re-allocation",
        "amount": payload.amount,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Verified"
    }

    await wallets_collection.update_one(
        {"email": target_email},
        {
            "$set": {"salary": payload.amount, "email": target_email},
            "$push": {"ledger_history": audit_entry}
        },
        upsert=True
    )
    return {"status": "Success", "new_salary": payload.amount}

# DEPOSIT FUNDS MUTATOR (INBOUND)
@app.post("/add-money", tags=["Ledger Actions"])
async def deposit_funds_ledger(payload: UnifiedTransactionSchema):
    target_email = payload.email.lower().strip()
    
    audit_entry = {
        "transaction_id": str(ObjectId()),
        "type": f"Deposit: {payload.purpose}",
        "amount": payload.amount,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Verified"
    }

    await wallets_collection.update_one(
        {"email": target_email},
        {
            "$inc": {"balance": payload.amount},
            "$push": {"ledger_history": audit_entry}
        },
        upsert=True
    )
    return {"status": "Success", "operation": "Inflow Credit Authorized"}

# WITHDRAW FUNDS MUTATOR (OUTBOUND)
@app.post("/withdrawn", tags=["Ledger Actions"])
async def withdraw_funds_ledger(payload: UnifiedTransactionSchema):
    target_email = payload.email.lower().strip()
    
    # Ensure the purpose is saved exactly as it appears in your master list
    # Use the 'purpose' sent from your frontend
    purpose = payload.purpose if payload.purpose else "General Miscellaneous Logistics"

    audit_entry = {
        "transaction_id": str(ObjectId()),
        "type": f"Withdrawal: {purpose}", # This must match your Analytics key
        "amount": -payload.amount,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Verified"
    }

    await wallets_collection.update_one(
        {"email": target_email},
        {
            "$inc": {"balance": -payload.amount},
            "$push": {"ledger_history": audit_entry}
        },
        upsert=True
    )
    return {"status": "Success"}
# Add these to your FastAPI main.py
@app.get("/balance/{email}")
async def get_wallet_balance(email: str):
    wallet = await wallets_collection.find_one({"email": email.lower().strip()})
    if not wallet: return {"balance": 0.0}
    
    # Calculate balance by summing every transaction in history
    # This ignores the 'balance' field entirely
    history = wallet.get("ledger_history", [])
    actual_balance = sum(item.get("amount", 0) for item in history)
    
    return {"balance": actual_balance}
@app.get("/api/transactions/{email}")
async def get_transactions(email: str):
    # This must return a list of transaction objects
    return []
@app.post("/add-money")
async def add_money(tx: Transaction):
    try:
        # 1. Logic: Find user in your DB and update their balance
        # Example pseudo-code:
        # database.update_balance(tx.email, tx.amount)
        # database.log_transaction(tx)
        
        return {"status": "success", "message": "Transaction recorded"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# Ensure this exact path exists in your FastAPI file
@app.post("/add-money") 
async def add_money(data: dict):
    # Your logic here to save to the database
    return {"status": "success"}
# =======================================================
# CORRECTED ANALYTICS ROUTE
# =======================================================
@app.get("/analytics/{email}")
async def get_analytics(email: str):
    target_email = email.lower().strip()
    wallet = await wallets_collection.find_one({"email": target_email})
    
    breakdown = {
        "Food & Groceries": 0.0,
        "Rent & Utilities": 0.0,
        "Entertainment & Travel": 0.0,
        "General Miscellaneous Logistics": 0.0
    }
    
    if not wallet or "ledger_history" not in wallet:
        return {"monthly_savings": 0.0, "monthly_spending": 0.0, "purpose_breakdown_spending": breakdown}

    ledger = wallet.get("ledger_history", [])
    savings = 0.0
    spending = 0.0

    # CORRECTED INDENTATION STARTS HERE
    for entry in ledger:
        amt = abs(float(entry.get("amount", 0)))
        tx_type = entry.get("type", "").lower() 
        
        if float(entry.get("amount", 0)) > 0:
            savings += amt
        else:
            spending += amt
            
            mapping_rules = {
                "Food & Groceries": ["food", "grocery"],
                "Rent & Utilities": ["rent", "utility", "bill"],
                "Entertainment & Travel": ["entertainment", "travel", "movie", "trip"],
            }
            
            matched = False
            for category, keywords in mapping_rules.items():
                if any(keyword in tx_type for keyword in keywords):
                    breakdown[category] += amt
                    matched = True
                    break
            
            if not matched and "withdrawal" in tx_type:
                breakdown["General Miscellaneous Logistics"] += amt
                
    return {
        "monthly_savings": savings,
        "monthly_spending": spending,
        "purpose_breakdown_spending": breakdown
    }

# =======================================================
# CLEANUP: REMOVE DUPLICATE ROUTES
# =======================================================
# Ensure you only have ONE '/add-money' route.
# If you have two, delete the simple one and keep the one with the database logic.
    
@app.get("/api/ledger-history/{email}")
async def get_ledger_history(email: str):
    wallet = await wallets_collection.find_one({"email": email.lower().strip()})
    if not wallet:
        return {"history": []}
    
    # Return the ledger, reversed so the newest transaction is at the top
    history = wallet.get("ledger_history", [])
    return {"history": history[::-1]}
@app.post("/update-salary", tags=["Ledger Actions"])
async def update_salary_allocation(payload: UnifiedTransactionSchema):
    target_email = payload.email.lower().strip()
    
    # Update the document. If it doesn't exist, create it (upsert).
    result = await wallets_collection.update_one(
        {"email": target_email},
        {
            "$set": {"salary": payload.amount}
        },
        upsert=True
    )
    return {"status": "Success", "new_salary": payload.amount}
# Ensure this is your logic in main.py
@app.post("/withdrawn", tags=["Ledger Actions"])
async def withdraw_funds_ledger(payload: UnifiedTransactionSchema):
    target_email = payload.email.lower().strip()
    
    # Force negative for ledger consistency
    withdrawal_amount = -abs(payload.amount)
    
    audit_entry = {
        "transaction_id": str(ObjectId()),
        "type": f"Withdrawal: {payload.purpose}",
        "amount": withdrawal_amount, 
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Verified"
    }

    # REMOVED '$inc' because it relies on potentially corrupted data.
    # We only update the ledger_history.
    await wallets_collection.update_one(
        {"email": target_email},
        {
            "$push": {"ledger_history": audit_entry}
        },
        upsert=True
    )
    return {"status": "Success"}