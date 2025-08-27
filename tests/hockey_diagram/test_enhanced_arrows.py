#!/usr/bin/env python3
"""
Test script to verify enhanced directional arrows on movement lines.
"""

import requests
import json
import base64

# API endpoint
API_URL = "http://localhost:8001/generate-from-spec"

def test_enhanced_arrows():
    """Test that movement arrows are now clearly visible with proper direction."""
    
    # Test specification with various movement types
    test_spec = {
        "title": "Test: Enhanced Movement Arrows", 
        "view": "full",
        "players": [
            {
                "position": "F1",
                "zone": "slot", 
                "team": "home",
                "has_puck": True
            },
            {
                "position": "F2",
                "zone": "high_slot",
                "team": "home"
            },
            {
                "position": "F3", 
                "zone": "left_point",
                "team": "home"
            },
            {
                "position": "X1",
                "zone": "right_corner",
                "team": "away"
            }
        ],
        "movements": [
            {
                "from_position": "F1",
                "to_position": "F2", 
                "movement_type": "pass",
                "label": "PASS"
            },
            {
                "from_position": "F2",
                "to_position": "F3",
                "movement_type": "skating", 
                "label": "SKATE"
            },
            {
                "from_position": "F3",
                "to_position": "X1",
                "movement_type": "shot",
                "label": "SHOT"
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
                with open("test_diagrams/enhanced_arrows_test.png", "wb") as f:
                    f.write(image_data)
                print("✅ Enhanced arrows test diagram generated: test_diagrams/enhanced_arrows_test.png")
                print("   Check that arrows are clearly visible with proper directional heads")
            else:
                print(f"❌ API request failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_enhanced_arrows()