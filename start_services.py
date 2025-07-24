#!/usr/bin/env python3
"""
Hockey Coach Startup Script
Starts all necessary services for the hockey coaching application
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent
PYTHON_PATH = "/Users/liammckendry/spacy_env/bin/python"

def start_service(name, script_path, port=None):
    """Start a service and return the process"""
    print(f"🚀 Starting {name}...")
    
    try:
        process = subprocess.Popen([
            PYTHON_PATH, 
            str(PROJECT_ROOT / script_path)
        ], cwd=PROJECT_ROOT)
        
        if port:
            print(f"   → {name} starting on port {port}")
        
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    """Start all hockey coach services"""
    print("🏒 Hockey Coach Application Startup")
    print("=" * 50)
    
    # Start the main hockey MCP server
    hockey_mcp = start_service(
        "Hockey MCP Server", 
        "servers/hockey_mcp.py", 
        8000
    )
    
    if hockey_mcp:
        print("   ⏳ Waiting for Hockey MCP Server to initialize...")
        time.sleep(5)
    
    # Start the direct API
    direct_api = start_service(
        "Hockey Direct API", 
        "servers/hockey_mcp_direct_api.py", 
        3003
    )
    
    if direct_api:
        print("   ⏳ Waiting for Direct API to initialize...")
        time.sleep(3)
    
    print("\n✅ Services Started Successfully!")
    print(f"🏒 Hockey MCP Server: http://localhost:8000")
    print(f"🔗 Direct API: http://localhost:3003")
    print(f"🌐 Web App: cd web_app && npm run dev")
    print("\n💡 Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        if hockey_mcp:
            hockey_mcp.terminate()
        if direct_api:
            direct_api.terminate()
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
