"""
WebSocket Router for Real-time Messaging
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import json
import asyncio
from datetime import datetime

from database import get_db
from models import User, Message
from auth import get_current_user_websocket
from websocket_manager import manager

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/messages/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, token: str = Query(...)):
    """WebSocket endpoint for real-time messaging"""
    
    # Verify user authentication
    try:
        current_user = await get_current_user_websocket(token)
        print(f"WebSocket auth: current_user.id={current_user.id}, user_id={user_id}")
        if current_user.id != user_id:
            print(f"WebSocket auth failed: ID mismatch")
            await websocket.close(code=1008, reason="Unauthorized")
            return
    except Exception as e:
        print(f"WebSocket auth error: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # Connect the user
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "join_conversation":
                # User wants to join a conversation
                conversation_id = message_data.get("conversation_id")
                if conversation_id:
                    manager.join_conversation(user_id, conversation_id)
                    
                    # Send confirmation
                    await manager.send_personal_message({
                        "type": "joined_conversation",
                        "data": {
                            "conversation_id": conversation_id,
                            "user_id": user_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }, user_id)
            
            elif message_type == "leave_conversation":
                # User wants to leave a conversation
                conversation_id = message_data.get("conversation_id")
                if conversation_id:
                    manager.leave_conversation(user_id, conversation_id)
                    
                    # Send confirmation
                    await manager.send_personal_message({
                        "type": "left_conversation",
                        "data": {
                            "conversation_id": conversation_id,
                            "user_id": user_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }, user_id)
            
            elif message_type == "typing":
                # User is typing
                conversation_id = message_data.get("conversation_id")
                is_typing = message_data.get("is_typing", False)
                if conversation_id:
                    await manager.send_typing_indicator(conversation_id, user_id, is_typing)
            
            elif message_type == "ping":
                # Heartbeat/ping message
                await manager.send_personal_message({
                    "type": "pong",
                    "data": {
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, user_id)
            
            else:
                # Unknown message type
                await manager.send_personal_message({
                    "type": "error",
                    "data": {
                        "message": f"Unknown message type: {message_type}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

@router.websocket("/admin/{admin_id}")
async def admin_websocket_endpoint(websocket: WebSocket, admin_id: int, token: str = Query(...)):
    """WebSocket endpoint for admin real-time messaging"""
    
    # Verify admin authentication
    try:
        current_user = await get_current_user_websocket(token)
        print(f"Admin WebSocket auth: current_user.id={current_user.id}, admin_id={admin_id}, is_admin={current_user.is_admin}")
        if current_user.id != admin_id or not current_user.is_admin:
            print(f"Admin WebSocket auth failed: ID mismatch or not admin")
            await websocket.close(code=1008, reason="Unauthorized")
            return
    except Exception as e:
        print(f"Admin WebSocket auth error: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # Connect the admin
    await manager.connect(websocket, admin_id)
    
    try:
        while True:
            # Wait for messages from the admin client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "join_conversation":
                # Admin wants to join a conversation
                conversation_id = message_data.get("conversation_id")
                if conversation_id:
                    manager.join_conversation(admin_id, conversation_id)
                    
                    # Send confirmation
                    await manager.send_personal_message({
                        "type": "joined_conversation",
                        "data": {
                            "conversation_id": conversation_id,
                            "user_id": admin_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }, admin_id)
            
            elif message_type == "leave_conversation":
                # Admin wants to leave a conversation
                conversation_id = message_data.get("conversation_id")
                if conversation_id:
                    manager.leave_conversation(admin_id, conversation_id)
                    
                    # Send confirmation
                    await manager.send_personal_message({
                        "type": "left_conversation",
                        "data": {
                            "conversation_id": conversation_id,
                            "user_id": admin_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }, admin_id)
            
            elif message_type == "typing":
                # Admin is typing
                conversation_id = message_data.get("conversation_id")
                is_typing = message_data.get("is_typing", False)
                if conversation_id:
                    await manager.send_typing_indicator(conversation_id, admin_id, is_typing)
            
            elif message_type == "ping":
                # Heartbeat/ping message
                await manager.send_personal_message({
                    "type": "pong",
                    "data": {
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, admin_id)
            
            else:
                # Unknown message type
                await manager.send_personal_message({
                    "type": "error",
                    "data": {
                        "message": f"Unknown message type: {message_type}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, admin_id)
                
    except WebSocketDisconnect:
        manager.disconnect(admin_id)
    except Exception as e:
        print(f"WebSocket error for admin {admin_id}: {e}")
        manager.disconnect(admin_id)
