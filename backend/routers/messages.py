from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from sqlalchemy import or_, and_

from database import get_db
from models import User, Message
from schemas import MessageResponse, MessageCreate
from auth import get_current_user
from utils.notification_utils import NotificationUtils
from websocket_manager import manager

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages for the current user"""
    try:
        query = db.query(Message).filter(
            or_(
                Message.sender_id == current_user.id,
                Message.receiver_id == current_user.id
            )
        )
        
        if user_id:
            query = query.filter(
                or_(
                    Message.sender_id == user_id,
                    Message.receiver_id == user_id
                )
            )
        
        messages = query.options(
            joinedload(Message.sender),
            joinedload(Message.receiver)
        ).order_by(Message.created_at.asc()).all()
        
        return [
            {
                "id": message.id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "message": message.message,
                "message_type": message.message_type,
                "conversation_id": message.conversation_id,
                "is_read": message.is_read,
                "is_important": message.is_important,
                "parent_message_id": message.parent_message_id,
                "created_at": message.created_at,
                "updated_at": message.updated_at,
                "sender": {
                    "id": message.sender.id,
                    "name": message.sender.name,
                    "surname": message.sender.surname,
                    "email": message.sender.email,
                    "username": message.sender.username,
                    "phone": message.sender.phone,
                    "profile_img": message.sender.profile_img,
                    "created_at": message.sender.created_at
                },
                "receiver": {
                    "id": message.receiver.id,
                    "name": message.receiver.name,
                    "surname": message.receiver.surname,
                    "email": message.receiver.email,
                    "username": message.receiver.username,
                    "phone": message.receiver.phone,
                    "profile_img": message.receiver.profile_img,
                    "created_at": message.receiver.created_at
                }
            }
            for message in messages
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")

@router.post("/", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message"""
    try:
        # Check if receiver exists
        receiver = db.query(User).filter(User.id == message_data.receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver not found")
        
        # Generate conversation ID if not provided
        conversation_id = message_data.conversation_id
        if not conversation_id:
            # Check if there's already a conversation between these users
            existing_conversation = db.query(Message.conversation_id).filter(
                Message.conversation_id.isnot(None),
                or_(
                    and_(Message.sender_id == current_user.id, Message.receiver_id == message_data.receiver_id),
                    and_(Message.sender_id == message_data.receiver_id, Message.receiver_id == current_user.id)
                )
            ).first()
            
            if existing_conversation:
                conversation_id = existing_conversation.conversation_id
            else:
                # Create new conversation ID
                conversation_id = f"conv_{current_user.id}_{message_data.receiver_id}_{int(datetime.utcnow().timestamp())}"
        
        # Create new message
        message = Message(
            sender_id=current_user.id,
            receiver_id=message_data.receiver_id,
            message=message_data.message,
            message_type=message_data.message_type,
            conversation_id=conversation_id,
            parent_message_id=message_data.parent_message_id,
            created_at=datetime.utcnow()
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Load relationships
        message = db.query(Message).options(
            joinedload(Message.sender),
            joinedload(Message.receiver)
        ).filter(Message.id == message.id).first()
        
        # Create notification for the receiver
        NotificationUtils.notify_new_message(db, message)
        
        # Send real-time notification via WebSocket
        message_data = {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "message": message.message,
            "message_type": message.message_type,
            "conversation_id": message.conversation_id,
            "is_read": message.is_read,
            "is_important": message.is_important,
            "parent_message_id": message.parent_message_id,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
            "sender": {
                "id": message.sender.id,
                "name": message.sender.name,
                "surname": message.sender.surname,
                "email": message.sender.email,
                "username": message.sender.username,
                "phone": message.sender.phone,
                "profile_img": message.sender.profile_img,
                "created_at": message.sender.created_at.isoformat()
            },
            "receiver": {
                "id": message.receiver.id,
                "name": message.receiver.name,
                "surname": message.receiver.surname,
                "email": message.receiver.email,
                "username": message.receiver.username,
                "phone": message.receiver.phone,
                "profile_img": message.receiver.profile_img,
                "created_at": message.receiver.created_at.isoformat()
            }
        }
        
        # Send real-time notification
        await manager.send_message_notification(
            message_data, 
            message.sender_id, 
            message.receiver_id, 
            message.conversation_id
        )
        
        return {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "message": message.message,
            "message_type": message.message_type,
            "conversation_id": message.conversation_id,
            "is_read": message.is_read,
            "is_important": message.is_important,
            "parent_message_id": message.parent_message_id,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "sender": {
                "id": message.sender.id,
                "name": message.sender.name,
                "surname": message.sender.surname,
                "email": message.sender.email,
                "username": message.sender.username,
                "phone": message.sender.phone,
                "profile_img": message.sender.profile_img,
                "created_at": message.sender.created_at
            },
            "receiver": {
                "id": message.receiver.id,
                "name": message.receiver.name,
                "surname": message.receiver.surname,
                "email": message.receiver.email,
                "username": message.receiver.username,
                "phone": message.receiver.phone,
                "profile_img": message.receiver.profile_img,
                "created_at": message.receiver.created_at
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@router.put("/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a message as read"""
    try:
        message = db.query(Message).filter(
            Message.id == message_id,
            Message.receiver_id == current_user.id
        ).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Mark the message as read
        message.is_read = True
        message.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Message marked as read"}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking message as read: {str(e)}")
