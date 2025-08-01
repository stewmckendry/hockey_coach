#!/usr/bin/env python3
"""
Debug version of telemetry hook to capture raw JSON payloads from Claude Code.
This will help us understand the exact structure of data Claude Code sends.
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

def main():
    """Debug entry point to capture raw JSON from Claude Code."""
    
    # Get event type from command line
    event_type = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    
    # Create debug log directory
    debug_dir = Path(__file__).parent.parent / "logs" / "claude_telemetry" / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamp for filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    
    # Read raw stdin
    raw_stdin = sys.stdin.read().strip()
    
    # Save raw input
    raw_file = debug_dir / f"{event_type}_{timestamp}_raw.txt"
    with open(raw_file, 'w') as f:
        f.write(raw_stdin)
    
    # Try to parse as JSON and save formatted
    try:
        if raw_stdin:
            json_data = json.loads(raw_stdin)
            
            # Save formatted JSON
            json_file = debug_dir / f"{event_type}_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            # Also append to a master debug log
            master_log = debug_dir / "all_events.jsonl"
            with open(master_log, 'a') as f:
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": event_type,
                    "raw_length": len(raw_stdin),
                    "parsed": True,
                    "data": json_data
                }
                f.write(json.dumps(log_entry) + '\n')
        else:
            # Log empty input
            master_log = debug_dir / "all_events.jsonl"
            with open(master_log, 'a') as f:
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": event_type,
                    "raw_length": 0,
                    "parsed": False,
                    "note": "Empty stdin"
                }
                f.write(json.dumps(log_entry) + '\n')
    
    except json.JSONDecodeError as e:
        # Save decode error
        error_file = debug_dir / f"{event_type}_{timestamp}_error.txt"
        with open(error_file, 'w') as f:
            f.write(f"JSON Decode Error: {e}\n")
            f.write(f"Raw input:\n{raw_stdin}\n")
        
        # Log to master
        master_log = debug_dir / "all_events.jsonl"
        with open(master_log, 'a') as f:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "raw_length": len(raw_stdin),
                "parsed": False,
                "error": str(e)
            }
            f.write(json.dumps(log_entry) + '\n')
    
    except Exception as e:
        # Log any other errors
        master_log = debug_dir / "all_events.jsonl"
        with open(master_log, 'a') as f:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "error": str(e),
                "error_type": type(e).__name__
            }
            f.write(json.dumps(log_entry) + '\n')
    
    # Always exit 0 to not interfere with Claude Code
    sys.exit(0)

if __name__ == "__main__":
    main()