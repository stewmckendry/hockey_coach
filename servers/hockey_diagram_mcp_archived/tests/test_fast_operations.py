"""
Test fast operations to confirm agent functionality without timeout issues.
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

async def test_fast_hockey_tools():
    """Test with hockey tools that should respond quickly."""
    try:
        logger.info("🧪 Testing fast hockey MCP operations...")
        
        # Create hockey diagram server (local, should be fast)
        hockey_server = MCPServerStdio(
            params={
                "command": str(Path(__file__).parent / "start_server.sh"),
                "args": [],
                "env": {}
            }
        )
        
        await hockey_server.connect()
        logger.info("✅ Hockey server connected")
        
        # Create agent with just hockey server
        agent = Agent(
            name="Fast Hockey Agent",
            instructions="You are a hockey diagram expert. Use list_hockey_formations to show available formations.",
            mcp_servers=[hockey_server],
            model="gpt-4o"
        )
        logger.info("✅ Agent created")
        
        # Test fast operation - list formations (should be instant)
        request = "List all available hockey formations"
        logger.info(f"🎯 Testing fast request: {request}")
        
        result = await Runner.run(agent, request)
        logger.info(f"✅ Fast operation completed")
        logger.info(f"📝 Response preview: {str(result)[:400]}...")
        
        await hockey_server.cleanup()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

async def test_simple_exa_search():
    """Test simple Exa web search (not deep research)."""
    try:
        logger.info("🧪 Testing simple Exa web search...")
        
        if not os.getenv("EXA_API_KEY"):
            logger.warning("⚠️ EXA_API_KEY not set, skipping Exa test")
            return True
        
        exa_server = MCPServerStdio(
            params={
                "command": "npx",
                "args": ["-y", "exa-mcp-server"],
                "env": {"EXA_API_KEY": os.getenv("EXA_API_KEY")}
            }
        )
        
        await exa_server.connect()
        logger.info("✅ Exa server connected")
        
        agent = Agent(
            name="Simple Search Agent",
            instructions="You are a research assistant. Use web_search_exa for simple web searches, not deep research.",
            mcp_servers=[exa_server],
            model="gpt-4o"
        )
        
        # Test simple web search (should be faster than deep research)
        request = "Use web_search_exa to quickly find basic information about hockey forechecking"
        logger.info(f"🎯 Testing simple search: {request}")
        
        result = await Runner.run(agent, request)
        logger.info(f"✅ Simple search completed")
        logger.info(f"📝 Response preview: {str(result)[:400]}...")
        
        await exa_server.cleanup()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

async def test_agent_without_mcp():
    """Test agent without MCP servers to establish baseline."""
    try:
        logger.info("🧪 Testing agent without MCP servers...")
        
        agent = Agent(
            name="Simple Agent",
            instructions="You are a hockey expert. Explain a 2-1-2 forecheck using your knowledge.",
            model="gpt-4o"
        )
        
        request = "Explain what a 2-1-2 forecheck is in hockey"
        logger.info(f"🎯 Testing baseline request: {request}")
        
        result = await Runner.run(agent, request)
        logger.info(f"✅ Baseline test completed")
        logger.info(f"📝 Response preview: {str(result)[:400]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

async def main():
    """Run fast operation tests."""
    logger.info("🚀 Starting fast operation tests...")
    
    # Test 1: Agent without MCP (baseline)
    baseline = await test_agent_without_mcp()
    
    # Test 2: Fast hockey tools
    hockey_fast = await test_fast_hockey_tools()
    
    # Test 3: Simple Exa search
    exa_simple = await test_simple_exa_search()
    
    logger.info("\n" + "="*50)
    logger.info("FAST OPERATION TEST RESULTS")
    logger.info("="*50)
    logger.info(f"Baseline (No MCP): {'✅ PASS' if baseline else '❌ FAIL'}")
    logger.info(f"Fast Hockey Tools: {'✅ PASS' if hockey_fast else '❌ FAIL'}")
    logger.info(f"Simple Exa Search: {'✅ PASS' if exa_simple else '❌ FAIL'}")
    
    all_passed = baseline and hockey_fast and exa_simple
    if all_passed:
        logger.info("🎉 All fast operation tests passed!")
        logger.info("💡 Timeout issue is with slow operations only")
    else:
        logger.info("⚠️ Some tests failed - investigating...")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)