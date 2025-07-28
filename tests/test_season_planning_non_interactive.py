#!/usr/bin/env python3
"""
Non-interactive test for Season Planning Agent to verify the fix.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add servers directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "servers"))

from hockey_agents.season_planning_agent import create_season_planning_agent, run_season_planning_agent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_agent():
    """Test the Season Planning Agent without interactive input."""
    print("🏒 Testing Season Planning Agent - Non-Interactive")
    print("=" * 60)
    
    try:
        # Create agent
        print("\n🚀 Initializing Season Planning Agent...")
        agent = await create_season_planning_agent()
        print("✅ Agent initialized successfully!")
        
        # Test a simple query
        print("\n📝 Testing with sample query...")
        test_query = "I'm coaching a U12 team. What should I focus on for the first month of the season?"
        
        print(f"\nUser: {test_query}")
        print("\nAssistant: ", end="", flush=True)
        
        response = await agent.run(test_query)
        print(response)
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
    finally:
        print("\n🧹 Test cleanup complete.")


if __name__ == "__main__":
    asyncio.run(test_agent())