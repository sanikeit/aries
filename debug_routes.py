#!/usr/bin/env python3

# Import the app and check registered routes
import sys
sys.path.append('/Users/sanikeit/Documents/trae_projects/aries/services/api')

from app.main import app

print("=== REGISTERED ROUTES ===")
for route in app.routes:
    try:
        if hasattr(route, 'methods'):
            print(f"Path: {route.path}, Methods: {route.methods}, Name: {route.name}")
        else:
            print(f"Path: {route.path}, Type: {type(route).__name__}, Name: {route.name}")
    except Exception as e:
        print(f"Error with route: {e}")
    
print("\n=== LOOKING FOR CAMERA ROUTES ===")
camera_routes = [r for r in app.routes if hasattr(r, 'path') and ('camera' in r.path or 'start_stream' in r.path)]
for route in camera_routes:
    if hasattr(route, 'methods'):
        print(f"Path: {route.path}, Methods: {route.methods}")
    else:
        print(f"Path: {route.path}, Type: {type(route).__name__}")