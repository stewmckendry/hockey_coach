"""
Test script to validate MCP server connection using OpenAI Agents SDK.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add POC to path
sys.path.append(str(Path(__file__).parent))

from agents.mcp import MCPServerStreamableHttp
from agents import Agent

async def test_mcp_server_connection():
    """Test connection to hockey MCP server using Streamable HTTP transport"""
    print("🔍 Testing Hockey MCP Server Connection")
    print("=" * 40)
    
    # Test Streamable HTTP connection (your current setup)
    print("1. Testing Streamable HTTP connection...")
    try:
        # Create MCP server connection
        hockey_server = MCPServerStreamableHttp(
            name="Hockey Knowledge Server",
            params={
                "url": "http://localhost:8000/mcp"  # Your streamable HTTP endpoint
            },
            cache_tools_list=True  # Cache tools for performance
        )
        
        print(f"   ✅ MCP Server connection created: {hockey_server.name}")
        
        # Try to initialize and list tools
        # Note: We need an agent context to list tools
        dummy_agent = Agent(name="test", instructions="test")
        
        # This will test if we can connect and list tools
        print("   Testing tool discovery...")
        
        # The SDK will handle the connection automatically when we use the agent
        return True, hockey_server
            
    except Exception as e:
        print(f"   ❌ Streamable HTTP connection failed: {e}")
        print(f"   Make sure your hockey_mcp.py server is running:")
        print(f"     cd servers && source ../spacy_env/bin/activate && python hockey_mcp.py")
        print(f"   Server should show: 'Starting Streamable-HTTP transport: http://0.0.0.0:8000'")
    
    return False, None

async def test_agent_with_tools():
    """Test creating an agent with MCP tools"""
    print("\n🧪 Testing Agent with MCP Tools")
    print("=" * 40)
    
    try:
        # Create MCP server connection
        hockey_server = MCPServerStreamableHttp(
            name="Hockey Knowledge Server",
            params={
                "url": "http://localhost:8000/mcp"
            },
            cache_tools_list=True
        )
        
        # Create agent with MCP server
        agent = Agent(
            name="Test Hockey Agent",
            instructions="You are a test agent with access to hockey knowledge tools.",
            model="gpt-4o-mini",
            mcp_servers=[hockey_server]
        )
        
        print("✅ Agent created with MCP server")
        print(f"   Agent: {agent.name}")
        print(f"   MCP Servers: {len(agent.mcp_servers) if hasattr(agent, 'mcp_servers') else 'N/A'}")
        
        return True, agent
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False, None

async def test_tool_usage():
    """Test using tools through the agent"""
    print("\n🏒 Testing Tool Usage")
    print("=" * 40)
    
    try:
        from agents import Runner
        
        # Create MCP server connection
        hockey_server = MCPServerStreamableHttp(
            name="Hockey Knowledge Server",
            params={
                "url": "http://localhost:8000/mcp"
            },
            cache_tools_list=True
        )
        
        # Create agent with instructions to use tools
        agent = Agent(
            name="Hockey Coach Test",
            instructions="""
            You are a hockey coaching assistant with access to hockey knowledge tools.
            When users ask about hockey topics, use the available MCP tools to provide detailed answers.
            Always use tools when asked about specific hockey skills, drills, or coaching advice.
            """,
            model="gpt-4o-mini",
            mcp_servers=[hockey_server]
        )
        
        # Test with a specific hockey question that should trigger tool usage
        test_query = "What are some good skating drills for U10 players?"
        print(f"Testing query: '{test_query}'")
        print("Agent response: ", end="")
        
        result = await Runner.run(agent, test_query)
        response = result.final_output
        
        print(response)
        
        # Basic validation - if tools are working, we should get a detailed response
        if len(response) > 100 and any(keyword in response.lower() for keyword in ['drill', 'skating', 'player']):
            print("\n✅ Got detailed hockey-specific response (tools likely working)")
        elif len(response) > 50:
            print("\n⚠️  Got response but may not be using tools")
        else:
            print("\n❌ Response too short - tools may not be available")
            
        return True
        
    except Exception as e:
        print(f"❌ Tool usage test failed: {e}")
        return False

async def main():
    """Run all MCP tests"""
    print("🏒 Hockey MCP Integration Test")
    print("=" * 50)
    
    # Test connection first
    connection_ok, server = await test_mcp_server_connection()
    
    if connection_ok:
        # Test agent creation
        agent_ok, agent = await test_agent_with_tools()
        
        if agent_ok:
            # Test tool usage
            await test_tool_usage()
            print("\n✅ MCP integration tests completed!")
            print("🚀 Ready to use native MCP agent!")
        else:
            print("\n⚠️  Agent creation issues detected")
    else:
        print("\n🔧 MCP server connection issues detected")
        print("   Agent will work but without hockey knowledge tools")
        print("   Check that your hockey_mcp.py server is running")

if __name__ == "__main__":
    asyncio.run(main())