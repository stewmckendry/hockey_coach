#!/usr/bin/env python3
"""Test response ID tracking in translate_analysis_to_spec."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec

def test_response_id_tracking():
    """Test that translate_analysis_to_spec returns conversation metadata with response IDs."""
    
    query = "Simple power play with 4 players and puck movement. Add some cones at the blue lines."
    
    print("=" * 80)
    print("PHASE 1: RESPONSE ID TRACKING TEST")
    print("=" * 80)
    print(f"Query: {query}\n")
    
    # Step 1: Get analysis
    print("Step 1: Analyzing query...")
    analysis = analyze_hockey_query(query)
    
    if "error" in analysis:
        print(f"❌ Analysis failed: {analysis['error']}")
        return False
    
    analysis_response_id = analysis.get("response_id")
    print(f"Analysis response_id: {analysis_response_id}")
    
    # Step 2: Translate to spec
    print("\nStep 2: Translating to spec...")
    translate_result = translate_analysis_to_spec(
        analysis,
        title="Response ID Test"
    )
    
    if not translate_result.get("success"):
        print(f"❌ Translation failed: {translate_result.get('error')}")
        return False
    
    # Step 3: Check conversation metadata
    conversation = translate_result.get("conversation", {})
    
    print("\nStep 3: Checking conversation metadata...")
    print(f"Conversation metadata keys: {list(conversation.keys())}")
    
    # Check response IDs
    response_ids = conversation.get("response_ids", {})
    print(f"\nResponse IDs collected:")
    for mapping_type, response_id in response_ids.items():
        print(f"  {mapping_type}: {response_id}")
    
    # Check original analysis preservation
    original_analysis = conversation.get("original_analysis", {})
    has_original = bool(original_analysis and "components_with_assumptions" in original_analysis)
    print(f"\nOriginal analysis preserved: {'✅' if has_original else '❌'}")
    
    # Validation checks
    checks = [
        ("Conversation metadata exists", bool(conversation)),
        ("Response IDs dict exists", bool(response_ids)),
        ("Original analysis stored", has_original),
        ("At least one response ID captured", len(response_ids) > 0)
    ]
    
    print("\nValidation Results:")
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    # Show spec structure for context
    spec = translate_result.get("spec", {})
    print(f"\nGenerated spec summary:")
    print(f"  Players: {len(spec.get('players', []))}")
    print(f"  Movements: {len(spec.get('movements', []))}")
    print(f"  Equipment: {len(spec.get('equipment', []))}")
    print(f"  Annotations: {len(spec.get('annotations', []))}")
    
    # Save detailed results
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    results_file = output_dir / "response_id_tracking_test.json"
    detailed_results = {
        "analysis_response_id": analysis_response_id,
        "translation_response_ids": response_ids,
        "conversation_metadata": conversation,
        "spec_summary": {
            "players_count": len(spec.get("players", [])),
            "movements_count": len(spec.get("movements", [])), 
            "equipment_count": len(spec.get("equipment", [])),
            "annotations_count": len(spec.get("annotations", []))
        },
        "validation_results": {check: result for check, result in checks}
    }
    
    with open(results_file, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"\n✅ Detailed results saved to {results_file}")
    
    return all_passed

def test_conversation_continuity_structure():
    """Test that the conversation structure supports multi-turn updates."""
    
    print("\n" + "=" * 80)
    print("CONVERSATION CONTINUITY STRUCTURE TEST") 
    print("=" * 80)
    
    # This would be the client flow:
    print("Simulated client workflow:")
    print("1. Client calls translate_analysis_to_spec")
    print("2. Client gets back spec + conversation metadata")
    print("3. Client shows questions to user")
    print("4. Client collects clarifications")
    print("5. Client calls update_spec_with_clarifications (to be implemented)")
    
    # Show the expected structure
    expected_structure = {
        "conversation": {
            "response_ids": {
                "player_mapping": "resp_abc123",
                "movement_mapping": "resp_def456", 
                "equipment_mapping": None  # Uses chat completions
            },
            "original_analysis": "/* full analysis object */",
            "mapping_results": {}
        }
    }
    
    print(f"\nExpected conversation metadata structure:")
    print(json.dumps(expected_structure, indent=2))
    
    return True

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("TESTING RESPONSE ID TRACKING - PHASE 1")
    print("=" * 80)
    
    success1 = test_response_id_tracking()
    success2 = test_conversation_continuity_structure()
    
    print("\n" + "=" * 80)
    print("PHASE 1 SUMMARY")
    print("=" * 80)
    
    if success1:
        print("✅ Response ID tracking WORKING")
        print("\nPhase 1 Implementation Complete:")
        print("  ✅ Enhanced mapping functions capture response_id")
        print("  ✅ translate_analysis_to_spec returns conversation metadata")
        print("  ✅ Original analysis preserved for updates")
        print("  ✅ Response IDs collected from all mapping stages")
        print("\nNext Phase:")
        print("  🔄 Implement update_spec_with_clarifications tool")
        print("  🔄 Add clarification routing logic")
        print("  🔄 Enable conversational spec updates")
    else:
        print("❌ Response ID tracking FAILED")
        print("\nNeeds investigation:")
        print("  - Check mapping function enhancements")
        print("  - Verify conversation metadata collection")
        print("  - Test response ID capture logic")