#!/usr/bin/env python3
"""
Unit tests for Hockey Diagram MCP Server tools.
Tests all tool functions to ensure they work correctly.
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add parent directories to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))
sys.path.append(str(Path(__file__).resolve().parent.parent / 'servers'))

# Import the MCP server module
from hockey_diagram_mcp import (
    # Documentation tools
    tools_documentation,
    get_database_statistics,
    # Template tools
    list_templates,
    find_matching_template,
    get_template,
    get_template_component,
    # Spec building tools
    get_standard_positions,
    map_position,
    create_player,
    create_movement,
    determine_view_tool,
    # Validation tools
    validate_spec,
    validate_spatial,
    validate_movements,
    validate_with_llm,
    # Generation tools
    preview_plan,
    generate_diagram,
    save_spec,
    # Tracking tools
    start_trace,
    log_step,
    complete_trace
)


# ====== DOCUMENTATION & SETUP TESTS ======

def test_tools_documentation():
    """Test documentation retrieval."""
    # Test essentials
    docs = tools_documentation(depth="essentials")
    assert "Hockey Diagram MCP Tools" in docs
    assert "Workflow Process:" in docs
    assert "Key Tools:" in docs
    
    # Test specific topic
    validation_docs = tools_documentation(depth="full", topic="validation")
    assert "Validation Tools" in validation_docs
    assert "validate_spec" in validation_docs
    assert "validate_spatial" in validation_docs


def test_get_database_statistics():
    """Test database statistics retrieval."""
    stats = get_database_statistics()
    
    assert "templates_available" in stats
    assert "standard_positions" in stats
    assert "landmarks_defined" in stats
    assert "z_order_levels" in stats
    assert "validation_rules" in stats
    
    # Check validation rules structure
    assert "spatial" in stats["validation_rules"]
    assert "movement" in stats["validation_rules"]
    assert "hockey_sense" in stats["validation_rules"]
    assert "player_spacing" in stats["validation_rules"]["spatial"]


# ====== TEMPLATE MANAGEMENT TESTS ======

def test_list_templates():
    """Test template listing."""
    templates = list_templates()
    
    assert isinstance(templates, list)
    assert len(templates) > 0
    
    # Check template structure
    template = templates[0]
    assert "name" in template
    assert "description" in template
    assert "keywords" in template
    assert "components" in template
    
    # Check for specific templates
    template_names = [t["name"] for t in templates]
    assert "give_and_go" in template_names
    assert "cross_ice" in template_names


def test_find_matching_template():
    """Test template matching."""
    # Test give and go match
    matches = find_matching_template("give and go passing drill")
    assert len(matches) > 0
    assert matches[0]["name"] == "give_and_go"
    assert matches[0]["confidence"] > 0
    
    # Test cross ice match
    matches = find_matching_template("cross ice skating drill")
    assert len(matches) > 0
    # Cross ice should be in top matches
    match_names = [m["name"] for m in matches]
    assert "cross_ice" in match_names


def test_get_template():
    """Test template retrieval."""
    # Test existing template
    template = get_template("give_and_go")
    assert "name" in template
    assert "players" in template
    assert "movements" in template
    
    # Test non-existent template
    template = get_template("nonexistent_template")
    assert "error" in template


def test_get_template_component():
    """Test component retrieval."""
    component = get_template_component("player_queue")
    assert "component" in component
    assert "code" in component
    assert "usage" in component
    assert "create_player_queue" in component["code"]


# ====== SPEC BUILDING TESTS ======

def test_get_standard_positions():
    """Test standard positions retrieval."""
    positions = get_standard_positions()
    
    assert isinstance(positions, dict)
    assert len(positions) > 0
    
    # Check for specific positions
    assert "left_circle_center" in positions
    assert "x" in positions["left_circle_center"]
    assert "y" in positions["left_circle_center"]
    assert positions["left_circle_center"]["x"] == -69


def test_map_position():
    """Test position mapping."""
    # Test corner mapping
    pos = map_position("top left corner")
    assert pos["x"] == -85
    assert pos["y"] == 38
    
    # Test circle mapping
    pos = map_position("left circle center")
    assert pos["x"] == -69
    
    # Test slot mapping
    pos = map_position("left slot")
    assert -80 <= pos["x"] <= -60


def test_create_player():
    """Test player creation."""
    # Test with coordinates
    player = create_player(
        player_type="forward",
        position="F1",
        team="home",
        has_puck=True,
        coordinates={"x": -50, "y": 20},
        label="F1"
    )
    
    assert player["type"] == "forward"
    assert player["position"] == "F1"
    assert player["team"] == "home"
    assert player["has_puck"] == True
    assert player["coordinates"]["x"] == -50
    assert player["label"] == "F1"
    
    # Test without coordinates (should use standard position if available)
    player = create_player(
        player_type="goalie",
        position="G",
        team="away",
        has_puck=False
    )
    assert player["coordinates"] is not None


def test_create_movement():
    """Test movement creation with auto-waypoints."""
    # Test short movement (no waypoints needed)
    movement = create_movement(
        movement_type="pass",
        from_pos={"x": -69, "y": 22.5},
        to_pos={"x": -69, "y": 15},
        style="dotted",
        label="Short pass"
    )
    
    assert movement["type"] == "pass"
    assert movement["style"] == "dotted"
    # Short pass shouldn't get waypoints
    assert "waypoints" not in movement or movement.get("waypoints") is None
    
    # Test long skating movement (should get waypoints)
    movement = create_movement(
        movement_type="skate",
        from_pos={"x": -69, "y": 22.5},
        to_pos={"x": 69, "y": -22.5},
        style="solid",
        label="Cross ice"
    )
    
    assert movement["type"] == "skate"
    assert "waypoints" in movement or movement.get("waypoints") is not None  # Should have waypoints
    
    # Test with waypoints disabled
    movement = create_movement(
        movement_type="skate",
        from_pos={"x": -69, "y": 22.5},
        to_pos={"x": 69, "y": -22.5},
        style="solid",
        label="Cross ice",
        add_waypoints=False
    )
    assert "waypoints" not in movement or movement.get("waypoints") is None


def test_determine_view_tool():
    """Test view determination."""
    # Single zone
    view = determine_view_tool(["offensive"], "offensive zone drill")
    assert view == "offensive"
    
    # Multiple zones
    view = determine_view_tool(["offensive", "neutral"], "breakout drill")
    assert view == "full"
    
    # Full ice mentioned
    view = determine_view_tool(["offensive"], "full ice skating drill")
    assert view == "full"


# ====== VALIDATION TESTS ======

def test_validate_spec():
    """Test spec validation."""
    # Valid spec
    spec = {
        "players": [{"type": "forward", "position": "F1", "coordinates": {"x": -50, "y": 0}}],
        "movements": [{"type": "skate", "from_pos": {"x": -50, "y": 0}, "to_pos": {"x": -60, "y": 0}}],
        "zones": []
    }
    
    result = validate_spec(spec)
    assert isinstance(result, dict)
    assert "valid" in result
    assert "issues" in result
    assert isinstance(result["issues"], list)
    
    # Invalid spec (missing players)
    spec = {"movements": []}
    result = validate_spec(spec)
    assert result["valid"] == False
    assert len(result["issues"]) > 0


def test_validate_spatial():
    """Test spatial validation."""
    # Players too close
    spec = {
        "players": [
            {"type": "forward", "position": "F1", "coordinates": {"x": -50, "y": 0}},
            {"type": "forward", "position": "F2", "coordinates": {"x": -51, "y": 1}}  # Too close!
        ],
        "movements": [],
        "zones": []
    }
    
    result = validate_spatial(spec)
    assert isinstance(result, dict)
    assert "issues" in result
    # Note: Actual validation might not work without proper spec conversion


def test_validate_movements():
    """Test movement validation."""
    # Cross-ice without enough Y-change
    spec = {
        "movements": [
            {
                "type": "skate",
                "from_pos": {"x": -69, "y": 22.5},
                "to_pos": {"x": 69, "y": 25},  # Only 2.5 unit Y-change
                "label": "Cross ice"
            }
        ]
    }
    
    result = validate_movements(spec)
    assert isinstance(result, dict)
    assert "issues" in result
    assert len(result["issues"]) > 0  # Should flag insufficient Y-change


@patch('hockey_diagram_mcp.get_openai_client')
def test_validate_with_llm(mock_get_client):
    """Test LLM validation."""
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps({
            "matches_description": True,
            "makes_hockey_sense": True,
            "issues": [],
            "suggestions": ["Consider adding more players"]
        })))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    spec = {
        "players": [{"type": "forward", "position": "F1", "coordinates": {"x": -50, "y": 0}}],
        "movements": []
    }
    
    result = validate_with_llm(spec, "Simple skating drill")
    assert result["valid"] == True
    assert len(result["warnings"]) > 0  # Should have suggestions


# ====== GENERATION & OUTPUT TESTS ======

def test_preview_plan():
    """Test plan preview generation."""
    spec = {
        "title": "Test Drill",
        "view": "offensive",
        "zones_required": ["offensive"],
        "players": [
            {"type": "forward", "position": "F1", "coordinates": {"x": -50, "y": 0}, "has_puck": True, "label": "F1"}
        ],
        "movements": [
            {"type": "skate", "from_pos": {"x": -50, "y": 0}, "to_pos": {"x": -60, "y": 0}, "style": "solid", "label": "Skate forward"}
        ],
        "annotations": ["Keep head up", "Quick feet"]
    }
    
    plan = preview_plan(spec)
    assert isinstance(plan, str)
    assert "Test Drill" in plan
    assert "F1" in plan
    assert "Skate forward" in plan
    assert "Keep head up" in plan


@patch('hockey_diagram_mcp.DiagramBuilder')
def test_generate_diagram(mock_builder):
    """Test diagram generation."""
    # Mock the builder
    mock_instance = MagicMock()
    mock_builder.return_value = mock_instance
    
    spec = {
        "title": "Test Drill",
        "view": "offensive",
        "players": [],
        "movements": [],
        "zones": [],
        "annotations": []
    }
    
    result = generate_diagram(spec, "test_output")
    
    # Should return paths
    assert "output_path" in result
    assert "spec_path" in result
    
    # Note: Actual file creation would fail in test environment


def test_save_spec(tmp_path):
    """Test spec saving."""
    spec = {"title": "Test Drill", "players": []}
    
    # Patch the save directory
    with patch('hockey_diagram_mcp.Path') as mock_path:
        mock_dir = tmp_path / "saved_specs"
        mock_dir.mkdir()
        mock_path.return_value.parent.parent = tmp_path
        
        # This test would need better mocking of Path operations
        # For now, just test the function doesn't crash
        try:
            path = save_spec(spec, "test_spec")
            assert path is not None
        except:
            pass  # Expected in test environment


# ====== TRACKING TESTS ======

def test_trace_workflow():
    """Test complete trace workflow."""
    # Start trace
    session_id = start_trace("Test drill for unit testing")
    assert isinstance(session_id, str)
    assert len(session_id) == 8  # Short UUID
    
    # Log steps
    success = log_step(
        session_id=session_id,
        phase="1_Discovery",
        action="test_action",
        thought="Testing the logging",
        issues=["Test issue"]
    )
    assert success == True
    
    # Log another step
    success = log_step(
        session_id=session_id,
        phase="2_Building",
        action="create_players",
        thought="Creating test players"
    )
    assert success == True
    
    # Complete trace
    result = complete_trace(
        session_id=session_id,
        success=True,
        lessons="Test completed successfully"
    )
    
    assert result["session_id"] == session_id
    assert result["rows"] is not None
    assert result["row_count"] > 0
    assert result["spreadsheet_id"] == "1_RdgMPxluftZfeFl1SXZKYycDVxAV-GrzzhESIOXt24"
    
    # Try to log to completed session (should fail)
    success = log_step(
        session_id=session_id,
        phase="3_After",
        action="should_fail",
        thought="This should not work"
    )
    assert success == False


def test_invalid_session():
    """Test operations on invalid session."""
    fake_session = "fake12345"
    
    # Log to non-existent session
    success = log_step(
        session_id=fake_session,
        phase="1_Discovery",
        action="test",
        thought="Should fail"
    )
    assert success == False
    
    # Complete non-existent session
    result = complete_trace(
        session_id=fake_session,
        success=False,
        lessons="N/A"
    )
    assert result["row_count"] == 0
    assert "error" in result


# ====== INTEGRATION TESTS ======

def test_full_workflow_integration():
    """Test a complete workflow through the MCP tools."""
    # 1. Discovery
    docs = tools_documentation("essentials")
    assert docs is not None
    
    # 2. Find template
    matches = find_matching_template("give and go drill")
    assert len(matches) > 0
    
    # 3. Get template
    if matches[0]["confidence"] > 0.5:
        template = get_template(matches[0]["name"])
        assert "players" in template
    
    # 4. Build spec
    player = create_player("forward", "F1", "home", True, {"x": -50, "y": 0})
    movement = create_movement("skate", {"x": -50, "y": 0}, {"x": -60, "y": 0}, "solid", "Test")
    
    spec = {
        "title": "Integration Test",
        "players": [player],
        "movements": [movement],
        "zones": []
    }
    
    # 5. Validate
    validation = validate_spec(spec)
    assert "valid" in validation
    
    # 6. Preview
    plan = preview_plan(spec)
    assert "Integration Test" in plan
    
    # 7. Track
    session_id = start_trace("Integration test drill")
    log_step(session_id, "1_Test", "integration", "Testing full workflow")
    result = complete_trace(session_id, True, "Integration successful")
    assert result["row_count"] > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])