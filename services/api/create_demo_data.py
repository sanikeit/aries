#!/usr/bin/env python3
"""
Demo data script for Aries Edge Platform
Creates sample cameras and mock analytics data for testing
"""

import asyncio
import random
import json
from datetime import datetime, timedelta
from uuid import uuid4
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine, AsyncSessionLocal
from app.models import models
from app.models.models import User, Camera, Stream, AIModel, AnalyticsJob, ROI, AlertEvent
from app.core.security import get_password_hash

async def create_demo_user(session: AsyncSession):
    """Create a demo user for testing"""
    # Check if user exists
    result = await session.execute(select(User).where(User.username == "demo"))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create demo user
        demo_user = User(
            id=uuid4(),
            username="demo",
            email="demo@aries.com",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
            role="admin",
            is_active=True
        )
        session.add(demo_user)
        await session.commit()
        await session.refresh(demo_user)
        print(f"Created demo user: {demo_user.username}")
        return demo_user
    else:
        print(f"Demo user already exists: {user.username}")
        return user

async def create_demo_cameras(session: AsyncSession, user_id):
    """Create sample cameras for the demo user"""
    # Sample camera configurations
    camera_configs = [
        {
            "name": "Main Entrance",
            "url": "rtsp://demo:demo123@192.168.1.100:554/stream1",
            "description": "Main building entrance camera",
            "location": "Building A, Front Door",
            "status": "online",
            "is_active": True
        },
        {
            "name": "Parking Lot",
            "url": "rtsp://demo:demo123@192.168.1.101:554/stream1",
            "description": "Parking area surveillance camera",
            "location": "North Parking Lot",
            "status": "online",
            "is_active": True
        },
        {
            "name": "Loading Dock",
            "url": "rtsp://demo:demo123@192.168.1.102:554/stream1",
            "description": "Loading dock security camera",
            "location": "West Loading Dock",
            "status": "offline",
            "is_active": False
        },
        {
            "name": "Warehouse Interior",
            "url": "rtsp://demo:demo123@192.168.1.103:554/stream1",
            "description": "Warehouse interior monitoring",
            "location": "Main Warehouse",
            "status": "online",
            "is_active": True
        }
    ]
    
    cameras = []
    for config in camera_configs:
        # Check if camera already exists
        result = await session.execute(select(Camera).where(Camera.name == config["name"], Camera.owner_id == user_id))
        existing = result.scalar_one_or_none()
        
        if not existing:
            camera = Camera(
                id=uuid4(),
                name=config["name"],
                type="rtsp",
                url=config["url"],
                description=config["description"],
                location=config["location"],
                status=config["status"],
                is_active=config["is_active"],
                owner_id=user_id
            )
            session.add(camera)
            await session.commit()
            await session.refresh(camera)
            print(f"Created camera: {camera.name}")
            cameras.append(camera)
        else:
            print(f"Camera already exists: {existing.name}")
            cameras.append(existing)
    
    return cameras

async def create_demo_streams(session: AsyncSession, cameras: list):
    """Create sample streams for online cameras"""
    for camera in cameras:
        if camera.status == "online":
            # Check if stream already exists
            result = await session.execute(select(Stream).where(Stream.camera_id == camera.id))
            existing = result.scalar_one_or_none()
            
            if not existing:
                stream = Stream(
                    id=uuid4(),
                    camera_id=camera.id,
                    type="hls",
                    status="active",
                    endpoint=f"/streams/{camera.id}/hls.m3u8",
                    quality="high",
                    metadata_enabled=True
                )
                session.add(stream)
                await session.commit()
                print(f"Created stream for camera: {camera.name}")

async def create_demo_ai_models(session: AsyncSession):
    """Create sample AI models"""
    models = [
        {
            "name": "YOLOv8n",
            "ai_model_type": "yolov8",
            "version": "8.0.0",
            "description": "YOLOv8 Nano - Fast object detection",
            "is_active": True,
            "config_path": "/models/yolov8n.yaml",
            "weights_path": "/models/yolov8n.pt",
            "labels_path": "/models/coco.names"
        },
        {
            "name": "YOLOv8s",
            "ai_model_type": "yolov8",
            "version": "8.0.0",
            "description": "YOLOv8 Small - Balanced accuracy and speed",
            "is_active": False,
            "config_path": "/models/yolov8s.yaml",
            "weights_path": "/models/yolov8s.pt",
            "labels_path": "/models/coco.names"
        }
    ]
    
    ai_models = []
    for model_data in models:
        # Check if model already exists
        result = await session.execute(select(AIModel).where(AIModel.name == model_data["name"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            ai_model = AIModel(
                id=uuid4(),
                name=model_data["name"],
                ai_model_type=model_data["ai_model_type"],
                version=model_data["version"],
                description=model_data["description"],
                is_active=model_data["is_active"],
                config_path=model_data["config_path"],
                weights_path=model_data["weights_path"],
                labels_path=model_data["labels_path"]
            )
            session.add(ai_model)
            await session.commit()
            await session.refresh(ai_model)
            print(f"Created AI model: {ai_model.name}")
            ai_models.append(ai_model)
        else:
            print(f"AI model already exists: {existing.name}")
            ai_models.append(existing)
    
    return ai_models

async def create_demo_analytics_jobs(session: AsyncSession, cameras: list, ai_models: list, user_id):
    """Create sample analytics jobs"""
    jobs = []
    for camera in cameras:
        if camera.status == "online":
            # Check if analytics job already exists
            result = await session.execute(select(AnalyticsJob).where(AnalyticsJob.camera_id == camera.id))
            existing = result.scalar_one_or_none()
            
            if not existing:
                job = AnalyticsJob(
                    id=uuid4(),
                    name=f"Detection - {camera.name}",
                    description=f"Object detection for {camera.name}",
                    is_active=True,
                    confidence_threshold=0.5,
                    nms_threshold=0.4,
                    max_detections=100,
                    camera_id=camera.id,
                    ai_model_id=ai_models[0].id,  # Use first AI model
                    created_by_id=user_id
                )
                session.add(job)
                await session.commit()
                await session.refresh(job)
                print(f"Created analytics job: {job.name}")
                jobs.append(job)
            else:
                print(f"Analytics job already exists: {existing.name}")
                jobs.append(existing)
    
    return jobs

async def create_demo_rois(session: AsyncSession, analytics_jobs: list):
    """Create sample regions of interest"""
    for job in analytics_jobs:
        # Create 2-3 ROIs per active analytics job
        for i in range(random.randint(2, 3)):
            # Check if ROI already exists
            result = await session.execute(select(ROI).where(ROI.analytics_job_id == job.id, ROI.name == f"Zone {i+1} - {job.name}"))
            existing = result.scalar_one_or_none()
            
            if not existing:
                roi = ROI(
                    id=uuid4(),
                    name=f"Zone {i+1} - {job.name}",
                    polygon_points=json.dumps([
                        {"x": 0.1 + i*0.2, "y": 0.1 + i*0.2},
                        {"x": 0.3 + i*0.2, "y": 0.1 + i*0.2},
                        {"x": 0.3 + i*0.2, "y": 0.3 + i*0.2},
                        {"x": 0.1 + i*0.2, "y": 0.3 + i*0.2}
                    ]),
                    roi_type="zone",
                    description=f"Detection zone {i+1} for {job.name}",
                    is_active=True,
                    alert_on_entry=True,
                    alert_on_exit=False,
                    analytics_job_id=job.id
                )
                session.add(roi)
                await session.commit()
                print(f"Created ROI: {roi.name}")

async def create_demo_alert_events(session: AsyncSession, cameras: list, analytics_jobs: list):
    """Create sample alert events"""
    object_classes = ["person", "car", "truck", "bus", "bicycle", "motorcycle"]
    alert_types = ["object_detected", "object_entered_zone", "object_exited_zone", "crowd_detected"]
    
    for camera in cameras:
        if camera.status == "online":
            # Find analytics job for this camera
            job = next((job for job in analytics_jobs if job.camera_id == camera.id), None)
            if not job:
                continue
                
            # Create alert events for the last 7 days
            for day in range(7):
                date = datetime.now() - timedelta(days=day)
                
                # Random number of alerts per day (10-30)
                num_alerts = random.randint(10, 30)
                
                for _ in range(num_alerts):
                    timestamp = date - timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                    
                    # Check if alert already exists (avoid duplicates)
                    result = await session.execute(select(AlertEvent).where(
                        AlertEvent.camera_id == camera.id,
                        AlertEvent.timestamp == timestamp
                    ))
                    existing = result.scalar_one_or_none()
                    
                    if not existing:
                        alert = AlertEvent(
                            id=uuid4(),
                            timestamp=timestamp,
                            alert_type=random.choice(alert_types),
                            confidence=random.uniform(0.7, 0.99),
                            object_class=random.choice(object_classes),
                            object_id=f"obj_{random.randint(1000, 9999)}",
                            bbox_x=random.uniform(0.1, 0.8),
                            bbox_y=random.uniform(0.1, 0.8),
                            bbox_width=random.uniform(0.05, 0.3),
                            bbox_height=random.uniform(0.05, 0.3),
                            snapshot_path=f"/snapshots/{camera.id}/{random.randint(1000, 9999)}.jpg",
                            event_metadata=json.dumps({
                                "speed": random.uniform(0, 50),
                                "direction": random.choice(["north", "south", "east", "west"]),
                                "color": random.choice(["red", "blue", "green", "white", "black"])
                            }),
                            processed=random.choice([True, False]),
                            camera_id=camera.id,
                            analytics_job_id=job.id
                        )
                        session.add(alert)
                
                await session.commit()
                print(f"Created sample alert events for camera: {camera.name}")

async def main():
    """Main function to create demo data"""
    print("Creating demo data for Aries Edge Platform...")
    
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(models.SQLModel.metadata.create_all)
        
        async with AsyncSessionLocal() as session:
            # Create demo user
            demo_user = await create_demo_user(session)
            
            # Create demo cameras
            cameras = await create_demo_cameras(session, demo_user.id)
            
            # Create demo streams
            await create_demo_streams(session, cameras)
            
            # Create demo AI models
            ai_models = await create_demo_ai_models(session)
            
            # Create demo analytics jobs
            analytics_jobs = await create_demo_analytics_jobs(session, cameras, ai_models, demo_user.id)
            
            # Create demo ROIs
            await create_demo_rois(session, analytics_jobs)
            
            # Create demo alert events
            await create_demo_alert_events(session, cameras, analytics_jobs)
            
            print("Demo data creation completed successfully!")
            print("\nDemo credentials:")
            print("Username: demo")
            print("Password: demo123")
            print("\nYou can now log in to the frontend and test the dynamic functionality!")
        
    except Exception as e:
        print(f"Error creating demo data: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())