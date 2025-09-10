#!/usr/bin/env python3
"""Debug what analyze_hockey_query returns for complex scenarios."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import analyze_hockey_query

def debug_scenario(query):
    """Show what analyze returns."""
    
    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print(f"{'='*80}")
    
    # Analyze query
    result = analyze_hockey_query(query)
    
    if "error" in result:
        print(f"❌ Analysis failed: {result.get('error')}")
        return
    
    # Extract components
    components = result.get("components_with_assumptions", {})
    movements = components.get("movements", [])
    
    print("\nMOVEMENTS FROM ANALYSIS:")
    print("-" * 60)
    for m in movements:
        print(f"\nMovement {m['id']}:")
        print(f"  Type: {m['type']}")
        print(f"  From Player: {m.get('from_player', 'NOT SPECIFIED')}")
        print(f"  To Area: {m.get('to_area', 'NOT SPECIFIED')}")
        print(f"  To Player: {m.get('to_player', 'NOT SPECIFIED')}")  
        print(f"  Description: {m['desc']}")
        print(f"  Assumption: {m.get('assumption', 'none')}")
    
    # Save for inspection
    output_file = Path(__file__).parent / "outputs" / f"debug_analysis_{query[:20].replace(' ', '_')}.json"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n📄 Full analysis saved to: {output_file}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test the problematic scenarios
    scenarios = [
        "Forwards cycle the puck in the offensive zone",
        "Goalie passes to defenseman who breaks out to winger"
    ]
    
    for scenario in scenarios:
        debug_scenario(scenario)