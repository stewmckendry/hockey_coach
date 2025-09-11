#!/usr/bin/env python3
"""Test equipment handling in hockey diagram MCP."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec, generate_diagram

def test_equipment_drill():
    """Test a drill that includes cones/pylons."""
    
    # Test scenario: Weaving drill with cones
    drill_query = "Players skate in a line weaving through 5 cones placed along the blue line, then take a shot on goal"
    
    print("=" * 80)
    print("TESTING EQUIPMENT DRILL")
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
    print(f"✅ Identified {len(equipment)} equipment items")
    for eq in equipment:
        print(f"  - {eq['type']}: {eq['position_desc']}")
    
    # Step 2: Translate to spec
    print("\nStep 2: Translating to spec...")
    translate_result = translate_analysis_to_spec(
        analysis,
        title="Cone Weaving Drill"
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
    
    spec_file = output_dir / "equipment_drill_spec.json"
    with open(spec_file, 'w') as f:
        json.dump(spec, f, indent=2)
    
    print(f"\n✅ Spec saved to {spec_file}")
    
    # Step 3: Generate diagram
    print("\nStep 3: Generating diagram...")
    diagram_result = generate_diagram(spec, output_name="equipment_drill")
    
    if diagram_result.get("success"):
        print(f"✅ Diagram saved to {diagram_result['image_path']}")
        print("\nElement counts:")
        for key, count in diagram_result["element_count"].items():
            print(f"  {key}: {count}")
    else:
        print(f"❌ Diagram generation failed: {diagram_result.get('error')}")
        return False
    
    return True

def test_multiple_equipment():
    """Test a drill with different types of equipment."""
    
    drill_query = "Set up 3 cones in the slot, 2 pucks at center ice, and have players skate around the cones then shoot the pucks"
    
    print("\n" + "=" * 80)
    print("TESTING MULTIPLE EQUIPMENT TYPES")
    print("=" * 80)
    print(f"Query: {drill_query}\n")
    
    # Analyze
    analysis = analyze_hockey_query(drill_query)
    
    if "error" in analysis:
        print(f"❌ Analysis failed: {analysis['error']}")
        return False
    
    # Check equipment variety
    equipment = analysis.get("components_with_assumptions", {}).get("equipment", [])
    equipment_types = set(eq['type'] for eq in equipment)
    print(f"✅ Identified {len(equipment_types)} equipment types: {equipment_types}")
    
    # Translate and save
    translate_result = translate_analysis_to_spec(
        analysis,
        title="Multi-Equipment Drill"
    )
    
    if translate_result.get("success"):
        spec = translate_result["spec"]
        
        # Save and generate
        output_dir = Path(__file__).parent / "outputs"
        spec_file = output_dir / "multi_equipment_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)
        
        print(f"✅ Spec saved to {spec_file}")
        
        # Generate diagram
        diagram_result = generate_diagram(spec, output_name="multi_equipment_drill")
        if diagram_result.get("success"):
            print(f"✅ Diagram saved to {diagram_result['image_path']}")
        
        return True
    
    return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("TESTING EQUIPMENT HANDLING IN HOCKEY DIAGRAMS")
    print("=" * 80)
    
    # Test basic cone drill
    success1 = test_equipment_drill()
    
    # Test multiple equipment types
    success2 = test_multiple_equipment()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Basic equipment drill: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Multiple equipment types: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All equipment tests passed!")
    else:
        print("\n⚠️ Some tests failed - check equipment handling")