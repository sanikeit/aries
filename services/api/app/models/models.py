from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    """Simplified User model"""
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    role: str = Field(default="viewer")
    status: str = Field(default="active")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    cameras: List["Camera"] = Relationship(back_populates="owner")
    analytics_jobs: List["AnalyticsJob"] = Relationship(back_populates="created_by")

class Camera(SQLModel, table=True):
    """Simplified Camera model"""
    __tablename__ = "cameras"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    type: str = Field(default="rtsp")
    url: str
    description: Optional[str] = None
    location: Optional[str] = None
    status: str = Field(default="offline")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Foreign keys
    owner_id: UUID = Field(foreign_key="users.id")
    
    # Relationships
    owner: User = Relationship(back_populates="cameras")
    analytics_jobs: List["AnalyticsJob"] = Relationship(back_populates="camera")
    streams: List["Stream"] = Relationship(back_populates="camera")

class Stream(SQLModel, table=True):
    """Stream configuration"""
    __tablename__ = "streams"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    camera_id: UUID = Field(foreign_key="cameras.id")
    type: str = Field(default="hls")
    status: str = Field(default="idle")
    endpoint: str
    quality: str = Field(default="medium")
    metadata_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    camera: Camera = Relationship(back_populates="streams")

class AIModel(SQLModel, table=True):
    """AI Model configuration"""
    __tablename__ = "ai_models"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    version: str
    ai_model_type: str = Field(default="yolov8")
    config_path: str
    weights_path: str
    labels_path: str
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    analytics_jobs: List["AnalyticsJob"] = Relationship(back_populates="ai_model")

class AnalyticsJob(SQLModel, table=True):
    """Analytics job configuration"""
    __tablename__ = "analytics_jobs"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    confidence_threshold: float = Field(default=0.5)
    nms_threshold: float = Field(default=0.4)
    max_detections: int = Field(default=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Foreign keys
    camera_id: UUID = Field(foreign_key="cameras.id")
    ai_model_id: UUID = Field(foreign_key="ai_models.id")
    created_by_id: UUID = Field(foreign_key="users.id")
    
    # Relationships
    camera: Camera = Relationship(back_populates="analytics_jobs")
    ai_model: AIModel = Relationship(back_populates="analytics_jobs")
    created_by: User = Relationship(back_populates="analytics_jobs")
    rois: List["ROI"] = Relationship(back_populates="analytics_job")

class ROI(SQLModel, table=True):
    """Region of Interest"""
    __tablename__ = "rois"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    polygon_points: str = Field(default="[]")  # JSON string for polygon points
    roi_type: str = Field(default="zone")
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    alert_on_entry: bool = Field(default=True)
    alert_on_exit: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Foreign keys
    analytics_job_id: UUID = Field(foreign_key="analytics_jobs.id")
    
    # Relationships
    analytics_job: AnalyticsJob = Relationship(back_populates="rois")

class AlertEvent(SQLModel, table=True):
    """Alert events"""
    __tablename__ = "alert_events"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    alert_type: str = Field(default="object_detected")
    confidence: float
    object_class: str
    object_id: Optional[str] = None
    bbox_x: float
    bbox_y: float
    bbox_width: float
    bbox_height: float
    snapshot_path: Optional[str] = None
    event_metadata: Optional[str] = None  # JSON string for metadata
    processed: bool = Field(default=False)
    
    # Foreign keys
    camera_id: UUID = Field(foreign_key="cameras.id")
    analytics_job_id: UUID = Field(foreign_key="analytics_jobs.id")
    
    # Relationships
    camera: Camera = Relationship()
    analytics_job: AnalyticsJob = Relationship()