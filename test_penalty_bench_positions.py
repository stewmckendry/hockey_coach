#!/usr/bin/env python3
"""
Test script to verify penalty box and bench positions are correctly positioned.
"""

import requests
import json
import base64

# API endpoint
API_URL = "http://localhost:8001/generate-from-spec"

def test_penalty_bench_positions():
    """Test that penalty boxes and benches are positioned correctly."""
    
    # Test specification with players in penalty boxes and near benches
    test_spec = {
        "title": "Test: Penalty Box and Bench Positions", 
        "view": "full",
        "players": [
            {
                "position": "F1",
                "zone": "penalty_box_home", 
                "team": "home",
                "label": "PENALTY"
            },
            {
                "position": "X1",
                "zone": "penalty_box_away",
                "team": "away",
                "label": "PENALTY"
            },
            {
                "position": "F2", 
                "zone": "bench_home",
                "team": "home",
                "label": "BENCH"
            },
            {
                "position": "X2",
                "zone": "bench_away",
                "team": "away", 
                "label": "BENCH"
            },
            {
                "position": "C",
                "zone": "center_ice",
                "team": "home",
                "has_puck": True
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
                with open("test_diagrams/penalty_bench_positions_test.png", "wb") as f:
                    f.write(image_data)
                print("✅ Penalty box and bench positions test diagram generated: test_diagrams/penalty_bench_positions_test.png")
                print("   Check that penalty boxes are near center ice on opposite sides")
                print("   Check that benches are positioned along the boards near center ice")
            else:
                print(f"❌ API request failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_penalty_bench_positions()