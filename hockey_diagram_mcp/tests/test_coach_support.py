#!/usr/bin/env python3
"""Test coach support in MCP v3 tools."""

import json
import sys
import os

# Add the servers directory to path (go up one level from tests/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'servers'))

def test_coach_in_analysis():
    """Test that analyze_hockey_query can handle coaches in drill descriptions."""
    
    # Mock analysis result with coaches
    mock_analysis = {
        "original_query": "3v3 drill with coach at center ice observing",
        "components_with_assumptions": {
            "rink": {"view": "offensive", "confidence": 0.9},
            "players": [
                {"id": "F1", "type": "forward", "team": "home", "position_desc": "right circle", "confidence": 0.8},
                {"id": "F2", "type": "forward", "team": "home", "position_desc": "left circle", "confidence": 0.8},
                {"id": "F3", "type": "forward", "team": "home", "position_desc": "slot", "confidence": 0.8}
            ],
            "movements": [],
            "coaches": [
                {
                    "id": "COACH1",
                    "position_desc": "at center ice",
                    "role": "observer", 
                    "assumption": "Coach positioned to observe entire drill",
                    "confidence": 0.9
                }
            ],
            "equipment": [],
            "annotations": []
        },
        "metadata": {"type": "drill", "phase": "practice"}
    }
    
    print("🧪 Testing coach support in MCP v3 tools...")
    print("=" * 60)
    
    # Test the translation function
    try:
        from hockey_diagram_mcp_v3 import translate_analysis_to_spec, map_coach_position
        
        print("✅ Successfully imported MCP v3 functions")
        
        # Test coach position mapping
        print("\n🎯 Testing coach position mapping:")
        test_positions = [
            "at center ice",
            "behind goal line", 
            "on bench",
            "offensive corner",
            "boards"
        ]
        
        for pos in test_positions:
            coords = map_coach_position(pos, "offensive")
            print(f"   '{pos}' -> {coords}")
        
        # Test translation with coaches
        print(f"\n📐 Testing translation with coaches...")
        result = translate_analysis_to_spec(mock_analysis)
        
        if result.get("success"):
            spec = result.get("spec", {})
            players = spec.get("players", [])
            
            # Count coaches in spec
            coaches = [p for p in players if p.get("type") == "coach"]
            regular_players = [p for p in players if p.get("type") != "coach"]
            
            print(f"✅ Translation successful!")
            print(f"   Regular players: {len(regular_players)}")
            print(f"   Coaches: {len(coaches)}")
            
            if coaches:
                coach = coaches[0]
                print(f"   Coach details:")
                print(f"     ID: {coach.get('id')}")
                print(f"     Position: {coach.get('coordinates')}")
                print(f"     Label: {coach.get('label')}")
                print(f"     Role: {coach.get('_role')}")
                
            # Save result for inspection
            with open("test_coach_spec_output.json", "w") as f:
                json.dump(spec, f, indent=2)
            print(f"\n💾 Saved test spec to test_coach_spec_output.json")
            
            return True
        else:
            print(f"❌ Translation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the hockey_diagram_mcp directory")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_coach_position_mapping():
    """Test coach position mapping function standalone."""
    
    print("\n🎯 Testing coach position mapping function...")
    
    test_cases = [
        # (description, zone, expected_area)
        ("at center ice", "offensive", "center"),
        ("behind goal line", "offensive", "behind_goal"),
        ("on bench", "full", "bench"),
        ("offensive corner", "offensive", "corner"),
        ("right boards", "neutral", "right_boards"),
        ("", "offensive", "default")  # Test default case
    ]
    
    try:
        from hockey_diagram_mcp_v3 import map_coach_position
        
        for desc, zone, expected in test_cases:
            coords = map_coach_position(desc, zone)
            print(f"   '{desc}' in {zone} zone -> {coords}")
            
            # Basic validation
            assert isinstance(coords, dict), f"Should return dict, got {type(coords)}"
            assert "x" in coords and "y" in coords, f"Missing x/y coordinates"
            assert isinstance(coords["x"], (int, float)), f"x should be numeric"
            assert isinstance(coords["y"], (int, float)), f"y should be numeric"
        
        print("✅ All coach position mapping tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Coach position mapping test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏒 TESTING COACH SUPPORT IN MCP V3 TOOLS")
    print("=" * 60)
    
    success1 = test_coach_position_mapping()
    success2 = test_coach_in_analysis()
    
    if success1 and success2:
        print(f"\n🎉 ALL COACH TESTS PASSED!")
        print("   Coach support successfully added to MCP v3 pipeline")
    else:
        print(f"\n❌ SOME TESTS FAILED!")
        print("   Check implementation and try again")
    
    print("\n" + "=" * 60)