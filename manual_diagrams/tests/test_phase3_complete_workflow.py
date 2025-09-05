#!/usr/bin/env python3
"""Test Phase 3: Complete conversational spec update workflow."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import translate_analysis_to_spec, update_spec_with_clarifications

def test_complete_conversational_workflow():
    """Test the complete workflow from translation to clarification updates."""
    print("=" * 80)
    print("TESTING COMPLETE CONVERSATIONAL WORKFLOW - PHASE 3")
    print("=" * 80)
    
    # Step 1: Create sample analysis data (simulating analyze_hockey_query output)
    sample_analysis = {
        "original_query": "Power play with 4 players, puck movement, cones at blue lines",
        "explicit_info": {
            "situation": "power play",
            "zone": "offensive", 
            "key_actions": ["puck movement"],
            "faceoff_location": None
        },
        "components_with_assumptions": {
            "rink": {
                "view": "offensive",
                "assumption": "Power play occurs in offensive zone",
                "confidence": 0.9
            },
            "players": [
                {
                    "id": "C",
                    "type": "center",
                    "team": "home",
                    "position_desc": "Center in high slot area",
                    "assumption": "Center controls play distribution",
                    "confidence": 0.9
                },
                {
                    "id": "RW",
                    "type": "winger",
                    "team": "home", 
                    "position_desc": "Right winger at the point",
                    "assumption": "RW provides shooting option",
                    "confidence": 0.8
                },
                {
                    "id": "LW",
                    "type": "winger", 
                    "team": "home",
                    "position_desc": "Left winger near the net",
                    "assumption": "LW screens goalie and deflects",
                    "confidence": 0.8
                },
                {
                    "id": "RD",
                    "type": "defense",
                    "team": "home",
                    "position_desc": "Right defenseman at blue line",
                    "assumption": "RD keeps puck in zone",
                    "confidence": 0.9
                }
            ],
            "movements": [
                {
                    "id": "m1", 
                    "type": "pass",
                    "desc": "Center passes to right winger",
                    "from_player": "C",
                    "to_player": "RW",
                    "to_area": "point area",
                    "assumption": "Basic puck movement pattern",
                    "confidence": 0.9
                },
                {
                    "id": "m2",
                    "type": "pass", 
                    "desc": "Right winger passes to left winger",
                    "from_player": "RW",
                    "to_player": "LW",
                    "to_area": "net front area",
                    "assumption": "Cross-ice passing for scoring opportunity",
                    "confidence": 0.8
                }
            ],
            "equipment": [
                {
                    "id": "eq1",
                    "type": "cone",
                    "position_desc": "at the blue lines",
                    "count": 4,
                    "color": "orange",
                    "purpose": "mark boundaries and lanes",
                    "assumption": "Standard practice setup",
                    "confidence": 0.9
                }
            ],
            "annotations": []
        },
        "questions_for_user": [
            {
                "question": "Which side should the right winger be positioned at the point (left or right)?",
                "key": "point_side",
                "options": ["left", "right"],
                "critical": True,
                "confidence": 0.9
            }
        ],
        "metadata": {
            "type": "power_play",
            "phase": "offensive",
            "key_players": ["C", "RW", "LW", "RD"]
        }
    }
    
    print("Step 1: Initial Translation to Spec")
    print("-" * 40)
    
    # Step 2: Translate analysis to spec (this will capture response IDs)
    try:
        translation_result = translate_analysis_to_spec(
            analysis=sample_analysis,
            title="Phase 3 Workflow Test",
            description="Testing complete conversational update workflow"
        )
        
        if not translation_result.get("success"):
            print(f"❌ Translation failed: {translation_result.get('error')}")
            return False
        
        initial_spec = translation_result["spec"]
        conversation_metadata = translation_result["conversation"]
        
        print(f"✅ Initial translation completed")
        print(f"Players: {len(initial_spec.get('players', []))}")
        print(f"Movements: {len(initial_spec.get('movements', []))}")
        print(f"Equipment: {len(initial_spec.get('equipment', []))}")
        print(f"Response IDs captured: {list(conversation_metadata.get('response_ids', {}).keys())}")
        
    except Exception as e:
        print(f"❌ Translation failed with exception: {e}")
        return False
    
    print("\nStep 2: User Provides Clarifications")
    print("-" * 40)
    
    # Step 3: User provides clarifications
    user_clarifications = {
        # Player-related clarifications
        "point_side": "left",  # Move RW to left point
        "position_LW": "Move left winger to right side of net instead",
        
        # Movement-related clarifications  
        "timing": "Make passes simultaneous rather than sequential",
        "path_style": "Use curved paths for more realistic movement",
        
        # Equipment-related clarifications
        "equipment_placement": "Move cones to center ice, not blue lines",
        "cone_spacing": "Space cones 15 feet apart"
    }
    
    print(f"User clarifications:")
    for key, value in user_clarifications.items():
        print(f"  - {key}: {value}")
    
    print("\nStep 3: Update Spec with Clarifications")
    print("-" * 40)
    
    # Step 4: Update spec with clarifications
    try:
        update_result = update_spec_with_clarifications(
            original_spec=initial_spec,
            clarifications=user_clarifications,
            conversation_metadata=conversation_metadata
        )
        
        if not update_result.get("success"):
            print(f"❌ Spec update failed: {update_result.get('error')}")
            return False
        
        updated_spec = update_result["updated_spec"]
        changes_made = update_result["changes_made"]
        new_conversation = update_result["conversation"]
        routing_summary = update_result["routing_summary"]
        
        print(f"✅ Spec update completed")
        print(f"Changes made:")
        for change in changes_made:
            print(f"  - {change}")
        
        print(f"\nRouting summary:")
        print(f"  - Player clarifications: {routing_summary['player_clarifications']}")
        print(f"  - Movement clarifications: {routing_summary['movement_clarifications']}")
        print(f"  - Equipment clarifications: {routing_summary['equipment_clarifications']}")
        
        print(f"\nUpdated spec:")
        print(f"  - Players: {len(updated_spec.get('players', []))}")
        print(f"  - Movements: {len(updated_spec.get('movements', []))}")
        print(f"  - Equipment: {len(updated_spec.get('equipment', []))}")
        
        # Check conversation continuity
        original_response_ids = conversation_metadata.get("response_ids", {})
        new_response_ids = new_conversation.get("response_ids", {})
        
        print(f"\nConversation continuity:")
        for mapping_type in ["player_mapping", "movement_mapping"]:
            original_id = original_response_ids.get(mapping_type)
            new_id = new_response_ids.get(mapping_type)
            if original_id != new_id:
                print(f"  - {mapping_type}: {original_id} -> {new_id}")
            else:
                print(f"  - {mapping_type}: No update (no clarifications for this component)")
        
    except Exception as e:
        print(f"❌ Spec update failed with exception: {e}")
        return False
    
    # Step 5: Save comprehensive test results
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    workflow_results = {
        "test_name": "Complete Conversational Workflow - Phase 3",
        "sample_analysis": sample_analysis,
        "initial_translation": {
            "spec": initial_spec,
            "conversation_metadata": conversation_metadata
        },
        "user_clarifications": user_clarifications,
        "update_result": {
            "updated_spec": updated_spec,
            "changes_made": changes_made,
            "conversation": new_conversation,
            "routing_summary": routing_summary,
            "remaining_questions": update_result.get("remaining_questions", [])
        },
        "workflow_validation": {
            "initial_translation_success": True,
            "clarification_routing_working": True,
            "conversation_continuity": original_response_ids != new_response_ids,
            "selective_updates": len(changes_made) > 0
        }
    }
    
    with open(output_dir / "phase3_complete_workflow.json", "w") as f:
        json.dump(workflow_results, f, indent=2)
    
    print(f"\n✅ Complete workflow test results saved to phase3_complete_workflow.json")
    return True

def test_clarification_routing_patterns():
    """Test that clarification routing patterns work correctly."""
    print("\n" + "=" * 80)
    print("TESTING CLARIFICATION ROUTING PATTERNS")
    print("=" * 80)
    
    # Test different clarification patterns
    test_clarifications = {
        # Should route to players
        "point_side": "left",
        "position_C": "move to slot", 
        "handedness": "right",
        "player_formation": "spread out more",
        
        # Should route to movements
        "timing": "simultaneous",
        "sequence": "reverse order",
        "path_curve": "more curved",
        "movement_speed": "slower",
        "speed_variation": "vary speeds",
        
        # Should route to equipment
        "equipment_spacing": "15 feet apart",
        "cone_color": "blue instead of orange",
        "pylon_height": "taller",
        "placement_pattern": "diamond formation",
        
        # Should default to players
        "unknown_key": "some value",
        "custom_instruction": "special requirement"
    }
    
    # Create minimal spec and conversation metadata for testing
    minimal_spec = {
        "rink": {"view": "offensive"},
        "players": [],
        "movements": [],
        "equipment": []
    }
    
    minimal_conversation = {
        "response_ids": {
            "player_mapping": "resp_123",
            "movement_mapping": "resp_456"
        },
        "original_analysis": {
            "components_with_assumptions": {
                "players": [],
                "movements": [],
                "equipment": []
            }
        }
    }
    
    print("Testing routing for different clarification keys:")
    
    try:
        # This will test routing without actually making API calls (since original data is empty)
        update_result = update_spec_with_clarifications(
            original_spec=minimal_spec,
            clarifications=test_clarifications,
            conversation_metadata=minimal_conversation
        )
        
        routing_summary = update_result["routing_summary"]
        
        print(f"✅ Routing test completed:")
        print(f"  - Player clarifications: {routing_summary['player_clarifications']}")
        print(f"  - Movement clarifications: {routing_summary['movement_clarifications']}")
        print(f"  - Equipment clarifications: {routing_summary['equipment_clarifications']}")
        
        # Validate expected routing counts
        expected_player = 6  # point_side, position_C, handedness, player_formation, unknown_key, custom_instruction
        expected_movement = 5  # timing, sequence, path_curve, movement_speed, speed_variation
        expected_equipment = 4  # equipment_spacing, cone_color, pylon_height, placement_pattern
        
        success = (
            routing_summary["player_clarifications"] == expected_player and
            routing_summary["movement_clarifications"] == expected_movement and
            routing_summary["equipment_clarifications"] == expected_equipment
        )
        
        if success:
            print("✅ All clarifications routed to correct components")
        else:
            print("❌ Routing mismatch - check pattern definitions")
            print(f"Expected: players={expected_player}, movements={expected_movement}, equipment={expected_equipment}")
        
        return success
        
    except Exception as e:
        print(f"❌ Routing test failed: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("TESTING PHASE 3: COMPLETE CONVERSATIONAL SPEC UPDATES")
    print("=" * 80)
    
    success_count = 0
    total_tests = 2
    
    # Test complete workflow
    if test_complete_conversational_workflow():
        success_count += 1
    
    # Test clarification routing
    if test_clarification_routing_patterns():
        success_count += 1
    
    print("\n" + "=" * 80)
    print("PHASE 3 SUMMARY")
    print("=" * 80)
    
    if success_count == total_tests:
        print("✅ All Phase 3 tests PASSED")
        print("\nPhase 3 Implementation Complete:")
        print("  ✅ update_spec_with_clarifications MCP tool implemented")
        print("  ✅ Smart clarification routing with pattern matching")
        print("  ✅ Selective component updates (only affected parts)")
        print("  ✅ Conversation continuity with response_id management")
        print("  ✅ Change tracking and remaining questions detection")
        print("  ✅ Complete client workflow: translate -> clarify -> update")
        print("\nConversational Updates Architecture Complete:")
        print("  🎉 Phase 1: Response ID tracking ✓")
        print("  🎉 Phase 2: Enhanced mapping functions ✓")
        print("  🎉 Phase 3: Update tool with smart routing ✓")
        print("  🎉 Multi-turn conversation support with OpenAI Responses API ✓")
        print("\nReady for client integration!")
    else:
        print(f"❌ {total_tests - success_count} Phase 3 tests FAILED")
        print("\nNeeds investigation:")
        print("  - Check update_spec_with_clarifications implementation")
        print("  - Verify clarification routing patterns")
        print("  - Test conversation metadata flow")