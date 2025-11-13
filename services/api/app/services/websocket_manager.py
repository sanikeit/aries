import asyncio
import json
from typing import Dict, Set, Any
from fastapi import WebSocket
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time detection data"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.camera_subscriptions: Dict[str, Set[WebSocket]] = {}  # camera_id -> set of websockets
        self.user_subscriptions: Dict[str, Set[WebSocket]] = {}    # user_id -> set of websockets
        
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if user_id:
            if user_id not in self.user_subscriptions:
                self.user_subscriptions[user_id] = set()
            self.user_subscriptions[user_id].add(websocket)
            
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        
        # Remove from user subscriptions
        if user_id and user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(websocket)
            if not self.user_subscriptions[user_id]:
                del self.user_subscriptions[user_id]
                
        # Remove from camera subscriptions
        for camera_id, websockets in self.camera_subscriptions.items():
            websockets.discard(websocket)
            if not websockets:
                del self.camera_subscriptions[camera_id]
                
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
    async def subscribe_to_camera(self, websocket: WebSocket, camera_id: str):
        """Subscribe a WebSocket to a specific camera"""
        if camera_id not in self.camera_subscriptions:
            self.camera_subscriptions[camera_id] = set()
        self.camera_subscriptions[camera_id].add(websocket)
        
        logger.info(f"WebSocket subscribed to camera {camera_id}")
        
    def unsubscribe_from_camera(self, websocket: WebSocket, camera_id: str):
        """Unsubscribe a WebSocket from a specific camera"""
        if camera_id in self.camera_subscriptions:
            self.camera_subscriptions[camera_id].discard(websocket)
            if not self.camera_subscriptions[camera_id]:
                del self.camera_subscriptions[camera_id]
                
        logger.info(f"WebSocket unsubscribed from camera {camera_id}")
        
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            # Remove broken connection
            await self.disconnect(websocket)
            
    async def broadcast_message(self, message: dict):
        """Broadcast a message to all connected WebSockets"""
        if not self.active_connections:
            return
            
        # Create list of send tasks
        tasks = []
        for connection in list(self.active_connections):
            tasks.append(self.send_personal_message(message, connection))
            
        # Send to all connections concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def broadcast_to_camera_subscribers(self, camera_id: str, message: dict):
        """Broadcast a message to WebSockets subscribed to a specific camera"""
        if camera_id not in self.camera_subscriptions:
            return
            
        websockets = list(self.camera_subscriptions[camera_id])
        if not websockets:
            return
            
        tasks = []
        for websocket in websockets:
            tasks.append(self.send_personal_message(message, websocket))
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def broadcast_to_user_subscribers(self, user_id: str, message: dict):
        """Broadcast a message to WebSockets subscribed to a specific user"""
        if user_id not in self.user_subscriptions:
            return
            
        websockets = list(self.user_subscriptions[user_id])
        if not websockets:
            return
            
        tasks = []
        for websocket in websockets:
            tasks.append(self.send_personal_message(message, websocket))
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    # Specific broadcast methods for detection data
    async def broadcast_detection(self, detection_data: dict):
        """Broadcast a new detection event"""
        message = {
            "type": "detection",
            "data": detection_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all connections
        await self.broadcast_message(message)
        
        # Also broadcast to camera-specific subscribers
        camera_id = detection_data.get("camera_id")
        if camera_id:
            await self.broadcast_to_camera_subscribers(camera_id, message)
            
    async def broadcast_object_counts(self, camera_id: str, counts: list):
        """Broadcast object count updates"""
        message = {
            "type": "object_counts",
            "camera_id": camera_id,
            "data": counts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all connections
        await self.broadcast_message(message)
        
        # Also broadcast to camera-specific subscribers
        await self.broadcast_to_camera_subscribers(camera_id, message)
        
    async def broadcast_detection_stats(self, camera_id: str, stats: dict):
        """Broadcast detection statistics"""
        message = {
            "type": "stats_update",
            "camera_id": camera_id,
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all connections
        await self.broadcast_message(message)
        
        # Also broadcast to camera-specific subscribers
        await self.broadcast_to_camera_subscribers(camera_id, message)
        
    async def broadcast_camera_detections(self, camera_id: str, detections_data: dict):
        """Broadcast complete detection data for a specific camera"""
        message = {
            "type": "camera_detections",
            "camera_id": camera_id,
            "data": detections_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all connections
        await self.broadcast_message(message)
        
        # Also broadcast to camera-specific subscribers
        await self.broadcast_to_camera_subscribers(camera_id, message)
        
    async def broadcast_alert(self, alert_data: dict):
        """Broadcast an alert event"""
        message = {
            "type": "alert",
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all connections
        await self.broadcast_message(message)
        
        # Also broadcast to camera-specific subscribers if applicable
        camera_id = alert_data.get("camera_id")
        if camera_id:
            await self.broadcast_to_camera_subscribers(camera_id, message)
            
    def get_connection_stats(self) -> dict:
        """Get current connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "camera_subscriptions": {
                camera_id: len(websockets) 
                for camera_id, websockets in self.camera_subscriptions.items()
            },
            "user_subscriptions": {
                user_id: len(websockets)
                for user_id, websockets in self.user_subscriptions.items()
            }
        }

# Global connection manager instance
connection_manager = ConnectionManager()