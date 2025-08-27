#!/usr/bin/env python3
"""
Test script to verify movement paths avoid going through nets.
"""

import requests
import json
import base64

# API endpoint
API_URL = "http://localhost:8001/generate-from-spec"

def test_net_avoidance():
    """Test that movement paths are adjusted to avoid going through goal nets."""
    
    # Test specification with movements that would go through nets
    test_spec = {
        "title": "Test: Movement Path Net Avoidance", 
        "view": "full",
        "players": [
            {
                "position": "F1",
                "zone": "left_corner", 
                "team": "home"
            },
            {
                "position": "F2",
                "zone": "right_corner",
                "team": "home"
            },
            {
                "position": "D1", 
                "zone": "defensive_left_corner",
                "team": "home"
            },
            {
                "position": "D2",
                "zone": "defensive_right_corner",
                "team": "home"
            },
            {
                "position": "G",
                "zone": "goal_crease",
                "team": "home",
                "has_puck": True
            }
        ],
        "movements": [
            {
                "from_position": "F1",
                "to_position": "F2", 
                "movement_type": "pass",
                "label": "CROSS-ICE"
            },
            {
                "from_position": "D1",
                "to_position": "D2",
                "movement_type": "pass", 
                "label": "BEHIND NET"
            },
            {
                "from_position": "G",
                "to_position": "F1",
                "movement_type": "pass",
                "label": "OUTLET"
            }
        ]
    }
    
    try:
        response = requests.post(API_URL, json={"spec": test_spec}, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success") and "base64_data" in result:
                # Decode and save image
                image_data = base64.b64decode(result["base64_data"])
                with open("test_diagrams/net_avoidance_test.png", "wb") as f:
                    f.write(image_data)
                print("✅ Net avoidance test diagram generated: test_diagrams/net_avoidance_test.png")
                print("   Check that movement paths curve around goal nets instead of going through them")
                print("   Cross-ice passes should avoid both nets appropriately")
            else:
                print(f"❌ API request failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_net_avoidance()