#!/usr/bin/env python3

import requests
import json

# Test different endpoints to debug the issue
base_url = "http://localhost:8000"

endpoints_to_test = [
    "/cameras/4a167529-8eeb-40ad-94d6-46a7cc963c61/start_stream",
    "/cameras/4a167529-8eeb-40ad-94d6-46a7cc963c61/stop_stream", 
    "/cameras/4a167529-8eeb-40ad-94d6-46a7cc963c61/stream_status",
    "/streams/4a167529-8eeb-40ad-94d6-46a7cc963c61/index.m3u8"
]

for endpoint in endpoints_to_test:
    url = base_url + endpoint
    print(f"\n=== Testing {endpoint} ===")
    
    try:
        if "start_stream" in endpoint or "stop_stream" in endpoint:
            response = requests.post(url)
        else:
            response = requests.get(url)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
    except Exception as e:
        print(f"Error: {e}")