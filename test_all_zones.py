#!/usr/bin/env python3
"""
Test script to create a diagram showing all 31 available zones with players positioned in each.
"""

import requests
import json
import base64

# API endpoint
API_URL = "http://localhost:8001/generate-from-spec"

def test_all_zones():
    """Test diagram showing players in all 31 available zones."""
    
    # All available zones from coordinate mapper
    zones = [
        "slot", "high_slot", "low_slot", "goal_mouth", "crease", "goal_crease",
        "left_point", "right_point", "center_point", "left_half_wall", "right_half_wall",
        "left_corner", "right_corner", "behind_net", "defensive_slot", "defensive_high_slot",
        "defensive_left_point", "defensive_right_point", "defensive_left_corner", "defensive_right_corner",
        "neutral_center", "neutral_left", "neutral_right", "top_of_circles", "hash_marks",
        "side_boards", "end_boards", "penalty_box_home", "penalty_box_away", "bench_home", "bench_away"
    ]
    
    # Create players for all zones, alternating teams
    players = []
    for i, zone in enumerate(zones):
        team = "home" if i % 2 == 0 else "away"
        position = "C" if team == "home" else "X1"
        
        # Mark center ice player with puck
        has_puck = (zone == "neutral_center")
        
        players.append({
            "position": position,
            "zone": zone,
            "team": team,
            "has_puck": has_puck,
            "label": zone  # Show zone name as label
        })
    
    test_spec = {
        "title": f"Test: All {len(zones)} Zones Validation", 
        "view": "full",
        "players": players
    }
    
    try:
        response = requests.post(API_URL, json={"spec": test_spec}, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success") and "base64_data" in result:
                # Decode and save image
                image_data = base64.b64decode(result["base64_data"])
                with open("test_diagrams/all_zones_validation.png", "wb") as f:
                    f.write(image_data)
                print(f"✅ All zones validation diagram generated: test_diagrams/all_zones_validation.png")
                print(f"   Shows players positioned in all {len(zones)} available zones")
                print("   Each zone is labeled with its name for verification")
                print("   Home team (blue) and away team (red) players alternate")
            else:
                print(f"❌ API request failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_all_zones()