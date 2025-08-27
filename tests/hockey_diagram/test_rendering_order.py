#!/usr/bin/env python3
"""
Test script to verify player circles are rendered on top of rink lines.
"""

import requests
import json
import base64

# API endpoint
API_URL = "http://localhost:8001/generate-from-spec"

def test_rendering_order():
    """Test that player circles render on top of rink lines."""
    
    # Test specification with players positioned over face-off dots and circles
    test_spec = {
        "title": "Test: Player Circle Rendering Order",
        "view": "offensive",
        "players": [
            {
                "position": "F1", 
                "zone": "offensive_left",  # On face-off dot
                "team": "home",
                "label": "ON_DOT"
            },
            {
                "position": "F2", 
                "zone": "left_circle",  # On face-off circle line
                "team": "away",
                "label": "ON_CIRCLE"
            },
            {
                "position": "C", 
                "zone": "slot",  # In high traffic area
                "team": "home",
                "label": "SLOT"
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
                with open("test_diagrams/rendering_order_test.png", "wb") as f:
                    f.write(image_data)
                print("✅ Rendering order test diagram generated: test_diagrams/rendering_order_test.png")
                print("   Check that player circles are clearly visible on top of rink lines")
            else:
                print(f"❌ API request failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_rendering_order()