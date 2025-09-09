"""
Test the hockey diagram agent with minimal MCP server dependencies.
"""

import asyncio
import logging
import os
from pathlib import Path

from agents import Agent, Runner
from agent_instructions import EXPERT_INSTRUCTIONS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_agent():
    """Test agent without MCP servers for basic functionality."""
    try:
        logger.info("🧪 Testing simple Hockey Diagram Expert Agent...")
        
        # Create agent without MCP servers for basic testing
        agent = Agent(
            name="Hockey Diagram Expert",
            instructions=EXPERT_INSTRUCTIONS,
            model="gpt-4o"
        )
        logger.info("✅ Agent created successfully")
        
        # Test basic interaction without MCP servers
        request = "Show me a 2-1-2 forecheck formation"
        logger.info(f"🎯 Testing request: {request}")
        
        result = await Runner.run(agent, request)
        logger.info(f"✅ Agent response received")
        logger.info(f"📝 Response preview: {str(result)[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

async def main():
    """Run the simple test."""
    logger.info("🚀 Starting simple agent test...")
    success = await test_simple_agent()
    
    if success:
        logger.info("🎉 Simple agent test completed successfully")
    else:
        logger.info("⚠️ Simple agent test failed")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)