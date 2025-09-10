#!/usr/bin/env python3
"""Dump single JSON response from MCP analysis to verify fields."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from servers.hockey_diagram_mcp_v3 import analyze_hockey_query
from pathlib import Path

def dump_single_response():
    """Test one MCP query and dump full response."""
    
    query = "Torpedo system neutral zone regroup with stretch pass"
    
    print(f"Testing: {query}")
    print("-" * 60)
    
    # Analyze with MCP enabled
    result = analyze_hockey_query(query, use_exa_mcp=True)
    
    if result.get("error"):
        print(f"❌ Error: {result.get('error')}")
        return
    
    # Save full JSON
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "mcp_torpedo_response.json"
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Saved to: {output_file}")
    
    # Print the full JSON to console for inspection
    print("\nFull JSON Response:")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    
    # Quick field check
    print("\n" + "=" * 60)
    print("Field Check:")
    print(f"- Players: {len(result.get('components_with_assumptions', {}).get('players', []))}")
    print(f"- Movements: {len(result.get('components_with_assumptions', {}).get('movements', []))}")
    print(f"- MCP calls made: {len(result.get('mcp_calls', []))}")
    
    # Check movement to_player fields
    movements = result.get('components_with_assumptions', {}).get('movements', [])
    for i, mov in enumerate(movements):
        print(f"\nMovement {i+1}:")
        print(f"  type: {mov.get('type')}")
        print(f"  from_player: {mov.get('from_player')}")
        print(f"  to_player: {mov.get('to_player', 'N/A')}")
        print(f"  to_area: {mov.get('to_area')}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    dump_single_response()