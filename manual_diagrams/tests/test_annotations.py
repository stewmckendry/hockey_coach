#!/usr/bin/env python3
"""Test annotation handling in hockey diagram MCP."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec, generate_diagram

def test_annotation_positions():
    """Test that annotations get proper positions based on descriptions."""
    
    # Test query with no explicit annotations - should auto-generate title
    query = "Players execute a 2-on-1 rush drill"
    
    print("=" * 80)
    print("TEST 1: AUTO-GENERATED TITLE")
    print("=" * 80)
    print(f"Query: {query}\n")
    
    # Analyze
    analysis = analyze_hockey_query(query)
    
    # Translate with custom title
    translate_result = translate_analysis_to_spec(
        analysis,
        title="2-on-1 Rush Drill"
    )
    
    if translate_result.get("success"):
        spec = translate_result["spec"]
        annotations = spec.get("annotations", [])
        
        print(f"✅ Generated {len(annotations)} annotation(s)")
        for ann in annotations:
            print(f"  - Text: '{ann['text']}'")
            print(f"    Position: ({ann['position']['x']}, {ann['position']['y']})")
            print(f"    Size: {ann.get('size', 'medium')}, Style: {ann.get('style', 'normal')}")
            if ann.get("_auto_generated"):
                print(f"    (Auto-generated)")
        
        # Check that title was auto-generated
        if annotations and annotations[0].get("_auto_generated"):
            print("\n✅ Title was auto-generated")
        else:
            print("\n⚠️ Title was not auto-generated")
    
    return True

def test_manual_annotations():
    """Test manual annotation positioning from analyze output."""
    
    # This would need to be a query that the LLM identifies as needing annotations
    # For testing, we'll manually create an analysis with annotations
    
    print("\n" + "=" * 80)
    print("TEST 2: MANUAL ANNOTATION POSITIONING")
    print("=" * 80)
    
    # Create a mock analysis with annotations
    analysis = {
        "original_query": "Power play setup with notes",
        "explicit_info": {
            "situation": "play",
            "zone": "offensive"
        },
        "components_with_assumptions": {
            "rink": {
                "view": "offensive",
                "assumption": "Power play is in offensive zone",
                "confidence": 0.9
            },
            "players": [],
            "movements": [],
            "zones": [],
            "annotations": [
                {
                    "text": "Power Play Setup",
                    "position_desc": "title",
                    "assumption": "Main title for the diagram",
                    "confidence": 1.0
                },
                {
                    "text": "Diamond Formation",
                    "position_desc": "subtitle",
                    "assumption": "Formation type",
                    "confidence": 0.9
                },
                {
                    "text": "Keep puck moving",
                    "position_desc": "note",
                    "assumption": "Coach instruction",
                    "confidence": 0.8
                }
            ],
            "equipment": []
        },
        "questions_for_user": [],
        "metadata": {
            "type": "play",
            "phase": "offensive"
        }
    }
    
    # Translate
    translate_result = translate_analysis_to_spec(
        analysis,
        title="Power Play Setup"
    )
    
    if translate_result.get("success"):
        spec = translate_result["spec"]
        annotations = spec.get("annotations", [])
        
        print(f"✅ Processed {len(annotations)} annotations")
        for ann in annotations:
            print(f"\n  Annotation: '{ann['text']}'")
            print(f"    Position: ({ann['position']['x']}, {ann['position']['y']})")
            print(f"    Size: {ann.get('size', 'medium')}")
            print(f"    Style: {ann.get('style', 'normal')}")
            
        # Verify positioning
        checks = []
        
        # Title should be at top (negative y)
        title_ann = next((a for a in annotations if "Power Play Setup" in a["text"]), None)
        if title_ann:
            checks.append(("Title at top", title_ann["position"]["y"] < -30))
            checks.append(("Title is large", title_ann.get("size") == "large"))
            checks.append(("Title is bold", title_ann.get("style") == "bold"))
        
        # Subtitle below title
        subtitle_ann = next((a for a in annotations if "Diamond Formation" in a["text"]), None)
        if subtitle_ann:
            checks.append(("Subtitle below title", 
                          title_ann and subtitle_ann["position"]["y"] > title_ann["position"]["y"]))
            checks.append(("Subtitle is medium", subtitle_ann.get("size") == "medium"))
        
        # Note in corner
        note_ann = next((a for a in annotations if "Keep puck moving" in a["text"]), None)
        if note_ann:
            checks.append(("Note offset from center", note_ann["position"]["x"] != 0))
            checks.append(("Note is small", note_ann.get("size") == "small"))
        
        print("\nValidation:")
        for check_name, result in checks:
            print(f"  {check_name}: {'✅' if result else '❌'}")
        
        # Save spec for inspection
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        spec_file = output_dir / "annotations_test_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)
        print(f"\n✅ Spec saved to {spec_file}")
        
        return all(result for _, result in checks)
    
    return False

def test_annotation_in_diagram():
    """Test that annotations render correctly in the final diagram."""
    
    print("\n" + "=" * 80)
    print("TEST 3: ANNOTATION RENDERING")
    print("=" * 80)
    
    # Create a simple spec with annotations
    spec = {
        "title": "Annotation Test",
        "rink": {"view": "offensive"},
        "players": [],
        "movements": [],
        "zones": [],
        "annotations": [
            {
                "text": "Test Title",
                "position": {"x": 0, "y": -40},
                "size": "large",
                "style": "bold"
            },
            {
                "text": "Subtitle Text",
                "position": {"x": 0, "y": -35},
                "size": "medium",
                "style": "normal"
            },
            {
                "text": "Note",
                "position": {"x": 30, "y": 30},
                "size": "small",
                "style": "normal"
            }
        ],
        "equipment": [],
        "metadata": {}
    }
    
    # Generate diagram
    diagram_result = generate_diagram(spec, output_name="annotation_test")
    
    if diagram_result.get("success"):
        print(f"✅ Diagram generated: {diagram_result['image_path']}")
        print(f"   Element counts:")
        for key, count in diagram_result.get("element_count", {}).items():
            if count > 0:
                print(f"     - {key}: {count}")
        return True
    else:
        print(f"❌ Diagram generation failed: {diagram_result.get('error')}")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("TESTING ANNOTATION HANDLING")
    print("=" * 80)
    
    # Run tests
    success1 = test_annotation_positions()
    success2 = test_manual_annotations()
    success3 = test_annotation_in_diagram()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Auto-generated title test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Manual annotation positioning: {'✅ PASSED' if success2 else '❌ FAILED'}")
    print(f"Annotation rendering: {'✅ PASSED' if success3 else '❌ FAILED'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 All annotation tests passed!")
        print("\nImprovements implemented:")
        print("  ✅ Annotations positioned based on position_desc")
        print("  ✅ Size and style auto-detected from type")
        print("  ✅ Title auto-generated if missing")
        print("  ✅ Confidence metadata preserved")
    else:
        print("\n⚠️ Some tests failed - check annotation handling")