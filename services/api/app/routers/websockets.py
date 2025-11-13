from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from fastapi.responses import JSONResponse
import json
import asyncio
import logging
from typing import Dict, Set
from app.core.security import verify_token
from app.core.dependencies import get_current_user_or_machine
from app.services.websocket_manager import connection_manager
from app.services.detection_simulator import detection_simulator
import socketio

router = APIRouter()
logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Handle Socket.IO connection"""
    logger.info(f"Socket.IO client connected: {sid}")
    await sio.emit('connected', {'sid': sid})

@sio.event
async def disconnect(sid):
    """Handle Socket.IO disconnection"""
    logger.info(f"Socket.IO client disconnected: {sid}")

@sio.event
async def authenticate(sid, data):
    """Handle authentication via Socket.IO"""
    token = data.get('token')
    if not token:
        await sio.emit('auth_error', {'error': 'No token provided'}, room=sid)
        return False
        
    payload = verify_token(token)
    if not payload:
        await sio.emit('auth_error', {'error': 'Invalid token'}, room=sid)
        return False
        
    username = payload.get("sub")
    if not username:
        await sio.emit('auth_error', {'error': 'Invalid token payload'}, room=sid)
        return False
        
    # Store user info in session
    async with sio.session(sid) as session:
        session['username'] = username
        session['authenticated'] = True
        
    await sio.emit('auth_success', {'username': username}, room=sid)
    logger.info(f"Socket.IO client authenticated: {username}")
    return True

@sio.event
async def subscribe_camera(sid, data):
    """Subscribe to camera-specific events"""
    camera_id = data.get('camera_id')
    if not camera_id:
        await sio.emit('error', {'error': 'Camera ID required'}, room=sid)
        return
        
    async with sio.session(sid) as session:
        if not session.get('authenticated'):
            await sio.emit('error', {'error': 'Not authenticated'}, room=sid)
            return
            
        # Add camera to user's subscriptions
        if 'cameras' not in session:
            session['cameras'] = set()
        session['cameras'].add(camera_id)
        
    await sio.emit('subscribed', {'camera_id': camera_id}, room=sid)
    logger.info(f"Client {sid} subscribed to camera {camera_id}")

@sio.event
async def unsubscribe_camera(sid, data):
    """Unsubscribe from camera-specific events"""
    camera_id = data.get('camera_id')
    if not camera_id:
        await sio.emit('error', {'error': 'Camera ID required'}, room=sid)
        return
        
    async with sio.session(sid) as session:
        if 'cameras' in session:
            session['cameras'].discard(camera_id)
            
    await sio.emit('unsubscribed', {'camera_id': camera_id}, room=sid)
    logger.info(f"Client {sid} unsubscribed from camera {camera_id}")

@sio.event
async def get_detection_stats(sid, data):
    """Get current detection statistics"""
    camera_id = data.get('camera_id')
    
    async with sio.session(sid) as session:
        if not session.get('authenticated'):
            await sio.emit('error', {'error': 'Not authenticated'}, room=sid)
            return
            
    # Calculate stats for specific camera or all cameras
    if camera_id:
        stats = await detection_simulator.calculate_detection_stats(camera_id)
    else:
        # Aggregate stats for all cameras
        stats = {
            "total_detections": 0,
            "objects_by_class": [],
            "average_confidence": 0.0,
            "detection_rate": 0.0
        }
        
    await sio.emit('detection_stats', stats, room=sid)

@sio.event
async def get_object_counts(sid, data):
    """Get current object counts"""
    camera_id = data.get('camera_id')
    
    async with sio.session(sid) as session:
        if not session.get('authenticated'):
            await sio.emit('error', {'error': 'Not authenticated'}, room=sid)
            return
            
    if camera_id:
        counts = detection_simulator.get_current_counts(camera_id)
        object_counts = [
            {
                "object_class": obj_class,
                "count": count,
                "last_updated": datetime.utcnow().isoformat()
            }
            for obj_class, count in counts.items()
        ]
    else:
        object_counts = []
        
    await sio.emit('object_counts', object_counts, room=sid)

# Legacy WebSocket endpoint for backward compatibility
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token for authentication")
):
    """
    Legacy WebSocket endpoint for real-time alerts and notifications.
    Authentication is done via query parameter as WebSocket doesn't support headers.
    """
    # Verify the JWT token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    username = payload.get("sub")
    if not username:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Accept the connection
    await connection_manager.connect(websocket, username)
    
    try:
        while True:
            # Receive and handle messages
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "subscribe_camera":
                    camera_id = message.get("camera_id")
                    if camera_id:
                        await connection_manager.subscribe_to_camera(websocket, camera_id)
                        logger.info(f"User {username} subscribed to camera {camera_id}")
                        
                elif message.get("type") == "unsubscribe_camera":
                    camera_id = message.get("camera_id")
                    if camera_id:
                        connection_manager.unsubscribe_from_camera(websocket, camera_id)
                        logger.info(f"User {username} unsubscribed from camera {camera_id}")
                        
                elif message.get("type") == "ping":
                    await connection_manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": asyncio.get_event_loop().time()}),
                        websocket
                    )
                    
                else:
                    logger.info(f"Received message from {username}: {message}")
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from {username}: {data}")
                
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, username)
        logger.info(f"WebSocket disconnected for user: {username}")
    except Exception as e:
        logger.error(f"WebSocket error for user {username}: {e}")
        connection_manager.disconnect(websocket, username)

@router.get("/health")
async def websocket_health():
    """Health check for WebSocket service"""
    stats = connection_manager.get_connection_stats()
    return {
        "status": "healthy",
        "socket_io_active": True,
        "legacy_websocket_active": True,
        "connection_stats": stats
    }

# Integration with detection simulator
detection_simulator.set_websocket_manager(connection_manager)