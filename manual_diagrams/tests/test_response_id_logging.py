#!/usr/bin/env python3
"""
Simple test to verify response_id logging in the update flow.
This will help diagnose if previous_response_id is being passed correctly.
"""

import sys
import os
import json

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec

def test():
    print("=" * 80)
    print("RESPONSE ID LOGGING TEST")
    print("=" * 80)
    
    # Step 1: Analyze
    query = "Center ice faceoff with all 10 players"
    print(f"\nQuery: {query}")
    
    analysis = analyze_hockey_query(query)
    if analysis.get("error"):
        print(f"Analysis failed: {analysis['error']}")
        return
    
    # Step 2: Initial translation
    print("\n--- INITIAL TRANSLATION ---")
    initial_result = translate_analysis_to_spec(
        analysis=analysis,
        title="Test"
    )
    
    if not initial_result.get("success"):
        print("Initial translation failed")
        return
    
    # CRITICAL: Extract response_id
    response_id = initial_result.get("response_id")
    print(f"\n✅ Initial translation returned response_id: {response_id}")
    
    if not response_id:
        print("❌ ERROR: No response_id returned! Cannot test update mode.")
        return
    
    # Step 3: Update with clarifications
    print("\n--- UPDATE WITH CLARIFICATIONS ---")
    print(f"Passing previous_response_id: {response_id}")
    
    clarifications = {
        "center_spacing": "Centers should be at (0, -1) and (0, 1)"
    }
    
    updated_result = translate_analysis_to_spec(
        analysis=analysis,
        existing_spec=initial_result["spec"],
        clarifications=clarifications,
        previous_response_id=response_id  # THIS IS WHAT WE'RE TESTING
    )
    
    if not updated_result.get("success"):
        print("Update failed")
        return
    
    new_response_id = updated_result.get("response_id")
    print(f"\n✅ Update returned new response_id: {new_response_id}")
    
    # Check if centers were actually moved
    updated_players = updated_result["spec"].get("players", [])
    centers = [p for p in updated_players if p.get("label") in ["C", "C2"]]
    
    if len(centers) == 2:
        c1, c2 = centers[0], centers[1]
        print(f"\nCenter positions after update:")
        print(f"  C1: ({c1['coordinates']['x']}, {c1['coordinates']['y']})")
        print(f"  C2: ({c2['coordinates']['x']}, {c2['coordinates']['y']})")
        
        dist = ((c1["coordinates"]["x"] - c2["coordinates"]["x"])**2 + 
                (c1["coordinates"]["y"] - c2["coordinates"]["y"])**2)**0.5
        
        if dist > 1.0:
            print(f"✅ Centers are now {dist:.1f} units apart (clarification applied)")
        else:
            print(f"❌ Centers are still only {dist:.1f} units apart (clarification NOT applied)")
            print("   This suggests conversation continuity is broken")
    
    print("\n" + "=" * 80)
    print("CHECK THE SERVER LOGS FOR:")
    print("  - '📍 Previous Response ID provided: ...'")
    print("  - '🔗 Calling map_positions_with_llm in UPDATE mode'") 
    print("  - '🔄 Continuing conversation from response: ...'")
    print("  - '📍 Previous Response ID in request: ...'")
    print("=" * 80)

if __name__ == "__main__":
    test()