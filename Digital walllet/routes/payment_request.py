from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime

from database import db
from auth.jwt_handler import get_current_user
from utils.notification_helper import create_notification

router = APIRouter(
    prefix="/payment-requests",
    tags=["Payment Requests"]
)


class PaymentRequestCreate(BaseModel):
    receiver_id: str
    amount: float


@router.post("/")
async def request_money(
    request: PaymentRequestCreate,
    current_user=Depends(get_current_user)
):

    receiver = await db.users.find_one(
        {"_id": ObjectId(request.receiver_id)}
    )

    if not receiver:
        raise HTTPException(
            status_code=404,
            detail="Receiver not found"
        )

    payment_request = {
        "sender_id": str(current_user["_id"]),
        "receiver_id": request.receiver_id,
        "amount": request.amount,
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = await db.payment_requests.insert_one(
        payment_request
    )

    await create_notification(
        request.receiver_id,
        f"Payment request of ₹{request.amount} received"
    )

    return {
        "message": "Request sent",
        "request_id": str(result.inserted_id)
    }


@router.get("/")
async def get_requests(
    current_user=Depends(get_current_user)
):

    requests = await db.payment_requests.find(
        {
            "receiver_id": str(current_user["_id"])
        }
    ).to_list(length=100)

    for req in requests:
        req["_id"] = str(req["_id"])

    return requests


@router.post("/{request_id}/accept")
async def accept_request(
    request_id: str,
    current_user=Depends(get_current_user)
):

    request = await db.payment_requests.find_one(
        {"_id": ObjectId(request_id)}
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    if request["status"] != "pending":
        raise HTTPException(
            status_code=400,
            detail="Already processed"
        )

    payer_wallet = await db.wallets.find_one(
        {
            "user_id": request["receiver_id"]
        }
    )

    requester_wallet = await db.wallets.find_one(
        {
            "user_id": request["sender_id"]
        }
    )

    if payer_wallet["balance"] < request["amount"]:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    await db.wallets.update_one(
        {
            "user_id": request["receiver_id"]
        },
        {
            "$inc": {
                "balance": -request["amount"]
            }
        }
    )

    await db.wallets.update_one(
        {
            "user_id": request["sender_id"]
        },
        {
            "$inc": {
                "balance": request["amount"]
            }
        }
    )

    transaction = {
        "sender_id": request["receiver_id"],
        "receiver_id": request["sender_id"],
        "amount": request["amount"],
        "type": "payment_request",
        "created_at": datetime.utcnow()
    }

    await db.transactions.insert_one(transaction)

    await db.payment_requests.update_one(
        {
            "_id": ObjectId(request_id)
        },
        {
            "$set": {
                "status": "accepted"
            }
        }
    )

    await create_notification(
        request["sender_id"],
        f"Your request for ₹{request['amount']} was accepted"
    )

    return {
        "message": "Payment request accepted"
    }


@router.post("/{request_id}/reject")
async def reject_request(
    request_id: str,
    current_user=Depends(get_current_user)
):

    request = await db.payment_requests.find_one(
        {"_id": ObjectId(request_id)}
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    await db.payment_requests.update_one(
        {
            "_id": ObjectId(request_id)
        },
        {
            "$set": {
                "status": "rejected"
            }
        }
    )

    await create_notification(
        request["sender_id"],
        f"Your request for ₹{request['amount']} was rejected"
    )

    return {
        "message": "Payment request rejected"
    }