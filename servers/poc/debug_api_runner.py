#!/usr/bin/env python3
"""
Debug version of API runner to isolate issues.
"""

import sys
import os

def main():
    try:
        print("DEBUG: Starting debug API runner...")
        print(f"DEBUG: Python version: {sys.version}")
        print(f"DEBUG: Arguments: {sys.argv}")
        print(f"DEBUG: Working directory: {os.getcwd()}")
        print(f"DEBUG: Python path: {sys.path}")
        
        if len(sys.argv) < 2:
            print("AGENT_ERROR:No message provided")
            sys.exit(1)
        
        message = sys.argv[1]
        print(f"DEBUG: Message received: '{message}'")
        
        # Test basic imports
        print("DEBUG: Testing basic imports...")
        import asyncio
        print("DEBUG: asyncio imported successfully")
        
        try:
            import agents
            print("DEBUG: agents imported successfully")
        except ImportError as e:
            print(f"AGENT_ERROR:Cannot import agents: {e}")
            sys.exit(1)
        
        try:
            from agents.mcp import MCPServerStreamableHttp
            print("DEBUG: MCP classes imported successfully")
        except ImportError as e:
            print(f"AGENT_ERROR:Cannot import MCP classes: {e}")
            sys.exit(1)
        
        # Test dotenv
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("DEBUG: dotenv loaded successfully")
        except ImportError as e:
            print(f"DEBUG: dotenv not available: {e}")
        
        print(f"AGENT_RESPONSE:Debug completed successfully! Message was: {message}")
        
    except Exception as e:
        print(f"AGENT_ERROR:Debug failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()