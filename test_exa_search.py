#!/usr/bin/env python3
"""Test script to verify Exa MCP server functionality"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_exa_search():
    """Test basic web search functionality of Exa MCP server"""
    
    # Create server parameters for Exa MCP
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "exa-mcp-server"],
        env={"EXA_API_KEY": "0e8f0e23-2e3d-4a95-8001-29fc9f7e2a84"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available Exa tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test web search
            print("\nTesting web search...")
            search_result = await session.call_tool(
                "web_search_exa",
                arguments={
                    "query": "hockey coaching drills for youth players",
                    "num_results": 3
                }
            )
            
            print("\nSearch Results:")
            print(json.dumps(search_result.content, indent=2))
            
            return search_result

if __name__ == "__main__":
    asyncio.run(test_exa_search())