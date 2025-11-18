"""
Notification utility functions for creating various types of notifications
"""
from sqlalchemy.orm import Session
from models import Notification, User, Message, Product, Order
from datetime import datetime, timedelta
from typing import Optional

class NotificationUtils:
    """Utility class for creating different types of notifications"""
    
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        message: str,
        notification_type: str = "general"
    ) -> Notification:
        """Create a notification for a user with 30-day expiration"""
        now = datetime.utcnow()
        expires_at = now + timedelta(days=30)  # Auto-delete after 30 days
        
        notification = Notification(
            user_id=user_id,
            message=message,
            is_read=False,
            created_at=now,
            expires_at=expires_at
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def notify_new_message(db: Session, message: Message) -> None:
        """Notify user when they receive a new message"""
        # Don't notify if it's the user's own message
        if message.sender_id == message.receiver_id:
            return
            
        # Get sender info for the notification
        sender = db.query(User).filter(User.id == message.sender_id).first()
        if not sender:
            return
            
        notification_message = f"New message from {sender.name} {sender.surname}: {message.message[:50]}{'...' if len(message.message) > 50 else ''}"
        
        NotificationUtils.create_notification(
            db=db,
            user_id=message.receiver_id,
            message=notification_message,
            notification_type="message"
        )
    
    @staticmethod
    def notify_product_approved(db: Session, product: Product) -> None:
        """Notify user when their product is approved"""
        notification_message = f"Great news! Your product '{product.title}' has been approved and is now live in the marketplace."
        
        NotificationUtils.create_notification(
            db=db,
            user_id=product.seller_id,
            message=notification_message,
            notification_type="product_approved"
        )
    
    @staticmethod
    def notify_product_rejected(db: Session, product: Product, reason: str = None) -> None:
        """Notify user when their product is rejected"""
        reason_text = f" Reason: {reason}" if reason else ""
        notification_message = f"Your product '{product.title}' was not approved.{reason_text} Please review and resubmit."
        
        NotificationUtils.create_notification(
            db=db,
            user_id=product.seller_id,
            message=notification_message,
            notification_type="product_rejected"
        )
    
    @staticmethod
    def notify_new_order(db: Session, order: Order) -> None:
        """Notify admin when a new order is placed"""
        # Get customer info
        customer = db.query(User).filter(User.id == order.user_id).first()
        customer_name = f"{customer.name} {customer.surname}" if customer else "Unknown Customer"
        
        notification_message = f"New order #{order.id} from {customer_name} for R{order.total_amount:.2f}"
        
        # Notify admin (assuming admin user ID is 1)
        NotificationUtils.create_notification(
            db=db,
            user_id=1,  # Admin user ID
            message=notification_message,
            notification_type="new_order"
        )
    
    @staticmethod
    def notify_order_status_update(db: Session, order: Order, new_status: str) -> None:
        """Notify user when their order status is updated"""
        status_messages = {
            "processing": "Your order is being processed",
            "shipped": "Your order has been shipped! You'll receive tracking details soon.",
            "delivered": "Your order has been delivered! Thank you for your purchase.",
            "cancelled": "Your order has been cancelled. If you have any questions, please contact support."
        }
        
        message = status_messages.get(new_status, f"Your order status has been updated to: {new_status}")
        notification_message = f"Order #{order.id}: {message}"
        
        NotificationUtils.create_notification(
            db=db,
            user_id=order.user_id,
            message=notification_message,
            notification_type="order_update"
        )
    
    @staticmethod
    def notify_low_stock(db: Session, product: Product) -> None:
        """Notify seller when their product is running low on stock"""
        notification_message = f"Low stock alert: '{product.title}' has only {product.stock_quantity} items left. Consider restocking soon."
        
        NotificationUtils.create_notification(
            db=db,
            user_id=product.seller_id,
            message=notification_message,
            notification_type="low_stock"
        )
    
    @staticmethod
    def notify_out_of_stock(db: Session, product: Product) -> None:
        """Notify seller when their product is out of stock"""
        notification_message = f"Out of stock: '{product.title}' is now out of stock. Please restock to continue selling."
        
        NotificationUtils.create_notification(
            db=db,
            user_id=product.seller_id,
            message=notification_message,
            notification_type="out_of_stock"
        )
    
    @staticmethod
    def notify_product_sold(db: Session, product: Product, quantity: int, order_id: int) -> None:
        """Notify seller when their product is sold"""
        notification_message = f"Sale! {quantity} unit(s) of '{product.title}' sold in order #{order_id}"
        
        NotificationUtils.create_notification(
            db=db,
            user_id=product.seller_id,
            message=notification_message,
            notification_type="product_sold"
        )
    
    @staticmethod
    def notify_admin_new_user(db: Session, user: User) -> None:
        """Notify admin when a new user registers"""
        notification_message = f"New user registered: {user.name} {user.surname} ({user.email})"
        
        NotificationUtils.create_notification(
            db=db,
            user_id=1,  # Admin user ID
            message=notification_message,
            notification_type="new_user"
        )
    
    @staticmethod
    def notify_user_welcome(db: Session, user: User) -> None:
        """Send welcome notification to new user"""
        notification_message = f"Welcome to Student Marketplace, {user.name}! Start by exploring products or listing your own items for sale."
        
        NotificationUtils.create_notification(
            db=db,
            user_id=user.id,
            message=notification_message,
            notification_type="welcome"
        )
    
    @staticmethod
    def cleanup_expired_notifications(db: Session) -> int:
        """Delete notifications that have expired (older than 30 days)"""
        now = datetime.utcnow()
        try:
            # Try with deleted_at check first (if column exists)
            expired_count = db.query(Notification).filter(
                Notification.expires_at < now,
                Notification.deleted_at.is_(None)  # Only delete non-manually deleted notifications
            ).count()
            
            db.query(Notification).filter(
                Notification.expires_at < now,
                Notification.deleted_at.is_(None)
            ).delete(synchronize_session=False)
        except Exception:
            # If deleted_at column doesn't exist, just delete expired notifications
            expired_count = db.query(Notification).filter(
                Notification.expires_at < now
            ).count()
            
            db.query(Notification).filter(
                Notification.expires_at < now
            ).delete(synchronize_session=False)
        
        db.commit()
        return expired_count
    
    @staticmethod
    def soft_delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
        """Soft delete a notification (mark as deleted)"""
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.deleted_at.is_(None)  # Only delete if not already deleted
            ).first()
            
            if notification:
                notification.deleted_at = datetime.utcnow()
                db.commit()
                return True
        except Exception:
            # If deleted_at column doesn't exist, just delete the notification
            notification = db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if notification:
                db.delete(notification)
                db.commit()
                return True
        return False
    
    @staticmethod
    def get_user_notifications(db: Session, user_id: int, include_deleted: bool = False) -> list:
        """Get notifications for a user, optionally including deleted ones"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        try:
            if not include_deleted:
                query = query.filter(Notification.deleted_at.is_(None))
        except Exception:
            # If deleted_at column doesn't exist, just return all notifications
            pass
        
        return query.order_by(Notification.created_at.desc()).all()
