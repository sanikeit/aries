from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class CameraCreate(BaseModel):
    name: str
    rtsp_uri: str
    description: Optional[str] = None
    location: Optional[str] = None

class CameraResponse(BaseModel):
    id: UUID
    name: str
    url: str
    description: Optional[str] = None
    location: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_uri: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None