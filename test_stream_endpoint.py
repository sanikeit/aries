#!/usr/bin/env python3

import requests
import json

# Test the stream start endpoint
url = "http://localhost:8000/cameras/4a167529-8eeb-40ad-94d6-46a7cc963c61/start_stream"

try:
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 500:
        print(f"\nFull Response: {response.__dict__}")
        
except Exception as e:
    print(f"Request failed: {e}")