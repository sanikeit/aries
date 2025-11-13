#!/usr/bin/env python3

from uuid import UUID

# Test the camera ID we're using
camera_id_str = "4a167529-8eeb-40ad-94d6-46a7cc963c61"

try:
    camera_id = UUID(camera_id_str)
    print(f"Valid UUID: {camera_id}")
    print(f"UUID version: {camera_id.version}")
    print(f"UUID variant: {camera_id.variant}")
except Exception as e:
    print(f"Invalid UUID: {e}")

# Test with the format used in the database
print(f"\nString format: '{camera_id_str}'")
print(f"UUID format: '{camera_id}'")