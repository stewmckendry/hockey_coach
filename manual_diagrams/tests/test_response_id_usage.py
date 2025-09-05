#!/usr/bin/env python3
"""
Test proper usage of previous_response_id for conversation continuity.

This test demonstrates how to correctly use the response_id returned from
translate_analysis_to_spec for multi-turn conversations with clarifications.
"""

import json
import sys
from pathlib import Path

# Add server directory to path
sys.path.append(str(Path(__file__).parent.parent / "servers"))

def test_response_id_chaining():
    """Test proper response ID chaining for conversation continuity."""
    
    print("=" * 80)
    print("TESTING RESPONSE ID CHAINING FOR CONVERSATION CONTINUITY")
    print("=" * 80)
    
    # Sample analysis from analyze_hockey_query
    initial_analysis = {
        "explicit_info": {
            "drill_type": "faceoff",
            "location": "center ice",
            "players": {
                "home": ["center", "left winger", "right winger", "left defenseman", "right defenseman"],
                "away": ["center", "left winger", "right winger", "left defenseman", "right defenseman"]
            }
        },
        "assumptions": {
            "rink_view": "full",
            "zone_context": "neutral zone",
            "formation": "standard faceoff formation"
        },
        "questions_for_user": []
    }
    
    print("\n1. INITIAL TRANSLATION (no previous_response_id)")
    print("-" * 40)
    
    # Initial call - no previous_response_id
    initial_spec_result = translate_analysis_to_spec(
        analysis=initial_analysis,
        title="Center Ice Faceoff",
        description="Standard center ice faceoff with all players"
        # Note: NO previous_response_id on first call
    )
    
    # Extract the response_id from the result
    response_id = initial_spec_result.get("response_id")
    conversation_meta = initial_spec_result.get("conversation", {})
    
    print(f"✅ Initial translation complete")
    print(f"   Response ID: {response_id}")
    print(f"   Conversation metadata: {json.dumps(conversation_meta.get('response_ids', {}), indent=2)}")
    
    if not response_id:
        print("⚠️  WARNING: No response_id returned from initial translation")
        print("   This means conversation continuity won't work properly")
    
    print("\n2. UPDATE WITH CLARIFICATIONS (using previous_response_id)")
    print("-" * 40)
    
    # User provides clarifications
    clarifications = {
        "center_spacing": "Centers should be slightly offset, not overlapping",
        "winger_positions": "Wingers closer to the circle edge"
    }
    
    print(f"User clarifications: {json.dumps(clarifications, indent=2)}")
    
    # Second call WITH previous_response_id for continuity
    updated_spec_result = translate_analysis_to_spec(
        analysis=initial_analysis,  # Same analysis
        existing_spec=initial_spec_result.get("spec"),  # Previous spec
        clarifications=clarifications,  # User clarifications
        previous_response_id=response_id  # CRITICAL: Pass the response_id from previous call
    )
    
    new_response_id = updated_spec_result.get("response_id")
    new_conversation_meta = updated_spec_result.get("conversation", {})
    
    print(f"\n✅ Updated translation complete")
    print(f"   New Response ID: {new_response_id}")
    print(f"   New conversation metadata: {json.dumps(new_conversation_meta.get('response_ids', {}), indent=2)}")
    
    if response_id and new_response_id:
        print(f"\n✅ Response ID chaining successful!")
        print(f"   Previous: {response_id}")
        print(f"   Current:  {new_response_id}")
        print(f"   This ensures the LLM maintains conversation context")
    else:
        print(f"\n⚠️  Response ID chaining issue detected")
        if not response_id:
            print("   - Initial call didn't return response_id")
        if not new_response_id:
            print("   - Update call didn't return new response_id")
    
    print("\n3. CORRECT USAGE PATTERN")
    print("-" * 40)
    print("""
    # Step 1: Initial call
    result1 = translate_analysis_to_spec(analysis=analysis)
    response_id = result1.get("response_id")
    
    # Step 2: Update with clarifications
    result2 = translate_analysis_to_spec(
        analysis=analysis,
        existing_spec=result1["spec"],
        clarifications=user_clarifications,
        previous_response_id=response_id  # <-- PASS THIS!
    )
    new_response_id = result2.get("response_id")
    
    # Step 3: Further updates chain from the new ID
    result3 = translate_analysis_to_spec(
        analysis=analysis,
        existing_spec=result2["spec"],
        clarifications=more_clarifications,
        previous_response_id=new_response_id  # <-- Use latest ID
    )
    """)
    
    return {
        "initial_response_id": response_id,
        "updated_response_id": new_response_id,
        "chaining_successful": bool(response_id and new_response_id)
    }

if __name__ == "__main__":
    # Import the actual function from the MCP server
    try:
        from hockey_diagram_mcp_v3 import translate_analysis_to_spec
        
        result = test_response_id_chaining()
        
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        if result["chaining_successful"]:
            print("✅ Response ID chaining is working correctly!")
            print("   The system properly maintains conversation continuity")
        else:
            print("❌ Response ID chaining has issues")
            print("   Check that map_positions_with_llm returns response_id")
            print("   Ensure the OpenAI Responses API is being used correctly")
            
    except ImportError as e:
        print(f"ERROR: Could not import MCP server: {e}")
        print("Make sure the MCP server is running and accessible")
    except Exception as e:
        print(f"ERROR during test: {e}")
        import traceback
        traceback.print_exc()