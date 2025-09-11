#!/usr/bin/env python3
"""Test with queries that should definitely trigger MCP and dump response."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from servers.hockey_diagram_mcp_v3 import analyze_hockey_query
from pathlib import Path

def test_mcp_triggers():
    """Test with obscure/invented terms that should trigger MCP search."""
    
    # Queries with terms that should trigger searches
    test_queries = [
        "Svechnikov lacrosse move behind the net",  # Specific modern move
        "Kucherov no-look saucer pass setup",  # Specific player technique
        "Flying V formation breakout",  # Mighty Ducks reference
        "Forsberg deke shooting drill",  # Specific deke style
        "Zorro mask celebration goal play"  # Very unusual term
    ]
    
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {query}")
        print("-" * 60)
        
        # Analyze with MCP enabled
        result = analyze_hockey_query(query, use_exa_mcp=True)
        
        if result.get("error"):
            print(f"❌ Error: {result.get('error')}")
            continue
        
        # Check if MCP was called
        mcp_calls = result.get('mcp_calls', [])
        print(f"✅ Analysis complete")
        print(f"   MCP calls made: {len(mcp_calls)}")
        
        if mcp_calls:
            print("   MCP tool calls:")
            for call in mcp_calls:
                print(f"   - {call.get('type', 'unknown')}")
        
        # Save if MCP was triggered
        if mcp_calls:
            output_file = output_dir / f"mcp_triggered_{i}_{query[:20].replace(' ', '_')}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"   📄 Saved to: {output_file.name}")
            
            # Show key parts of response
            print("\n   Key Response Fields:")
            print(f"   - API used: {result.get('api_used')}")
            print(f"   - Players: {len(result.get('components_with_assumptions', {}).get('players', []))}")
            print(f"   - Movements: {len(result.get('components_with_assumptions', {}).get('movements', []))}")
            
            # Check movements for to_player
            movements = result.get('components_with_assumptions', {}).get('movements', [])
            for j, mov in enumerate(movements[:2]):  # Show first 2
                print(f"\n   Movement {j+1}:")
                print(f"     type: {mov.get('type')}")
                print(f"     from_player: {mov.get('from_player')}")
                print(f"     to_player: {mov.get('to_player', 'N/A')}")
                print(f"     to_area: {mov.get('to_area')}")
            
            # Show first 100 chars of the analysis to see if search influenced it
            orig_query = result.get('original_query', '')
            if orig_query:
                print(f"\n   Analysis incorporated search: {orig_query[:100]}...")
            
            return result  # Return first successful MCP trigger
        else:
            print("   ℹ️ MCP not triggered - model had sufficient knowledge")
    
    print("\n" + "="*60)
    print("⚠️ None of the queries triggered MCP. Model may have comprehensive knowledge.")
    return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    result = test_mcp_triggers()
    
    if result and result.get('mcp_calls'):
        print("\n" + "="*60)
        print("✅ Successfully triggered and captured MCP response!")
        print("Check outputs/ directory for full JSON with MCP integration.")
    else:
        print("\n" + "="*60)
        print("💡 Try more obscure or invented terms to trigger MCP search.")