"""
WebSocket Manager for Real-time Messaging
"""
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # Store active connections by user ID
        self.active_connections: Dict[int, WebSocket] = {}
        # Store connections by conversation ID for broadcasting
        self.conversation_connections: Dict[str, Set[int]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a WebSocket connection and store it"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected via WebSocket")
        
    def disconnect(self, user_id: int):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            # Remove from conversation connections
            for conversation_id, users in self.conversation_connections.items():
                users.discard(user_id)
            print(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
                return True
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)
                return False
        return False
    
    async def broadcast_to_conversation(self, message: dict, conversation_id: str, exclude_user: int = None):
        """Broadcast a message to all users in a conversation"""
        if conversation_id in self.conversation_connections:
            users_to_notify = self.conversation_connections[conversation_id].copy()
            if exclude_user:
                users_to_notify.discard(exclude_user)
            
            for user_id in users_to_notify:
                await self.send_personal_message(message, user_id)
    
    def join_conversation(self, user_id: int, conversation_id: str):
        """Add a user to a conversation's connection list"""
        if conversation_id not in self.conversation_connections:
            self.conversation_connections[conversation_id] = set()
        self.conversation_connections[conversation_id].add(user_id)
        print(f"User {user_id} joined conversation {conversation_id}")
    
    def leave_conversation(self, user_id: int, conversation_id: str):
        """Remove a user from a conversation's connection list"""
        if conversation_id in self.conversation_connections:
            self.conversation_connections[conversation_id].discard(user_id)
            print(f"User {user_id} left conversation {conversation_id}")
    
    async def send_message_notification(self, message_data: dict, sender_id: int, receiver_id: int, conversation_id: str):
        """Send a new message notification to the receiver"""
        notification = {
            "type": "new_message",
            "data": {
                "message": message_data,
                "conversation_id": conversation_id,
                "sender_id": sender_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Send to receiver
        await self.send_personal_message(notification, receiver_id)
        
        # Also broadcast to conversation if both users are online
        await self.broadcast_to_conversation(notification, conversation_id, exclude_user=sender_id)
    
    async def send_typing_indicator(self, conversation_id: str, user_id: int, is_typing: bool):
        """Send typing indicator to conversation participants"""
        typing_data = {
            "type": "typing",
            "data": {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        await self.broadcast_to_conversation(typing_data, conversation_id, exclude_user=user_id)

# Global connection manager instance
manager = ConnectionManager()
