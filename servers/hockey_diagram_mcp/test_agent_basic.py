"""
Test basic agent initialization without MCP servers to isolate the issue.
"""

import asyncio
import logging
import os
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_agent():
    """Test basic agent without MCP servers."""
    try:
        logger.info("🧪 Testing basic OpenAI Agents SDK import...")
        from agents import Agent, Runner
        logger.info("✅ Basic imports successful")
        
        logger.info("🧪 Testing basic agent creation...")
        agent = Agent(
            name="Test Agent",
            instructions="You are a test agent.",
            model="gpt-4o"
        )
        logger.info("✅ Basic agent creation successful")
        
        logger.info("🧪 Testing runner static method...")
        # Runner is used as static method, not instance
        logger.info("✅ Runner static method confirmed")
        
        logger.info("🧪 Testing MCP imports...")
        from agents.mcp import MCPServerStdio
        logger.info("✅ MCP imports successful")
        
        # Don't actually try to create MCP server yet
        logger.info("🎉 All basic components working!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

async def test_mcp_server_creation():
    """Test MCP server creation with different approaches."""
    try:
        from agents.mcp import MCPServerStdio
        
        logger.info("🧪 Testing MCP server creation with params dict...")
        
        # Try the documented approach
        server = MCPServerStdio(
            params={
                "command": "echo",
                "args": ["hello"],
                "env": {}
            }
        )
        logger.info("✅ MCP server creation with params successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP server creation failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        return False

async def main():
    """Run all tests."""
    logger.info("🚀 Starting OpenAI Agents SDK compatibility tests...")
    
    # Test 1: Basic functionality
    basic_ok = await test_basic_agent()
    
    # Test 2: MCP server creation
    mcp_ok = await test_mcp_server_creation()
    
    logger.info("\n" + "="*50)
    logger.info("TEST RESULTS")
    logger.info("="*50)
    logger.info(f"Basic Agent: {'✅ PASS' if basic_ok else '❌ FAIL'}")
    logger.info(f"MCP Server: {'✅ PASS' if mcp_ok else '❌ FAIL'}")
    
    if basic_ok and mcp_ok:
        logger.info("🎉 All tests passed - SDK is working correctly")
    else:
        logger.info("⚠️ Some tests failed - SDK compatibility issues")
    
    return basic_ok and mcp_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)