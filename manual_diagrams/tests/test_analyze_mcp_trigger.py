#!/usr/bin/env python3
"""Test analyze_hockey_query with a query that should trigger MCP."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from servers.hockey_diagram_mcp_v3 import analyze_hockey_query

def test_mcp_trigger():
    """Test with query that should trigger MCP search."""
    
    print("=" * 80)
    print("Testing: Analyze with MCP Trigger Query")
    print("=" * 80)
    
    # Query with unfamiliar term that should trigger search
    query = "Torpedo system neutral zone regroup with stretch pass"
    
    print(f"\n1. Analyzing query: {query}")
    print("   This should trigger Exa MCP search for 'Torpedo system'...")
    
    # Analyze with MCP enabled
    result = analyze_hockey_query(query, use_exa_mcp=True)
    
    if result.get("error"):
        print(f"\n❌ Analysis failed: {result.get('error')}")
        if result.get("debug"):
            print("\nDebug info:")
            print(json.dumps(result.get("debug"), indent=2))
        return None
    
    print(f"\n✅ Analysis successful!")
    print(f"   API used: {result.get('api_used', 'unknown')}")
    print(f"   MCP tools called: {len(result.get('mcp_calls', []))}")
    
    # Check if MCP was actually used
    if result.get('mcp_calls'):
        print("\n   MCP calls made:")
        for call in result.get('mcp_calls', []):
            print(f"   - {call.get('type')}: {call.get('details', '')[:100]}")
    
    # Show components
    components = result.get("components_with_assumptions", {})
    print(f"\n2. Components extracted:")
    print(f"   Players: {len(components.get('players', []))}")
    print(f"   Movements: {len(components.get('movements', []))}")
    
    # Check if torpedo system was properly analyzed
    print("\n3. Analysis details:")
    explicit = result.get("explicit_info", {})
    print(f"   Zone: {explicit.get('zone')}")
    print(f"   Key actions: {explicit.get('key_actions', [])}")
    
    # Show metadata
    metadata = result.get("metadata", {})
    print(f"\n4. Metadata:")
    print(f"   Type: {metadata.get('type')}")
    print(f"   Phase: {metadata.get('phase')}")
    
    return result

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    result = test_mcp_trigger()
    
    if result:
        print("\n" + "=" * 80)
        if result.get('mcp_calls'):
            print("✅ MCP was triggered and used successfully!")
        else:
            print("⚠️ MCP was not triggered - model may have had sufficient knowledge")
        print("=" * 80)