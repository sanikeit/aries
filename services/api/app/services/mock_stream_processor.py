"""
Mock Stream Processor for testing HLS streaming functionality
Generates test HLS streams without requiring real RTSP sources
"""

import asyncio
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MockStreamProcessor:
    """Mock stream processor that generates test HLS streams"""
    
    def __init__(self, output_dir: str = "./hls_streams"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.active_streams: Dict[str, bool] = {}
        self.stream_tasks: Dict[str, asyncio.Task] = {}
        
    async def start_stream(self, camera_id: str, rtsp_url: str) -> bool:
        """Start generating mock HLS stream for a camera"""
        if camera_id in self.active_streams:
            logger.warning(f"Stream already active for camera {camera_id}")
            return True
            
        try:
            self.active_streams[camera_id] = True
            task = asyncio.create_task(self._generate_mock_stream(camera_id, rtsp_url))
            self.stream_tasks[camera_id] = task
            logger.info(f"Started mock stream for camera {camera_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start mock stream for camera {camera_id}: {e}")
            self.active_streams.pop(camera_id, None)
            return False
    
    async def stop_stream(self, camera_id: str) -> bool:
        """Stop generating mock HLS stream for a camera"""
        if camera_id not in self.active_streams:
            logger.warning(f"No active stream for camera {camera_id}")
            return False
            
        try:
            self.active_streams[camera_id] = False
            if camera_id in self.stream_tasks:
                self.stream_tasks[camera_id].cancel()
                del self.stream_tasks[camera_id]
            logger.info(f"Stopped mock stream for camera {camera_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop mock stream for camera {camera_id}: {e}")
            return False
    
    def get_stream_status(self, camera_id: str) -> Dict[str, Any]:
        """Get current stream status"""
        return {
            "camera_id": camera_id,
            "active": camera_id in self.active_streams and self.active_streams[camera_id],
            "start_time": datetime.now().isoformat() if camera_id in self.active_streams else None,
            "segments_generated": self._count_segments(camera_id)
        }
    
    async def _generate_mock_stream(self, camera_id: str, rtsp_url: str):
        """Generate mock HLS stream segments"""
        camera_dir = self.output_dir / camera_id
        camera_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate master playlist
        master_playlist = camera_dir / "index.m3u8"
        await self._write_master_playlist(master_playlist, camera_id)
        
        segment_index = 0
        
        while self.active_streams.get(camera_id, False):
            try:
                # Generate segment
                segment_file = camera_dir / f"segment_{segment_index:06d}.ts"
                await self._generate_segment(segment_file, segment_index)
                
                # Update media playlist
                media_playlist = camera_dir / "playlist.m3u8"
                await self._update_media_playlist(media_playlist, segment_index)
                
                segment_index += 1
                
                # Wait for next segment (4 seconds for 4-second segments)
                await asyncio.sleep(4)
                
            except asyncio.CancelledError:
                logger.info(f"Mock stream generation cancelled for camera {camera_id}")
                break
            except Exception as e:
                logger.error(f"Error generating mock stream for camera {camera_id}: {e}")
                await asyncio.sleep(1)
    
    async def _write_master_playlist(self, playlist_path: Path, camera_id: str):
        """Write master HLS playlist"""
        content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x480
playlist.m3u8
"""
        playlist_path.write_text(content)
        logger.debug(f"Created master playlist for camera {camera_id}")
    
    async def _generate_segment(self, segment_path: Path, index: int):
        """Generate a mock video segment"""
        # Create a small dummy TS file (in real implementation, this would be actual video data)
        dummy_data = b"\x47\x40\x00\x10" * 1024  # Simple TS packet header repeated
        segment_path.write_bytes(dummy_data)
        logger.debug(f"Generated segment {index} at {segment_path}")
    
    async def _update_media_playlist(self, playlist_path: Path, last_segment: int):
        """Update media playlist with latest segments"""
        # Keep last 5 segments in playlist
        start_segment = max(0, last_segment - 4)
        
        segments = []
        for i in range(start_segment, last_segment + 1):
            segments.append(f"#EXTINF:4.0,")
            segments.append(f"segment_{i:06d}.ts")
        
        content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:4
#EXT-X-MEDIA-SEQUENCE:{start_segment}
{chr(10).join(segments)}
"""
        playlist_path.write_text(content)
        logger.debug(f"Updated media playlist with segments {start_segment}-{last_segment}")
    
    def _count_segments(self, camera_id: str) -> int:
        """Count generated segments for a camera"""
        camera_dir = self.output_dir / camera_id
        if not camera_dir.exists():
            return 0
        return len(list(camera_dir.glob("segment_*.ts")))

# Global instance
mock_stream_processor = MockStreamProcessor()