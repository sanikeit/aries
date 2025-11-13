# Test script for video streaming functionality
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

# Test credentials
test_credentials = {
    "username": "demo",
    "password": "demo123"
}

def test_auth():
    """Test authentication"""
    print("Testing authentication...")
    response = requests.post(f"{BASE_URL}/auth/token", data=test_credentials)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✓ Authentication successful, token: {token[:20]}...")
        return token
    else:
        print(f"✗ Authentication failed: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"URL: {response.url}")
        return None

def test_get_cameras(token):
    """Test getting cameras"""
    print("\nTesting get cameras...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cameras/", headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response text: {response.text[:500]}")
    if response.status_code == 200:
        cameras = response.json()
        print(f"✓ Found {len(cameras)} cameras")
        for camera in cameras:
            print(f"  - Camera {camera['id']}: {camera['name']} ({camera['status']})")
        return cameras
    else:
        print(f"✗ Failed to get cameras: {response.status_code}")
        print(response.text)
        return []

def test_stream_status(token, camera_id):
    """Test stream status endpoint"""
    print(f"\nTesting stream status for camera {camera_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cameras/{camera_id}/stream_status", headers=headers)
    if response.status_code == 200:
        status = response.json()
        print(f"✓ Stream status retrieved")
        print(f"  - Stream active: {status['stream_active']}")
        print(f"  - Stream URL: {status['stream_url']}")
        print(f"  - Camera active: {status['camera_active']}")
        return status
    else:
        print(f"✗ Failed to get stream status: {response.status_code}")
        print(response.text)
        return None

def test_start_stream(token, camera_id):
    """Test starting a stream"""
    print(f"\nTesting start stream for camera {camera_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/cameras/{camera_id}/start_stream", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Stream started successfully")
        print(f"  - Message: {result['message']}")
        print(f"  - Stream URL: {result['stream_url']}")
        return result
    else:
        print(f"✗ Failed to start stream: {response.status_code}")
        print(response.text)
        return None

def test_stream_segments(token, camera_id):
    """Test HLS stream segments"""
    print(f"\nTesting HLS stream segments for camera {camera_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test playlist
    playlist_url = f"http://localhost:8000/api/streams/{camera_id}/index.m3u8"
    response = requests.get(playlist_url, headers=headers)
    if response.status_code == 200:
        print(f"✓ HLS playlist accessible")
        print(f"  - Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"  - Content length: {len(response.content)} bytes")
        # Show first few lines of playlist
        lines = response.text.split('\n')[:10]
        print(f"  - Playlist preview: {lines}")
    else:
        print(f"✗ HLS playlist not accessible: {response.status_code}")
        print(response.text)

def main():
    """Main test function"""
    print("=== Aries Edge Video Streaming Test ===\n")
    
    # Test authentication
    token = test_auth()
    if not token:
        return
    
    # Test getting cameras
    cameras = test_get_cameras(token)
    if not cameras:
        print("No cameras found. Please add cameras first.")
        return
    
    # Test with first camera
    test_camera = cameras[0]
    camera_id = test_camera['id']
    
    # Test stream status
    test_stream_status(token, camera_id)
    
    # Test start stream
    test_start_stream(token, camera_id)
    
    # Wait a moment for stream to initialize
    import time
    time.sleep(2)
    
    # Test stream status again
    test_stream_status(token, camera_id)
    
    # Test HLS segments
    test_stream_segments(token, camera_id)
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    main()