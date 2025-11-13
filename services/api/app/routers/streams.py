from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path
import os
from app.core.dependencies import get_current_user_or_machine
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db.session import get_db
from app.models.models import User, Camera, AIModel, AnalyticsJob
from app.services.mock_stream_processor import mock_stream_processor
from uuid import uuid4
from datetime import datetime

router = APIRouter()

@router.get("/{camera_id}/{filename:path}")
async def get_stream_segment(
    camera_id: str,
    filename: str,
    current_user: dict = Depends(get_current_user_or_machine)
):
    """
    Securely serve HLS stream segments with authentication.
    Supports both user JWT tokens and machine API keys.
    """
    # Construct the file path securely
    base_path = Path(settings.HLS_OUTPUT_DIR)
    camera_path = base_path / camera_id
    file_path = camera_path / filename
    
    # Security check: ensure the path is within the allowed directory
    try:
        file_path.resolve().relative_to(base_path.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: invalid path"
        )
    
    # Check if file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stream segment not found: {filename}"
        )
    
    # Determine content type based on file extension
    content_type = "application/octet-stream"
    if filename.endswith('.m3u8'):
        content_type = "application/vnd.apple.mpegurl"
    elif filename.endswith('.ts'):
        content_type = "video/mp2t"
    
    # Serve the file with appropriate headers for HLS streaming
    return FileResponse(
        path=str(file_path),
        media_type=content_type,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Access-Control-Allow-Origin": "*"
        }
    )

@router.get("/{camera_id}/")
async def get_stream_playlist(
    camera_id: str,
    current_user: dict = Depends(get_current_user_or_machine)
):
    """
    Serve the main HLS playlist (m3u8) file for a camera stream.
    """
    return await get_stream_segment(camera_id, "index.m3u8", current_user)

@router.post("/upload")
async def upload_video_stream(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_or_machine)
):
    """
    Upload a video file and create a temporary HLS stream for testing.
    Persists a Camera and AnalyticsJob so the detection simulator emits events.
    """
    # Determine owner (use current user or demo fallback)
    result = await db.execute(select(User).where(User.username == current_user.get("username", "demo")))
    user = result.scalar_one_or_none()
    if not user:
        # Fallback to demo user
        result = await db.execute(select(User).where(User.username == "demo"))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Generate camera id and target dir
    camera_id = str(uuid4())
    camera_dir = Path(settings.HLS_OUTPUT_DIR) / camera_id
    camera_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded file to camera directory
    video_path = camera_dir / "source.mp4"
    try:
        contents = await file.read()
        with open(video_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save file: {e}")

    # Create camera record (type=file, status=online)
    camera = Camera(
        id=uuid4(),
        name=file.filename or "Uploaded Video",
        type="file",
        url=str(video_path),
        description="Uploaded video stream",
        location="Local Uploads",
        status="online",
        is_active=True,
        owner_id=user.id,
        created_at=datetime.utcnow()
    )
    db.add(camera)
    await db.commit()
    await db.refresh(camera)

    # Attach active AI model if available and create analytics job
    result = await db.execute(select(AIModel).where(AIModel.is_active == True))
    ai_model = result.scalars().first()
    if ai_model:
        job = AnalyticsJob(
            name=f"Upload-{camera.name}",
            description="Auto job for uploaded video",
            is_active=True,
            confidence_threshold=0.5,
            nms_threshold=0.4,
            max_detections=100,
            camera_id=camera.id,
            ai_model_id=ai_model.id,
            created_by_id=user.id,
            created_at=datetime.utcnow()
        )
        db.add(job)
        await db.commit()

    # Start mock stream processor for this camera id using saved video path
    await mock_stream_processor.start_stream(str(camera.id), str(video_path))

    return {
        "camera_id": str(camera.id),
        "stream_url": f"/streams/{camera.id}/"
    }
