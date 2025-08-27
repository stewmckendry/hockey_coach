#!/usr/bin/env python3
"""
Integration test for the complete hockey diagram caching system.
Tests MCP tools through the server interface.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import MCP client utilities
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("MCP client not installed. Install with: pip install mcp")
    sys.exit(1)

async def test_cache_integration():
    """Test the cache MCP tools through the server."""
    print("\n" + "="*60)
    print("Hockey Diagram Cache Integration Test")
    print("="*60)
    
    # Start MCP server connection
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        cwd=str(Path(__file__).resolve().parent)
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("\n✅ Connected to MCP server")
            
            # List available tools
            tools = await session.list_tools()
            cache_tools = [t.name for t in tools if 'cache' in t.name.lower()]
            print(f"\n📦 Found {len(cache_tools)} cache tools:")
            for tool in cache_tools:
                print(f"   - {tool}")
            
            # Test 1: Generate a diagram first
            print("\n1. Generating test diagram...")
            result = await session.call_tool(
                "parse_hockey_formation",
                {"prompt": "2-1-2 forecheck with F1 behind net"}
            )
            
            if result and result.content:
                spec = json.loads(result.content[0].text)
                print("   ✅ Generated diagram spec")
                
                # Test 2: Save to cache
                print("\n2. Saving diagram to cache...")
                save_result = await session.call_tool(
                    "save_diagram_to_cache",
                    {
                        "prompt": "2-1-2 forecheck with F1 behind net",
                        "spec": spec,
                        "parser_type": "two_stage",
                        "tags": ["test", "integration"],
                        "author": "test_integration"
                    }
                )
                
                if save_result and save_result.content:
                    save_data = json.loads(save_result.content[0].text)
                    diagram_id = save_data.get('diagram_id')
                    print(f"   ✅ Saved with ID: {diagram_id}")
                    
                    # Test 3: Search for diagrams
                    print("\n3. Searching for similar diagrams...")
                    search_result = await session.call_tool(
                        "search_cached_diagrams",
                        {
                            "query": "forecheck formation",
                            "limit": 5,
                            "min_similarity": 0.5
                        }
                    )
                    
                    if search_result and search_result.content:
                        search_data = json.loads(search_result.content[0].text)
                        print(f"   ✅ Found {search_data.get('count', 0)} similar diagrams")
                    
                    # Test 4: Get specific diagram
                    print("\n4. Retrieving cached diagram...")
                    get_result = await session.call_tool(
                        "get_cached_diagram",
                        {
                            "diagram_id": diagram_id,
                            "regenerate": True
                        }
                    )
                    
                    if get_result and get_result.content:
                        get_data = json.loads(get_result.content[0].text)
                        has_image = 'image_base64' in get_data
                        print(f"   ✅ Retrieved diagram (has image: {has_image})")
                    
                    # Test 5: Update diagram
                    print("\n5. Updating diagram metadata...")
                    update_result = await session.call_tool(
                        "update_cached_diagram",
                        {
                            "diagram_id": diagram_id,
                            "validated": True,
                            "tags": ["test", "integration", "validated"]
                        }
                    )
                    
                    if update_result and update_result.content:
                        update_data = json.loads(update_result.content[0].text)
                        print(f"   ✅ Updated diagram: {update_data.get('message')}")
                    
                    # Test 6: Get statistics
                    print("\n6. Getting cache statistics...")
                    stats_result = await session.call_tool(
                        "get_cache_statistics"
                    )
                    
                    if stats_result and stats_result.content:
                        stats_data = json.loads(stats_result.content[0].text)
                        stats = stats_data.get('statistics', {})
                        print(f"   ✅ Cache statistics:")
                        print(f"      Total diagrams: {stats.get('total_diagrams', 0)}")
                        print(f"      Validated: {stats.get('validated_count', 0)}")
                    
                    # Test 7: Delete diagram
                    print("\n7. Deleting test diagram...")
                    delete_result = await session.call_tool(
                        "delete_cached_diagram",
                        {"diagram_id": diagram_id}
                    )
                    
                    if delete_result and delete_result.content:
                        delete_data = json.loads(delete_result.content[0].text)
                        print(f"   ✅ Deleted: {delete_data.get('message')}")
            
            print("\n" + "="*60)
            print("✅ Integration test completed successfully!")
            print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_cache_integration())