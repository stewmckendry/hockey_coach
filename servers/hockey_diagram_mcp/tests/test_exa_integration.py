"""
Test Exa search MCP integration with the hockey diagram agent.
"""

import asyncio
import logging
import os
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_exa_standalone():
    """Test Exa MCP server standalone."""
    try:
        logger.info("🧪 Testing Exa MCP server standalone...")
        
        if not os.getenv("EXA_API_KEY"):
            logger.error("❌ EXA_API_KEY environment variable not set")
            return False
        
        # Create Exa server
        exa_server = MCPServerStdio(
            params={
                "command": "npx",
                "args": ["-y", "exa-mcp-server"],
                "env": {"EXA_API_KEY": os.getenv("EXA_API_KEY")}
            }
        )
        
        # Connect to server
        await exa_server.connect()
        logger.info("✅ Exa server connected")
        
        # Create agent with just Exa server
        agent = Agent(
            name="Research Agent",
            instructions="You are a research assistant that can search the web for hockey-related information.",
            mcp_servers=[exa_server],
            model="gpt-4o"
        )
        logger.info("✅ Agent created with Exa server")
        
        # Test web search for hockey tactics
        request = "Search for information about the Swedish torpedo forecheck system in hockey"
        logger.info(f"🎯 Testing request: {request}")
        
        result = await Runner.run(agent, request)
        logger.info(f"✅ Exa search completed")
        logger.info(f"📝 Response preview: {str(result)[:300]}...")
        
        # Cleanup
        await exa_server.cleanup()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

async def test_exa_with_hockey_agent():
    """Test Exa integration with the full hockey agent."""
    try:
        logger.info("🧪 Testing Exa with full hockey diagram agent...")
        
        # Import the hockey agent
        from hockey_diagram_agent import HockeyDiagramExpert
        
        agent = HockeyDiagramExpert()
        await agent.initialize()
        logger.info("✅ Hockey agent initialized (should include Exa now)")
        
        # Check agent capabilities to see if Exa is included
        capabilities = await agent.get_agent_capabilities()
        logger.info(f"📋 MCP servers: {capabilities['mcp_servers']}")
        
        # Test research request for unknown formation
        request = "Research and generate a diagram for the Finnish torpedo forecheck system"
        logger.info(f"🎯 Testing research request: {request}")
        
        result = await agent.generate_diagram(request)
        logger.info(f"✅ Result success: {result['success']}")
        logger.info(f"📝 Response preview: {result['response'][:300]}...")
        logger.info(f"🛠️ Tools used: {result.get('tools_used', [])}")
        
        return result['success']
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

async def main():
    """Run Exa integration tests."""
    logger.info("🚀 Starting Exa MCP integration tests...")
    
    # Test 1: Standalone Exa server
    exa_standalone = await test_exa_standalone()
    
    # Test 2: Exa with hockey agent
    exa_with_agent = await test_exa_with_hockey_agent()
    
    logger.info("\n" + "="*50)
    logger.info("EXA INTEGRATION TEST RESULTS")
    logger.info("="*50)
    logger.info(f"Standalone Exa Server: {'✅ PASS' if exa_standalone else '❌ FAIL'}")
    logger.info(f"Exa with Hockey Agent: {'✅ PASS' if exa_with_agent else '❌ FAIL'}")
    
    if exa_standalone and exa_with_agent:
        logger.info("🎉 All Exa integration tests passed!")
    else:
        logger.info("⚠️ Some Exa integration tests failed")
    
    return exa_standalone and exa_with_agent

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)