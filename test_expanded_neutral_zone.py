#!/usr/bin/env python3
"""
Test script to verify the expanded neutral zone view provides better tactical visibility.
"""

import requests
import json
import base64

# API endpoint
API_URL = "http://localhost:8001/generate-from-spec"

def test_expanded_neutral_zone():
    """Test that neutral zone view is now expanded for better tactical visibility."""
    
    # Test specification with players spread across the neutral zone area
    test_spec = {
        "title": "Test: Expanded Neutral Zone View", 
        "view": "neutral",
        "players": [
            {
                "position": "C",
                "zone": "center_ice", 
                "team": "home",
                "has_puck": True
            },
            {
                "position": "F1",
                "zone": "neutral_left",
                "team": "home"
            },
            {
                "position": "F2", 
                "zone": "neutral_right",
                "team": "home"
            },
            {
                "position": "D1",
                "zone": "defensive_blue_line",
                "team": "home"
            },
            {
                "position": "D2",
                "zone": "offensive_blue_line", 
                "team": "home"
            }
        ],
        "movements": [
            {
                "from_position": "C",
                "to_position": "F1", 
                "movement_type": "pass",
                "label": "BREAKOUT"
            },
            {
                "from_position": "D1",
                "to_position": "D2",
                "movement_type": "skating", 
                "label": "REGROUP"
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
                with open("test_diagrams/expanded_neutral_zone_test.png", "wb") as f:
                    f.write(image_data)
                print("✅ Expanded neutral zone test diagram generated: test_diagrams/expanded_neutral_zone_test.png")
                print("   Check that the view now shows more of the ice surface for better tactical context")
                print("   Should show from approximately the goal lines (xlim: -50 to 50)")
            else:
                print(f"❌ API request failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_expanded_neutral_zone()