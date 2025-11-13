import asyncio
import random
import json
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.models import Camera, AnalyticsJob, AlertEvent, AIModel
from app.db.session import AsyncSessionLocal

class DetectionSimulator:
    """
    Simulates real-time object detection similar to OpenDataCam
    Generates realistic detection events with tracking and counting
    """
    
    def __init__(self):
        self.is_running = False
        self.detection_rate = 0.5  # detections per second per camera
        self.object_classes = ["person", "car", "truck", "bus", "bicycle", "motorcycle"]
        self.active_detections: Dict[str, Dict] = {}  # Track active objects
        self.object_counters: Dict[str, Dict] = {}  # Object counting per camera
        self.websocket_manager = None
        
    def set_websocket_manager(self, websocket_manager):
        """Set the WebSocket manager for real-time updates"""
        self.websocket_manager = websocket_manager
        
    async def get_active_cameras(self, session: AsyncSession) -> List[Camera]:
        """Get all active cameras with analytics jobs"""
        result = await session.execute(
            select(Camera)
            .where(Camera.status == "online", Camera.is_active == True)
        )
        return result.scalars().all()
        
    async def get_analytics_job_for_camera(self, session: AsyncSession, camera_id: str) -> Optional[AnalyticsJob]:
        """Get active analytics job for camera"""
        result = await session.execute(
            select(AnalyticsJob)
            .where(
                AnalyticsJob.camera_id == camera_id,
                AnalyticsJob.is_active == True
            )
        )
        return result.scalar_one_or_none()
        
    def generate_object_id(self, camera_id: str, object_class: str) -> str:
        """Generate a unique object ID with tracking simulation"""
        # Simulate object tracking - some objects persist across frames
        if random.random() < 0.3:  # 30% chance of reusing existing object
            existing_objects = [
                obj_id for obj_id, obj_data in self.active_detections.items()
                if obj_data["camera_id"] == camera_id and obj_data["class"] == object_class
                and (datetime.utcnow() - obj_data["last_seen"]).seconds < 30  # Track for 30 seconds
            ]
            if existing_objects:
                return random.choice(existing_objects)
                
        return f"{object_class}_{uuid4().hex[:8]}"
        
    def generate_bounding_box(self, camera_id: str, object_class: str) -> Dict:
        """Generate realistic bounding box coordinates"""
        # Different object types have different typical sizes and positions
        if object_class == "person":
            width = random.uniform(0.05, 0.15)  # People are relatively small
            height = random.uniform(0.15, 0.35)
            x = random.uniform(0.1, 0.8)
            y = random.uniform(0.3, 0.7)  # People usually appear in lower part of frame
        elif object_class in ["car", "truck", "bus"]:
            width = random.uniform(0.15, 0.4)  # Vehicles are larger
            height = random.uniform(0.1, 0.25)
            x = random.uniform(0.05, 0.7)
            y = random.uniform(0.4, 0.8)  # Vehicles on road area
        else:  # bicycles, motorcycles
            width = random.uniform(0.08, 0.2)
            height = random.uniform(0.1, 0.2)
            x = random.uniform(0.1, 0.8)
            y = random.uniform(0.4, 0.8)
            
        return {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        
    def generate_object_metadata(self, object_class: str) -> Dict:
        """Generate additional metadata for detected objects"""
        metadata = {}
        
        if object_class in ["car", "truck", "bus", "motorcycle"]:
            metadata["speed"] = random.uniform(0, 60)  # km/h
            metadata["direction"] = random.choice(["north", "south", "east", "west"])
            metadata["color"] = random.choice(["red", "blue", "green", "white", "black", "silver"])
            
        if object_class == "person":
            metadata["posture"] = random.choice(["standing", "walking", "running"])
            metadata["bag"] = random.choice(["none", "backpack", "handbag", "briefcase"])
            
        return metadata
        
    async def simulate_detection(self, camera: Camera, analytics_job: AnalyticsJob):
        """Simulate a single detection event"""
        object_class = random.choice(self.object_classes)
        object_id = self.generate_object_id(camera.id, object_class)
        bbox = self.generate_bounding_box(camera.id, object_class)
        confidence = random.uniform(0.7, 0.99)
        metadata = self.generate_object_metadata(object_class)
        
        # Update active detections
        self.active_detections[object_id] = {
            "camera_id": camera.id,
            "class": object_class,
            "last_seen": datetime.utcnow()
        }
        
        # Update object counters
        if camera.id not in self.object_counters:
            self.object_counters[camera.id] = {}
        
        if object_class not in self.object_counters[camera.id]:
            self.object_counters[camera.id][object_class] = 0
            
        # Count new objects (not recently seen)
        if (datetime.utcnow() - self.active_detections[object_id].get("first_seen", datetime.utcnow())).seconds < 1:
            self.object_counters[camera.id][object_class] += 1
            
        # Create alert event
        alert_event = AlertEvent(
            id=uuid4(),
            timestamp=datetime.utcnow(),
            alert_type="object_detected",
            confidence=confidence,
            object_class=object_class,
            object_id=object_id,
            bbox_x=bbox["x"],
            bbox_y=bbox["y"],
            bbox_width=bbox["width"],
            bbox_height=bbox["height"],
            snapshot_path=f"/snapshots/{camera.id}/{uuid4().hex[:8]}.jpg",
            event_metadata=json.dumps(metadata),
            processed=True,
            camera_id=camera.id,
            analytics_job_id=analytics_job.id
        )
        
        return alert_event
        
    async def save_detection_to_db(self, alert_event: AlertEvent):
        """Save detection event to database"""
        async with AsyncSessionLocal() as session:
            session.add(alert_event)
            await session.commit()
            
    async def broadcast_detection(self, alert_event: AlertEvent):
        """Broadcast detection via WebSocket"""
        if self.websocket_manager:
            detection_data = {
                "id": str(alert_event.id),
                "timestamp": alert_event.timestamp.isoformat(),
                "camera_id": str(alert_event.camera_id),
                "object_class": alert_event.object_class,
                "confidence": alert_event.confidence,
                "bbox": {
                    "x": alert_event.bbox_x,
                    "y": alert_event.bbox_y,
                    "width": alert_event.bbox_width,
                    "height": alert_event.bbox_height
                },
                "object_id": alert_event.object_id,
                "speed": json.loads(alert_event.event_metadata or "{}").get("speed"),
                "direction": json.loads(alert_event.event_metadata or "{}").get("direction"),
                "color": json.loads(alert_event.event_metadata or "{}").get("color")
            }
            
            await self.websocket_manager.broadcast_detection(detection_data)
            
    async def broadcast_object_counts(self, camera_id: str):
        """Broadcast current object counts for a camera"""
        if self.websocket_manager and camera_id in self.object_counters:
            counts = []
            for object_class, count in self.object_counters[camera_id].items():
                counts.append({
                    "object_class": object_class,
                    "count": count,
                    "last_updated": datetime.utcnow().isoformat()
                })
                
            await self.websocket_manager.broadcast_object_counts(camera_id, counts)
            
    async def calculate_detection_stats(self, camera_id: str) -> Dict:
        """Calculate detection statistics for a camera"""
        async with AsyncSessionLocal() as session:
            # Get recent detections (last hour)
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            result = await session.execute(
                select(AlertEvent)
                .where(
                    AlertEvent.camera_id == camera_id,
                    AlertEvent.timestamp >= one_hour_ago
                )
            )
            recent_detections = result.scalars().all()
            
            if not recent_detections:
                return {
                    "total_detections": 0,
                    "objects_by_class": [],
                    "average_confidence": 0.0,
                    "detection_rate": 0.0
                }
                
            # Calculate statistics
            total_detections = len(recent_detections)
            
            # Objects by class
            objects_by_class = {}
            total_confidence = 0.0
            
            for detection in recent_detections:
                obj_class = detection.object_class
                if obj_class not in objects_by_class:
                    objects_by_class[obj_class] = 0
                objects_by_class[obj_class] += 1
                total_confidence += detection.confidence
                
            # Convert to list format
            objects_by_class_list = [
                {
                    "object_class": obj_class,
                    "count": count,
                    "last_updated": datetime.utcnow().isoformat()
                }
                for obj_class, count in objects_by_class.items()
            ]
            
            average_confidence = total_confidence / total_detections if total_detections > 0 else 0.0
            
            # Detection rate (detections per minute)
            time_span_minutes = 60  # Last hour
            detection_rate = total_detections / time_span_minutes if time_span_minutes > 0 else 0.0
            
            return {
                "total_detections": total_detections,
                "objects_by_class": objects_by_class_list,
                "average_confidence": average_confidence,
                "detection_rate": detection_rate
            }
            
    async def broadcast_detection_stats(self, camera_id: str):
        """Broadcast detection statistics for a camera"""
        if self.websocket_manager:
            stats = await self.calculate_detection_stats(camera_id)
            await self.websocket_manager.broadcast_detection_stats(camera_id, stats)
            
    async def run_simulation(self):
        """Main simulation loop"""
        self.is_running = True
        
        while self.is_running:
            try:
                async with AsyncSessionLocal() as session:
                    # Get active cameras
                    cameras = await self.get_active_cameras(session)
                    
                    for camera in cameras:
                        # Get analytics job for camera
                        analytics_job = await self.get_analytics_job_for_camera(session, camera.id)
                        if not analytics_job:
                            continue
                            
                        # Generate detections based on detection rate
                        # Use a simple random approach instead of poisson
                        detections_this_cycle = random.randint(0, int(self.detection_rate * 2))
                        
                        for _ in range(detections_this_cycle):
                            # Simulate detection
                            alert_event = await self.simulate_detection(camera, analytics_job)
                            
                            # Save to database
                            await self.save_detection_to_db(alert_event)
                            
                            # Broadcast detection
                            await self.broadcast_detection(alert_event)
                            
                        # Broadcast object counts and stats periodically
                        if random.random() < 0.1:  # 10% chance each cycle
                            await self.broadcast_object_counts(camera.id)
                            await self.broadcast_detection_stats(camera.id)
                            
                # Wait before next cycle
                await asyncio.sleep(1)  # 1 second cycle
                
            except Exception as e:
                print(f"Error in detection simulation: {e}")
                await asyncio.sleep(5)  # Wait longer on error
                
    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        
    def update_detection_rate(self, rate: float):
        """Update the detection rate"""
        self.detection_rate = max(0.1, min(5.0, rate))  # Between 0.1 and 5.0
        
    def reset_counters(self, camera_id: Optional[str] = None):
        """Reset object counters"""
        if camera_id:
            self.object_counters[camera_id] = {}
        else:
            self.object_counters = {}
            
    def get_current_counts(self, camera_id: str) -> Dict[str, int]:
        """Get current object counts for a camera"""
        return self.object_counters.get(camera_id, {})

# Global simulator instance
detection_simulator = DetectionSimulator()