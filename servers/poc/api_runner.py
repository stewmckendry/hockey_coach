#!/usr/bin/env python3
"""
Simple script to run agent from API calls.
Usage: python api_runner.py "message here"
"""

import sys
import asyncio
import os
from pathlib import Path

# Add POC to path
sys.path.append(str(Path(__file__).parent))

# Load environment
from dotenv import load_dotenv
load_dotenv()

from agents import Runner
from poc_agents.api_test_agent import create_api_agent

async def run_agent_with_message(message: str):
    """Run agent with the provided message"""
    try:
        agent = create_api_agent()
        result = await Runner.run(agent, message)
        print("AGENT_RESPONSE:" + result.final_output)
        return True
    except Exception as e:
        print("AGENT_ERROR:" + str(e))
        return False

def main():
    if len(sys.argv) < 2:
        print("AGENT_ERROR:No message provided")
        sys.exit(1)
    
    message = sys.argv[1]
    success = asyncio.run(run_agent_with_message(message))
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()