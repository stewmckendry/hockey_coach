#!/usr/bin/env python3
"""Analyze hybrid approaches that keep separate calls but improve cohesion."""

print("=" * 80)
print("HYBRID APPROACHES: SEPARATE CALLS + BETTER COHESION")
print("=" * 80)

print("\nAPPROACH 1: SEQUENTIAL CALLS WITH CASCADE")
print("-" * 50)

approach1 = '''
def translate_analysis_to_spec(
    analysis, title=None, description=None, 
    existing_spec=None, clarifications=None, previous_response_id=None
):
    """Single tool that orchestrates separate calls with cascading context."""
    
    if existing_spec and clarifications:
        # UPDATE MODE: Use existing spec as foundation
        return update_with_cascade(existing_spec, clarifications, analysis, previous_response_id)
    else:
        # INITIAL MODE: Fresh translation
        return initial_translation_with_cascade(analysis, title, description)

def update_with_cascade(existing_spec, clarifications, analysis, previous_response_id):
    """Update mode with cascading context between calls."""
    
    # 1. Update players first (with existing spec context)
    player_result = map_positions_with_llm(
        players=analysis["components_with_assumptions"]["players"],
        clarifications=clarifications,
        existing_spec_context=existing_spec,  # NEW: Pass existing spec for context
        previous_response_id=previous_response_id
    )
    
    # 2. Update movements (with updated players + existing spec context) 
    movement_result = map_movements_with_llm(
        movements=analysis["components_with_assumptions"]["movements"],
        players=player_result["players_mapped"],  # Use updated players
        clarifications=clarifications,
        existing_spec_context=existing_spec,  # NEW: Pass existing spec for context
        previous_response_id=player_result["response_id"]  # Chain response IDs
    )
    
    # 3. Update equipment (with final context)
    equipment_result = map_equipment_with_llm(
        equipment=analysis["components_with_assumptions"]["equipment"],
        clarifications=clarifications,
        existing_spec_context=existing_spec,  # NEW: Pass existing spec for context
        final_layout_context={  # NEW: Pass final layout
            "players": player_result["players_mapped"],
            "movements": movement_result["movements_mapped"]
        }
    )
    
    # Build final spec with all updates
    return build_cohesive_spec(player_result, movement_result, equipment_result)
'''

print("APPROACH 1 BENEFITS:")
print("✅ Separate specialized calls (detailed focus)")
print("✅ Cascading context between calls") 
print("✅ Each call sees existing spec for stability")
print("✅ Chain response IDs for full conversation continuity")
print("✅ Final layout context prevents inconsistencies")

print("\nAPPROACH 2: SMART ROUTING WITH EXISTING SPEC CONTEXT")
print("-" * 50)

approach2 = '''
def translate_analysis_to_spec(
    analysis, title=None, description=None,
    existing_spec=None, clarifications=None, previous_response_id=None
):
    """Enhanced single tool with smart routing but existing spec awareness."""
    
    if existing_spec and clarifications:
        # Determine what needs updating using smart routing
        routing = analyze_clarification_impact(clarifications, existing_spec)
        
        # Only update components that need changes
        if routing["needs_player_update"]:
            updated_players = update_players_with_context(
                existing_spec, clarifications, analysis, previous_response_id
            )
        else:
            updated_players = existing_spec["players"]  # Keep unchanged
        
        if routing["needs_movement_update"]: 
            updated_movements = update_movements_with_context(
                existing_spec, updated_players, clarifications, analysis, previous_response_id
            )
        else:
            updated_movements = existing_spec["movements"]  # Keep unchanged
            
        if routing["needs_equipment_update"]:
            updated_equipment = update_equipment_with_context(
                existing_spec, clarifications, analysis
            )
        else:
            updated_equipment = existing_spec["equipment"]  # Keep unchanged
            
        return build_updated_spec(updated_players, updated_movements, updated_equipment)
    
def analyze_clarification_impact(clarifications, existing_spec):
    """Analyze which components need updates and detect cross-component effects."""
    
    impact = {
        "needs_player_update": False,
        "needs_movement_update": False, 
        "needs_equipment_update": False,
        "cross_component_effects": []
    }
    
    for key, value in clarifications.items():
        # Check for cross-component keywords
        if any(keyword in key.lower() or keyword in str(value).lower() 
               for keyword in ["formation", "spread", "closer", "zone", "defensive"]):
            # Cross-component change - update multiple components
            impact["needs_player_update"] = True
            impact["needs_movement_update"] = True
            impact["cross_component_effects"].append(key)
        elif any(keyword in key for keyword in ["position", "point", "player"]):
            impact["needs_player_update"] = True
            # If players move significantly, movements might need adjustment
            if "closer" in str(value).lower() or "move" in str(value).lower():
                impact["needs_movement_update"] = True
        # ... other routing logic
    
    return impact
'''

print("APPROACH 2 BENEFITS:")
print("✅ Smart impact analysis prevents unnecessary updates")
print("✅ Cross-component effects detected automatically")  
print("✅ Selective updates for efficiency")
print("✅ Existing spec context preserved")
print("✅ Ripple effects handled intelligently")

print("\nAPPROACH 3: CONVERSATION BRANCHING")
print("-" * 50)

approach3 = '''
def translate_analysis_to_spec(
    analysis, title=None, description=None,
    existing_spec=None, clarifications=None, 
    previous_response_ids=None  # Dict of component-specific IDs
):
    """Use separate response_id branches for different components."""
    
    if existing_spec and clarifications:
        # Each component maintains its own conversation branch
        response_ids = previous_response_ids or {}
        
        # Route clarifications to components
        routing = smart_route_clarifications(clarifications)
        
        results = {}
        
        # Update players (with their specific conversation ID)
        if routing.get("player_clarifications"):
            results["players"] = map_positions_with_llm(
                players=analysis["components_with_assumptions"]["players"],
                clarifications=routing["player_clarifications"],
                existing_context=existing_spec["players"],
                previous_response_id=response_ids.get("players")
            )
        
        # Update movements (with their specific conversation ID + updated players)
        if routing.get("movement_clarifications"):
            results["movements"] = map_movements_with_llm(
                movements=analysis["components_with_assumptions"]["movements"],
                clarifications=routing["movement_clarifications"],
                existing_context=existing_spec["movements"],
                updated_players=results.get("players", {}).get("players_mapped", existing_spec["players"]),
                previous_response_id=response_ids.get("movements")
            )
        
        return build_spec_from_results(results, existing_spec)
'''

print("APPROACH 3 BENEFITS:")
print("✅ Component-specific conversation branches")
print("✅ Granular conversation tracking")
print("✅ Selective updates with dependencies")
print("✅ Preserves unchanged components exactly")

print("\n" + "=" * 80)
print("RECOMMENDATION ANALYSIS")
print("-" * 50)

print("🎯 RECOMMENDED APPROACH: #1 (Sequential Calls with Cascade)")
print("\nReasons:")
print("✅ Best of both worlds - separate specialized calls + cohesion")
print("✅ Existing spec context prevents unwanted changes") 
print("✅ Cascading ensures components work together")
print("✅ Response ID chaining maintains full conversation")
print("✅ Each LLM call focused on its specialty")
print("✅ Natural dependency flow: players → movements → equipment")

print("\nImplementation Strategy:")
print("1. Keep existing mapping functions")
print("2. Add existing_spec_context parameter to each")
print("3. Chain response IDs between calls")
print("4. Pass updated results to subsequent calls")
print("5. Enhanced prompts: 'Start with existing spec, apply clarifications'")

print("\nKey Prompt Enhancement:")
enhancement = '''
# For each mapping function, when existing_spec_context is provided:

PROMPT_TEMPLATE = f"""
SPEC UPDATE MODE - {component_type.upper()} MAPPING

EXISTING SPEC CONTEXT:
{json.dumps(existing_spec_context, indent=2)}

You are updating the {component_type} part of this hockey diagram spec.

INSTRUCTIONS:
1. START with the existing {component_type} as your foundation
2. Apply these clarifications: {clarifications}
3. Keep unchanged elements stable unless clarifications require changes
4. Ensure your updates work with the overall spec context
5. Be conservative - only change what the clarifications specifically request

ORIGINAL ANALYSIS (for reference):
{analysis_data}

Generate updated {component_type} that incorporate the clarifications while maintaining spec cohesion.
"""
'''

print(enhancement)

print("\n" + "=" * 80)
print("IMPLEMENTATION PRIORITY")
print("-" * 50)
print("🚀 HIGH PRIORITY - This gives us the best solution:")
print("  ✅ Keeps specialized calls (avoids mega-call issues)")
print("  ✅ Adds cohesion through cascading context")  
print("  ✅ Maintains conversation continuity")
print("  ✅ Handles cross-component dependencies naturally")
print("  ✅ Conservative updates (only change what's needed)")

print("\n📋 Implementation Steps:")
print("1. Add existing_spec_context parameter to mapping functions")
print("2. Enhance prompts for update mode")
print("3. Implement cascading call sequence")
print("4. Add response ID chaining")
print("5. Test with complex cross-component clarifications")

print("=" * 80)