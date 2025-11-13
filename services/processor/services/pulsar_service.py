import pulsar
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class PulsarService:
    """Service for Pulsar message broker integration"""
    
    def __init__(self):
        self.client = None
        self.producer = None
        self.consumer = None
        self.is_connected = False
    
    def connect(self, pulsar_url: str = "pulsar://localhost:6650") -> bool:
        """Connect to Pulsar broker"""
        try:
            self.client = pulsar.Client(pulsar_url)
            self.is_connected = True
            logger.info(f"Connected to Pulsar broker at {pulsar_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Pulsar broker: {e}")
            return False
    
    def create_producer(self, topic: str) -> bool:
        """Create a producer for sending messages"""
        try:
            if not self.client:
                logger.error("Pulsar client not connected")
                return False
            
            self.producer = self.client.create_producer(topic)
            logger.info(f"Created producer for topic: {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to create producer: {e}")
            return False
    
    def create_consumer(self, topic: str, subscription_name: str) -> bool:
        """Create a consumer for receiving messages"""
        try:
            if not self.client:
                logger.error("Pulsar client not connected")
                return False
            
            self.consumer = self.client.subscribe(
                topic=topic,
                subscription_name=subscription_name,
                consumer_type=pulsar.ConsumerType.Shared,
                initial_position=pulsar.InitialPosition.Earliest
            )
            logger.info(f"Created consumer for topic: {topic}, subscription: {subscription_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create consumer: {e}")
            return False
    
    def send_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Send metadata to the broker"""
        try:
            if not self.producer:
                logger.error("Producer not created")
                return False
            
            message = json.dumps(metadata).encode('utf-8')
            self.producer.send(message)
            logger.debug(f"Sent metadata: {metadata}")
            return True
        except Exception as e:
            logger.error(f"Failed to send metadata: {e}")
            return False
    
    def receive_control_message(self, timeout_ms: int = 1000) -> Optional[Dict[str, Any]]:
        """Receive control message from broker"""
        try:
            if not self.consumer:
                logger.error("Consumer not created")
                return None
            
            try:
                msg = self.consumer.receive(timeout_millis=timeout_ms)
                if msg:
                    data = json.loads(msg.data().decode('utf-8'))
                    self.consumer.acknowledge(msg)
                    logger.debug(f"Received control message: {data}")
                    return data
            except pulsar.Timeout:
                # No message available within timeout
                pass
            
            return None
        except Exception as e:
            logger.error(f"Failed to receive control message: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from Pulsar broker"""
        try:
            if self.producer:
                self.producer.close()
            if self.consumer:
                self.consumer.close()
            if self.client:
                self.client.close()
            
            self.is_connected = False
            logger.info("Disconnected from Pulsar broker")
        except Exception as e:
            logger.error(f"Error disconnecting from Pulsar: {e}")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.disconnect()