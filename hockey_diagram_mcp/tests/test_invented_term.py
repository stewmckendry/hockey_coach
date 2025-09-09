#!/usr/bin/env python3
"""Test with invented hockey term to force MCP trigger."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from servers.hockey_diagram_mcp_v3 import analyze_hockey_query
from pathlib import Path

# Use completely invented terms that don't exist
query = "Zamboni weave pattern with quantum deke finish"

print(f"Testing invented query: {query}")
print("This MUST trigger MCP search since 'quantum deke' doesn't exist")
print("-" * 60)

# Analyze with MCP
result = analyze_hockey_query(query, use_exa_mcp=True)

if result.get("error"):
    print(f"❌ Error: {result.get('error')}")
    if result.get("debug"):
        print("Debug info:")
        print(json.dumps(result.get("debug"), indent=2))
else:
    # Save response
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "mcp_invented_response.json"
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Saved to: {output_file}")
    
    # Check MCP usage
    mcp_calls = result.get('mcp_calls', [])
    print(f"\n{'='*60}")
    print(f"MCP ANALYSIS:")
    print(f"MCP calls made: {len(mcp_calls)}")
    
    if mcp_calls:
        print("🎯 MCP WAS TRIGGERED! Details:")
        for i, call in enumerate(mcp_calls, 1):
            print(f"\nCall {i}:")
            print(f"  Type: {call.get('type', 'unknown')}")
            details = call.get('details', '')
            if details:
                print(f"  Details preview: {details[:200]}...")
    else:
        print("⚠️ MCP was NOT triggered - model attempted to handle unknown terms")
    
    # Show the full response
    print(f"\n{'='*60}")
    print("FULL JSON RESPONSE:")
    print(json.dumps(result, indent=2))
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    comp = result.get('components_with_assumptions', {})
    print(f"- Players: {len(comp.get('players', []))}")
    print(f"- Movements: {len(comp.get('movements', []))}")
    print(f"- API used: {result.get('api_used')}")
    print(f"- Response ID: {result.get('response_id', 'N/A')[:30]}...")