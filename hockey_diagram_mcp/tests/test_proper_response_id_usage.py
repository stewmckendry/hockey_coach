#!/usr/bin/env python3
"""
Demonstrate the CORRECT way to use previous_response_id for conversation continuity.

This test shows how to properly chain response IDs when using clarifications
to update a diagram spec through multiple rounds of refinement.
"""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec

def test_proper_response_id_usage():
    """Demonstrate correct usage of previous_response_id for conversation continuity."""
    
    print("=" * 80)
    print("CORRECT USAGE OF previous_response_id FOR CONVERSATION CONTINUITY")
    print("=" * 80)
    
    # STEP 1: Analyze the hockey query
    query = "Center ice faceoff with all 10 players"
    
    print(f"\n📝 Query: {query}")
    print("\n1️⃣  STEP 1: Analyzing query...")
    
    analysis = analyze_hockey_query(query)
    
    if analysis.get("error"):
        print(f"❌ Analysis failed: {analysis['error']}")
        return False
    
    print("✅ Analysis complete")
    
    # Check for questions
    if analysis.get("questions_for_user"):
        print("\n❓ Questions from analysis:")
        for q in analysis["questions_for_user"]:
            print(f"   - {q['question']}")
    
    # STEP 2: Initial translation (NO previous_response_id)
    print("\n2️⃣  STEP 2: Initial translation to spec...")
    
    initial_result = translate_analysis_to_spec(
        analysis=analysis,
        title="Center Ice Faceoff",
        description="Standard center ice faceoff setup"
        # NOTE: NO previous_response_id on first call
    )
    
    if not initial_result.get("success"):
        print(f"❌ Initial translation failed: {initial_result.get('error')}")
        return False
    
    initial_spec = initial_result["spec"]
    initial_response_id = initial_result.get("response_id")  # Critical: Extract this!
    conversation_meta = initial_result.get("conversation", {})
    
    print("✅ Initial translation complete")
    print(f"   📍 Response ID: {initial_response_id}")
    print(f"   🏒 Players mapped: {len(initial_spec.get('players', []))}")
    
    # Show response IDs from each mapping stage
    response_ids = conversation_meta.get("response_ids", {})
    if response_ids:
        print("\n   Mapping stage response IDs:")
        for stage, rid in response_ids.items():
            print(f"     - {stage}: {rid}")
    
    # Check for overlapping centers
    players = initial_spec.get("players", [])
    centers = [p for p in players if p.get("label") in ["C", "C2"]]
    if len(centers) == 2:
        c1, c2 = centers[0], centers[1]
        if c1["coordinates"]["x"] == c2["coordinates"]["x"] and c1["coordinates"]["y"] == c2["coordinates"]["y"]:
            print(f"\n⚠️  Detected overlapping centers at ({c1['coordinates']['x']}, {c1['coordinates']['y']})")
    
    # STEP 3: User provides clarifications
    print("\n3️⃣  STEP 3: User provides clarifications...")
    
    clarifications = {
        "center_positioning": "The two centers should be slightly offset - home center at (0, -1) and away center at (0, 1) for the faceoff",
        "winger_distance": "Wingers should be 15 feet from center ice dot",
        "defensemen_position": "Defensemen stay closer to their blue lines"
    }
    
    print("   User clarifications:")
    for key, value in clarifications.items():
        print(f"     - {key}: {value}")
    
    # STEP 4: Update with clarifications (WITH previous_response_id)
    print("\n4️⃣  STEP 4: Updating spec with clarifications...")
    print(f"   🔗 Using previous_response_id: {initial_response_id}")
    
    updated_result = translate_analysis_to_spec(
        analysis=analysis,  # Same analysis
        existing_spec=initial_spec,  # Pass the previous spec
        clarifications=clarifications,  # User's clarifications
        previous_response_id=initial_response_id  # CRITICAL: Pass the response_id!
    )
    
    if not updated_result.get("success"):
        print(f"❌ Update failed: {updated_result.get('error')}")
        return False
    
    updated_spec = updated_result["spec"]
    updated_response_id = updated_result.get("response_id")
    updated_conversation = updated_result.get("conversation", {})
    
    print("✅ Spec updated with clarifications")
    print(f"   📍 New Response ID: {updated_response_id}")
    print(f"   🏒 Players: {len(updated_spec.get('players', []))}")
    
    # Check if centers are now properly spaced
    updated_centers = [p for p in updated_spec["players"] if p.get("label") in ["C", "C2"]]
    if len(updated_centers) == 2:
        c1, c2 = updated_centers[0], updated_centers[1]
        dist = ((c1["coordinates"]["x"] - c2["coordinates"]["x"])**2 + 
                (c1["coordinates"]["y"] - c2["coordinates"]["y"])**2)**0.5
        print(f"\n   ✅ Centers now separated by {dist:.1f} units")
        print(f"      Home: ({c1['coordinates']['x']}, {c1['coordinates']['y']})")
        print(f"      Away: ({c2['coordinates']['x']}, {c2['coordinates']['y']})")
    
    # STEP 5: Further refinement (chaining from updated_response_id)
    print("\n5️⃣  STEP 5: Further refinement...")
    
    more_clarifications = {
        "face_direction": "All players should face center ice",
        "goalie_position": "Goalies stay in their creases"
    }
    
    print("   Additional clarifications:")
    for key, value in more_clarifications.items():
        print(f"     - {key}: {value}")
    
    print(f"\n   🔗 Using previous_response_id: {updated_response_id}")
    
    final_result = translate_analysis_to_spec(
        analysis=analysis,
        existing_spec=updated_spec,  # Use the updated spec
        clarifications=more_clarifications,
        previous_response_id=updated_response_id  # Use the LATEST response_id
    )
    
    if final_result.get("success"):
        final_response_id = final_result.get("response_id")
        print(f"✅ Final refinement complete")
        print(f"   📍 Final Response ID: {final_response_id}")
    
    # SUMMARY
    print("\n" + "=" * 80)
    print("CONVERSATION CONTINUITY SUMMARY")
    print("=" * 80)
    
    print("\n🔗 Response ID Chain:")
    print(f"   1. Initial:     {initial_response_id}")
    print(f"   2. After clarifications: {updated_response_id}")
    if 'final_response_id' in locals():
        print(f"   3. Final:       {final_response_id}")
    
    print("\n✅ KEY PATTERN FOR CORRECT USAGE:")
    print("""
    # Initial call
    result1 = translate_analysis_to_spec(analysis)
    response_id_1 = result1["response_id"]  # <-- EXTRACT THIS
    
    # Update with clarifications  
    result2 = translate_analysis_to_spec(
        analysis=analysis,
        existing_spec=result1["spec"],
        clarifications=user_clarifications,
        previous_response_id=response_id_1  # <-- PASS IT HERE
    )
    response_id_2 = result2["response_id"]  # <-- EXTRACT NEW ID
    
    # Further updates chain from latest ID
    result3 = translate_analysis_to_spec(
        analysis=analysis, 
        existing_spec=result2["spec"],
        clarifications=more_clarifications,
        previous_response_id=response_id_2  # <-- USE LATEST ID
    )
    """)
    
    print("\n🎯 BENEFITS OF PROPER RESPONSE ID CHAINING:")
    print("   • LLM maintains conversation context across refinements")
    print("   • Better understanding of iterative changes")
    print("   • More coherent updates that consider previous decisions")
    print("   • Improved spatial reasoning through conversation continuity")
    
    # Save results
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    test_results = {
        "test": "proper_response_id_usage",
        "response_id_chain": [
            initial_response_id,
            updated_response_id,
            final_response_id if 'final_response_id' in locals() else None
        ],
        "initial_spec": initial_spec,
        "updated_spec": updated_spec,
        "final_spec": final_result["spec"] if final_result.get("success") else None
    }
    
    with open(output_dir / "response_id_usage_test.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📁 Test results saved to outputs/response_id_usage_test.json")
    
    return True

if __name__ == "__main__":
    try:
        success = test_proper_response_id_usage()
        if success:
            print("\n🎉 Test completed successfully!")
        else:
            print("\n❌ Test failed")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()