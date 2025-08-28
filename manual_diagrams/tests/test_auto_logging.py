#!/usr/bin/env python3
"""
Test automatic trace logging functionality.
"""

import sys
import json
from pathlib import Path

# Setup paths
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent / "servers"))

from auto_trace_logger import start_session, complete_session, get_session_for_sheets, _logger


def test_auto_logging():
    """Test that tools automatically log their calls."""
    
    # Import tools after paths are set
    from hockey_diagram_mcp import (
        find_matching_template,
        create_player,
        validate_spec,
        generate_diagram
    )
    
    print("Testing automatic trace logging...")
    
    # Start a session
    session_id = start_session("Test auto-logging drill")
    print(f"✅ Started session: {session_id}")
    
    # Call tools - they should auto-log
    print("\nCalling tools (should auto-log)...")
    
    # 1. Find template
    matches = find_matching_template("give and go drill")
    print(f"  - find_matching_template: Found {len(matches)} matches")
    
    # 2. Create player
    player = create_player(
        player_type="forward",
        position="F1",
        team="home",
        has_puck=True,
        coordinates={"x": -50, "y": 0}
    )
    print(f"  - create_player: Created {player['position']}")
    
    # 3. Validate spec
    spec = {
        "title": "Test Drill",
        "rink": {"view": "offensive"},
        "players": [player],
        "movements": [],
        "zones": [],
        "annotations": ["Test"]
    }
    validation = validate_spec(spec)
    print(f"  - validate_spec: Valid={validation.get('valid', False)}")
    
    # Complete session
    session_data = complete_session(session_id, success=True, lessons="Auto-logging works!")
    print(f"\n✅ Session completed with {len(session_data.get('tool_calls', []))} tool calls logged")
    
    # Get data for sheets
    sheets_data = get_session_for_sheets(session_id)
    print(f"✅ Prepared {sheets_data['row_count']} rows for Google Sheets")
    
    # Display trace
    print("\n📊 Trace Log:")
    print("-" * 80)
    for i, call in enumerate(session_data.get("tool_calls", []), 1):
        print(f"{i}. [{call['phase']}] {call['tool']} - {call['thought']}")
        if call.get('result_summary'):
            print(f"   Result: {call['result_summary']}")
    
    # Check trace file exists
    trace_file = _logger.log_dir / f"session_{session_id}.json"
    if trace_file.exists():
        print(f"\n✅ Trace file saved: {trace_file}")
        with open(trace_file, 'r') as f:
            data = json.load(f)
        print(f"   - Session: {data['session_id']}")
        print(f"   - Tool calls: {len(data['tool_calls'])}")
        print(f"   - Duration: {data.get('duration_seconds', 0):.2f} seconds")
    else:
        print(f"\n❌ Trace file not found: {trace_file}")
    
    return session_id


if __name__ == "__main__":
    test_auto_logging()