#!/usr/bin/env python3
"""
Startup script for Hockey Diagram MCP Server.
This script handles proper environment setup and launches the MCP server.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    # Add parent directories to Python path
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent
    
    # Add necessary paths
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(current_dir.parent / "src"))
    sys.path.insert(0, str(project_root))
    
    # Load environment variables from thunder_playbook .env if available
    env_file = Path("/Users/liammckendry/thunder_playbook/.env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"')
    
    # Set PYTHONPATH for imports
    os.environ['PYTHONPATH'] = f"{current_dir}:{current_dir.parent / 'src'}:{os.environ.get('PYTHONPATH', '')}"
    
    # Import and run the MCP server
    from hockey_diagram_mcp import main as run_server
    
    # Run the server
    run_server()

if __name__ == "__main__":
    main()