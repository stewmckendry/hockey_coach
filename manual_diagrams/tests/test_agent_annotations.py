#!/usr/bin/env python3
"""
Test agent annotation workflow - automatic logging + agent thoughts.
"""

import sys
import json
from pathlib import Path

# Setup paths
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent / "servers"))

from auto_trace_logger import (
    start_session, 
    complete_session, 
    get_session_for_sheets,
    add_agent_annotations
)


def test_annotation_workflow():
    """Test the agent annotation workflow."""
    
    # Import tools after paths are set
    from hockey_diagram_mcp import (
        find_matching_template,
        create_player,
        validate_spec
    )
    
    print("Testing agent annotation workflow...")
    print("=" * 60)
    
    # Start a session
    session_id = start_session("Test drill with agent reasoning")
    print(f"✅ Started session: {session_id}\n")
    
    # Step 1: Find template (auto-logged)
    print("Step 1: Finding template...")
    matches = find_matching_template("give and go passing drill")
    print(f"  Auto-logged: find_matching_template -> {len(matches)} matches")
    
    # Step 2: Create player (auto-logged)
    print("\nStep 2: Creating player...")
    player = create_player(
        player_type="forward",
        position="F1",
        team="home",
        has_puck=True,
        coordinates={"x": -69, "y": 22.5}
    )
    print(f"  Auto-logged: create_player -> {player['position']}")
    
    # Step 3: Validate spec (auto-logged)
    print("\nStep 3: Validating spec...")
    spec = {
        "title": "Give and Go",
        "rink": {"view": "offensive"},
        "players": [player],
        "movements": [],
        "zones": [],
        "annotations": ["Give and go drill"]
    }
    validation = validate_spec(spec)
    print(f"  Auto-logged: validate_spec -> Valid={validation.get('valid', False)}")
    
    # Now add agent's chain of thought
    print("\n" + "=" * 60)
    print("Adding agent's chain of thought...")
    
    agent_thoughts = [
        {"step": 1, "thought": "User requested give and go drill - this is a fundamental passing drill with pivot player"},
        {"step": 2, "thought": "Creating F1 as the pivot player at left faceoff dot, they will hold position with puck"},
        {"step": 3, "thought": "Validating initial setup before adding F2 and movement patterns"}
    ]
    
    success = add_agent_annotations(agent_thoughts, session_id)
    print(f"✅ Added {len(agent_thoughts)} agent thoughts: {success}")
    
    # Complete session
    session_data = complete_session(
        session_id, 
        success=True, 
        lessons="Agent annotations provide reasoning context beyond raw tool calls"
    )
    print(f"\n✅ Session completed")
    
    # Get data for sheets
    sheets_data = get_session_for_sheets(session_id)
    
    # Display the combined trace
    print("\n" + "=" * 60)
    print("📊 Combined Trace (Auto-log + Agent Thoughts):")
    print("-" * 60)
    
    for row in sheets_data["rows"]:
        step = row[3]
        phase = row[4]
        tool = row[5]
        agent_thought = row[6] or "(no agent thought)"
        args_summary = row[7][:50] + "..." if len(row[7]) > 50 else row[7]
        result = row[8]
        
        print(f"\nStep {step}: [{phase}] {tool}")
        print(f"  Inputs:  {args_summary}")
        print(f"  Output:  {result}")
        print(f"  Thought: {agent_thought}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  - Automatic logging captured: tool calls, inputs, outputs")
    print(f"  - Agent added: reasoning and decision process")
    print(f"  - Total rows for Sheets: {sheets_data['row_count']}")
    
    return session_id


if __name__ == "__main__":
    test_annotation_workflow()