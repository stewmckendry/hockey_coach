#!/usr/bin/env python3
"""
API runner using native MCP integration with comprehensive tool logging.

This script provides the bridge between the web API and the native MCP hockey agent,
with detailed logging of tool usage using OpenAI Agents SDK native capabilities.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add POC to path
sys.path.append(str(Path(__file__).parent))

from poc_agents.web_native_mcp_agent import run_web_mcp_agent_with_logging

async def run_native_mcp_agent(message: str) -> str:
    """
    Run the native MCP hockey agent with tool logging.
    
    Returns the agent's response as a string.
    """
    try:
        response = await run_web_mcp_agent_with_logging(message)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main entry point for API calls"""
    if len(sys.argv) < 2:
        print("AGENT_ERROR:No message provided")
        sys.exit(1)
    
    message = sys.argv[1]
    
    try:
        response = asyncio.run(run_native_mcp_agent(message))
        print(f"AGENT_RESPONSE:{response}")
    except Exception as e:
        print(f"AGENT_ERROR:{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Called with message argument (for web API)
        main()
    else:
        # Interactive mode for testing
        print("Native MCP Hockey Agent - Interactive Mode")
        print("Type 'quit' to exit")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if user_input:
                    print("Agent: ", end="")
                    response = asyncio.run(run_native_mcp_agent(user_input))
                    print(response)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nGoodbye!")