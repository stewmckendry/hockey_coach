#!/usr/bin/env python3
"""
Test script to create diagrams for all preset formations.
"""

import requests
import json
import base64
import os

# API endpoint
API_URL = "http://localhost:8001/generate-from-spec"

# List of all preset formations from elements.py
PRESET_FORMATIONS = [
    "2-1-2_forecheck",
    "1-2-2_forecheck", 
    "1-3-1_powerplay",
    "box_penalty_kill",
    "neutral_zone_trap",
    "breakout_strong_side",
    "cycle_offensive_zone",
    "diamond_penalty_kill",
    "defensive_zone_coverage",
    "overload_powerplay"
]

def test_formation(formation_name):
    """Test a specific preset formation."""
    
    # Import formations from elements.py
    import sys
    sys.path.append('servers/hockey_diagram_mcp')
    from elements import FORMATIONS
    
    if formation_name not in FORMATIONS:
        print(f"⚠️  Formation '{formation_name}' not found in FORMATIONS")
        return False
        
    formation = FORMATIONS[formation_name]
    
    test_spec = {
        "title": f"Formation: {formation_name.replace('_', ' ').title()}",
        "description": formation.get("description", ""),
        "view": "full",
        "players": formation.get("players", []),
        "movements": formation.get("movements", []),
        "zones": formation.get("zones", [])
    }
    
    try:
        response = requests.post(API_URL, json={"spec": test_spec}, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success") and "base64_data" in result:
                # Decode and save image
                image_data = base64.b64decode(result["base64_data"])
                filename = f"test_diagrams/formation_{formation_name}.png"
                with open(filename, "wb") as f:
                    f.write(image_data)
                print(f"✅ Generated: {filename}")
                return True
            else:
                print(f"❌ API request failed for {formation_name}: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error {response.status_code} for {formation_name}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error for {formation_name}: {e}")
        return False

def main():
    """Generate diagrams for all preset formations."""
    
    # Ensure test_diagrams directory exists
    os.makedirs("test_diagrams", exist_ok=True)
    
    print("Generating diagrams for all preset formations...")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for formation in PRESET_FORMATIONS:
        if test_formation(formation):
            successful += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Results: {successful} successful, {failed} failed")
    
    if successful == len(PRESET_FORMATIONS):
        print("✅ All preset formations generated successfully!")
    else:
        print(f"⚠️  Some formations failed to generate")

if __name__ == "__main__":
    main()