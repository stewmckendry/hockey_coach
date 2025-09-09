#!/usr/bin/env python3
"""Test v3 pipeline with analyze -> translate -> validate flow."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec
from hockey_diagram_mcp_v2 import validate_diagram_spec_full, generate_diagram

def test_pipeline():
    """Test the full v3 pipeline."""
    
    # Test query
    query = "2v1 drill - F1 passes to F2 who drives to the net"
    
    print("=" * 80)
    print("TESTING V3 PIPELINE")
    print("=" * 80)
    print(f"Query: {query}\n")
    
    # Step 1: Analyze query
    print("Step 1: Analyzing query...")
    analysis_result = analyze_hockey_query(query)
    
    if "error" in analysis_result:
        print(f"❌ Analysis failed: {analysis_result.get('error')}")
        return
    
    # Count players and movements from the actual result
    player_count = len(analysis_result.get("components_with_assumptions", {}).get("players", []))
    movement_count = len(analysis_result.get("components_with_assumptions", {}).get("movements", []))
    
    print(f"✅ Analysis complete:")
    print(f"   - Players: {player_count}")
    print(f"   - Movements: {movement_count}")
    
    # Step 2: Translate to spec
    print("\nStep 2: Translating to spec...")
    translate_result = translate_analysis_to_spec(
        analysis_result,  # Pass the whole analysis result
        title="2v1 Passing Drill"
    )
    
    if not translate_result.get("success"):
        print(f"❌ Translation failed: {translate_result.get('error')}")
        return
    
    spec = translate_result["spec"]
    print(f"✅ Translation complete:")
    print(f"   - Players in spec: {len(spec.get('players', []))}")
    print(f"   - Movements in spec: {len(spec.get('movements', []))}")
    
    # Show movement structure
    if spec.get("movements"):
        print("\nMovement structure check:")
        for i, mov in enumerate(spec["movements"]):
            print(f"\nMovement {i+1}:")
            print(f"  Type: {mov.get('type')}")
            print(f"  From: {mov.get('from')} (should be {{x,y}} object)")
            print(f"  To: {mov.get('to')} (should be {{x,y}} object)")
            if mov.get("waypoints"):
                print(f"  Waypoints: {len(mov['waypoints'])} points")
                print(f"    First waypoint: {mov['waypoints'][0]} (should be {{x,y}} object)")
    
    # Step 3: Validate spec
    print("\nStep 3: Validating spec...")
    validation_result = validate_diagram_spec_full(spec, query, use_llm=False)
    
    print(f"\n{'✅' if validation_result['valid'] else '❌'} Validation result:")
    print(f"   - Structure valid: {validation_result.get('structure_valid')}")
    print(f"   - Spatial valid: {validation_result.get('spatial_valid')}")
    print(f"   - Hockey sense valid: {validation_result.get('hockey_sense_valid')}")
    
    if validation_result.get("issues"):
        print(f"   - Issues: {validation_result['issues']}")
    if validation_result.get("warnings"):
        print(f"   - Warnings: {validation_result['warnings']}")
    
    # Step 4: Generate diagram (if valid)
    if validation_result["valid"]:
        print("\nStep 4: Generating diagram...")
        diagram_result = generate_diagram(spec)
        
        if diagram_result.get("success"):
            print(f"✅ Diagram generated successfully!")
            print(f"   - Output file: {diagram_result.get('file_path')}")
            print(f"   - Elements: {diagram_result.get('element_count', {})}")
        else:
            print(f"❌ Diagram generation failed: {diagram_result.get('error')}")
    else:
        print("\n⚠️ Skipping diagram generation due to validation errors")
    
    # Save spec for inspection
    output_file = Path(__file__).parent / "outputs" / "test_v3_spec.json"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(spec, f, indent=2)
    print(f"\n📄 Spec saved to: {output_file}")
    
    print("\n" + "=" * 80)
    print("PIPELINE TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in environment")
        sys.exit(1)
    
    test_pipeline()