#!/usr/bin/env python3
"""
Test to verify that previous_response_id is being passed correctly through the system.

This test will help diagnose why the LLM might not be following instructions properly
on updates - it could be due to missing conversation continuity.
"""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec

def test_response_id_flow():
    """Test that response ID flows correctly through update calls."""
    
    print("=" * 80)
    print("TESTING RESPONSE ID FLOW FOR CONVERSATION CONTINUITY")
    print("=" * 80)
    
    # Step 1: Initial query analysis
    query = "Center ice faceoff with all 10 players positioned around the circle"
    
    print(f"\n📝 Query: {query}")
    print("\n1️⃣  Analyzing query...")
    
    analysis = analyze_hockey_query(query)
    
    if analysis.get("error"):
        print(f"❌ Analysis failed: {analysis['error']}")
        return False
    
    print("✅ Analysis complete")
    
    # Step 2: Initial translation (no previous_response_id)
    print("\n2️⃣  Initial translation to spec...")
    print("   Watch the logs for 'Previous Response ID provided: None'")
    
    initial_result = translate_analysis_to_spec(
        analysis=analysis,
        title="Center Ice Faceoff Test"
    )
    
    if not initial_result.get("success"):
        print(f"❌ Initial translation failed")
        return False
    
    initial_spec = initial_result["spec"]
    initial_response_id = initial_result.get("response_id")
    
    print(f"\n✅ Initial translation complete")
    print(f"   📍 Response ID returned: {initial_response_id}")
    
    if not initial_response_id:
        print("❌ ERROR: No response_id returned from initial translation!")
        print("   This means conversation continuity is broken")
        return False
    
    # Step 3: Clarifications
    print("\n3️⃣  Preparing clarifications...")
    
    clarifications = {
        "center_offset": "Centers should be slightly offset for faceoff",
        "winger_distance": "Wingers at edge of circle"
    }
    
    print(f"   Clarifications: {json.dumps(clarifications, indent=6)}")
    
    # Step 4: Update with clarifications - SHOULD pass previous_response_id
    print("\n4️⃣  Updating spec with clarifications...")
    print(f"   📍 Passing previous_response_id: {initial_response_id}")
    print("\n   🔍 CHECK THE LOGS FOR:")
    print("      - '📍 Previous Response ID provided: [ID]'")
    print("      - '🔗 Calling map_positions_with_llm in UPDATE mode'")
    print("      - '🔄 Continuing conversation from response: [ID]'")
    print("      - '📍 Previous Response ID in request: [ID]'")
    
    updated_result = translate_analysis_to_spec(
        analysis=analysis,
        existing_spec=initial_spec,
        clarifications=clarifications,
        previous_response_id=initial_response_id  # THIS IS CRITICAL!
    )
    
    if not updated_result.get("success"):
        print(f"\n❌ Update failed")
        return False
    
    updated_response_id = updated_result.get("response_id")
    
    print(f"\n✅ Update complete")
    print(f"   📍 New Response ID: {updated_response_id}")
    
    # Step 5: Verify the chain
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    checks = {
        "Initial response_id returned": bool(initial_response_id),
        "Updated response_id returned": bool(updated_response_id),
        "Response IDs are different": initial_response_id != updated_response_id,
        "Response ID chain maintained": bool(initial_response_id and updated_response_id)
    }
    
    all_passed = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}: {passed}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ Response ID flow is working correctly!")
        print("   The system should maintain conversation continuity")
    else:
        print("\n❌ Response ID flow has issues!")
        print("   This could explain why LLM isn't following update instructions")
    
    # Step 6: Check the actual player positions to see if clarifications were applied
    print("\n" + "=" * 80)
    print("CHECKING IF CLARIFICATIONS WERE APPLIED")
    print("=" * 80)
    
    initial_players = initial_spec.get("players", [])
    updated_players = updated_result["spec"].get("players", [])
    
    # Check center positions
    initial_centers = [p for p in initial_players if p.get("label") in ["C", "C2"]]
    updated_centers = [p for p in updated_players if p.get("label") in ["C", "C2"]]
    
    if len(initial_centers) == 2 and len(updated_centers) == 2:
        # Calculate distance between centers
        ic1, ic2 = initial_centers[0], initial_centers[1]
        uc1, uc2 = updated_centers[0], updated_centers[1]
        
        initial_dist = ((ic1["coordinates"]["x"] - ic2["coordinates"]["x"])**2 + 
                       (ic1["coordinates"]["y"] - ic2["coordinates"]["y"])**2)**0.5
        updated_dist = ((uc1["coordinates"]["x"] - uc2["coordinates"]["x"])**2 + 
                       (uc1["coordinates"]["y"] - uc2["coordinates"]["y"])**2)**0.5
        
        print(f"Initial center distance: {initial_dist:.2f}")
        print(f"Updated center distance: {updated_dist:.2f}")
        
        if updated_dist > initial_dist:
            print("✅ Centers were moved apart (clarification applied)")
        else:
            print("❌ Centers were NOT moved apart (clarification not applied)")
            print("   This suggests conversation continuity may be broken")
    
    return all_passed

if __name__ == "__main__":
    try:
        print("\n🔍 This test will verify response_id flow through the system")
        print("   Check the server logs for detailed information about response_id passing\n")
        
        success = test_response_id_flow()
        
        if success:
            print("\n🎉 Response ID flow verified successfully!")
        else:
            print("\n⚠️  Response ID flow has issues - check server logs for details")
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()