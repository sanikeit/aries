from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AnalyticsJobCreate(BaseModel):
    name: str
    description: Optional[str] = None
    camera_id: int
    model_id: int
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    nms_threshold: float = Field(default=0.4, ge=0.0, le=1.0)
    max_detections: int = Field(default=100, ge=1, le=1000)

class AnalyticsJobResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    camera_id: int
    model_id: int
    confidence_threshold: float
    nms_threshold: float
    max_detections: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ROICreate(BaseModel):
    name: str
    polygon_points: List[Dict[str, float]]
    roi_type: str = Field(default="zone")
    analytics_job_id: int
    description: Optional[str] = None
    alert_on_entry: bool = Field(default=True)
    alert_on_exit: bool = Field(default=False)

class ROIResponse(BaseModel):
    id: int
    name: str
    polygon_points: List[Dict[str, float]]
    roi_type: str
    analytics_job_id: int
    description: Optional[str] = None
    alert_on_entry: bool
    alert_on_exit: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True