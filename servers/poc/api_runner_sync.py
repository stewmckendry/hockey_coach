#!/usr/bin/env python3
"""
Synchronous API runner for web integration.
Avoids async event loop conflicts in subprocess environment.
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path

# Add POC to path
sys.path.append(str(Path(__file__).parent))

def run_agent_via_subprocess(message: str) -> str:
    """
    Run the agent in a completely separate Python process to avoid async conflicts.
    This creates a clean environment for the async MCP agent.
    """
    
    # Escape the message for safe inclusion in Python script
    escaped_message = message.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    # Create a temporary script that will run the agent
    poc_path = str(Path(__file__).parent)
    script_content = f'''
import asyncio
import sys
import os
from pathlib import Path

# Add POC to path
sys.path.append("{poc_path}")

async def main():
    try:
        from poc_agents.web_native_mcp_agent import run_web_mcp_agent_with_logging
        response = await run_web_mcp_agent_with_logging("''' + escaped_message + '''")
        print("SUCCESS:" + response)
    except Exception as e:
        print("ERROR:" + str(e))

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    # Write script to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        temp_script = f.name
    
    try:
        # Run the script in a separate Python process
        result = subprocess.run([
            '/Users/liammckendry/spacy_env/bin/python',
            temp_script
        ], 
        capture_output=True, 
        text=True, 
        timeout=60,
        cwd=str(Path(__file__).parent)
        )
        
        if result.returncode == 0:
            # Parse the output
            for line in result.stdout.split('\n'):
                if line.startswith('SUCCESS:'):
                    return line[8:]  # Remove 'SUCCESS:' prefix
                elif line.startswith('ERROR:'):
                    raise Exception(line[6:])  # Remove 'ERROR:' prefix
            
            raise Exception(f"No valid response found in output: {result.stdout}")
        else:
            raise Exception(f"Subprocess failed with code {result.returncode}: {result.stderr}")
            
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_script)
        except:
            pass

def main():
    """Main entry point for API calls"""
    if len(sys.argv) < 2:
        print("AGENT_ERROR:No message provided")
        sys.exit(1)
    
    message = sys.argv[1]
    
    try:
        response = run_agent_via_subprocess(message)
        print(f"AGENT_RESPONSE:{response}")
    except Exception as e:
        print(f"AGENT_ERROR:{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()