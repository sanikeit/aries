import asyncio
import json
import logging
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.models import AlertEvent, Camera, AnalyticsJob
from app.core.config import settings
from pulsar import Client, ConsumerType, InitialPosition
from sqlmodel import select

logger = logging.getLogger(__name__)

class MetadataConsumer:
    def __init__(self):
        self.client = None
        self.consumer = None
        self.is_running = False
    
    async def connect(self):
        """Connect to Pulsar broker"""
        try:
            self.client = Client(settings.PULSAR_URL)
            self.consumer = self.client.subscribe(
                topic='aries-metadata-raw',
                subscription_name='api-consumer',
                consumer_type=ConsumerType.Shared,
                initial_position=InitialPosition.Earliest
                )
            logger.info("Connected to Pulsar broker for metadata consumption")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Pulsar broker: {e}")
            return False
    
    async def process_message(self, message: Dict[str, Any]):
        """Process incoming metadata message"""
        try:
            # Parse the message
            camera_id = message.get('camera_id')
            analytics_job_id = message.get('analytics_job_id')
            alert_type = message.get('alert_type', 'object_detected')
            
            if not camera_id or not analytics_job_id:
                logger.warning(f"Invalid message format: {message}")
                return
            
            # Create alert event in database
            async with AsyncSessionLocal() as session:
                # Get camera and analytics job
                camera_result = await session.execute(
                    select(Camera).where(Camera.id == camera_id)
                )
                camera = camera_result.scalar_one_or_none()
                
                job_result = await session.execute(
                    select(AnalyticsJob).where(AnalyticsJob.id == analytics_job_id)
                )
                job = job_result.scalar_one_or_none()
                
                if not camera or not job:
                    logger.warning(f"Camera or job not found: camera_id={camera_id}, job_id={analytics_job_id}")
                    return
                
                # Create alert event
                alert_event = AlertEvent(
                    camera_id=camera_id,
                    analytics_job_id=analytics_job_id,
                    alert_type=alert_type,
                    confidence=message.get('confidence', 0.0),
                    object_class=message.get('object_class', 'unknown'),
                    object_id=message.get('object_id'),
                    bbox_x=message.get('bbox', {}).get('x', 0.0),
                    bbox_y=message.get('bbox', {}).get('y', 0.0),
                    bbox_width=message.get('bbox', {}).get('width', 0.0),
                    bbox_height=message.get('bbox', {}).get('height', 0.0),
                    snapshot_path=message.get('snapshot_path'),
                    event_metadata=json.dumps(message.get('metadata', {}))
                )
                
                session.add(alert_event)
                await session.commit()
                
                logger.info(f"Alert event created: {alert_event.id} for camera {camera_id}")
                
                # Publish to alerts-critical topic for real-time notifications
                await self.publish_critical_alert(alert_event)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def publish_critical_alert(self, alert_event: AlertEvent):
        """Publish critical alerts to the alerts-critical topic"""
        try:
            producer = self.client.create_producer('aries-alerts-critical')
            
            alert_data = {
                'id': alert_event.id,
                'timestamp': alert_event.timestamp.isoformat(),
                'camera_id': alert_event.camera_id,
                'analytics_job_id': alert_event.analytics_job_id,
                'alert_type': alert_event.alert_type,
                'confidence': alert_event.confidence,
                'object_class': alert_event.object_class,
                'object_id': alert_event.object_id,
                'bbox': {
                    'x': alert_event.bbox_x,
                    'y': alert_event.bbox_y,
                    'width': alert_event.bbox_width,
                    'height': alert_event.bbox_height
                },
                'snapshot_path': alert_event.snapshot_path,
                'metadata': alert_event.metadata
            }
            
            producer.send(json.dumps(alert_data).encode('utf-8'))
            producer.close()
            
            logger.info(f"Critical alert published: {alert_event.id}")
            
        except Exception as e:
            logger.error(f"Error publishing critical alert: {e}")
    
    async def consume_metadata(self):
        """Main consumer loop for processing metadata messages"""
        logger.info("Starting metadata consumer service...")
        
        while True:
            try:
                if not self.client:
                    connected = await self.connect()
                    if not connected:
                        await asyncio.sleep(5)
                        continue
                
                # Receive message with timeout
                if not self.consumer:
                    await asyncio.sleep(1)
                    continue

                msg = self.consumer.receive(timeout_millis=1000)
                
                if msg:
                    try:
                        # Parse message
                        message_data = json.loads(msg.data().decode('utf-8'))
                        logger.debug(f"Received message: {message_data}")
                        
                        # Process the message
                        await self.process_message(message_data)
                        
                        # Acknowledge the message
                        self.consumer.acknowledge(msg)
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in message: {e}")
                        self.consumer.negative_acknowledge(msg)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        self.consumer.negative_acknowledge(msg)
                
            except Exception as e:
                logger.error(f"Consumer error: {e}")
                await asyncio.sleep(1)

# Global consumer instance
metadata_consumer = MetadataConsumer()

async def consume_metadata():
    """Entry point for the background consumer service"""
    await metadata_consumer.consume_metadata()
