import asyncio
import cv2
import numpy as np
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from uuid import uuid4

logger = logging.getLogger(__name__)

@dataclass
class StreamConfig:
    """Video stream configuration"""
    camera_id: str
    url: str
    quality: str = "medium"  # low, medium, high
    fps: int = 15
    width: int = 640
    height: int = 480
    buffer_size: int = 30
    reconnect_attempts: int = 3
    reconnect_delay: int = 5

class VideoStreamProcessor:
    """
    Video stream processor for real-time video analytics
    Handles RTSP streams, frame processing, and HLS streaming
    """
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_connected = False
        self.frame_buffer: List[np.ndarray] = []
        self.metadata_buffer: List[Dict[str, Any]] = []
        self.current_frame: Optional[np.ndarray] = None
        self.frame_count = 0
        self.error_count = 0
        self.last_frame_time = datetime.utcnow()
        self.stream_status = "idle"
        self.stream_metadata: Dict[str, Any] = {}
        
    async def connect(self) -> bool:
        """Connect to the video stream"""
        try:
            # Configure OpenCV for RTSP streaming
            self.cap = cv2.VideoCapture(self.config.url)
            
            # Set buffer size to reduce latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.config.buffer_size)
            
            # Set resolution based on quality
            if self.config.quality == "high":
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            elif self.config.quality == "medium":
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            else:  # low
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            
            # Test connection
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.is_connected = True
                self.stream_status = "connected"
                self.current_frame = frame
                self.frame_count += 1
                self.last_frame_time = datetime.utcnow()
                logger.info(f"Successfully connected to stream: {self.config.camera_id}")
                return True
            else:
                logger.error(f"Failed to read initial frame from stream: {self.config.camera_id}")
                self.cleanup()
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to stream {self.config.camera_id}: {e}")
            self.cleanup()
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            try:
                self.cap.release()
            except Exception as e:
                logger.error(f"Error releasing video capture: {e}")
        
        self.cap = None
        self.is_connected = False
        self.stream_status = "disconnected"
        self.frame_buffer.clear()
        self.metadata_buffer.clear()
    
    async def read_frame(self) -> Optional[np.ndarray]:
        """Read a single frame from the stream"""
        if not self.cap or not self.is_connected:
            return None
        
        try:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.current_frame = frame
                self.frame_count += 1
                self.last_frame_time = datetime.utcnow()
                self.error_count = 0  # Reset error count on successful read
                return frame
            else:
                self.error_count += 1
                logger.warning(f"Failed to read frame from stream {self.config.camera_id}, error count: {self.error_count}")
                
                # If too many consecutive errors, disconnect
                if self.error_count >= self.config.reconnect_attempts:
                    logger.error(f"Too many consecutive errors, disconnecting from stream {self.config.camera_id}")
                    self.cleanup()
                
                return None
                
        except Exception as e:
            logger.error(f"Error reading frame from stream {self.config.camera_id}: {e}")
            self.error_count += 1
            
            if self.error_count >= self.config.reconnect_attempts:
                self.cleanup()
            
            return None
    
    def get_stream_info(self) -> Dict[str, Any]:
        """Get current stream information"""
        if not self.cap:
            return {
                "camera_id": self.config.camera_id,
                "status": self.stream_status,
                "connected": False,
                "frame_count": self.frame_count,
                "error_count": self.error_count
            }
        
        # Get video properties
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        bitrate = self.cap.get(cv2.CAP_PROP_BITRATE)
        
        return {
            "camera_id": self.config.camera_id,
            "status": self.stream_status,
            "connected": self.is_connected,
            "frame_count": self.frame_count,
            "error_count": self.error_count,
            "fps": fps if fps > 0 else self.config.fps,
            "resolution": f"{int(width)}x{int(height)}",
            "bitrate": bitrate,
            "last_frame_time": self.last_frame_time.isoformat(),
            "stream_metadata": self.stream_metadata
        }
    
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a frame and extract metadata"""
        height, width = frame.shape[:2]
        
        # Basic frame analysis
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "frame_number": self.frame_count,
            "resolution": {"width": width, "height": height},
            "brightness": float(np.mean(frame)),
            "contrast": float(np.std(frame)),
            "motion_score": 0.0,  # Will be calculated if previous frame exists
            "quality_score": 1.0  # Will be calculated based on various factors
        }
        
        # Calculate motion score if we have a previous frame
        if len(self.frame_buffer) > 0:
            prev_frame = self.frame_buffer[-1]
            if prev_frame.shape == frame.shape:
                # Simple motion detection using frame difference
                diff = cv2.absdiff(prev_frame, frame)
                motion_score = float(np.mean(diff))
                metadata["motion_score"] = motion_score
        
        # Add frame to buffer (keep last 10 frames for analysis)
        self.frame_buffer.append(frame.copy())
        if len(self.frame_buffer) > 10:
            self.frame_buffer.pop(0)
        
        # Add metadata to buffer
        self.metadata_buffer.append(metadata)
        if len(self.metadata_buffer) > 100:
            self.metadata_buffer.pop(0)
        
        return metadata
    
    async def generate_hls_segment(self, duration: int = 2) -> Optional[Dict[str, Any]]:
        """Generate HLS segment from buffered frames"""
        if not self.frame_buffer:
            return None
        
        try:
            # Create video writer for HLS segment
            segment_id = str(uuid4())[:8]
            output_path = f"/tmp/hls_{self.config.camera_id}_{segment_id}.ts"
            
            # Get frame dimensions from first frame
            first_frame = self.frame_buffer[0]
            height, width = first_frame.shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, self.config.fps, (width, height))
            
            # Write frames to segment
            for frame in self.frame_buffer:
                out.write(frame)
            
            out.release()
            
            # Calculate segment metadata
            segment_metadata = {
                "segment_id": segment_id,
                "camera_id": self.config.camera_id,
                "duration": duration,
                "frame_count": len(self.frame_buffer),
                "resolution": f"{width}x{height}",
                "file_path": output_path,
                "timestamp": datetime.utcnow().isoformat(),
                "size": cv2.imencode('.jpg', first_frame)[1].nbytes * len(self.frame_buffer)  # Approximate size
            }
            
            return segment_metadata
            
        except Exception as e:
            logger.error(f"Error generating HLS segment for camera {self.config.camera_id}: {e}")
            return None
    
    def get_recent_metadata(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent frame metadata"""
        return self.metadata_buffer[-count:] if self.metadata_buffer else []
    
    def get_frame_at_time(self, timestamp: datetime) -> Optional[np.ndarray]:
        """Get frame closest to specified timestamp"""
        if not self.metadata_buffer:
            return None
        
        # Find metadata entry closest to timestamp
        closest_idx = 0
        min_time_diff = float('inf')
        
        for i, metadata in enumerate(self.metadata_buffer):
            meta_time = datetime.fromisoformat(metadata["timestamp"])
            time_diff = abs((meta_time - timestamp).total_seconds())
            
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_idx = i
        
        # Return corresponding frame if available
        if closest_idx < len(self.frame_buffer):
            return self.frame_buffer[closest_idx]
        
        return None

class StreamManager:
    """
    Manages multiple video streams and provides HLS streaming capabilities
    """
    
    def __init__(self):
        self.streams: Dict[str, VideoStreamProcessor] = {}
        self.hls_playlists: Dict[str, List[Dict[str, Any]]] = {}
        self.max_segments_per_playlist = 10
        
    async def start_stream(self, camera_id: str, stream_url: str, config: Optional[StreamConfig] = None) -> bool:
        """Start a new video stream"""
        if camera_id in self.streams:
            logger.warning(f"Stream already exists for camera {camera_id}")
            return True
        
        # Create stream configuration
        if not config:
            config = StreamConfig(camera_id=camera_id, url=stream_url)
        else:
            config.camera_id = camera_id
            config.url = stream_url
        
        # Create and start stream processor
        processor = VideoStreamProcessor(config)
        success = await processor.connect()
        
        if success:
            self.streams[camera_id] = processor
            self.hls_playlists[camera_id] = []
            logger.info(f"Successfully started stream for camera {camera_id}")
            
            # Start background processing
            asyncio.create_task(self._process_stream(camera_id))
            
        return success
    
    async def stop_stream(self, camera_id: str) -> bool:
        """Stop a video stream"""
        if camera_id not in self.streams:
            logger.warning(f"Stream not found for camera {camera_id}")
            return False
        
        processor = self.streams[camera_id]
        processor.cleanup()
        
        del self.streams[camera_id]
        if camera_id in self.hls_playlists:
            del self.hls_playlists[camera_id]
        
        logger.info(f"Stopped stream for camera {camera_id}")
        return True
    
    async def _process_stream(self, camera_id: str):
        """Background processing for a stream"""
        processor = self.streams.get(camera_id)
        if not processor:
            return
        
        try:
            while processor.is_connected:
                # Read frame
                frame = await processor.read_frame()
                if frame is not None:
                    # Process frame
                    metadata = processor.process_frame(frame)
                    
                    # Generate HLS segment every few seconds
                    if processor.frame_count % (processor.config.fps * 2) == 0:
                        segment = await processor.generate_hls_segment(duration=2)
                        if segment:
                            await self._add_hls_segment(camera_id, segment)
                
                # Small delay to prevent CPU overload
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error processing stream {camera_id}: {e}")
        finally:
            # Cleanup if processing stops
            if camera_id in self.streams:
                await self.stop_stream(camera_id)
    
    async def _add_hls_segment(self, camera_id: str, segment: Dict[str, Any]):
        """Add HLS segment to playlist"""
        if camera_id not in self.hls_playlists:
            self.hls_playlists[camera_id] = []
        
        playlist = self.hls_playlists[camera_id]
        playlist.append(segment)
        
        # Keep only recent segments
        if len(playlist) > self.max_segments_per_playlist:
            # Remove oldest segment
            old_segment = playlist.pop(0)
            # Clean up old segment file
            try:
                import os
                if os.path.exists(old_segment["file_path"]):
                    os.remove(old_segment["file_path"])
            except Exception as e:
                logger.warning(f"Failed to remove old segment file: {e}")
    
    def get_stream_info(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Get stream information"""
        processor = self.streams.get(camera_id)
        if not processor:
            return None
        
        info = processor.get_stream_info()
        
        # Add HLS playlist info
        if camera_id in self.hls_playlists:
            playlist = self.hls_playlists[camera_id]
            info["hls_segments"] = len(playlist)
            info["hls_playlist_duration"] = sum(seg["duration"] for seg in playlist)
        
        return info
    
    def get_hls_playlist(self, camera_id: str) -> Optional[str]:
        """Generate HLS playlist (m3u8) for a camera"""
        if camera_id not in self.hls_playlists:
            return None
        
        playlist = self.hls_playlists[camera_id]
        if not playlist:
            return None
        
        # Generate M3U8 playlist
        m3u8_content = ["#EXTM3U", "#EXT-X-VERSION:3", "#EXT-X-TARGETDURATION:3"]
        
        for segment in playlist:
            m3u8_content.append(f"#EXTINF:{segment['duration']:.3f},")
            m3u8_content.append(f"segment_{segment['segment_id']}.ts")
        
        m3u8_content.append("#EXT-X-ENDLIST")
        
        return "\n".join(m3u8_content)
    
    def get_active_streams(self) -> List[str]:
        """Get list of active stream camera IDs"""
        return [camera_id for camera_id, processor in self.streams.items() if processor.is_connected]
    
    def get_all_stream_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information for all streams"""
        return {
            camera_id: processor.get_stream_info()
            for camera_id, processor in self.streams.items()
        }

# Global stream manager instance
stream_manager = StreamManager()