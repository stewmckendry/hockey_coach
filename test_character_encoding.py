#!/usr/bin/env python3
"""
Test script to verify character encoding is fixed for X players.
"""

import requests
import json
import base64

# API endpoint
API_URL = "http://localhost:8001/generate-from-spec"

def test_character_encoding():
    """Test that X players now display correctly without encoding issues."""
    
    # Test specification with all X player positions
    test_spec = {
        "title": "Test: Character Encoding Fix", 
        "view": "offensive",
        "players": [
            {
                "position": "X1",
                "zone": "slot", 
                "team": "away",
                "has_puck": True
            },
            {
                "position": "X2",
                "zone": "left_point",
                "team": "away"
            },
            {
                "position": "X3", 
                "zone": "right_point",
                "team": "away"
            },
            {
                "position": "X4",
                "zone": "left_corner",
                "team": "away"
            },
            {
                "position": "X5",
                "zone": "right_corner", 
                "team": "away"
            },
            {
                "position": "XG",
                "zone": "goal_crease",
                "team": "away"
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
                with open("test_diagrams/character_encoding_test.png", "wb") as f:
                    f.write(image_data)
                print("✅ Character encoding test diagram generated: test_diagrams/character_encoding_test.png")
                print("   Check that all X players display as X1, X2, X3, X4, X5, XG (not X� symbols)")
            else:
                print(f"❌ API request failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_character_encoding()