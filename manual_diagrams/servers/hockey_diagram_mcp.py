#!/usr/bin/env python3
"""
Hockey Diagram MCP Server - Tools for creating programmatic hockey diagrams.
Provides validation, templates, specs, and generation tools for the hockey-diagram-expert agent.
"""

from __future__ import annotations

import json
import logging
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from typing_extensions import TypedDict
from pydantic import BaseModel
from datetime import datetime
import uuid
from openai import OpenAI

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

from mcp.server.fastmcp import FastMCP

# Import diagram utilities
from drill_utilities import (
    STANDARD_POSITIONS, LANDMARKS, Z_ORDER,
    determine_view, validate_spatial_placement, validate_diagram_elements,
    create_smooth_path_with_waypoints, map_description_to_position,
    create_player_queue, create_equipment_zone
)
from drill_template_finder import DrillTemplateFinder
from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation
from agent_trace_logger import AgentTraceLogger
from spec_converter import dict_to_diagram_spec, validate_spec_dict
from auto_trace_logger import auto_log, start_session, set_session, complete_session, get_session_for_sheets, add_agent_annotations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Hockey Diagram MCP Server", stateless_http=True)

# Initialize OpenAI for LLM-as-judge validation (lazy load)
client = None

def get_openai_client():
    """Get or create OpenAI client."""
    global client
    if client is None:
        try:
            client = OpenAI()
        except Exception:
            # If OpenAI not configured, validation will gracefully degrade
            pass
    return client

# ====== DATA MODELS ======

class DiagramValidationResult(TypedDict):
    """Result of diagram validation."""
    valid: bool
    issues: List[str]
    warnings: List[str]
    fixes_applied: List[str]

class TemplateMatch(TypedDict):
    """Template matching result."""
    name: str
    confidence: float
    template_file: str
    components: List[str]
    description: str

class DiagramPlan(TypedDict):
    """Human-readable diagram plan."""
    title: str
    zones: List[str]
    view: str
    players: List[Dict[str, Any]]
    movements: List[Dict[str, Any]]
    equipment: List[Dict[str, Any]]
    key_points: List[str]

# ====== DOCUMENTATION & SETUP TOOLS ======

@mcp.tool("hockey_diagram_tools_documentation")
def tools_documentation(
    depth: str = "essentials",
    topic: Optional[str] = None
) -> str:
    """
    Get documentation for hockey diagram MCP tools.
    
    Args:
        depth: "essentials" for quick reference, "full" for comprehensive docs
        topic: Specific tool name or "overview" for general guide
    """
    logger.info(f"📚 [TOOL CALL] tools_documentation: depth={depth}, topic={topic}")
    
    if depth == "essentials":
        return """
# Hockey Diagram MCP Tools - Quick Reference

## Workflow Process:
1. **Discovery**: search templates, get positions/specs
2. **Building**: create players, movements with auto-waypoints
3. **Validation**: validate spatial placement, movements, hockey logic
4. **Generation**: preview plan, generate diagram
5. **Tracking**: trace logging to Google Sheets

## Key Tools:
- `list_templates()` - See available drill templates
- `find_matching_template()` - Match drill description to template
- `get_standard_positions()` - Get coordinate reference
- `create_movement()` - Auto-adds waypoints for smooth paths
- `validate_spatial()` - Check collisions
- `validate_with_llm()` - Hockey sense validation
- `generate_diagram()` - Create the diagram
- `start_trace()` / `complete_trace()` - Session tracking

## Common Patterns:
- Give-and-go: Stationary pivot + moving player
- Cross-ice: Same zone, Y-change 40+ units
- Continuous: Players rotate between sides
"""
    
    elif topic == "validation":
        return """
# Validation Tools

## validate_spec(spec)
- Checks overall spec structure
- Validates z-order hierarchy
- Ensures required fields present

## validate_spatial(spec)  
- Player-to-player spacing (min 3 units)
- Player-to-boards spacing (min 2 units)
- Equipment-to-player spacing (min 4 units)
- Label collision detection (min 5 units)

## validate_movements(spec)
- Ensures waypoints present for curves
- Checks cross-ice has Y-change 40+ units
- Validates movement types match styles

## validate_with_llm(spec, description)
- Uses GPT-4 to check hockey sense
- Validates drill makes tactical sense
- Suggests improvements
"""
    
    return "Use depth='essentials' or topic='validation' for specific docs"

@mcp.tool("hockey_diagram_get_database_statistics")
def get_database_statistics() -> Dict[str, Any]:
    """Get statistics about available diagram resources."""
    logger.info("📊 [TOOL CALL] get_database_statistics")
    
    template_dir = Path(__file__).parent.parent / "templates"
    template_count = len(list(template_dir.glob("*.json"))) if template_dir.exists() else 0
    
    return {
        "templates_available": template_count,
        "standard_positions": len(STANDARD_POSITIONS),
        "landmarks_defined": len(LANDMARKS),
        "z_order_levels": len(Z_ORDER),
        "validation_rules": {
            "spatial": ["player_spacing", "board_proximity", "equipment_overlap", "label_collision"],
            "movement": ["waypoint_presence", "cross_ice_validation", "arc_direction"],
            "hockey_sense": ["llm_validation_available"]
        }
    }

# ====== TEMPLATE MANAGEMENT TOOLS ======

@mcp.tool("hockey_diagram_list_templates")
def list_templates() -> List[Dict[str, Any]]:
    """List all available drill templates with descriptions."""
    logger.info("📋 [TOOL CALL] list_templates")
    
    finder = DrillTemplateFinder()
    templates = []
    
    for pattern_name, pattern_info in finder.drill_patterns.items():
        templates.append({
            "name": pattern_name,
            "description": pattern_info["description"],
            "keywords": ", ".join(pattern_info["keywords"]),  # Convert list to string
            "components": ", ".join(pattern_info["components"])  # Convert list to string
        })
    
    return templates

@mcp.tool("hockey_diagram_find_matching_template")
@auto_log(phase="1_Discovery")
def find_matching_template(description: str) -> List[Dict[str, Any]]:
    """
    Find templates that match the drill description.
    
    Args:
        description: Natural language drill description
        
    Returns:
        List of matching templates sorted by confidence
    """
    logger.info(f"🔍 [TOOL CALL] find_matching_template: '{description[:50]}...'")
    
    finder = DrillTemplateFinder()
    matches, _ = finder.find_matching_templates(description)
    
    return matches[:3]  # Return top 3 matches

@mcp.tool("hockey_diagram_get_template")
def get_template(template_name: str) -> Dict[str, Any]:
    """
    Get complete template specification.
    
    Args:
        template_name: Name of template (e.g., "give_and_go", "cross_ice")
    """
    logger.info(f"📄 [TOOL CALL] get_template: {template_name}")
    
    template_file = Path(__file__).parent.parent / "templates" / f"{template_name}_base.json"
    
    if template_file.exists():
        with open(template_file, 'r') as f:
            return json.load(f)
    
    return {"error": f"Template '{template_name}' not found"}

@mcp.tool("hockey_diagram_get_template_component")
def get_template_component(component_name: str) -> Dict[str, Any]:
    """
    Get a reusable component definition.
    
    Args:
        component_name: Component name (e.g., "player_queue", "cone_pattern")
    """
    logger.info(f"🧩 [TOOL CALL] get_template_component: {component_name}")
    
    finder = DrillTemplateFinder()
    code = finder.get_component_code(component_name)
    
    return {
        "component": component_name,
        "code": code,
        "usage": f"Use this code snippet to add {component_name} to your diagram"
    }

# ====== SPEC BUILDING & CONFIGURATION TOOLS ======

@mcp.tool("hockey_diagram_get_standard_positions")
def get_standard_positions() -> Dict[str, Dict[str, float]]:
    """Get all standard position coordinates."""
    logger.info("📍 [TOOL CALL] get_standard_positions")
    return STANDARD_POSITIONS

@mcp.tool("hockey_diagram_map_position")
def map_position(description: str) -> Dict[str, float]:
    """
    Map natural language position to coordinates.
    
    Args:
        description: Natural language like "top of left circle", "right corner"
    """
    logger.info(f"🗺️ [TOOL CALL] map_position: '{description}'")
    return map_description_to_position(description)

@mcp.tool("hockey_diagram_create_player")
@auto_log(phase="2_Building")
def create_player(
    player_type: str,
    position: str,
    team: str,
    has_puck: bool,
    coordinates: Optional[Dict[str, float]] = None,
    label: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a properly formatted player object.
    
    Args:
        player_type: "forward", "defense", "goalie", "coach"
        position: Position code (e.g., "F1", "D1", "G")
        team: "home" or "away"
        has_puck: Whether player has the puck
        coordinates: {"x": float, "y": float} or None to use standard position
        label: Display label (defaults to position)
    """
    logger.info(f"👤 [TOOL CALL] create_player: {position} ({player_type})")
    
    if coordinates is None:
        # Try to map from standard positions
        if position in STANDARD_POSITIONS:
            coordinates = STANDARD_POSITIONS[position]
        else:
            coordinates = {"x": 0, "y": 0}
    
    return {
        "type": player_type,
        "position": position,
        "coordinates": coordinates,
        "team": team,
        "has_puck": has_puck,
        "label": label or position
    }

@mcp.tool("hockey_diagram_create_movement")
def create_movement(
    movement_type: str,
    from_pos: Dict[str, float],
    to_pos: Dict[str, float],
    style: str,
    label: str,
    add_waypoints: bool = True
) -> Dict[str, Any]:
    """
    Create movement with automatic waypoint generation.
    
    Args:
        movement_type: "skate", "pass", "shot", "carry", "pressure"
        from_pos: Starting position {"x": float, "y": float}
        to_pos: Ending position {"x": float, "y": float}
        style: "solid", "dotted", "dashed", "wavy"
        label: Description of movement
        add_waypoints: Auto-generate smooth waypoints (default True)
    """
    logger.info(f"➡️ [TOOL CALL] create_movement: {movement_type} - {label}")
    
    movement = {
        "type": movement_type,
        "from_pos": from_pos,
        "to_pos": to_pos,
        "style": style,
        "label": label
    }
    
    # Auto-add waypoints for skating/carrying movements
    if add_waypoints and movement_type in ["skate", "carry"]:
        # Calculate if this needs waypoints
        x_dist = abs(to_pos["x"] - from_pos["x"])
        y_dist = abs(to_pos["y"] - from_pos["y"])
        total_dist = (x_dist**2 + y_dist**2)**0.5
        
        if total_dist > 10 or y_dist > 20:  # Needs waypoints
            waypoints = create_smooth_path_with_waypoints(from_pos, to_pos, num_interpolation_points=100)
            movement["waypoints"] = waypoints
            logger.info(f"  ↪️ Added {len(waypoints)} waypoints for smooth path")
    
    return movement

@mcp.tool("hockey_diagram_determine_view")
def determine_view_tool(zones_required: List[str], description: str) -> str:
    """
    Determine optimal rink view based on drill requirements.
    
    Args:
        zones_required: List of zones used ["offensive", "defensive", "neutral"]
        description: Original drill description for context
    """
    logger.info(f"👁️ [TOOL CALL] determine_view: zones={zones_required}")
    return determine_view(zones_required, description)

# ====== VALIDATION TOOLS ======

@mcp.tool("hockey_diagram_validate_spec")
@auto_log(phase="3_Validation")
def validate_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete spec validation including structure and hockey rules.
    
    Args:
        spec: Complete diagram specification
    """
    logger.info("✅ [TOOL CALL] validate_spec")
    
    issues = []
    warnings = []
    
    # Basic structure validation
    if "players" not in spec:
        issues.append("Missing 'players' in spec")
    if "movements" not in spec:
        issues.append("Missing 'movements' in spec")
    
    # Validate without full conversion first
    dict_issues = validate_spec_dict(spec)
    issues.extend(dict_issues)
    
    # Try full conversion for deeper validation
    try:
        diagram_spec = dict_to_diagram_spec(spec)
        if diagram_spec:
            diagram_issues = validate_diagram_elements(diagram_spec)
            issues.extend(diagram_issues)
    except Exception as e:
        warnings.append(f"Could not validate diagram elements: {str(e)}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "fixes_applied": []
    }

@mcp.tool("hockey_diagram_validate_spatial")
def validate_spatial(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate spatial placement to prevent collisions.
    
    Checks:
    - Player-to-player spacing (min 3 units)
    - Player-to-boards spacing (min 2 units)
    - Equipment-to-player spacing (min 4 units)
    - Label collision detection
    """
    logger.info("📏 [TOOL CALL] validate_spatial")
    
    try:
        # Convert to proper spec object
        diagram_spec = dict_to_diagram_spec(spec)
        if diagram_spec:
            spatial_issues = validate_spatial_placement(diagram_spec)
        else:
            # Fallback to basic dict validation
            spatial_issues = ["Could not convert spec for spatial validation"]
        
        return {
            "valid": len(spatial_issues) == 0,
            "issues": spatial_issues,
            "warnings": [],
            "fixes_applied": []
        }
    except Exception as e:
        return {
            "valid": False,
            "issues": [str(e)],
            "warnings": ["Could not complete spatial validation"],
            "fixes_applied": []
        }

@mcp.tool("hockey_diagram_validate_movements")
def validate_movements(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate movement paths and patterns.
    
    Checks:
    - Waypoints present for curves
    - Cross-ice has sufficient Y-change (40+ units)
    - Movement types match styles
    """
    logger.info("〰️ [TOOL CALL] validate_movements")
    
    issues = []
    warnings = []
    
    for movement in spec.get("movements", []):
        # Check for waypoints on long movements
        if movement.get("type") in ["skate", "carry"]:
            from_pos = movement.get("from_pos", {})
            to_pos = movement.get("to_pos", {})
            
            x_dist = abs(to_pos.get("x", 0) - from_pos.get("x", 0))
            y_dist = abs(to_pos.get("y", 0) - from_pos.get("y", 0))
            total_dist = (x_dist**2 + y_dist**2)**0.5
            
            if total_dist > 15 and "waypoints" not in movement:
                issues.append(f"Movement '{movement.get('label', 'unnamed')}' needs waypoints for smooth path")
            
            # Check cross-ice movements
            if "cross" in movement.get("label", "").lower() and y_dist < 40:
                issues.append(f"Cross-ice movement has insufficient Y-change ({y_dist:.1f} units, need 40+)")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "fixes_applied": []
    }

@mcp.tool("hockey_diagram_validate_with_llm")
def validate_with_llm(
    spec: Dict[str, Any],
    original_description: str
) -> Dict[str, Any]:
    """
    Use LLM-as-judge to validate hockey sense and tactical correctness.
    
    Args:
        spec: Diagram specification
        original_description: Original drill description for comparison
    """
    logger.info("🤖 [TOOL CALL] validate_with_llm")
    
    # Format spec for LLM review
    spec_summary = f"""
    Players: {len(spec.get('players', []))}
    Movements: {len(spec.get('movements', []))}
    Zones used: {spec.get('zones_required', [])}
    View: {spec.get('view', 'unknown')}
    """
    
    prompt = f"""
    As a hockey coach, review this drill diagram specification:
    
    Original Request: {original_description}
    
    Diagram Spec Summary:
    {spec_summary}
    
    Player Positions:
    {json.dumps(spec.get('players', []), indent=2)[:500]}
    
    Movements:
    {json.dumps(spec.get('movements', []), indent=2)[:500]}
    
    Please validate:
    1. Does this match the drill description?
    2. Does the drill make hockey sense tactically?
    3. Are player positions logical for this drill?
    4. Are the movements realistic?
    
    Respond with JSON:
    {{
        "matches_description": true/false,
        "makes_hockey_sense": true/false,
        "issues": ["list of specific issues"],
        "suggestions": ["list of improvements"]
    }}
    """
    
    openai_client = get_openai_client()
    if not openai_client:
        return {
            "valid": True,  # Don't block on missing OpenAI
            "issues": [],
            "warnings": ["LLM validation unavailable - OpenAI not configured"],
            "fixes_applied": []
        }
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        issues = []
        if not result.get("matches_description"):
            issues.append("Diagram doesn't match drill description")
        if not result.get("makes_hockey_sense"):
            issues.append("Drill doesn't make tactical hockey sense")
        issues.extend(result.get("issues", []))
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": result.get("suggestions", []),
            "fixes_applied": []
        }
        
    except Exception as e:
        return {
            "valid": True,  # Don't block on LLM failure
            "issues": [],
            "warnings": [f"LLM validation unavailable: {str(e)}"],
            "fixes_applied": []
        }

# ====== GENERATION & OUTPUT TOOLS ======

@mcp.tool("hockey_diagram_preview_plan")
def preview_plan(spec: Dict[str, Any]) -> str:
    """
    Generate human-readable plan for approval.
    
    Args:
        spec: Diagram specification
    """
    logger.info("👀 [TOOL CALL] preview_plan")
    
    plan = []
    plan.append(f"## Diagram Plan: {spec.get('title', 'Hockey Drill')}\n")
    
    # Zones and view
    plan.append(f"**View**: {spec.get('view', 'offensive')}")
    plan.append(f"**Zones**: {', '.join(spec.get('zones_required', ['offensive']))}\n")
    
    # Players
    plan.append("**Players:**")
    for player in spec.get("players", []):
        puck = "🏒" if player.get("has_puck") else ""
        plan.append(f"- {player.get('label', 'X')}: {player.get('type')} at ({player['coordinates']['x']:.0f}, {player['coordinates']['y']:.0f}) {puck}")
    
    # Movements
    plan.append("\n**Movement Sequence:**")
    for i, movement in enumerate(spec.get("movements", []), 1):
        plan.append(f"{i}. {movement.get('label', 'Movement')}: {movement.get('type')} ({movement.get('style')})")
    
    # Equipment
    if spec.get("equipment") or spec.get("zones"):
        plan.append("\n**Equipment:**")
        for item in spec.get("equipment", []) + spec.get("zones", []):
            if item.get("type") == "equipment" or item.get("type") == "cone":
                plan.append(f"- {item.get('type', 'Equipment')} at ({item.get('position', {}).get('x', 0):.0f}, {item.get('position', {}).get('y', 0):.0f})")
    
    # Key points
    plan.append("\n**Key Coaching Points:**")
    for point in spec.get("annotations", []):
        plan.append(f"- {point}")
    
    return "\n".join(plan)

@mcp.tool("hockey_diagram_generate_diagram")
@auto_log(phase="4_Generation")
def generate_diagram(
    spec: Dict[str, Any],
    output_name: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate the hockey diagram from specification.
    
    Args:
        spec: Complete diagram specification
        output_name: Optional name for output file
        
    Returns:
        Dict with output_path and spec_path
    """
    logger.info(f"🎨 [TOOL CALL] generate_diagram: {output_name or 'auto'}")
    
    try:
        # Convert dict spec to proper DiagramSpec object
        diagram_spec = dict_to_diagram_spec(spec)
        if not diagram_spec:
            return {
                "output_path": "",
                "spec_path": "",
                "success": False,
                "error": "Failed to convert spec to DiagramSpec object"
            }
        
        # Generate output name if not provided
        if not output_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"diagram_{timestamp}"
        
        # Build diagram
        builder = DiagramBuilder()
        output_path = Path(__file__).parent.parent / "outputs" / f"{output_name}.png"
        builder.build(diagram_spec, str(output_path))
        
        # Save spec as well
        spec_path = output_path.with_suffix(".json")
        with open(spec_path, 'w') as f:
            json.dump(spec, f, indent=2)
        
        logger.info(f"✨ Generated diagram: {output_path}")
        
        return {
            "output_path": str(output_path),
            "spec_path": str(spec_path),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to generate diagram: {str(e)}")
        return {
            "output_path": "",
            "spec_path": "",
            "success": False,
            "error": str(e)
        }

@mcp.tool("hockey_diagram_save_spec")
def save_spec(spec: Dict[str, Any], name: str) -> str:
    """Save specification for reuse or iteration."""
    logger.info(f"💾 [TOOL CALL] save_spec: {name}")
    
    spec_dir = Path(__file__).parent.parent / "saved_specs"
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    spec_path = spec_dir / f"{name}.json"
    with open(spec_path, 'w') as f:
        json.dump(spec, f, indent=2)
    
    return str(spec_path)

# ====== TRACKING & LOGGING TOOLS ======

# Store active trace sessions in memory
trace_sessions: Dict[str, AgentTraceLogger] = {}

@mcp.tool("hockey_diagram_start_trace")
def start_trace(drill_request: str) -> str:
    """
    Initialize trace session for tracking agent decisions.
    
    Args:
        drill_request: Original drill description
        
    Returns:
        Session ID for this trace
    """
    logger.info(f"📝 [TOOL CALL] start_trace: '{drill_request[:50]}...'")
    
    trace_logger = AgentTraceLogger()
    trace_logger.start_session(drill_request)
    
    session_id = trace_logger.session_id
    trace_sessions[session_id] = trace_logger
    
    return session_id

@mcp.tool("hockey_diagram_log_step")
def log_step(
    session_id: str,
    phase: str,
    action: str,
    thought: str,
    issues: Optional[List[str]] = None
) -> bool:
    """
    Log a step in the agent's process.
    
    Args:
        session_id: Trace session ID
        phase: Current phase (e.g., "1_Discovery", "2_Template")
        action: Action taken (e.g., "search_templates")
        thought: Agent's reasoning
        issues: Any issues found
    """
    logger.info(f"📝 [TOOL CALL] log_step: {phase} - {action}")
    
    if session_id in trace_sessions:
        trace_sessions[session_id].log_step(
            phase=phase,
            action=action,
            thought=thought,
            issues=issues
        )
        return True
    
    return False

@mcp.tool("hockey_diagram_complete_trace")
def complete_trace(
    session_id: str,
    success: bool,
    lessons: str
) -> Dict[str, Any]:
    """
    Complete trace session and get rows for Google Sheets.
    
    Args:
        session_id: Trace session ID
        success: Whether diagram was successful
        lessons: Key insights learned
        
    Returns:
        Dict with sheet_rows ready for Google Sheets
    """
    logger.info(f"📝 [TOOL CALL] complete_trace: {session_id} - {'Success' if success else 'Failed'}")
    
    if session_id in trace_sessions:
        trace_logger = trace_sessions[session_id]
        trace_logger.complete_session(success, lessons)
        
        # Get rows for Google Sheets
        rows = trace_logger.get_sheet_rows()
        
        # Clean up session
        del trace_sessions[session_id]
        
        return {
            "session_id": session_id,
            "rows": rows,
            "row_count": len(rows),
            "spreadsheet_id": "1_RdgMPxluftZfeFl1SXZKYycDVxAV-GrzzhESIOXt24",
            "sheet_name": "Agent_Trace_Log"
        }
    
    return {
        "session_id": session_id,
        "rows": [],
        "row_count": 0,
        "error": "Session not found"
    }

# ====== AUTOMATIC SESSION MANAGEMENT ======

@mcp.tool("hockey_diagram_init_session")
def init_session(drill_request: str, session_id: Optional[str] = None) -> str:
    """Initialize a new auto-trace session. Optional session_id for parallel runs.
    
    Args:
        drill_request: Description of the drill being created
        session_id: Optional session ID for parallel runs (auto-generated if not provided)
        
    Returns:
        Session ID for this trace
    """
    logger.info(f"🎬 [SESSION INIT] Starting session for: {drill_request}")
    return start_session(drill_request, session_id)

@mcp.tool("hockey_diagram_set_active_session")
def set_active_session(session_id: str) -> bool:
    """Set the active session for this thread. Use when running multiple parallel sessions.
    
    Args:
        session_id: Session ID to make active
        
    Returns:
        True if session exists and was activated
    """
    logger.info(f"🔄 [SESSION SET] Activating session: {session_id}")
    return set_session(session_id)

@mcp.tool("hockey_diagram_finalize_session")
def finalize_session(session_id: Optional[str] = None, success: bool = True, lessons: str = None) -> Dict[str, Any]:
    """Complete a session and prepare trace for upload.
    
    Args:
        session_id: Session ID (uses current active session if not provided)
        success: Whether the diagram was successfully created
        lessons: Key insights learned
        
    Returns:
        Session data with trace ready for upload
    """
    logger.info(f"🏁 [SESSION COMPLETE] Finalizing session")
    return complete_session(session_id, success, lessons)

@mcp.tool("hockey_diagram_get_trace_for_sheets")
def get_trace_for_sheets(session_id: Optional[str] = None) -> Dict[str, Any]:
    """Get session trace formatted for Google Sheets upload.
    
    Args:
        session_id: Session ID (uses current active session if not provided)
        
    Returns:
        Dictionary with rows ready for Google Sheets
    """
    logger.info(f"📊 [TRACE EXPORT] Preparing trace for Sheets")
    data = get_session_for_sheets(session_id)
    
    if "error" not in data:
        data["spreadsheet_id"] = "1_RdgMPxluftZfeFl1SXZKYycDVxAV-GrzzhESIOXt24"
        data["sheet_name"] = "Auto_Trace_Log"
        data["instructions"] = "Use google-sheets MCP tool to upload rows to the spreadsheet"
    
    return data

@mcp.tool("hockey_diagram_add_agent_thoughts")
def add_agent_thoughts(annotations: List[Dict[str, str]], session_id: Optional[str] = None) -> bool:
    """Add agent's chain of thought annotations to the trace after tool execution.
    
    Args:
        annotations: List of dicts with 'step' and 'thought' keys
        session_id: Session ID (uses current active session if not provided)
        
    Returns:
        True if annotations were added successfully
        
    Example:
        annotations = [
            {"step": 1, "thought": "User wants a 2v1 rush, searching for rush templates"},
            {"step": 2, "thought": "Found rush template, now building players for 2v1 scenario"},
            {"step": 3, "thought": "Validating to ensure proper spacing and hockey sense"}
        ]
    """
    logger.info(f"💭 [AGENT THOUGHTS] Adding {len(annotations)} annotations")
    return add_agent_annotations(annotations, session_id)

# ====== SERVER INITIALIZATION ======

def main():
    """Main entry point for the Hockey Diagram MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hockey Diagram MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                       help="Transport mechanism (stdio or sse)")
    parser.add_argument("--host", default="localhost", help="Host for SSE transport")
    parser.add_argument("--port", type=int, default=8001, help="Port for SSE transport")
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        import asyncio
        from mcp.server.stdio import stdio_server
        
        async def run_stdio():
            async with stdio_server() as streams:
                await mcp.run(
                    streams[0], streams[1],
                    mcp.create_initialization_options()
                )
        
        logger.info("🏒 Starting Hockey Diagram MCP Server (stdio mode)")
        try:
            asyncio.run(run_stdio())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
    else:
        # SSE/HTTP mode
        logger.info(f"🏒 Starting Hockey Diagram MCP Server at http://{args.host}:{args.port}")
        mcp.run(transport="sse", host=args.host, port=args.port)

if __name__ == "__main__":
    main()