#!/usr/bin/env python3
"""Test the mock stream processor"""

import asyncio
import sys
import os
sys.path.append('/Users/sanikeit/Documents/trae_projects/aries/services/api')

from app.services.mock_stream_processor import mock_stream_processor

async def test_mock_stream():
    """Test the mock stream processor"""
    print("Testing mock stream processor...")
    
    # Test starting a stream
    camera_id = "test-camera-123"
    rtsp_url = "rtsp://test:1234@192.168.1.100:554/stream1"
    
    result = await mock_stream_processor.start_stream(camera_id, rtsp_url)
    print(f"Start stream result: {result}")
    
    if result:
        print("Stream started successfully")
        
        # Wait a bit for segments to generate
        await asyncio.sleep(5)
        
        # Check status
        status = mock_stream_processor.get_stream_status(camera_id)
        print(f"Stream status: {status}")
        
        # Check if files were created
        import os
        from pathlib import Path
        
        stream_dir = Path(f"./hls_streams/{camera_id}")
        if stream_dir.exists():
            files = list(stream_dir.glob("*"))
            print(f"Files in stream directory: {[f.name for f in files]}")
        else:
            print("Stream directory not found")
        
        # Stop the stream
        stop_result = await mock_stream_processor.stop_stream(camera_id)
        print(f"Stop stream result: {stop_result}")
    else:
        print("Failed to start stream")

if __name__ == "__main__":
    asyncio.run(test_mock_stream())