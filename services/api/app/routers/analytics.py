from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.models import User, AnalyticsJob, AIModel, ROI
from app.schemas.analytics import AnalyticsJobCreate, AnalyticsJobResponse, ROICreate, ROIResponse
from sqlmodel import select

router = APIRouter()

@router.post("/jobs", response_model=AnalyticsJobResponse)
async def create_analytics_job(
    job: AnalyticsJobCreate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new analytics job"""
    # Get current user ID
    result = await db.execute(select(User).where(User.username == current_user["username"]))
    user = result.scalar_one()
    
    # Verify camera belongs to user
    camera_result = await db.execute(
        select(AnalyticsJob).where(AnalyticsJob.camera_id == job.camera_id)
    )
    if not camera_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Verify model exists
    model_result = await db.execute(select(AIModel).where(AIModel.id == job.model_id))
    if not model_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Create analytics job
    db_job = AnalyticsJob(
        name=job.name,
        description=job.description,
        camera_id=job.camera_id,
        model_id=job.model_id,
        created_by_id=user.id,
        confidence_threshold=job.confidence_threshold,
        nms_threshold=job.nms_threshold,
        max_detections=job.max_detections
    )
    
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    
    return db_job

@router.get("/jobs", response_model=List[AnalyticsJobResponse])
async def read_analytics_jobs(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of analytics jobs"""
    # Get current user ID
    result = await db.execute(select(User).where(User.username == current_user["username"]))
    user = result.scalar_one()
    
    # Query jobs created by user
    result = await db.execute(
        select(AnalyticsJob)
        .where(AnalyticsJob.created_by_id == user.id)
        .offset(skip)
        .limit(limit)
    )
    jobs = result.scalars().all()
    
    return jobs

@router.post("/roi", response_model=ROIResponse)
async def create_roi(
    roi: ROICreate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new Region of Interest"""
    # Verify analytics job exists and belongs to user
    result = await db.execute(
        select(AnalyticsJob).where(AnalyticsJob.id == roi.analytics_job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analytics job not found"
        )
    
    # Create ROI
    db_roi = ROI(
        name=roi.name,
        polygon_points=roi.polygon_points,
        roi_type=roi.roi_type,
        analytics_job_id=roi.analytics_job_id,
        description=roi.description,
        alert_on_entry=roi.alert_on_entry,
        alert_on_exit=roi.alert_on_exit
    )
    
    db.add(db_roi)
    await db.commit()
    await db.refresh(db_roi)
    
    return db_roi

@router.get("/roi/{job_id}", response_model=List[ROIResponse])
async def read_rois_for_job(
    job_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all ROIs for an analytics job"""
    # Verify job exists
    result = await db.execute(
        select(AnalyticsJob).where(AnalyticsJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analytics job not found"
        )
    
    # Query ROIs
    result = await db.execute(
        select(ROI).where(ROI.analytics_job_id == job_id)
    )
    rois = result.scalars().all()
    
    return rois