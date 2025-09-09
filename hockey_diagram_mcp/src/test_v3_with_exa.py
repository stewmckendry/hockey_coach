#!/usr/bin/env python3
"""
Test script for v3 MCP server with Exa integration.
This demonstrates how the analyze_hockey_query tool will work with Exa MCP.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

def test_analyze_hockey_query():
    """Test the analyze_hockey_query tool with various queries."""
    
    print("🏒 Testing Hockey Diagram MCP v3 with Exa Integration")
    print("=" * 60)
    
    # Test queries
    test_cases = [
        {
            "name": "Standard faceoff",
            "query": "offensive zone faceoff at right dot, bump back to weak side winger who shoots",
            "use_exa": True
        },
        {
            "name": "Unfamiliar term",
            "query": "set up a Michigan move play in the offensive zone",
            "use_exa": True
        },
        {
            "name": "Without search",
            "query": "2v1 rush drill starting at center ice",
            "use_exa": False
        }
    ]
    
    for test in test_cases:
        print(f"\n📋 Test: {test['name']}")
        print(f"Query: {test['query']}")
        print(f"Use Exa: {test['use_exa']}")
        print("-" * 40)
        
        # Simulate calling the MCP tool
        print("Would call: analyze_hockey_query(")
        print(f"    query='{test['query']}',")
        print(f"    use_exa_mcp={test['use_exa']}")
        print(")")
        
        # Expected behavior
        if test['use_exa']:
            print("\n✅ Expected: LLM can use web_search_exa for unfamiliar terms")
            print("   - If 'Michigan move' is unfamiliar, search for it")
            print("   - If 'weak side' needs clarification, search for it")
        else:
            print("\n⚠️ Expected: LLM uses only built-in hockey knowledge")
    
    print("\n" + "=" * 60)
    print("📝 Implementation Notes:")
    print("1. The MCP tool receives the query")
    print("2. It prepares an OpenAI API call with:")
    print("   - System/user prompts from config file")
    print("   - Exa MCP server in tools array (if enabled)")
    print("3. OpenAI Responses API handles MCP communication")
    print("4. LLM can call web_search_exa directly when needed")
    print("5. Final JSON response includes all diagram components")
    
    print("\n🚀 When Responses API is available:")
    print("   client.responses.create() will handle MCP tools directly")
    print("   No custom code needed for tool orchestration")

if __name__ == "__main__":
    test_analyze_hockey_query()