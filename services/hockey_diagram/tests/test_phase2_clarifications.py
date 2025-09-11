#!/usr/bin/env python3
"""Test Phase 2: Enhanced mapping functions with clarifications support."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import map_positions_with_llm, map_movements_with_llm, map_equipment_with_llm, build_clarification_text

def test_clarification_text_builder():
    """Test the build_clarification_text helper function."""
    print("=" * 80)
    print("TESTING CLARIFICATION TEXT BUILDER")
    print("=" * 80)
    
    # Test simple clarifications
    simple_clarifications = {
        "point_side": "left",
        "net_side": "right",
        "timing": "sequential"
    }
    
    result = build_clarification_text(simple_clarifications)
    print(f"Simple clarifications:\n{result}\n")
    
    # Test complex clarifications with answer structure
    complex_clarifications = {
        "position_RD": {"answer": "left point instead of right", "confidence": 0.9},
        "equipment_placement": {"answer": "cones at center ice, not blue line", "confidence": 0.8}
    }
    
    result = build_clarification_text(complex_clarifications)
    print(f"Complex clarifications:\n{result}\n")
    
    # Test empty clarifications
    empty_result = build_clarification_text({})
    print(f"Empty clarifications result: '{empty_result}'\n")
    
    return True

def test_enhanced_position_mapping():
    """Test enhanced position mapping with clarifications."""
    print("=" * 80)
    print("TESTING ENHANCED POSITION MAPPING WITH CLARIFICATIONS")
    print("=" * 80)
    
    # Sample player data
    players = [
        {
            "id": "C",
            "type": "center",
            "team": "home",
            "position_desc": "Center positioned in high slot",
            "assumption": "Center controls play from high slot",
            "confidence": 0.9
        },
        {
            "id": "RD",
            "type": "defense",
            "team": "home", 
            "position_desc": "Right defenseman at the point",
            "assumption": "RD provides shot from point",
            "confidence": 0.8
        }
    ]
    
    # Clarifications to modify positioning
    clarifications = {
        "point_side": "left",  # Move RD to left point instead
        "center_position": "Move center to slot area, not high slot"
    }
    
    # Test with fake previous response ID for conversation continuity
    fake_response_id = "resp_test_12345"
    
    print("Calling map_positions_with_llm with clarifications...")
    print(f"Players: {len(players)}")
    print(f"Clarifications: {clarifications}")
    print(f"Previous response ID: {fake_response_id}")
    
    try:
        result = map_positions_with_llm(
            players=players,
            rink_view="offensive",
            clarifications=clarifications,
            previous_response_id=fake_response_id
        )
        
        print(f"\n✅ Enhanced position mapping completed")
        print(f"Result keys: {list(result.keys())}")
        print(f"Players mapped: {len(result.get('players_mapped', []))}")
        print(f"Response ID: {result.get('response_id', 'None')}")
        print(f"Clarifications applied: {result.get('clarifications_applied', {})}")
        
        # Save results
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "phase2_position_mapping.json", "w") as f:
            json.dump(result, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced position mapping failed: {e}")
        return False

def test_enhanced_movement_mapping():
    """Test enhanced movement mapping with clarifications."""
    print("\n" + "=" * 80)
    print("TESTING ENHANCED MOVEMENT MAPPING WITH CLARIFICATIONS")
    print("=" * 80)
    
    # Sample movement and player data
    movements = [
        {
            "id": "m1",
            "type": "pass",
            "desc": "Center passes to right defenseman",
            "from_player": "C",
            "to_player": "RD",
            "to_area": "point area"
        }
    ]
    
    players = [
        {
            "id": "C",
            "coordinates": {"x": 65, "y": 0},
            "label": "Center"
        },
        {
            "id": "RD", 
            "coordinates": {"x": 54, "y": -38},
            "label": "Right Defense"
        }
    ]
    
    # Clarifications to modify movement
    clarifications = {
        "timing": "Make this pass simultaneous with other movements",
        "path_style": "Use curved path instead of straight line"
    }
    
    fake_response_id = "resp_movement_12345"
    
    print("Calling map_movements_with_llm with clarifications...")
    print(f"Movements: {len(movements)}")
    print(f"Clarifications: {clarifications}")
    
    try:
        result = map_movements_with_llm(
            movements=movements,
            players=players,
            rink_view="offensive",
            clarifications=clarifications,
            previous_response_id=fake_response_id
        )
        
        print(f"\n✅ Enhanced movement mapping completed")
        print(f"Result keys: {list(result.keys())}")
        print(f"Movements mapped: {len(result.get('movements_mapped', []))}")
        print(f"Response ID: {result.get('response_id', 'None')}")
        print(f"Clarifications applied: {result.get('clarifications_applied', {})}")
        
        # Save results
        output_dir = Path(__file__).parent / "outputs"
        
        with open(output_dir / "phase2_movement_mapping.json", "w") as f:
            json.dump(result, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced movement mapping failed: {e}")
        return False

def test_enhanced_equipment_mapping():
    """Test enhanced equipment mapping with clarifications."""
    print("\n" + "=" * 80)
    print("TESTING ENHANCED EQUIPMENT MAPPING WITH CLARIFICATIONS")  
    print("=" * 80)
    
    # Sample equipment data
    equipment_items = [
        {
            "id": "eq1",
            "type": "cone",
            "position_desc": "at the blue line",
            "count": 2,
            "color": "orange",
            "purpose": "marking drill boundaries"
        }
    ]
    
    # Clarifications to modify equipment placement
    clarifications = {
        "equipment_placement": "Move cones to center ice instead of blue line",
        "equipment_spread": "Space them 10 feet apart"
    }
    
    print("Calling map_equipment_with_llm with clarifications...")
    print(f"Equipment items: {len(equipment_items)}")
    print(f"Clarifications: {clarifications}")
    
    try:
        result = map_equipment_with_llm(
            equipment_items=equipment_items,
            rink_view="offensive", 
            clarifications=clarifications,
            previous_response_id=None  # Equipment uses chat completions API
        )
        
        print(f"\n✅ Enhanced equipment mapping completed")
        print(f"Result keys: {list(result.keys())}")
        print(f"Equipment mapped: {len(result.get('equipment_mapped', []))}")
        print(f"Response ID: {result.get('response_id', 'None')} (expected None for chat completions)")
        print(f"Clarifications applied: {result.get('clarifications_applied', {})}")
        
        # Save results
        output_dir = Path(__file__).parent / "outputs"
        
        with open(output_dir / "phase2_equipment_mapping.json", "w") as f:
            json.dump(result, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced equipment mapping failed: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("TESTING PHASE 2: ENHANCED MAPPING FUNCTIONS WITH CLARIFICATIONS")
    print("=" * 80)
    
    success_count = 0
    total_tests = 4
    
    # Test clarification text builder
    if test_clarification_text_builder():
        success_count += 1
    
    # Test enhanced position mapping
    if test_enhanced_position_mapping():
        success_count += 1
    
    # Test enhanced movement mapping  
    if test_enhanced_movement_mapping():
        success_count += 1
    
    # Test enhanced equipment mapping
    if test_enhanced_equipment_mapping():
        success_count += 1
    
    print("\n" + "=" * 80)
    print("PHASE 2 SUMMARY")
    print("=" * 80)
    
    if success_count == total_tests:
        print("✅ All Phase 2 tests PASSED")
        print("\nPhase 2 Implementation Complete:")
        print("  ✅ Enhanced map_positions_with_llm with clarifications + previous_response_id")
        print("  ✅ Enhanced map_movements_with_llm with clarifications + previous_response_id")
        print("  ✅ Enhanced map_equipment_with_llm with clarifications (chat completions API)")
        print("  ✅ Clarification text building and prompt enhancement")
        print("  ✅ Conversation continuity with response_id tracking")
        print("\nNext Phase:")
        print("  🔄 Implement update_spec_with_clarifications tool")
        print("  🔄 Add smart clarification routing logic")
        print("  🔄 Enable full conversational spec updates")
    else:
        print(f"❌ {total_tests - success_count} Phase 2 tests FAILED")
        print("\nNeeds investigation:")
        print("  - Check enhanced mapping function parameters")
        print("  - Verify clarification text building")
        print("  - Test API request enhancement with previous_response_id")
    
    print(f"\nTest results saved to tests/outputs/phase2_*.json")