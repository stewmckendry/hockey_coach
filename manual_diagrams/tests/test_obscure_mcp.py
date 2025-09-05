#!/usr/bin/env python3
"""Test with an obscure query to trigger MCP and dump response."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from servers.hockey_diagram_mcp_v3 import analyze_hockey_query
from pathlib import Path

# Use a very obscure/unusual term
query = "Zegras Michigan alley-oop play setup"

print(f"Testing obscure query: {query}")
print("This should trigger MCP search for 'Zegras Michigan alley-oop'")
print("-" * 60)

# Analyze with MCP
result = analyze_hockey_query(query, use_exa_mcp=True)

if result.get("error"):
    print(f"❌ Error: {result.get('error')}")
else:
    # Save response
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "mcp_zegras_response.json"
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Saved to: {output_file}")
    
    # Check MCP usage
    mcp_calls = result.get('mcp_calls', [])
    print(f"\nMCP calls made: {len(mcp_calls)}")
    if mcp_calls:
        print("MCP was triggered! Tool calls:")
        for call in mcp_calls:
            print(f"  - {call.get('type', 'unknown')}: {call.get('details', '')[:100]}")
    
    # Print key fields
    print("\nJSON Response Structure:")
    print(json.dumps(result, indent=2)[:2000])  # First 2000 chars
    
    # Check movements
    print("\nMovement Analysis:")
    movements = result.get('components_with_assumptions', {}).get('movements', [])
    for i, mov in enumerate(movements):
        print(f"Movement {i+1}:")
        print(f"  type: {mov.get('type')}")
        print(f"  from_player: {mov.get('from_player')}")
        print(f"  to_player: {mov.get('to_player', 'N/A')}")
        print(f"  to_area: {mov.get('to_area')}")