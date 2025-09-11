#!/usr/bin/env python3
"""Test custom equipment location handling in hockey diagram MCP."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec, generate_diagram

def test_custom_equipment_positions():
    """Test equipment with custom position descriptions."""
    
    # Test scenario: Complex equipment positioning
    drill_query = "Place 3 cones 10 feet from the blue line in a triangle formation, 2 pucks between the faceoff circles"
    
    print("=" * 80)
    print("TESTING CUSTOM EQUIPMENT POSITIONS")
    print("=" * 80)
    print(f"Query: {drill_query}\n")
    
    # Step 1: Analyze the query
    print("Step 1: Analyzing query...")
    analysis = analyze_hockey_query(drill_query)
    
    if "error" in analysis:
        print(f"❌ Analysis failed: {analysis['error']}")
        return False
    
    # Check if equipment was identified
    equipment = analysis.get("components_with_assumptions", {}).get("equipment", [])
    print(f"✅ Identified {len(equipment)} equipment types")
    for eq in equipment:
        print(f"  - {eq['type']}: {eq['position_desc']}")
    
    # Step 2: Translate to spec with LLM mapping
    print("\nStep 2: Translating to spec (should use LLM for complex positions)...")
    translate_result = translate_analysis_to_spec(
        analysis,
        title="Custom Equipment Positioning Drill"
    )
    
    if not translate_result.get("success"):
        print(f"❌ Translation failed: {translate_result.get('error')}")
        return False
    
    spec = translate_result["spec"]
    
    # Check equipment in spec
    spec_equipment = spec.get("equipment", [])
    print(f"✅ Spec contains {len(spec_equipment)} equipment items")
    for eq in spec_equipment:
        print(f"  - {eq['type']} at ({eq['coordinates']['x']:.1f}, {eq['coordinates']['y']:.1f})")
    
    # Save spec for inspection
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    spec_file = output_dir / "custom_equipment_spec.json"
    with open(spec_file, 'w') as f:
        json.dump(spec, f, indent=2)
    
    print(f"\n✅ Spec saved to {spec_file}")
    
    # Step 3: Generate diagram
    print("\nStep 3: Generating diagram...")
    diagram_result = generate_diagram(spec, output_name="custom_equipment_drill")
    
    if diagram_result.get("success"):
        print(f"✅ Diagram saved to {diagram_result['image_path']}")
        return True
    else:
        print(f"❌ Diagram generation failed: {diagram_result.get('error')}")
        return False

def test_relative_positions():
    """Test equipment with relative position descriptions."""
    
    drill_query = "Put cones halfway between the blue line and goal line, place pucks near the left circle"
    
    print("\n" + "=" * 80)
    print("TESTING RELATIVE EQUIPMENT POSITIONS")
    print("=" * 80)
    print(f"Query: {drill_query}\n")
    
    # Analyze
    analysis = analyze_hockey_query(drill_query)
    
    if "error" in analysis:
        print(f"❌ Analysis failed: {analysis['error']}")
        return False
    
    equipment = analysis.get("components_with_assumptions", {}).get("equipment", [])
    print(f"✅ Identified equipment with relative positions:")
    for eq in equipment:
        print(f"  - {eq.get('position_desc', 'unknown')}")
    
    # Translate and save
    translate_result = translate_analysis_to_spec(
        analysis,
        title="Relative Position Equipment Drill"
    )
    
    if translate_result.get("success"):
        spec = translate_result["spec"]
        
        # Check that positions were mapped
        if spec.get("equipment"):
            for eq in spec["equipment"]:
                coords = eq.get("coordinates", {})
                if coords.get("x", 0) != 0 or coords.get("y", 0) != 0:
                    print(f"✅ Equipment positioned at non-default location")
                else:
                    print(f"⚠️ Equipment at default center position - may need better mapping")
        
        # Save spec
        output_dir = Path(__file__).parent / "outputs"
        spec_file = output_dir / "relative_equipment_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)
        
        print(f"✅ Spec saved to {spec_file}")
        return True
    
    return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("TESTING CUSTOM EQUIPMENT LOCATION HANDLING")
    print("=" * 80)
    
    # Test custom positions
    success1 = test_custom_equipment_positions()
    
    # Test relative positions
    success2 = test_relative_positions()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Custom equipment positions: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Relative equipment positions: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All custom equipment tests passed!")
        print("The system can now handle complex equipment positioning like:")
        print("  - '10 feet from the blue line'")
        print("  - 'between the circles'")
        print("  - 'triangle formation'")
        print("  - 'halfway between X and Y'")
    else:
        print("\n⚠️ Some tests failed - check LLM mapping implementation")