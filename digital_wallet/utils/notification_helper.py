from datetime import datetime
from database import db

async def create_notification(user_id: str, message: str):
    notification = {
        "user_id": user_id,
        "message": message,
        "is_read": False,
        "created_at": datetime.utcnow()
    }

    await db.notifications.insert_one(notification)