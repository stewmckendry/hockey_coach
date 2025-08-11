#!/usr/bin/env python3
"""
Comprehensive test of all Hockey Diagram Spec Model entities
Tests all zones, players, movements, and views from SPEC_MODEL.md
"""

import json
import base64
import requests
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

API_URL = "http://localhost:8001/api/mcp"

def call_hockey_diagram_tool(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Call the generate_diagram_from_spec tool via API"""
    try:
        response = requests.post(
            API_URL,
            json={
                "tool": "generate_diagram_from_spec",
                "parameters": {"spec": spec}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result["data"]
        return {"error": f"API error: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def save_diagram(base64_data: str, filename: str):
    """Save base64 diagram to file"""
    try:
        # Remove data URL prefix if present
        if "base64," in base64_data:
            base64_data = base64_data.split("base64,")[1]
        
        # Decode and save
        image_data = base64.b64decode(base64_data)
        output_path = Path(f"test_diagrams/{filename}.png")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(image_data)
        
        return str(output_path)
    except Exception as e:
        return f"Error saving: {e}"

def test_offensive_zones():
    """Test all offensive zone positions"""
    spec = {
        "title": "Test: All Offensive Zones",
        "view": "offensive",
        "players": [
            {"position": "F1", "zone": "slot", "team": "home", "label": "slot"},
            {"position": "F2", "zone": "high_slot", "team": "home", "label": "high_slot"},
            {"position": "F3", "zone": "low_slot", "team": "home", "label": "low_slot"},
            {"position": "C", "zone": "point", "team": "home", "label": "point"},
            {"position": "LW", "zone": "left_point", "team": "home", "label": "left_point"},
            {"position": "RW", "zone": "right_point", "team": "home", "label": "right_point"},
            {"position": "D1", "zone": "left_circle", "team": "away", "label": "left_circle"},
            {"position": "D2", "zone": "right_circle", "team": "away", "label": "right_circle"},
            {"position": "LD", "zone": "behind_net", "team": "away", "label": "behind_net"},
            {"position": "RD", "zone": "left_corner", "team": "away", "label": "left_corner"},
            {"position": "X1", "zone": "right_corner", "team": "away", "label": "right_corner"},
            {"position": "X2", "zone": "goal_line", "team": "away", "label": "goal_line"},
            {"position": "X3", "zone": "offensive_left", "team": "away", "label": "offensive_left"},
            {"position": "X4", "zone": "offensive_right", "team": "away", "label": "offensive_right"},
            {"position": "X5", "zone": "offensive_slot", "team": "away", "label": "offensive_slot"}
        ],
        "movements": []
    }
    
    result = call_hockey_diagram_tool(spec)
    return {
        "test": "offensive_zones",
        "spec": spec,
        "result": result,
        "saved_to": save_diagram(result.get("diagram", ""), "01_offensive_zones") if "diagram" in result else None
    }

def test_neutral_zones():
    """Test all neutral zone positions"""
    spec = {
        "title": "Test: All Neutral Zones",
        "view": "full",
        "players": [
            {"position": "F1", "zone": "neutral_left", "team": "home", "label": "neutral_left"},
            {"position": "F2", "zone": "neutral_center", "team": "home", "label": "neutral_center"},
            {"position": "F3", "zone": "neutral_right", "team": "home", "label": "neutral_right"},
            {"position": "C", "zone": "center_ice", "team": "home", "label": "center_ice"}
        ],
        "movements": []
    }
    
    result = call_hockey_diagram_tool(spec)
    return {
        "test": "neutral_zones",
        "spec": spec,
        "result": result,
        "saved_to": save_diagram(result.get("diagram", ""), "02_neutral_zones") if "diagram" in result else None
    }

def test_defensive_zones():
    """Test all defensive zone positions"""
    spec = {
        "title": "Test: All Defensive Zones",
        "view": "defensive",
        "players": [
            {"position": "D1", "zone": "defensive_left", "team": "home", "label": "defensive_left"},
            {"position": "D2", "zone": "defensive_right", "team": "home", "label": "defensive_right"},
            {"position": "F1", "zone": "defensive_slot", "team": "home", "label": "defensive_slot"},
            {"position": "F2", "zone": "defensive_point", "team": "home", "label": "defensive_point"},
            {"position": "F3", "zone": "defensive_left_circle", "team": "away", "label": "def_left_circle"},
            {"position": "C", "zone": "defensive_right_circle", "team": "away", "label": "def_right_circle"},
            {"position": "LW", "zone": "defensive_goal_line", "team": "away", "label": "def_goal_line"},
            {"position": "RW", "zone": "defensive_behind_net", "team": "away", "label": "def_behind_net"},
            {"position": "LD", "zone": "defensive_left_corner", "team": "away", "label": "def_left_corner"},
            {"position": "RD", "zone": "defensive_right_corner", "team": "away", "label": "def_right_corner"}
        ],
        "movements": []
    }
    
    result = call_hockey_diagram_tool(spec)
    return {
        "test": "defensive_zones",
        "spec": spec,
        "result": result,
        "saved_to": save_diagram(result.get("diagram", ""), "03_defensive_zones") if "diagram" in result else None
    }

def test_all_player_roles():
    """Test all player role types"""
    spec = {
        "title": "Test: All Player Roles",
        "view": "full",
        "players": [
            # Forwards
            {"position": "F1", "zone": "offensive_slot", "team": "home", "label": "F1"},
            {"position": "F2", "zone": "offensive_left", "team": "home", "label": "F2"},
            {"position": "F3", "zone": "offensive_right", "team": "home", "label": "F3"},
            {"position": "F4", "zone": "neutral_left", "team": "home", "label": "F4"},
            {"position": "F5", "zone": "neutral_right", "team": "home", "label": "F5"},
            {"position": "C", "zone": "center_ice", "team": "home", "label": "C"},
            {"position": "LW", "zone": "left_point", "team": "home", "label": "LW"},
            {"position": "RW", "zone": "right_point", "team": "home", "label": "RW"},
            
            # Defense
            {"position": "D1", "zone": "defensive_left", "team": "away", "label": "D1"},
            {"position": "D2", "zone": "defensive_right", "team": "away", "label": "D2"},
            {"position": "D3", "zone": "defensive_slot", "team": "away", "label": "D3"},
            {"position": "D4", "zone": "defensive_point", "team": "away", "label": "D4"},
            {"position": "LD", "zone": "defensive_left_circle", "team": "away", "label": "LD"},
            {"position": "RD", "zone": "defensive_right_circle", "team": "away", "label": "RD"},
            
            # Goalie
            {"position": "G", "zone": "defensive_behind_net", "team": "away", "label": "G"},
            
            # Generic players
            {"position": "X1", "zone": "neutral_center", "team": "away", "label": "X1"},
            {"position": "P1", "zone": "point", "team": "home", "label": "P1"}
        ],
        "movements": []
    }
    
    result = call_hockey_diagram_tool(spec)
    return {
        "test": "all_player_roles",
        "spec": spec,
        "result": result,
        "saved_to": save_diagram(result.get("diagram", ""), "04_all_player_roles") if "diagram" in result else None
    }

def test_all_movement_types():
    """Test all movement types"""
    spec = {
        "title": "Test: All Movement Types",
        "view": "full",
        "players": [
            {"position": "F1", "zone": "offensive_slot", "team": "home", "has_puck": True},
            {"position": "F2", "zone": "left_point", "team": "home"},
            {"position": "F3", "zone": "right_point", "team": "home"},
            {"position": "D1", "zone": "defensive_left", "team": "home"},
            {"position": "D2", "zone": "defensive_right", "team": "home"},
            {"position": "C", "zone": "center_ice", "team": "home"}
        ],
        "movements": [
            {"from_position": "F1", "to_position": "F2", "movement_type": "pass", "label": "pass"},
            {"from_position": "F2", "to_position": "F3", "movement_type": "shot", "label": "shot"},
            {"from_position": "F3", "to_position": "D1", "movement_type": "carry", "label": "carry"},
            {"from_position": "D1", "to_position": "D2", "movement_type": "skating", "label": "skating"},
            {"from_position": "D2", "to_position": "C", "movement_type": "lateral", "label": "lateral"},
            {"from_position": "C", "to_position": "F1", "movement_type": "support", "label": "support"}
        ]
    }
    
    result = call_hockey_diagram_tool(spec)
    return {
        "test": "all_movement_types",
        "spec": spec,
        "result": result,
        "saved_to": save_diagram(result.get("diagram", ""), "05_all_movement_types") if "diagram" in result else None
    }

def test_different_views():
    """Test all view types"""
    views = ["full", "offensive", "defensive", "neutral"]
    results = []
    
    for view in views:
        spec = {
            "title": f"Test: {view.capitalize()} View",
            "view": view,
            "players": [
                {"position": "F1", "zone": "offensive_slot" if view in ["offensive", "full"] else "center_ice", "team": "home"},
                {"position": "D1", "zone": "defensive_left" if view in ["defensive", "full"] else "neutral_left", "team": "home"},
                {"position": "C", "zone": "center_ice" if view in ["neutral", "full"] else "slot", "team": "home"}
            ],
            "movements": []
        }
        
        result = call_hockey_diagram_tool(spec)
        saved_to = save_diagram(result.get("diagram", ""), f"06_view_{view}") if "diagram" in result else None
        
        results.append({
            "view": view,
            "spec": spec,
            "result": result,
            "saved_to": saved_to
        })
    
    return {
        "test": "different_views",
        "results": results
    }

def test_team_designations():
    """Test home vs away team colors"""
    spec = {
        "title": "Test: Team Designations (Home vs Away)",
        "view": "full",
        "players": [
            # Home team (should be one color)
            {"position": "F1", "zone": "offensive_slot", "team": "home", "label": "Home F1"},
            {"position": "F2", "zone": "offensive_left", "team": "home", "label": "Home F2"},
            {"position": "F3", "zone": "offensive_right", "team": "home", "label": "Home F3"},
            {"position": "D1", "zone": "defensive_left", "team": "home", "label": "Home D1"},
            {"position": "D2", "zone": "defensive_right", "team": "home", "label": "Home D2"},
            
            # Away team (should be different color)
            {"position": "X1", "zone": "neutral_center", "team": "away", "label": "Away X1"},
            {"position": "X2", "zone": "neutral_left", "team": "away", "label": "Away X2"},
            {"position": "X3", "zone": "neutral_right", "team": "away", "label": "Away X3"},
            {"position": "X4", "zone": "point", "team": "away", "label": "Away X4"},
            {"position": "X5", "zone": "center_ice", "team": "away", "label": "Away X5"}
        ],
        "movements": [
            {"from_position": "F1", "to_position": "F2", "movement_type": "pass", "label": "Home pass"},
            {"from_position": "X1", "to_position": "X2", "movement_type": "pass", "label": "Away pass"}
        ]
    }
    
    result = call_hockey_diagram_tool(spec)
    return {
        "test": "team_designations",
        "spec": spec,
        "result": result,
        "saved_to": save_diagram(result.get("diagram", ""), "07_team_designations") if "diagram" in result else None
    }

def test_special_zones():
    """Test special zones like bench and penalty box"""
    spec = {
        "title": "Test: Special Zones (Bench & Penalty Box)",
        "view": "full",
        "players": [
            {"position": "P1", "zone": "bench", "team": "home", "label": "Bench"},
            {"position": "P2", "zone": "penalty_box", "team": "away", "label": "Penalty Box"},
            {"position": "F1", "zone": "center_ice", "team": "home", "label": "On Ice"}
        ],
        "movements": []
    }
    
    result = call_hockey_diagram_tool(spec)
    return {
        "test": "special_zones",
        "spec": spec,
        "result": result,
        "saved_to": save_diagram(result.get("diagram", ""), "08_special_zones") if "diagram" in result else None
    }

def test_complex_formation():
    """Test a complex real-world formation"""
    spec = {
        "title": "Test: 2-1-2 Forecheck with Movements",
        "view": "full",
        "players": [
            {"position": "F1", "zone": "offensive_slot", "team": "home", "has_puck": False, "label": "F1 Press"},
            {"position": "F2", "zone": "offensive_left", "team": "home", "label": "F2 Support"},
            {"position": "F3", "zone": "offensive_right", "team": "home", "label": "F3 Support"},
            {"position": "D1", "zone": "neutral_left", "team": "home", "label": "D1 High"},
            {"position": "D2", "zone": "neutral_right", "team": "home", "label": "D2 High"},
            
            {"position": "X1", "zone": "behind_net", "team": "away", "has_puck": True, "label": "Puck Carrier"},
            {"position": "X2", "zone": "defensive_left", "team": "away", "label": "X2"},
            {"position": "X3", "zone": "defensive_right", "team": "away", "label": "X3"},
            {"position": "X4", "zone": "defensive_left_circle", "team": "away", "label": "X4"},
            {"position": "X5", "zone": "defensive_right_circle", "team": "away", "label": "X5"}
        ],
        "movements": [
            {"from_position": "F1", "to_position": "X1", "movement_type": "skating", "label": "Pressure"},
            {"from_position": "F2", "to_position": "X2", "movement_type": "support", "label": "Cut passing lane"},
            {"from_position": "F3", "to_position": "X3", "movement_type": "support", "label": "Cut passing lane"},
            {"from_position": "X1", "to_position": "X4", "movement_type": "pass", "label": "Breakout pass"}
        ]
    }
    
    result = call_hockey_diagram_tool(spec)
    return {
        "test": "complex_formation",
        "spec": spec,
        "result": result,
        "saved_to": save_diagram(result.get("diagram", ""), "09_complex_formation") if "diagram" in result else None
    }

def test_coverage_zones():
    """Test coverage zone overlays"""
    spec = {
        "title": "Test: Coverage Zones",
        "view": "defensive",
        "players": [
            {"position": "D1", "zone": "defensive_left", "team": "home", "label": "D1"},
            {"position": "D2", "zone": "defensive_right", "team": "home", "label": "D2"},
            {"position": "F1", "zone": "defensive_slot", "team": "home", "label": "F1"}
        ],
        "movements": [],
        "zones": [
            {"zone_type": "coverage", "area": "defensive_left", "team": "home", "opacity": 0.2},
            {"zone_type": "coverage", "area": "defensive_right", "team": "home", "opacity": 0.2},
            {"zone_type": "pressure", "area": "defensive_slot", "team": "home", "opacity": 0.3}
        ]
    }
    
    result = call_hockey_diagram_tool(spec)
    return {
        "test": "coverage_zones",
        "spec": spec,
        "result": result,
        "saved_to": save_diagram(result.get("diagram", ""), "10_coverage_zones") if "diagram" in result else None
    }

def main():
    """Run all tests and generate comprehensive report"""
    print("=" * 80)
    print("HOCKEY DIAGRAM SPEC MODEL VALIDATION TEST")
    print("=" * 80)
    print(f"Testing started at: {datetime.now().isoformat()}")
    print(f"API Endpoint: {API_URL}")
    print("=" * 80)
    
    # Create output directory
    Path("test_diagrams").mkdir(exist_ok=True)
    
    # Run all tests
    all_results = []
    
    tests = [
        ("Offensive Zones", test_offensive_zones),
        ("Neutral Zones", test_neutral_zones),
        ("Defensive Zones", test_defensive_zones),
        ("Player Roles", test_all_player_roles),
        ("Movement Types", test_all_movement_types),
        ("View Types", test_different_views),
        ("Team Designations", test_team_designations),
        ("Special Zones", test_special_zones),
        ("Complex Formation", test_complex_formation),
        ("Coverage Zones", test_coverage_zones)
    ]
    
    for test_name, test_func in tests:
        print(f"\nRunning test: {test_name}...")
        try:
            result = test_func()
            all_results.append(result)
            
            # Check for success
            if isinstance(result, dict):
                if "error" in result.get("result", {}):
                    print(f"  ❌ ERROR: {result['result']['error']}")
                elif "saved_to" in result and result["saved_to"]:
                    print(f"  ✅ SUCCESS: Diagram saved to {result['saved_to']}")
                else:
                    print(f"  ⚠️  Result: {result}")
            
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            all_results.append({
                "test": test_name,
                "error": str(e)
            })
    
    # Save complete results to JSON
    output_file = "test_results.json"
    with open(output_file, "w") as f:
        # Convert results to JSON-serializable format
        clean_results = []
        for result in all_results:
            if isinstance(result, dict):
                # Remove base64 diagram data from saved results (too large)
                clean_result = result.copy()
                if "result" in clean_result and "diagram" in clean_result.get("result", {}):
                    clean_result["result"]["diagram"] = "<base64_data_removed>"
                clean_results.append(clean_result)
        
        json.dump(clean_results, f, indent=2)
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests run: {len(all_results)}")
    print(f"Results saved to: {output_file}")
    print(f"Diagrams saved to: test_diagrams/")
    print(f"Testing completed at: {datetime.now().isoformat()}")
    print("=" * 80)

if __name__ == "__main__":
    main()