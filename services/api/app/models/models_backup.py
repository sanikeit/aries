from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from uuid import UUID, uuid4
from enum import Enum
from sqlalchemy import Column, Enum as SQLEnum

# Local enums for database models (SQLModel compatible)
class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class CameraType(str, Enum):
    IP = "ip"
    USB = "usb"
    RTSP = "rtsp"
    FILE = "file"

class CameraStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    RECORDING = "recording"

class StreamStatus(str, Enum):
    IDLE = "idle"
    STREAMING = "streaming"
    ERROR = "error"
    STOPPED = "stopped"

class StreamType(str, Enum):
    HLS = "hls"
    WEBRTC = "webrtc"
    RTMP = "rtmp"

class DetectionClass(str, Enum):
    PERSON = "person"
    # Add other detection classes as needed

class EventType(str, Enum):
    OBJECT_DETECTED = "object_detected"
    LINE_CROSSED = "line_crossed"
    ZONE_ENTERED = "zone_entered"
    ZONE_EXITED = "zone_exited"

# Simple string constants for SQLModel fields
USER_ROLE_VALUES = ["admin", "operator", "viewer"]
USER_STATUS_VALUES = ["active", "inactive", "suspended"]
CAMERA_TYPE_VALUES = ["ip", "usb", "rtsp", "file"]
CAMERA_STATUS_VALUES = ["online", "offline", "error", "recording"]
STREAM_TYPE_VALUES = ["hls", "webrtc", "rtmp"]
STREAM_STATUS_VALUES = ["idle", "streaming", "error", "stopped"]

class User(SQLModel, table=True):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    role: str = Field(default="viewer")
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    cameras: List["Camera"] = Relationship(back_populates="owner")
    analytics_jobs: List["AnalyticsJob"] = Relationship(back_populates="created_by")

class Camera(SQLModel, table=True):
    """Camera model for RTSP stream configuration"""
    __tablename__ = "cameras"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    type: str = Field(default="rtsp")
    url: str  # RTSP URI or file path
    description: Optional[str] = None
    location: Optional[str] = None
    status: str = Field(default="offline")
    is_active: bool = Field(default=True)
    roi: Optional[Dict[str, Any]] = None
    analytics_config: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Foreign keys
    owner_id: UUID = Field(foreign_key="users.id")
    
    # Relationships
    owner: User = Relationship(back_populates="cameras")
    analytics_jobs: List["AnalyticsJob"] = Relationship(back_populates="camera")
    streams: List["Stream"] = Relationship(back_populates="camera")

class Stream(SQLModel, table=True):
    """Stream configuration for video output"""
    __tablename__ = "streams"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    camera_id: UUID = Field(foreign_key="cameras.id")
    type: str = Field(default="hls")
    status: str = Field(default="idle")
    endpoint: str  # Output URL/path
    quality: str = Field(default="medium")  # low, medium, high, ultra
    metadata_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    camera: Camera = Relationship(back_populates="streams")

class Model(SQLModel, table=True):
    """AI model configuration"""
    __tablename__ = "models"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    version: str
    model_type: str = Field(default="yolov8")  # yolov8, yolov9, etc.
    config_path: str  # Path to model config file
    weights_path: str  # Path to model weights
    labels_path: str  # Path to labels file
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    accuracy_metrics: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"type_": "JSON"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    analytics_jobs: List["AnalyticsJob"] = Relationship(back_populates="model")

class AnalyticsJob(SQLModel, table=True):
    """Analytics job linking camera to model with configuration"""
    __tablename__ = "analytics_jobs"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    confidence_threshold: float = Field(default=0.5)
    nms_threshold: float = Field(default=0.4)
    max_detections: int = Field(default=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Foreign keys
    camera_id: UUID = Field(foreign_key="cameras.id")
    model_id: UUID = Field(foreign_key="models.id")
    created_by_id: UUID = Field(foreign_key="users.id")
    
    # Relationships
    camera: Camera = Relationship(back_populates="analytics_jobs")
    model: Model = Relationship(back_populates="analytics_jobs")
    created_by: User = Relationship(back_populates="analytics_jobs")
    rois: List["ROI"] = Relationship(back_populates="analytics_job")
    detections: List["Detection"] = Relationship(back_populates="analytics_job")

class ROI(SQLModel, table=True):
    """Region of Interest for analytics"""
    __tablename__ = "rois"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    polygon_points: List[Dict[str, float]] = Field(sa_column_kwargs={"type_": "JSON"})
    roi_type: str = Field(default="zone")  # zone, line, area
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

class Detection(SQLModel, table=True):
    """Object detection results"""
    __tablename__ = "detections"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    camera_id: UUID = Field(foreign_key="cameras.id")
    analytics_job_id: UUID = Field(foreign_key="analytics_jobs.id")
    class_name: DetectionClass = Field(index=True)
    confidence: float = Field(ge=0, le=1)
    bbox_x: float = Field(ge=0)
    bbox_y: float = Field(ge=0)
    bbox_width: float = Field(gt=0)
    bbox_height: float = Field(gt=0)
    frame_number: int = Field(gt=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"type_": "JSON"})
    
    # Relationships
    analytics_job: AnalyticsJob = Relationship(back_populates="detections")

class AnalyticsEvent(SQLModel, table=True):
    """Analytics events from video processing"""
    __tablename__ = "analytics_events"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    camera_id: UUID = Field(foreign_key="cameras.id")
    analytics_job_id: UUID = Field(foreign_key="analytics_jobs.id")
    event_type: EventType = Field(index=True)
    detections: List[UUID] = Field(default=None, sa_column_kwargs={"type_": "JSON"})  # List of detection IDs
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"type_": "JSON"})

class AlertEvent(SQLModel, table=True):
    """Alert events from video analytics"""
    __tablename__ = "alert_events"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    alert_type: str = Field(index=True)  # zone_entry, zone_exit, object_detected, etc.
    confidence: float
    object_class: DetectionClass
    object_id: Optional[str] = None
    bbox_x: float
    bbox_y: float
    bbox_width: float
    bbox_height: float
    snapshot_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"type_": "JSON"})
    processed: bool = Field(default=False)
    
    # Foreign keys
    camera_id: UUID = Field(foreign_key="cameras.id")
    analytics_job_id: UUID = Field(foreign_key="analytics_jobs.id")
    
    # Relationships
    analytics_job: AnalyticsJob = Relationship(back_populates="alert_events")

class ApiKey(SQLModel, table=True):
    """API key for machine-to-machine authentication"""
    __tablename__ = "api_keys"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    key: str = Field(unique=True, index=True)
    permissions: List[str] = Field(default=None, sa_column_kwargs={"type_": "JSON"})
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class SystemConfig(SQLModel, table=True):
    """System configuration and settings"""
    __tablename__ = "system_config"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    key: str = Field(unique=True, index=True)
    value: Dict[str, Any] = Field(sa_column_kwargs={"type_": "JSON"})
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None