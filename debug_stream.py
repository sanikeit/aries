#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.insert(0, '/Users/sanikeit/Documents/trae_projects/aries/services/api')

from app.services.mock_stream_processor import mock_stream_processor

async def test_stream_processor():
    """Test the mock stream processor directly"""
    print("Testing mock stream processor...")
    
    # Test camera ID
    camera_id = "test-camera-123"
    rtsp_url = "rtsp://test.example.com/stream"
    
    try:
        # Test start stream
        print(f"Starting stream for camera {camera_id}...")
        success = await mock_stream_processor.start_stream(camera_id, rtsp_url)
        print(f"Start stream result: {success}")
        
        if success:
            # Check status
            status = mock_stream_processor.get_stream_status(camera_id)
            print(f"Stream status: {status}")
            
            # Wait a bit to let it generate some segments
            await asyncio.sleep(5)
            
            # Check if files were created
            import os
            from pathlib import Path
            
            stream_dir = Path("./hls_streams") / camera_id
            if stream_dir.exists():
                files = list(stream_dir.glob("*"))
                print(f"Generated files: {[f.name for f in files]}")
            
            # Stop stream
            print(f"Stopping stream for camera {camera_id}...")
            stop_success = await mock_stream_processor.stop_stream(camera_id)
            print(f"Stop stream result: {stop_success}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_stream_processor())