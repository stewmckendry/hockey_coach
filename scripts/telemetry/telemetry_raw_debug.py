#!/usr/bin/env python3
"""
Enhanced debug script to capture full raw JSON from Claude Code.
This will help diagnose why we're getting empty values.
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

def main():
    """Capture complete raw JSON for debugging."""
    
    event_type = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    
    # Create debug directory
    debug_dir = Path(__file__).parent.parent / "logs" / "claude_telemetry" / "raw_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    # Read ALL stdin
    raw_stdin = sys.stdin.read()
    
    # Save complete raw input
    raw_file = debug_dir / f"{event_type}_{timestamp}_complete.json"
    
    try:
        if raw_stdin.strip():
            # Try to parse and pretty-print
            json_data = json.loads(raw_stdin)
            
            # Save pretty-printed JSON
            with open(raw_file, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            # Also create a summary file
            summary_file = debug_dir / f"{event_type}_{timestamp}_summary.txt"
            with open(summary_file, 'w') as f:
                f.write(f"Event Type: {event_type}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"JSON Keys: {list(json_data.keys())}\n")
                f.write(f"Session ID: {json_data.get('session_id', 'N/A')}\n")
                f.write("\nKey Values:\n")
                
                # Log specific interesting fields
                if event_type == "UserPromptSubmit":
                    prompt = json_data.get('prompt', '')
                    f.write(f"Prompt Length: {len(prompt)}\n")
                    f.write(f"Prompt Preview: {repr(prompt[:200])}\n")
                elif event_type == "Notification":
                    message = json_data.get('message', '')
                    f.write(f"Message Length: {len(message)}\n")
                    f.write(f"Message: {repr(message)}\n")
                elif event_type in ["PreToolUse", "PostToolUse"]:
                    f.write(f"Tool Name: {json_data.get('tool_name', 'N/A')}\n")
                    tool_input = json_data.get('tool_input', {})
                    f.write(f"Tool Input Keys: {list(tool_input.keys()) if isinstance(tool_input, dict) else 'N/A'}\n")
        else:
            # Save empty stdin notice
            with open(raw_file, 'w') as f:
                f.write("EMPTY STDIN RECEIVED\n")
    
    except Exception as e:
        # Save error details
        error_file = debug_dir / f"{event_type}_{timestamp}_error.txt"
        with open(error_file, 'w') as f:
            f.write(f"Error: {e}\n")
            f.write(f"Raw stdin length: {len(raw_stdin)}\n")
            f.write(f"Raw stdin repr: {repr(raw_stdin[:500])}\n")
    
    sys.exit(0)

if __name__ == "__main__":
    main()