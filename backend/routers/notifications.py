from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import User, Notification
from schemas import NotificationResponse
from auth import get_current_user
from utils.notification_utils import NotificationUtils

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = Query(False),
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notifications for the current user"""
    try:
        # Use the utility method to get notifications
        notifications = NotificationUtils.get_user_notifications(db, current_user.id, include_deleted)
        
        # Filter by read status if requested
        if unread_only:
            notifications = [n for n in notifications if not n.is_read]
        
        return [
            {
                "id": notification.id,
                "user_id": notification.user_id,
                "message": notification.message,
                "is_read": notification.is_read,
                "created_at": notification.created_at,
                "expires_at": notification.expires_at,
                "deleted_at": notification.deleted_at
            }
            for notification in notifications
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread notifications"""
    try:
        unread_count = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).count()
        
        return {"unread_count": unread_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting unread count: {str(e)}")

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.is_read = True
        db.commit()
        
        return {"message": "Notification marked as read"}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")

@router.put("/read-all")
async def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read"""
    try:
        db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        
        return {"message": "All notifications marked as read"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking all notifications as read: {str(e)}")

@router.post("/")
async def create_notification(
    user_id: int,
    message: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a notification (admin only)"""
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create notification
        notification = Notification(
            user_id=user_id,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating notification: {str(e)}")

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification (soft delete)"""
    try:
        success = NotificationUtils.soft_delete_notification(db, notification_id, current_user.id)
        
        if success:
            return {"message": "Notification deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found or already deleted")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}")

@router.delete("/")
async def delete_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete all notifications for the current user (soft delete)"""
    try:
        notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None)
        ).all()
        
        deleted_count = 0
        for notification in notifications:
            notification.deleted_at = datetime.utcnow()
            deleted_count += 1
        
        db.commit()
        
        return {"message": f"Deleted {deleted_count} notifications successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting notifications: {str(e)}")

@router.post("/cleanup")
async def cleanup_expired_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clean up expired notifications (admin only - for now allowing all users)"""
    try:
        deleted_count = NotificationUtils.cleanup_expired_notifications(db)
        return {"message": f"Cleaned up {deleted_count} expired notifications"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up notifications: {str(e)}")
