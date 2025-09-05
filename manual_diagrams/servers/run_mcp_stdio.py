#!/usr/bin/env python3
"""
Simple stdio wrapper for Hockey Diagram MCP Server.
"""
import sys
import os
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent / "src"))

# Load environment
env_file = Path("/Users/liammckendry/thunder_playbook/.env")
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"')

# Import the MCP server after paths are set
from hockey_diagram_mcp_v3 import mcp

# Run in stdio mode
if __name__ == "__main__":
    mcp.run()