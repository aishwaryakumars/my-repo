from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from database import db
from auth.jwt_handler import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
async def get_notifications(
    current_user=Depends(get_current_user)
):

    notifications = await db.notifications.find(
        {
            "user_id": str(current_user["_id"])
        }
    ).sort("created_at", -1).to_list(length=100)

    for n in notifications:
        n["_id"] = str(n["_id"])

    return notifications


@router.put("/{notification_id}")
async def mark_as_read(
    notification_id: str,
    current_user=Depends(get_current_user)
):

    notification = await db.notifications.find_one(
        {
            "_id": ObjectId(notification_id)
        }
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    if notification["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )

    await db.notifications.update_one(
        {"_id": ObjectId(notification_id)},
        {
            "$set": {
                "is_read": True
            }
        }
    )

    return {"message": "Notification marked as read"}