"""
Shared schemas for Aries-Edge Platform
Compatible with SQLModel and Pydantic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from sqlmodel import SQLModel

# Enums
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
    BICYCLE = "bicycle"
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    AIRPLANE = "airplane"
    BUS = "bus"
    TRAIN = "train"
    TRUCK = "truck"
    BOAT = "boat"
    TRAFFIC_LIGHT = "traffic light"
    FIRE_HYDRANT = "fire hydrant"
    STOP_SIGN = "stop sign"
    PARKING_METER = "parking meter"
    BENCH = "bench"
    BIRD = "bird"
    CAT = "cat"
    DOG = "dog"
    HORSE = "horse"
    SHEEP = "sheep"
    COW = "cow"
    ELEPHANT = "elephant"
    BEAR = "bear"
    ZEBRA = "zebra"
    GIRAFFE = "giraffe"
    BACKPACK = "backpack"
    UMBRELLA = "umbrella"
    HANDBAG = "handbag"
    TIE = "tie"
    SUITCASE = "suitcase"
    FRISBEE = "frisbee"
    SKIS = "skis"
    SNOWBOARD = "snowboard"
    SPORTS_BALL = "sports ball"
    KITE = "kite"
    BASEBALL_BAT = "baseball bat"
    BASEBALL_GLOVE = "baseball glove"
    SKATEBOARD = "skateboard"
    SURFBOARD = "surfboard"
    TENNIS_RACKET = "tennis racket"
    BOTTLE = "bottle"
    WINE_GLASS = "wine glass"
    CUP = "cup"
    FORK = "fork"
    KNIFE = "knife"
    SPOON = "spoon"
    BOWL = "bowl"
    BANANA = "banana"
    APPLE = "apple"
    SANDWICH = "sandwich"
    ORANGE = "orange"
    BROCCOLI = "broccoli"
    CARROT = "carrot"
    HOT_DOG = "hot dog"
    PIZZA = "pizza"
    DONUT = "donut"
    CAKE = "cake"
    CHAIR = "chair"
    COUCH = "couch"
    POTTED_PLANT = "potted plant"
    BED = "bed"
    DINING_TABLE = "dining table"
    TOILET = "toilet"
    TV = "tv"
    LAPTOP = "laptop"
    MOUSE = "mouse"
    REMOTE = "remote"
    KEYBOARD = "keyboard"
    CELL_PHONE = "cell phone"
    MICROWAVE = "microwave"
    OVEN = "oven"
    TOASTER = "toaster"
    SINK = "sink"
    REFRIGERATOR = "refrigerator"
    BOOK = "book"
    CLOCK = "clock"
    VASE = "vase"
    SCISSORS = "scissors"
    TEDDY_BEAR = "teddy bear"
    HAIR_DRIER = "hair drier"
    TOOTHBRUSH = "toothbrush"

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    API = "api"

class EventType(str, Enum):
    OBJECT_DETECTED = "object_detected"
    LINE_CROSSED = "line_crossed"
    ZONE_ENTERED = "zone_entered"
    ZONE_EXITED = "zone_exited"

class WsMessageType(str, Enum):
    CONNECTION = "connection"
    DETECTION = "detection"
    ANALYTICS = "analytics"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

# Base models
class TimestampMixin(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# User models
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: str = Field(min_length=1, max_length=100)
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE

class User(UserBase, TimestampMixin):
    id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

class CreateUser(UserBase):
    password: str = Field(min_length=8)

class UpdateUser(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    password: Optional[str] = Field(None, min_length=8)

# Camera models
class BoundingBox(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)

class AnalyticsConfig(BaseModel):
    enabled: bool
    detection_classes: List[str]
    confidence_threshold: float = Field(ge=0, le=1)
    iou_threshold: float = Field(ge=0, le=1)

class CameraBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: CameraType
    url: str = Field(pattern=r'^[a-zA-Z][a-zA-Z0-9+.-]*://.*')
    is_active: bool = True
    roi: Optional[List[BoundingBox]] = None
    analytics_config: Optional[AnalyticsConfig] = None

class Camera(CameraBase, TimestampMixin):
    id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    status: CameraStatus = CameraStatus.OFFLINE

class CreateCamera(CameraBase):
    pass

class UpdateCamera(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[CameraType] = None
    url: Optional[str] = Field(None, pattern=r'^[a-zA-Z][a-zA-Z0-9+.-]*://.*')
    is_active: Optional[bool] = None
    roi: Optional[List[BoundingBox]] = None
    analytics_config: Optional[AnalyticsConfig] = None

# Stream models
class StreamBase(BaseModel):
    camera_id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    type: StreamType
    endpoint: str = Field(pattern=r'^[a-zA-Z][a-zA-Z0-9+.-]*://.*')
    quality: str = Field(pattern=r'^(low|medium|high|ultra)$')
    metadata_enabled: bool = True

class Stream(StreamBase, TimestampMixin):
    id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    status: StreamStatus = StreamStatus.IDLE

class CreateStream(StreamBase):
    pass

# Detection models
class BoundingBoxDetection(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    confidence: float = Field(ge=0, le=1)

class DetectionBase(BaseModel):
    camera_id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    class_name: DetectionClass
    bbox: BoundingBoxDetection
    confidence: float = Field(ge=0, le=1)
    frame_number: int = Field(gt=0)
    metadata: Optional[Dict[str, Any]] = None

class Detection(DetectionBase):
    id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CreateDetection(DetectionBase):
    pass

# Analytics event models
class AnalyticsEventBase(BaseModel):
    camera_id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    event_type: EventType
    detections: List[Detection]
    metadata: Optional[Dict[str, Any]] = None

class AnalyticsEvent(AnalyticsEventBase):
    id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CreateAnalyticsEvent(AnalyticsEventBase):
    pass

# Authentication models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(gt=0)
    refresh_token: Optional[str] = None

class Login(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)

class ApiKeyBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    permissions: List[str]
    expires_at: Optional[datetime] = None

class ApiKey(ApiKeyBase, TimestampMixin):
    id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    key: str
    last_used: Optional[datetime] = None

class CreateApiKey(ApiKeyBase):
    pass

# WebSocket message models
class WsMessageBase(BaseModel):
    payload: Dict[str, Any]
    camera_id: Optional[str] = Field(None, pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

class WsMessage(WsMessageBase):
    type: WsMessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DetectionWsMessage(WsMessage):
    type: WsMessageType = WsMessageType.DETECTION
    payload: Detection

class AnalyticsWsMessage(WsMessage):
    type: WsMessageType = WsMessageType.ANALYTICS
    payload: AnalyticsEvent

# Configuration models
class SystemConfig(BaseModel):
    max_cameras: int = Field(gt=0)
    max_streams_per_camera: int = Field(gt=0)
    detection_threshold: float = Field(ge=0, le=1)
    nms_threshold: float = Field(ge=0, le=1)
    stream_quality: str = Field(pattern=r'^(low|medium|high|ultra)$')
    analytics_enabled: bool
    retention_days: int = Field(gt=0)

class UpdateSystemConfig(BaseModel):
    max_cameras: Optional[int] = Field(None, gt=0)
    max_streams_per_camera: Optional[int] = Field(None, gt=0)
    detection_threshold: Optional[float] = Field(None, ge=0, le=1)
    nms_threshold: Optional[float] = Field(None, ge=0, le=1)
    stream_quality: Optional[str] = Field(None, pattern=r'^(low|medium|high|ultra)$')
    analytics_enabled: Optional[bool] = None
    retention_days: Optional[int] = Field(None, gt=0)

# SQLModel compatibility
class UserModel(SQLModel, User):
    pass

class CameraModel(SQLModel, Camera):
    pass

class StreamModel(SQLModel, Stream):
    pass

class DetectionModel(SQLModel, Detection):
    pass

class AnalyticsEventModel(SQLModel, AnalyticsEvent):
    pass

class ApiKeyModel(SQLModel, ApiKey):
    pass