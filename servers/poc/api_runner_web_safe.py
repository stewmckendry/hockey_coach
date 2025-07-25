#!/usr/bin/env python3
"""
Web-safe API runner that handles async properly in subprocess environment.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add POC to path
sys.path.append(str(Path(__file__).parent))

def main():
    """Main entry point that properly handles async in subprocess"""
    if len(sys.argv) < 2:
        print("AGENT_ERROR:No message provided")
        sys.exit(1)
    
    message = sys.argv[1]
    
    try:
        # Import after setting up path
        from poc_agents.web_native_mcp_agent import run_web_mcp_agent_with_logging
        
        # Set up new event loop for subprocess
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the async agent
            response = loop.run_until_complete(run_web_mcp_agent_with_logging(message))
            print(f"AGENT_RESPONSE:{response}")
        finally:
            loop.close()
            
    except Exception as e:
        print(f"AGENT_ERROR:{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()