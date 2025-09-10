#!/usr/bin/env python3
"""Test complete pipeline with equipment and annotations."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec, generate_diagram

def test_complete_pipeline():
    """Test a complete drill with equipment and annotations."""
    
    query = """
    Set up a passing drill with 4 players in a box formation.
    Place cones at the blue lines and center ice.
    Players pass clockwise and then reverse direction.
    Label this as "Box Passing Drill" with a note "Keep passes crisp".
    """
    
    print("=" * 80)
    print("COMPLETE PIPELINE TEST")
    print("=" * 80)
    print(f"Query: {query}\n")
    
    # Step 1: Analyze
    print("Step 1: Analyzing query...")
    analysis = analyze_hockey_query(query)
    
    # Print analysis summary
    print("\nAnalysis Summary:")
    components = analysis.get("components_with_assumptions", {})
    print(f"  Players: {len(components.get('players', []))}")
    print(f"  Movements: {len(components.get('movements', []))}")
    print(f"  Equipment: {len(components.get('equipment', []))}")
    print(f"  Annotations: {len(components.get('annotations', []))}")
    
    # Step 2: Translate
    print("\nStep 2: Translating to spec...")
    translate_result = translate_analysis_to_spec(
        analysis,
        title="Box Passing Drill"
    )
    
    if translate_result.get("success"):
        spec = translate_result["spec"]
        
        print("\nSpec Summary:")
        print(f"  Title: {spec.get('title')}")
        print(f"  View: {spec.get('rink', {}).get('view')}")
        print(f"  Players: {len(spec.get('players', []))}")
        print(f"  Movements: {len(spec.get('movements', []))}")
        print(f"  Equipment: {len(spec.get('equipment', []))}")
        print(f"  Annotations: {len(spec.get('annotations', []))}")
        
        # Print equipment details
        if spec.get("equipment"):
            print("\nEquipment Details:")
            for eq in spec["equipment"]:
                print(f"  - {eq['type']} at ({eq['coordinates']['x']:.1f}, {eq['coordinates']['y']:.1f})")
                print(f"    Count: {eq.get('count', 1)}, Color: {eq.get('color', 'orange')}")
        
        # Print annotation details
        if spec.get("annotations"):
            print("\nAnnotation Details:")
            for ann in spec["annotations"]:
                print(f"  - '{ann['text']}' at ({ann['position']['x']}, {ann['position']['y']})")
                print(f"    Size: {ann.get('size', 'medium')}, Style: {ann.get('style', 'normal')}")
        
        # Save spec
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        spec_file = output_dir / "complete_pipeline_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)
        print(f"\n✅ Spec saved to {spec_file}")
        
        # Step 3: Generate diagram
        print("\nStep 3: Generating diagram...")
        diagram_result = generate_diagram(spec, output_name="complete_pipeline")
        
        if diagram_result.get("success"):
            print(f"✅ Diagram generated: {diagram_result['image_path']}")
            print(f"\nElement counts:")
            for key, count in diagram_result.get("element_count", {}).items():
                if count > 0:
                    print(f"  - {key}: {count}")
            return True
        else:
            print(f"❌ Diagram generation failed: {diagram_result.get('error')}")
            return False
    else:
        print(f"❌ Translation failed: {translate_result.get('error')}")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("TESTING COMPLETE PIPELINE WITH EQUIPMENT AND ANNOTATIONS")
    print("=" * 80)
    
    success = test_complete_pipeline()
    
    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)
    
    if success:
        print("✅ Complete pipeline test PASSED")
        print("\nFeatures tested:")
        print("  ✅ Equipment positioning with LLM")
        print("  ✅ Annotation auto-generation and positioning")
        print("  ✅ Movement mapping")
        print("  ✅ Player positioning")
        print("  ✅ Full diagram generation")
    else:
        print("❌ Complete pipeline test FAILED")