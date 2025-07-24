#!/usr/bin/env python3
"""
Simple FastMCP Client Test Script
Tests direct connection to the hockey MCP server
"""

import asyncio
import sys
import json
from fastmcp import Client

async def test_hockey_mcp():
    """Test connection to hockey MCP server"""
    try:
        # Connect directly to the hockey MCP server
        client = Client("http://localhost:8000")
        
        async with client:
            print("✅ Connected to hockey MCP server")
            
            # Test ping
            await client.ping()
            print("✅ Ping successful")
            
            # List available tools
            tools = await client.list_tools()
            print(f"✅ Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test a simple tool call
            if len(sys.argv) > 1:
                tool_name = sys.argv[1]
                params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
                
                print(f"\n🔧 Calling tool: {tool_name}")
                result = await client.call_tool(tool_name, params)
                print(f"✅ Result: {result}")
                
                return result
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_hockey_mcp())
    if len(sys.argv) > 1:
        print(json.dumps(result, indent=2))
