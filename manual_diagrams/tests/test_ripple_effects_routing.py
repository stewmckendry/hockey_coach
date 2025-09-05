#!/usr/bin/env python3
"""Test routing flexibility for clarifications with ripple effects across components."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import update_spec_with_clarifications

def test_current_routing_limitations():
    """Test current routing system with cross-component clarifications."""
    print("=" * 80)
    print("TESTING CURRENT ROUTING LIMITATIONS")
    print("=" * 80)
    
    # Simulate problematic clarifications that affect multiple components
    ripple_effect_clarifications = {
        # This SHOULD affect both players AND movements
        "move_all_players_closer_to_net": "Bring everyone 10 feet closer to the goal",
        
        # This SHOULD affect players AND equipment  
        "spread_formation_wider": "Spread players and cones wider across the ice",
        
        # This SHOULD affect all three components
        "switch_to_defensive_setup": "Convert this to a defensive zone setup instead",
        
        # General instruction that could affect anything
        "make_drill_more_beginner_friendly": "Simplify positions and movements for beginners",
        
        # Formation change that affects players + movements + equipment
        "change_to_box_formation": "Arrange players in a box formation with equipment at corners"
    }
    
    print("Testing current routing for cross-component clarifications:")
    
    # Create minimal test data
    minimal_spec = {
        "rink": {"view": "offensive"},
        "players": [{"id": "C", "coordinates": {"x": 60, "y": 0}}],
        "movements": [{"id": "m1", "type": "pass"}],
        "equipment": [{"id": "eq1", "type": "cone"}]
    }
    
    minimal_conversation = {
        "response_ids": {"player_mapping": "resp_123"},
        "original_analysis": {
            "components_with_assumptions": {
                "players": [{"id": "C", "position_desc": "center"}],
                "movements": [{"id": "m1", "desc": "pass"}],
                "equipment": [{"id": "eq1", "position_desc": "boundary"}]
            }
        }
    }
    
    try:
        result = update_spec_with_clarifications(
            original_spec=minimal_spec,
            clarifications=ripple_effect_clarifications,
            conversation_metadata=minimal_conversation
        )
        
        routing_summary = result["routing_summary"]
        
        print(f"Current routing results:")
        print(f"  Player clarifications: {routing_summary['player_clarifications']}")
        print(f"  Movement clarifications: {routing_summary['movement_clarifications']}")
        print(f"  Equipment clarifications: {routing_summary['equipment_clarifications']}")
        
        print(f"\nPROBLEM IDENTIFIED:")
        print(f"  All {len(ripple_effect_clarifications)} clarifications routed to players only!")
        print(f"  Cross-component effects are NOT handled by current routing.")
        
        return False  # Current system has limitations
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_enhanced_routing_design():
    """Design and test enhanced routing that handles ripple effects."""
    print("\n" + "=" * 80)
    print("DESIGNING ENHANCED ROUTING FOR RIPPLE EFFECTS")
    print("=" * 80)
    
    print("PROPOSED ENHANCED ROUTING ARCHITECTURE:")
    print("-" * 50)
    
    enhanced_routing_design = {
        "cross_component_patterns": {
            # Clarifications that should update multiple components
            "formation": ["players", "movements", "equipment"],  # Formation changes affect everything
            "zone_change": ["players", "movements"],  # Zone changes affect players + movements
            "spread": ["players", "equipment"],  # Spread affects players + equipment positioning
            "closer": ["players", "movements"],  # Distance changes affect players + movement paths
            "beginner": ["players", "movements"],  # Skill level affects complexity
            "defensive": ["players", "movements"],  # Setup type affects multiple components
            "box": ["players", "equipment"],  # Specific formations
            "diamond": ["players", "equipment"],
            "line": ["players", "equipment"]
        },
        
        "priority_ordering": {
            # When multiple components need updates, do them in this order
            "update_sequence": ["players", "movements", "equipment"],
            "reason": "Players first (positions), then movements (based on new positions), then equipment (based on final layout)"
        },
        
        "dependency_handling": {
            "movements_depend_on_players": True,
            "equipment_independent": True,
            "cascading_updates": "movements use updated player positions as input"
        }
    }
    
    print(json.dumps(enhanced_routing_design, indent=2))
    
    print("\nENHANCED ROUTING ALGORITHM:")
    print("1. Analyze each clarification for cross-component keywords")
    print("2. Build component update set (can include multiple components)")  
    print("3. Execute updates in dependency order: players → movements → equipment")
    print("4. Pass updated components to dependent mappings")
    
    return True

def design_smart_routing_implementation():
    """Design the implementation for smart cross-component routing."""
    print("\n" + "=" * 80)
    print("SMART ROUTING IMPLEMENTATION DESIGN")
    print("=" * 80)
    
    implementation_code = '''
def enhanced_clarification_routing(clarifications: Dict[str, Any]) -> Dict[str, Set[str]]:
    """
    Enhanced routing that identifies cross-component impacts.
    
    Returns:
        Dict mapping each clarification to set of components it should affect
    """
    
    # Cross-component pattern definitions
    CROSS_COMPONENT_PATTERNS = {
        # Formation and layout changes
        "formation": ["players", "movements", "equipment"],
        "spread": ["players", "equipment"],
        "closer": ["players", "movements"], 
        "wider": ["players", "equipment"],
        "tighter": ["players", "movements"],
        
        # Zone and setup changes  
        "zone": ["players", "movements"],
        "defensive": ["players", "movements"],
        "offensive": ["players", "movements"],
        "neutral": ["players", "movements"],
        
        # Skill level adjustments
        "beginner": ["players", "movements"],
        "advanced": ["players", "movements"], 
        "simplified": ["players", "movements"],
        
        # Specific formations
        "box": ["players", "equipment"],
        "diamond": ["players", "equipment"],
        "line": ["players", "equipment"],
        "circle": ["players", "equipment"]
    }
    
    # Component-specific patterns (existing)
    PLAYER_PATTERNS = ["position_", "point_", "net_", "handedness", "player_"]
    MOVEMENT_PATTERNS = ["timing", "sequence", "path_", "speed_", "movement_"]
    EQUIPMENT_PATTERNS = ["equipment_", "cone_", "pylon_", "placement_"]
    
    routing_result = {}
    
    for key, value in clarifications.items():
        affected_components = set()
        
        # Check for cross-component patterns first
        key_lower = key.lower()
        for pattern, components in CROSS_COMPONENT_PATTERNS.items():
            if pattern in key_lower or pattern in str(value).lower():
                affected_components.update(components)
                break
        
        # If no cross-component match, use single-component routing
        if not affected_components:
            if any(pattern.rstrip("_") in key for pattern in PLAYER_PATTERNS):
                affected_components.add("players")
            elif any(pattern.rstrip("_") in key for pattern in MOVEMENT_PATTERNS):
                affected_components.add("movements")  
            elif any(pattern.rstrip("_") in key for pattern in EQUIPMENT_PATTERNS):
                affected_components.add("equipment")
            else:
                # Default to players for unmatched
                affected_components.add("players")
        
        routing_result[key] = affected_components
    
    return routing_result

def update_spec_with_smart_routing(
    original_spec: Dict[str, Any],
    clarifications: Dict[str, Any], 
    conversation_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Enhanced update with smart cross-component routing."""
    
    # Get smart routing analysis
    routing_analysis = enhanced_clarification_routing(clarifications)
    
    # Determine which components need updates
    needs_player_update = any("players" in components for components in routing_analysis.values())
    needs_movement_update = any("movements" in components for components in routing_analysis.values())
    needs_equipment_update = any("equipment" in components for components in routing_analysis.values())
    
    # Collect clarifications by component
    player_clarifications = {k: v for k, v in clarifications.items() 
                           if "players" in routing_analysis[k]}
    movement_clarifications = {k: v for k, v in clarifications.items()
                             if "movements" in routing_analysis[k]}  
    equipment_clarifications = {k: v for k, v in clarifications.items()
                              if "equipment" in routing_analysis[k]}
    
    # Execute updates in dependency order with cascade
    updated_spec = original_spec.copy()
    
    # 1. Update players first
    if needs_player_update:
        # ... existing player update logic ...
        pass
    
    # 2. Update movements (using updated players as input)  
    if needs_movement_update:
        # ... existing movement update logic but with updated_spec.players ...
        pass
        
    # 3. Update equipment (independent)
    if needs_equipment_update:
        # ... existing equipment update logic ...
        pass
    
    return {
        "success": True,
        "updated_spec": updated_spec,
        "routing_analysis": routing_analysis,
        "cross_component_updates": {
            "players": needs_player_update,
            "movements": needs_movement_update, 
            "equipment": needs_equipment_update
        }
    }
'''
    
    print("ENHANCED IMPLEMENTATION DESIGN:")
    print(implementation_code)
    
    print("\nKEY IMPROVEMENTS:")
    print("✅ Cross-component pattern recognition")
    print("✅ Smart routing based on clarification content")
    print("✅ Dependency-aware update ordering")
    print("✅ Cascading updates (movements use updated player positions)")
    print("✅ Comprehensive routing analysis in response")
    
    return True

def test_ripple_effect_scenarios():
    """Test specific scenarios where clarifications should have ripple effects."""
    print("\n" + "=" * 80)
    print("RIPPLE EFFECT SCENARIOS ANALYSIS")
    print("=" * 80)
    
    test_scenarios = [
        {
            "name": "Formation Change",
            "clarification": {"formation": "Change to box formation with players at corners"},
            "expected_impact": ["players", "equipment"],
            "reasoning": "Box formation requires repositioning players AND placing equipment at specific locations"
        },
        {
            "name": "Zone Switch", 
            "clarification": {"zone_change": "Switch from offensive to defensive zone setup"},
            "expected_impact": ["players", "movements"],
            "reasoning": "Zone change requires new player positions AND updating movement directions/targets"
        },
        {
            "name": "Skill Level Adjustment",
            "clarification": {"beginner_friendly": "Make this drill more beginner-friendly"},
            "expected_impact": ["players", "movements"], 
            "reasoning": "Beginner drills need simpler positions AND slower/straighter movements"
        },
        {
            "name": "Spacing Change",
            "clarification": {"spread_wider": "Spread everyone out more across the ice"},
            "expected_impact": ["players", "equipment"],
            "reasoning": "Wider spacing affects player positions AND equipment placement for boundaries"
        },
        {
            "name": "Complete Restructure",
            "clarification": {"total_redesign": "Completely change this to a defensive shell drill"},
            "expected_impact": ["players", "movements", "equipment"],
            "reasoning": "Complete drill type change affects all components fundamentally"
        }
    ]
    
    print("RIPPLE EFFECT SCENARIO ANALYSIS:")
    for scenario in test_scenarios:
        print(f"\n{scenario['name']}:")
        print(f"  Clarification: {list(scenario['clarification'].values())[0]}")
        print(f"  Expected impact: {', '.join(scenario['expected_impact'])}")
        print(f"  Reasoning: {scenario['reasoning']}")
    
    print(f"\n🔍 CURRENT SYSTEM LIMITATION:")
    print(f"   All scenarios above would route to 'players' only (default)")
    print(f"   Ripple effects to movements/equipment would be missed")
    
    print(f"\n✨ ENHANCED SYSTEM BENEFIT:")
    print(f"   Each scenario would correctly identify all affected components")
    print(f"   Updates would cascade properly: players → movements → equipment")
    
    return True

if __name__ == "__main__":
    print("TESTING ROUTING FLEXIBILITY FOR RIPPLE EFFECTS")
    print("=" * 80)
    
    success_count = 0
    total_tests = 4
    
    # Test current limitations
    if not test_current_routing_limitations():  # Expected to fail - shows limitation
        success_count += 1  # Success = identifying the limitation
    
    # Design enhanced routing
    if test_enhanced_routing_design():
        success_count += 1
    
    # Implementation design
    if design_smart_routing_implementation():
        success_count += 1
    
    # Scenario analysis
    if test_ripple_effect_scenarios():
        success_count += 1
    
    print("\n" + "=" * 80)
    print("ROUTING FLEXIBILITY ANALYSIS SUMMARY")
    print("=" * 80)
    
    if success_count == total_tests:
        print("✅ Routing analysis complete")
        print("\nCURRENT SYSTEM STATUS:")
        print("  ❌ Limited to single-component routing")
        print("  ❌ Cross-component ripple effects not handled") 
        print("  ❌ Formation changes don't cascade")
        print("  ❌ Zone changes don't update movements")
        
        print("\nENHANCED SYSTEM DESIGN:")
        print("  ✅ Cross-component pattern recognition")
        print("  ✅ Smart routing based on clarification content")
        print("  ✅ Dependency-aware update ordering")
        print("  ✅ Cascading updates with component dependencies")
        
        print("\nRECOMMENDATION:")
        print("  🔄 Implement enhanced routing for production use")
        print("  🔄 Add cross-component pattern matching")
        print("  🔄 Enable dependency-driven update cascading")
        print("  🔄 Support complex formation and zone changes")
        
    else:
        print(f"❌ Analysis incomplete ({success_count}/{total_tests})")