#!/usr/bin/env python3
"""
Test script to verify left/right orientation fix.
"""

import requests
import json
import base64

# API endpoint
API_URL = "http://localhost:8001/generate-from-spec"

def test_orientation_fix():
    """Test that left/right orientations are now correct."""
    
    # Test specification with left/right positions
    test_spec = {
        "title": "Test: Left/Right Orientation Fix",
        "view": "offensive",
        "players": [
            {
                "position": "X3", 
                "zone": "offensive_left",
                "team": "away",
                "label": "LEFT"
            },
            {
                "position": "X4", 
                "zone": "offensive_right", 
                "team": "away",
                "label": "RIGHT"
            },
            {
                "position": "LW", 
                "zone": "left_point",
                "team": "home", 
                "label": "LEFT_POINT"
            },
            {
                "position": "RW",
                "zone": "right_point", 
                "team": "home",
                "label": "RIGHT_POINT"
            }
        ]
    }
    
    try:
        response = requests.post(API_URL, json={"spec": test_spec}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success") and "base64_data" in result:
                # Decode and save image
                image_data = base64.b64decode(result["base64_data"])
                with open("test_diagrams/orientation_fix_test.png", "wb") as f:
                    f.write(image_data)
                print("✅ Orientation fix test diagram generated: test_diagrams/orientation_fix_test.png")
                print("   Check that LEFT players are on the left side and RIGHT players are on the right side")
            else:
                print(f"❌ API request failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("   Make sure the hockey diagram server is running on port 8001")

if __name__ == "__main__":
    test_orientation_fix()