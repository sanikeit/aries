#!/usr/bin/env python3

import sys
import base64
import json

# JWT token from the request
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vIiwiZXhwIjoxNzYyOTg4MzQxfQ.uDQqRKornm7cDDF4UqSF42wX-eq6ui1xxbjT51Xg0qw"

def decode_jwt(token):
    """Decode JWT token without verification"""
    try:
        # Split the token
        parts = token.split('.')
        if len(parts) != 3:
            print("Invalid JWT format")
            return None
        
        # Decode header
        header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
        print(f"Header: {header}")
        
        # Decode payload
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
        print(f"Payload: {payload}")
        
        # Check expiration
        if 'exp' in payload:
            import datetime
            exp_time = datetime.datetime.fromtimestamp(payload['exp'])
            current_time = datetime.datetime.now()
            print(f"Expiration time: {exp_time}")
            print(f"Current time: {current_time}")
            print(f"Token expired: {current_time > exp_time}")
        
        return payload
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None

if __name__ == "__main__":
    print("Decoding JWT token...")
    decode_jwt(token)