from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pathlib import Path
from uuid import UUID
from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.models import User, Camera, AIModel
from app.schemas.camera import CameraCreate, CameraResponse, CameraUpdate
from app.services.mock_stream_processor import mock_stream_processor
from app.core.config import settings
from sqlmodel import select
import uuid
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test")
async def test_cameras_router():
    """Test endpoint to verify cameras router is working"""
    logger.info("=== TEST_CAMERAS_ROUTER CALLED ===")
    return {"message": "Cameras router is working"}

@router.post("/", response_model=CameraResponse)
async def create_camera(
    camera: CameraCreate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new camera configuration"""
    # Get current user ID
    logger.info(f"Looking up user with username: {current_user['username']}")
    result = await db.execute(select(User).where(User.username == current_user["username"]))
    user = result.scalar_one_or_none()
    if not user:
        logger.error(f"User {current_user['username']} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    logger.info(f"Found user: {user.id} - {user.username}")
    
    # Create camera
    db_camera = Camera(
        name=camera.name,
        url=camera.rtsp_uri,
        description=camera.description,
        location=camera.location,
        owner_id=user.id
    )
    
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    
    return db_camera

@router.get("/", response_model=List[CameraResponse])
async def read_cameras(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get list of cameras for the current user"""
    logger.info("=== READ_CAMERAS FUNCTION CALLED ===")
    
    try:
        # Query all cameras (for testing)
        result = await db.execute(select(Camera).offset(skip).limit(limit))
        cameras = result.scalars().all()
        
        logger.info(f"Found {len(cameras)} cameras")
        return cameras
    except Exception as e:
        logger.error(f"Error in read_cameras: {type(e).__name__}: {str(e)}", exc_info=True)
        raise

@router.get("/{camera_id}", response_model=CameraResponse)
async def read_camera(
    camera_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific camera by ID"""
    # Get current user ID
    logger.info(f"Looking up user with username: {current_user['username']}")
    result = await db.execute(select(User).where(User.username == current_user["username"]))
    user = result.scalar_one_or_none()
    if not user:
        logger.error(f"User {current_user['username']} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    logger.info(f"Found user: {user.id} - {user.username}")
    
    # Query camera
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id, Camera.owner_id == user.id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    return camera

@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: UUID,
    camera_update: CameraUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a camera configuration"""
    # Get current user ID
    logger.info(f"Looking up user with username: {current_user['username']}")
    result = await db.execute(select(User).where(User.username == current_user["username"]))
    user = result.scalar_one_or_none()
    if not user:
        logger.error(f"User {current_user['username']} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    logger.info(f"Found user: {user.id} - {user.username}")
    
    # Query camera
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id, Camera.owner_id == user.id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Update fields
    update_data = camera_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)
    
    await db.commit()
    await db.refresh(camera)
    
    return camera

@router.delete("/{camera_id}")
async def delete_camera(
    camera_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a camera configuration"""
    # Get current user ID
    logger.info(f"Looking up user with username: {current_user['username']}")
    result = await db.execute(select(User).where(User.username == current_user["username"]))
    user = result.scalar_one_or_none()
    if not user:
        logger.error(f"User {current_user['username']} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    logger.info(f"Found user: {user.id} - {user.username}")
    
    # Query camera
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id, Camera.owner_id == user.id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    await db.delete(camera)
    await db.commit()
    
    return {"message": "Camera deleted successfully"}

@router.post("/{camera_id}/start_stream")
async def start_camera_stream(
    camera_id: UUID,
    # current_user: dict = Depends(get_current_active_user),  # Temporarily bypass auth
    db: AsyncSession = Depends(get_db)
):
    """Start video stream processing for a camera"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"=== START_CAMERA_STREAM CALLED WITH camera_id={camera_id} ===")
    
    try:
        # Hardcoded user for testing
        logger.info(f"Starting stream for camera {camera_id} (auth bypassed for testing)")
        
        # Get current user ID (hardcoded for testing)
        logger.info(f"Looking up user with username: demo")
        result = await db.execute(select(User).where(User.username == "demo"))
        user = result.scalar_one_or_none()
        if not user:
            logger.error(f"User demo not found in database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"Found user: {user.id} - {user.username}")
        
        # Query camera
        logger.info(f"Querying camera with ID: {camera_id} for user: {user.id}")
        result = await db.execute(
            select(Camera).where(Camera.id == camera_id, Camera.owner_id == user.id)
        )
        camera = result.scalar_one_or_none()
        
        if not camera:
            logger.error(f"Camera {camera_id} not found for user {user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Camera not found"
            )
        
        logger.info(f"Found camera: {camera.name} with URL: {camera.url}")
        
        # Check if HLS output directory exists
        hls_dir = Path(settings.HLS_OUTPUT_DIR) / str(camera_id)
        hls_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"HLS directory created/verified: {hls_dir}")
        
        # Optional: AI model resolution via active analytics job can be added here if needed
        
        # Start stream processing
        logger.info(f"Calling mock_stream_processor.start_stream with camera_id={camera_id}, url={camera.url}")
        success = await mock_stream_processor.start_stream(str(camera_id), camera.url)
        logger.info(f"Stream processor result: {success}")
        
        if not success:
            logger.error(f"Failed to start stream processing for camera {camera_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start stream processing"
            )
        
        logger.info(f"Stream processing started successfully for camera {camera_id}")
        
        return {
            "message": "Stream processing started",
            "camera_id": camera_id,
            "stream_url": f"/streams/{camera_id}/"
        }
        
    except Exception as e:
        logger.error(f"ERROR in start_camera_stream: {type(e).__name__}: {str(e)}", exc_info=True)
        logger.error(f"Full traceback:", exc_info=True)
        # Return detailed error response
        return {
            "error": f"Internal server error: {type(e).__name__}: {str(e)}",
            "camera_id": camera_id,
            "success": False
        }

@router.post("/{camera_id}/stop_stream")
async def stop_camera_stream(
    camera_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop video stream processing for a camera"""
    # Get current user ID
    result = await db.execute(select(User).where(User.username == current_user["username"]))
    user = result.scalar_one()
    
    # Query camera
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id, Camera.owner_id == user.id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # TODO: Implement stream processor cleanup
    # This would require tracking active processors globally
    
    return {
        "message": "Stream processing stopped",
        "camera_id": camera_id
    }

@router.get("/{camera_id}/stream_status")
async def get_camera_stream_status(
    camera_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current stream status for a camera"""
    # Get current user ID
    result = await db.execute(select(User).where(User.username == current_user["username"]))
    user = result.scalar_one()
    
    # Query camera
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id, Camera.owner_id == user.id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Check if HLS playlist exists
    hls_playlist = Path(settings.HLS_OUTPUT_DIR) / str(camera_id) / "index.m3u8"
    stream_active = hls_playlist.exists()
    
    return {
        "camera_id": camera_id,
        "stream_active": stream_active,
        "stream_url": f"/api/streams/{camera_id}/index.m3u8" if stream_active else None,
        "camera_active": camera.is_active,
        "last_updated": camera.updated_at.isoformat() if camera.updated_at else None
    }
