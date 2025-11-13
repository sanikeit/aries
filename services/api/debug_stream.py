#!/usr/bin/env python3
"""Debug the stream processor issue"""

import asyncio
import sys
import os
sys.path.append('/Users/sanikeit/Documents/trae_projects/aries/services/api')

from uuid import UUID
from app.services.mock_stream_processor import mock_stream_processor

async def debug_stream_processor():
    """Debug the stream processor"""
    print("Debugging stream processor...")
    
    # Test with the actual camera ID from the database
    camera_id = "4a167529-8eeb-40ad-94d6-46a7cc963c61"
    rtsp_url = "rtsp://demo:demo123@192.168.1.100:554/stream1"
    
    try:
        print(f"Testing start_stream with camera_id: {camera_id}")
        result = await mock_stream_processor.start_stream(camera_id, rtsp_url)
        print(f"Start stream result: {result}")
        
        if result:
            print("Stream started successfully")
            
            # Wait a bit
            await asyncio.sleep(2)
            
            # Check status
            status = mock_stream_processor.get_stream_status(camera_id)
            print(f"Stream status: {status}")
            
            # Stop the stream
            stop_result = await mock_stream_processor.stop_stream(camera_id)
            print(f"Stop stream result: {stop_result}")
        else:
            print("Failed to start stream")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_stream_processor())