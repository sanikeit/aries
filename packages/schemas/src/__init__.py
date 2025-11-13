# Aries-Edge Schemas

from .schemas import (
    # Enums
    UserRole,
    UserStatus,
    CameraType,
    CameraStatus,
    StreamStatus,
    StreamType,
    DetectionClass,
    TokenType,
    EventType,
    WsMessageType,
    
    # Base models
    TimestampMixin,
    
    # User models
    UserBase,
    User,
    CreateUser,
    UpdateUser,
    
    # Camera models
    BoundingBox,
    AnalyticsConfig,
    CameraBase,
    Camera,
    CreateCamera,
    UpdateCamera,
    
    # Stream models
    StreamBase,
    Stream,
    CreateStream,
    
    # Detection models
    BoundingBoxDetection,
    DetectionBase,
    Detection,
    CreateDetection,
    
    # Analytics models
    AnalyticsEventBase,
    AnalyticsEvent,
    CreateAnalyticsEvent,
    
    # Authentication models
    Token,
    Login,
    ApiKeyBase,
    ApiKey,
    CreateApiKey,
    
    # WebSocket models
    WsMessageBase,
    WsMessage,
    DetectionWsMessage,
    AnalyticsWsMessage,
    
    # Configuration models
    SystemConfig,
    UpdateSystemConfig,
    
    # SQLModel compatibility
    UserModel,
    CameraModel,
    StreamModel,
    DetectionModel,
    AnalyticsEventModel,
    ApiKeyModel,
)

__version__ = "1.0.0"
__all__ = [
    # Enums
    "UserRole",
    "UserStatus", 
    "CameraType",
    "CameraStatus",
    "StreamStatus",
    "StreamType",
    "DetectionClass",
    "TokenType",
    "EventType",
    "WsMessageType",
    
    # Base models
    "TimestampMixin",
    
    # User models
    "UserBase",
    "User",
    "CreateUser",
    "UpdateUser",
    
    # Camera models
    "BoundingBox",
    "AnalyticsConfig",
    "CameraBase",
    "Camera",
    "CreateCamera",
    "UpdateCamera",
    
    # Stream models
    "StreamBase",
    "Stream",
    "CreateStream",
    
    # Detection models
    "BoundingBoxDetection",
    "DetectionBase",
    "Detection",
    "CreateDetection",
    
    # Analytics models
    "AnalyticsEventBase",
    "AnalyticsEvent",
    "CreateAnalyticsEvent",
    
    # Authentication models
    "Token",
    "Login",
    "ApiKeyBase",
    "ApiKey",
    "CreateApiKey",
    
    # WebSocket models
    "WsMessageBase",
    "WsMessage",
    "DetectionWsMessage",
    "AnalyticsWsMessage",
    
    # Configuration models
    "SystemConfig",
    "UpdateSystemConfig",
    
    # SQLModel compatibility
    "UserModel",
    "CameraModel",
    "StreamModel",
    "DetectionModel",
    "AnalyticsEventModel",
    "ApiKeyModel",
]