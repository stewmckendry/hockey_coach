#!/usr/bin/env python3
"""
Hockey Diagram MCP Server v2 - Enhanced 11-tool design.
Following n8n pattern for clarity and reduced cognitive load.
Includes preview capabilities and relative positioning.
"""

from __future__ import annotations

import json
import logging
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import uuid

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

from mcp.server.fastmcp import FastMCP

# Import diagram utilities
from drill_utilities import (
    STANDARD_POSITIONS, LANDMARKS, Z_ORDER,
    determine_view, validate_spatial_placement, validate_diagram_elements,
    create_smooth_path_with_waypoints, map_description_to_position
)
from drill_template_finder import DrillTemplateFinder
from hockey_diagram_builder import DiagramBuilder, DiagramSpec
from spec_converter import dict_to_diagram_spec, validate_spec_dict
from auto_trace_logger import start_session, complete_session, get_session_for_sheets, add_agent_annotations

# Import modular components
from diagram_schemas import (
    NODE_SCHEMAS, DIAGRAM_SPEC_SCHEMA,
    PLAYER_TYPES, MOVEMENT_TYPES, MOVEMENT_STYLES,
    RINK_VIEWS, ZONE_TYPES, ZONE_SHAPES, TEXT_ANCHORS
)
from position_mapper import (
    map_position, calculate_waypoints,
    OFFENSIVE_POSITIONS, DEFENSIVE_POSITIONS, NEUTRAL_POSITIONS,
    parse_relative_position, enhance_position_with_relative
)
from validators import validate_node, validate_spec, check_spatial_conflicts
from diagram_examples import get_examples_for_node

# Import trace logging
import functools

def trace_tool(func):
    """Decorator to automatically log tool calls to trace."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract session_id if present
        session_id = kwargs.get('session_id')
        tool_name = func.__name__
        trace_logger = None
        
        # Log the call if session exists
        if session_id:
            from auto_trace_logger import get_logger
            trace_logger = get_logger()
            # Log args without session_id to avoid clutter
            log_args = {k: v for k, v in kwargs.items() if k != 'session_id'}
            trace_logger.log_tool_call(
                session_id=session_id,
                tool_name=tool_name,
                args=log_args,
                result=None
            )
        
        # Execute the tool
        result = func(*args, **kwargs)
        
        # Update result in trace
        if session_id and trace_logger:
            trace_logger.update_last_result(session_id, result)
        
        return result
    return wrapper

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI for LLM validation (lazy load)
try:
    from openai import OpenAI
    from dotenv import load_dotenv
    import os
    
    # Load .env file from current directory or parent
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        # Try parent directory
        load_dotenv(Path(__file__).parent.parent.parent / ".env")
    
    client = OpenAI()
    logger.info("✅ OpenAI client initialized successfully")
except Exception as e:
    client = None
    logger.warning(f"⚠️ OpenAI client not available: {e}")

# Initialize MCP server
mcp = FastMCP("Hockey Diagram MCP v2", stateless_http=True)

# ============================================================================
# WORKFLOW INSTRUCTIONS
# ============================================================================

WORKFLOW_INSTRUCTIONS = """
## Hockey Diagram Generation Workflow

### Phase 1: Initialize
1. Call `initialize_diagram` with drill description
2. Review returned instructions and session_id
3. Use provided MCP tools (hockey_kb, exa) for research if needed

### Phase 2: Discovery
1. Call `search_diagram_template` to find matching patterns
2. Optionally `fetch_diagram_template` for full template details
3. Use `search_diagram_node` to understand spec structure

### Phase 3: Build
1. Use mapping tools for natural language positions:
   - `map_position_to_coordinates` - Convert positions like "left faceoff dot" to {x, y}
   - `map_movement_to_coordinates` - Generate complete movements with waypoints
2. Build spec using schemas from `search_diagram_node`:
   - "players" - Player positions and types
   - "movements" - Skating, passing, shooting patterns
   - "rink" - View and zone configuration
3. Call `validate_diagram_node_minimal` for each section

### Phase 4: Validate
1. Call `validate_diagram_spec_full` with complete spec
2. Fix any issues using suggestions
3. Get human approval if needed

### Phase 5: Generate
1. Call `generate_diagram` to create SVG/PNG
2. Review trace in response
3. Upload trace to Google Sheets with reasoning

### Available Node Types:
- `players` - Player configuration schema
- `movements` - Movement patterns and styles
- `rink` - Rink view and zones
- `zones` - Zone markers and boundaries
- `annotations` - Text annotations

### Hockey Rules:
- Max 6 players per team on ice (including goalie)
- Only one player can have puck at a time
- Cross-ice movements need 40+ unit Y-axis change
- Validate spatial placement to avoid collisions
"""

# ============================================================================
# TOOL 1: INITIALIZE
# ============================================================================

@mcp.tool("initialize_diagram")
def initialize_diagram(drill_request: str) -> Dict[str, Any]:
    """Initialize a hockey diagram generation session with instructions.
    
    Args:
        drill_request: Natural language description of the drill
        
    Returns:
        Session info with workflow instructions and available tools
    """
    logger.info(f"🏒 [INIT] Starting diagram for: {drill_request[:50]}...")
    
    session_id = start_session(drill_request)
    
    return {
        "session_id": session_id,
        "drill_request": drill_request,
        "workflow_instructions": WORKFLOW_INSTRUCTIONS,
        "tool_sequence": [
            "search_diagram_template → fetch_diagram_template (optional)",
            "map_position_to_coordinates (for player positions)",
            "map_movement_to_coordinates (for movements with waypoints)",
            "search_diagram_node (for spec schemas)",
            "validate_diagram_node_minimal (as you build)",
            "validate_diagram_spec_full (complete validation)",
            "generate_diagram (create output)"
        ],
        "available_mcp_tools": {
            "hockey_kb": "Search hockey knowledge base",
            "exa": "Web search for hockey tactics",
            "google-sheets": "Upload trace log"
        },
        "next_step": "Use search_diagram_template to find matching drill patterns"
    }

# ============================================================================
# TOOL 2: SEARCH DIAGRAM NODE
# ============================================================================

@mcp.tool("search_diagram_node")
@trace_tool
def search_diagram_node(node_type: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Get schema and instructions for a diagram spec node.
    
    Args:
        node_type: Type of node (players|movements|rink|zones|annotations)
        
    Returns:
        Schema, enums, examples, and constraints for the node type
    """
    logger.info(f"📋 [SCHEMA] Getting schema for: {node_type}")
    
    # Use imported schemas from diagram_schemas module
    if node_type not in NODE_SCHEMAS:
        return {
            "error": f"Unknown node type: {node_type}",
            "available_types": list(NODE_SCHEMAS.keys())
        }
    
    # Build response with schema and enhanced guidance  
    base_schema = NODE_SCHEMAS[node_type]
    
    # Get examples and patterns
    examples_data = get_examples_for_node(node_type)
    
    # Create node-specific enhanced responses
    schemas = {
        "players": {
            "description": "Player positions and configurations",
            "schema": base_schema,
            "enums": {
                "type": PLAYER_TYPES,
                "team": ["home", "visitor"],
                "common_positions": ["F1", "F2", "F3", "D1", "D2", "G", "COACH"]
            },
            "examples": [
                {"type": "forward", "position": "F1", "team": "home", "has_puck": True, "coordinates": {"x": -50, "y": 0}},
                {"type": "defense", "position": "D1", "team": "away", "has_puck": False, "coordinates": {"x": -75, "y": 20}}
            ],
            "constraints": [
                "Max 6 players per team on ice",
                "Only one player can have puck",
                "Positions: F1-F3 (forwards), D1-D2 (defense), G (goalie)"
            ],
            "landmark_positions": {
                "offensive_zone": dict(OFFENSIVE_POSITIONS),
                "neutral_zone": dict(NEUTRAL_POSITIONS),
                "defensive_zone": dict(DEFENSIVE_POSITIONS)
            }
        },
        "movements": {
            "description": "Movement patterns (skating, passing, shooting)",
            "schema": base_schema,
            "enums": {
                "type": MOVEMENT_TYPES,
                "style": MOVEMENT_STYLES
            },
            "style_mapping": {
                "skate": "solid (continuous movement)",
                "pass": "dotted (puck movement)",
                "shot": "dashed (shot on goal)",
                "carry": "wavy (puck control)",
                "pressure": "dashed (defensive pressure)"
            },
            "examples": [
                {"type": "pass", "from_pos": {"x": -50, "y": 0}, "to_pos": {"x": -50, "y": 20}, "style": "dotted"},
                {"type": "skate", "from_pos": {"x": 0, "y": 0}, "to_pos": {"x": 50, "y": 0}, "style": "solid", "label": "Drive net"}
            ],
            "hints": [
                "ALWAYS add waypoints for curved/realistic paths",
                "Cross-ice needs 40+ unit Y-change",
                "Label key movements for clarity",
                "Use 2-3 waypoints for smooth curves"
            ],
            "waypoint_examples": {
                "curve_to_net": {
                    "description": "Driving to net from corner",
                    "waypoints": [
                        {"x": -85, "y": -30},
                        {"x": -77, "y": -15}
                    ]
                },
                "cross_ice": {
                    "description": "Cross-ice pass reception route",
                    "waypoints": [
                        {"x": -50, "y": 0},
                        {"x": -25, "y": -20}
                    ]
                },
                "cycle_path": {
                    "description": "Cycling along boards",
                    "waypoints": [
                        {"x": -89, "y": -30},
                        {"x": -89, "y": -20}
                    ]
                }
            }
        },
        "rink": {
            "description": "Rink view and configuration",
            "schema": base_schema,
            "enums": {
                "view": RINK_VIEWS
            },
            "view_guidelines": {
                "full": "Complete rink - use for full-ice drills",
                "half": "Half ice - use for station drills",
                "offensive": "Offensive zone focus - most drills",
                "defensive": "Defensive zone focus - breakouts",
                "neutral": "Neutral zone - transition drills"
            }
        },
        "zones": {
            "description": "Zone markers and boundaries",
            "schema": base_schema,
            "enums": {
                "type": ZONE_TYPES,
                "shape": ZONE_SHAPES
            }
        },
        "annotations": {
            "description": "Text annotations and notes",
            "schema": base_schema,
            "enums": {
                "anchor": TEXT_ANCHORS
            },
            "examples": [
                "U12 Give and Go Drill",
                "Focus: Quick passing and communication",
                "Duration: 5 minutes"
            ]
        }
    }
    
    if node_type not in schemas:
        return {
            "error": f"Unknown node type: {node_type}",
            "available_types": list(schemas.keys())
        }
    
    # Add examples and patterns to the response
    response = schemas[node_type]
    response["examples"] = examples_data.get("examples", {})
    response["patterns"] = examples_data.get("patterns", {})
    
    return response

# ============================================================================
# TOOL 3: SEARCH DIAGRAM TEMPLATE
# ============================================================================

@mcp.tool("search_diagram_template")
@trace_tool
def search_diagram_template(query: str, template_type: Optional[str] = None, limit: int = 3, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search for matching drill templates.
    
    Args:
        query: Search query (e.g., "2v1 rush", "breakout")
        template_type: Optional filter (drill|component|position)
        limit: Max results to return
        
    Returns:
        List of matching templates with previews
    """
    logger.info(f"🔍 [SEARCH] Templates for: {query}")
    
    finder = DrillTemplateFinder()
    matches, components = finder.find_matching_templates(query)
    
    results = []
    for match in matches[:limit]:
        result = {
            "name": match["name"],
            "confidence": match["confidence"],
            "description": match["description"],
            "template_file": match["template_file"],
            "components": match["components"],
            "preview": {
                "has_template": match.get("template_data") is not None,
                "keywords": finder.drill_patterns[match["name"]]["keywords"][:3]
            }
        }
        
        # Add preview if template exists
        if match.get("template_data"):
            data = match["template_data"]
            result["preview"]["player_count"] = len(data.get("players", []))
            result["preview"]["movement_count"] = len(data.get("movements", []))
            result["preview"]["view"] = data.get("rink", {}).get("view", "unknown")
        
        results.append(result)
    
    return results

# ============================================================================
# TOOL 4: FETCH DIAGRAM TEMPLATE
# ============================================================================

@mcp.tool("fetch_diagram_template")
@trace_tool
def fetch_diagram_template(template_name: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Fetch complete template JSON.
    
    Args:
        template_name: Name of template (e.g., "give_and_go", "rush")
        
    Returns:
        Complete template specification
    """
    logger.info(f"📄 [FETCH] Template: {template_name}")
    
    finder = DrillTemplateFinder()
    
    # Find the template file
    if template_name not in finder.drill_patterns:
        return {
            "error": f"Template not found: {template_name}",
            "available": list(finder.drill_patterns.keys())
        }
    
    template_info = finder.drill_patterns[template_name]
    template_path = finder.template_dir / template_info["template_file"]
    
    # Load template if it exists
    if template_path.exists():
        with open(template_path, 'r') as f:
            template_data = json.load(f)
        return {
            "name": template_name,
            "description": template_info["description"],
            "template": template_data,
            "components": template_info["components"],
            "usage_hints": [
                "Use as starting point",
                "Modify positions and movements as needed",
                "Validate after modifications"
            ]
        }
    else:
        # Return component suggestions if no template file
        return {
            "name": template_name,
            "description": template_info["description"],
            "components": template_info["components"],
            "template": None,
            "message": "Template file not found, use components to build from scratch"
        }

# ============================================================================
# TOOL 5: VALIDATE DIAGRAM NODE MINIMAL
# ============================================================================

@mcp.tool("validate_diagram_node_minimal")
@trace_tool
def validate_diagram_node_minimal(node_type: str, node_data: Any, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Validate a single node of the diagram spec.
    
    Args:
        node_type: Type of node (players|movements|rink|zones|annotations)
        node_data: The node data to validate
        
    Returns:
        Validation results with issues and fixes
    """
    logger.info(f"✅ [VALIDATE NODE] {node_type}")
    
    # Use modular validator for basic schema validation
    result = validate_node(node_type, node_data)
    
    # Add additional hockey-specific warnings
    warnings = []
    fixes = {}
    
    if node_type == "players" and result["valid"]:
        has_puck_count = sum(1 for p in node_data if p.get("has_puck", False))
        if has_puck_count == 0:
            warnings.append("No player has puck - is this intentional?")
            
    elif node_type == "movements" and result["valid"]:
        for i, movement in enumerate(node_data):
            # Check cross-ice movements
            if movement.get("type") == "skate":
                from_pos = movement.get("from", {})
                to_pos = movement.get("to", {})
                from_y = from_pos.get("y", 0)
                to_y = to_pos.get("y", 0)
                if abs(to_y - from_y) > 40:
                    if "waypoints" not in movement:
                        warnings.append(f"Movement {i}: Cross-ice movement should have waypoints for smooth curve")
                        
    elif node_type == "rink" and result["valid"]:
        if "view" not in node_data:
            warnings.append("No view specified, will use 'offensive' by default")
            fixes["rink"] = {"view": "offensive"}
    
    return {
        "valid": result["valid"],
        "issues": result.get("errors", []),
        "warnings": warnings,
        "fixes": fixes if fixes else None,
        "path": result.get("path")
    }

# ============================================================================
# TOOL 6: VALIDATE DIAGRAM SPEC FULL
# ============================================================================

@mcp.tool("validate_diagram_spec_full")
@trace_tool
def validate_diagram_spec_full(spec: Dict[str, Any], original_request: Optional[str] = None, session_id: Optional[str] = None, use_llm: bool = True) -> Dict[str, Any]:
    """Complete validation of entire diagram specification.
    
    Args:
        spec: Complete diagram specification
        original_request: Original drill description for context
        use_llm: Whether to use LLM for semantic validation (default: True)
        
    Returns:
        Comprehensive validation with structure, spatial, and hockey sense checks
    """
    logger.info(f"🔍 [VALIDATE FULL] Spec with {len(spec.get('players', []))} players")
    
    # Use modular validators
    validation_result = validate_spec(spec)
    structure_valid = validation_result["valid"]
    structure_issues = validation_result.get("errors", [])
    
    # Spatial validation using modular function
    spatial_issues = check_spatial_conflicts(spec)
    spatial_valid = len(spatial_issues) == 0
    
    # Hockey sense validation (LLM if available and enabled)
    hockey_sense_valid = True
    llm_feedback = None
    llm_warnings = []
    llm_issues = []
    
    if original_request and client and use_llm:
        try:
            # Build detailed spec summary for LLM
            players = spec.get('players', [])
            movements = spec.get('movements', [])
            
            # Count offensive and defensive players
            home_players = [p for p in players if p.get('team') == 'home']
            away_players = [p for p in players if p.get('team') == 'away']
            
            # Summarize player positions
            player_summary = []
            for p in players:
                pos = p.get('position', 'Unknown')
                coords = p.get('coordinates', {})
                team = p.get('team', 'unknown')
                player_summary.append(f"{pos} at ({coords.get('x', 0)}, {coords.get('y', 0)}) [{team}]")
            
            # Summarize movements
            movement_summary = []
            for m in movements:
                m_type = m.get('type', 'unknown')
                from_pos = m.get('from_pos', {})
                to_pos = m.get('to_pos', {})
                movement_summary.append(f"{m_type}: ({from_pos.get('x', 0)}, {from_pos.get('y', 0)}) → ({to_pos.get('x', 0)}, {to_pos.get('y', 0)})")
            
            prompt = f"""
            Analyze if this hockey diagram matches the drill request.
            
            DRILL REQUEST: "{original_request}"
            
            GENERATED DIAGRAM:
            Players ({len(players)} total - {len(home_players)} home/offensive, {len(away_players)} away/defensive):
            {chr(10).join(player_summary[:10]) if player_summary else "None"}
            
            Movements ({len(movements)}):
            {chr(10).join(movement_summary[:10]) if movement_summary else "None"}
            
            Zones: {len(spec.get('zones', []))} zones
            Rink view: {spec.get('rink', {}).get('view', 'full')}
            
            HOCKEY DRILL NOTATION:
            - "2v1" means 2 offensive players vs 1 defensive player (3 total)
            - "3v2" means 3 offensive players vs 2 defensive players (5 total)
            - "5v4" means 5 offensive vs 4 defensive (power play, often just show offensive 5)
            - Home team is typically offensive, away team is defensive
            - Count forwards/defense by position (F1, F2, F3 = forwards; D1, D2 = defense)
            
            CRITICAL CHECKS:
            1. PLAYER COUNT for drill notation - BE VERY STRICT:
               - "2v1" → EXACTLY 2 home players AND EXACTLY 1 away player (total=3)
               - "3v2" → EXACTLY 3 home players AND EXACTLY 2 away players (total=5)
               - If counts don't match, MATCH MUST BE "NO"
               
            2. MOVEMENT REQUIREMENTS - BE STRICT:
               - "pass" in request → MUST have pass movement
               - "shot" in request → MUST have shot movement
               - Missing required movements = MATCH: NO
            
            3. Positioning - BE LENIENT (minor variations OK)
            
            DECISION RULE: Wrong player count = ALWAYS NO. Missing key movements = ALWAYS NO.
            
            OUTPUT FORMAT (use | as separator):
            MATCH: YES or NO
            ISSUES: List only CRITICAL mismatches (semicolon separated) or "none"
            WARNINGS: List minor concerns (semicolon separated) or "none"
            MISSING: List only ESSENTIAL missing elements or "none"
            
            Example for correct 2v1:
            MATCH: YES
            ISSUES: none
            WARNINGS: none
            MISSING: none
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            llm_response = response.choices[0].message.content.strip()
            logger.info(f"LLM validation response: {llm_response}")
            
            # Parse LLM response
            lines = llm_response.split('\n')
            for line in lines:
                if '|' in line or ':' in line:
                    sep = '|' if '|' in line else ':'
                    parts = line.split(sep, 1)
                    if len(parts) == 2:
                        key = parts[0].strip().upper()
                        value = parts[1].strip()
                        
                        if key == "MATCH" and value.upper() == "NO":
                            hockey_sense_valid = False
                        elif key == "ISSUES" and value.lower() != "none":
                            issues = [i.strip() for i in value.split(';') if i.strip()]
                            llm_issues.extend(issues)
                        elif key == "WARNINGS" and value.lower() != "none":
                            warnings = [w.strip() for w in value.split(';') if w.strip()]
                            llm_warnings.extend(warnings)
                        elif key == "MISSING" and value.lower() != "none":
                            missing = [m.strip() for m in value.split(';') if m.strip()]
                            for item in missing:
                                llm_issues.append(f"Missing: {item}")
            
            # Create consolidated feedback
            if llm_issues or llm_warnings:
                llm_feedback = "LLM Analysis: " + "; ".join(llm_issues[:2]) if llm_issues else None
                
        except Exception as e:
            logger.warning(f"LLM validation failed: {e}")
            pass
    
    # Compile results
    all_issues = structure_issues + spatial_issues + llm_issues
    all_warnings = llm_warnings
    
    suggestions = []
    if "players" in spec and len(spec["players"]) == 1 and "give" in str(original_request).lower():
        suggestions.append("Give-and-go requires 2+ players")
    
    # Add any LLM suggestions to suggestions list
    for warning in llm_warnings:
        if warning not in suggestions:
            suggestions.append(warning)
    
    return {
        "valid": structure_valid and spatial_valid and hockey_sense_valid,
        "structure_valid": structure_valid,
        "spatial_valid": spatial_valid, 
        "hockey_sense_valid": hockey_sense_valid,
        "issues": all_issues,
        "warnings": all_warnings,
        "suggestions": suggestions,
        "llm_analysis": {
            "performed": original_request is not None and client is not None and use_llm,
            "match": hockey_sense_valid,
            "feedback": llm_feedback,
            "issues": llm_issues,
            "warnings": llm_warnings
        }
    }

# ============================================================================
# TOOL 7: PREVIEW DIAGRAM
# ============================================================================

@mcp.tool("preview_diagram")
@trace_tool
def preview_diagram(spec: Dict[str, Any], format: str = "ascii", session_id: Optional[str] = None) -> Dict[str, Any]:
    """Preview the diagram as ASCII art or coordinate list.
    
    Args:
        spec: Diagram specification to preview
        format: "ascii" for ASCII art, "coordinates" for coordinate list
        
    Returns:
        Preview representation of the diagram
    """
    logger.info(f"👁️ [PREVIEW] Generating {format} preview")
    
    if format == "ascii":
        # Create simple ASCII representation
        # Full rink is 200x85, scale down to 40x17 for ASCII
        ascii_width = 40
        ascii_height = 17
        
        # Initialize ASCII grid
        grid = [[' ' for _ in range(ascii_width)] for _ in range(ascii_height)]
        
        # Draw basic rink outline
        for x in range(ascii_width):
            grid[0][x] = '-'
            grid[ascii_height-1][x] = '-'
        for y in range(ascii_height):
            grid[y][0] = '|'
            grid[y][ascii_width-1] = '|'
            
        # Add center line
        center_x = ascii_width // 2
        for y in range(1, ascii_height-1):
            grid[y][center_x] = '|'
            
        # Add goals
        grid[ascii_height//2][1] = 'G'
        grid[ascii_height//2][ascii_width-2] = 'G'
        
        # Plot players
        players = spec.get("players", [])
        for player in players:
            coords = player.get("coordinates", {})
            x = coords.get("x", 0)
            y = coords.get("y", 0)
            
            # Convert rink coords to ASCII coords
            ascii_x = int((x + 100) * ascii_width / 200)
            ascii_y = int((y + 42.5) * ascii_height / 85)
            
            # Clamp to grid bounds
            ascii_x = max(1, min(ascii_width-2, ascii_x))
            ascii_y = max(1, min(ascii_height-2, ascii_y))
            
            # Get player symbol
            pos = player.get("position", "")
            if pos.startswith("F"):
                symbol = 'F'
            elif pos.startswith("D"):
                symbol = 'D'
            elif pos.startswith("G"):
                symbol = 'G'
            else:
                symbol = 'P'
                
            grid[ascii_y][ascii_x] = symbol
            
        # Convert grid to string
        ascii_art = '\n'.join([''.join(row) for row in grid])
        
        return {
            "format": "ascii",
            "preview": ascii_art,
            "legend": {
                "F": "Forward",
                "D": "Defense", 
                "G": "Goalie",
                "P": "Player",
                "|": "Lines",
                "-": "Boards"
            }
        }
        
    elif format == "coordinates":
        # Generate coordinate list
        coord_list = []
        
        # List players
        players = spec.get("players", [])
        for player in players:
            coords = player.get("coordinates", {})
            coord_list.append({
                "type": "player",
                "position": player.get("position"),
                "team": player.get("team"),
                "x": coords.get("x"),
                "y": coords.get("y")
            })
            
        # List movements
        movements = spec.get("movements", [])
        for i, movement in enumerate(movements):
            from_pos = movement.get("from_pos", {})
            to_pos = movement.get("to_pos", {})
            coord_list.append({
                "type": "movement",
                "movement_type": movement.get("type"),
                "from": f"({from_pos.get('x')}, {from_pos.get('y')})",
                "to": f"({to_pos.get('x')}, {to_pos.get('y')})",
                "waypoints": movement.get("waypoints", [])
            })
            
        # List zones
        zones = spec.get("zones", [])
        for zone in zones:
            pos = zone.get("position", {})
            coord_list.append({
                "type": "zone",
                "zone_type": zone.get("type"),
                "shape": zone.get("shape"),
                "position": f"({pos.get('x')}, {pos.get('y')})",
                "dimensions": zone.get("dimensions", {})
            })
            
        return {
            "format": "coordinates",
            "total_elements": {
                "players": len(players),
                "movements": len(movements),
                "zones": len(zones),
                "annotations": len(spec.get("annotations", []))
            },
            "coordinates": coord_list,
            "rink_view": spec.get("rink", {}).get("view", "full")
        }
        
    else:
        return {
            "error": f"Unknown format: {format}",
            "available_formats": ["ascii", "coordinates"]
        }

# ============================================================================
# TOOL 8: GENERATE DIAGRAM
# ============================================================================

@mcp.tool("generate_diagram")
@trace_tool
def generate_diagram(spec: Dict[str, Any], output_name: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Generate the hockey diagram and save files.
    
    Args:
        spec: Complete validated diagram specification
        output_name: Optional name for output files
        
    Returns:
        Paths to generated files and execution trace
    """
    logger.info(f"🎨 [GENERATE] Creating diagram: {output_name or 'diagram'}")
    
    # Create trace for this generation
    trace = []
    
    # Step 1: Convert spec
    trace.append({"step": 1, "action": "convert_spec", "status": "starting"})
    try:
        diagram_spec = dict_to_diagram_spec(spec)
        if not diagram_spec:
            return {
                "success": False,
                "error": "Failed to convert spec to diagram - returned None",
                "trace": trace
            }
        trace[-1]["status"] = "success"
    except Exception as e:
        logger.error(f"Error converting spec: {e}")
        import traceback
        error_detail = traceback.format_exc()
        return {
            "success": False,
            "error": f"Failed to convert spec: {str(e)}",
            "error_detail": error_detail,
            "trace": trace
        }
    
    # Step 2: Generate output paths
    if not output_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"diagram_{timestamp}"
    
    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    png_path = output_dir / f"{output_name}.png"
    
    # Step 3: Generate diagram
    trace.append({"step": 2, "action": "generate_png", "status": "starting"})
    try:
        builder = DiagramBuilder()
        result_path = builder.build(diagram_spec, str(png_path))
        trace[-1]["status"] = "success"
        trace[-1]["output_path"] = str(result_path)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Diagram generation error: {e}\n{tb}")
        trace[-1]["status"] = "failed"
        trace[-1]["error"] = str(e)
        trace[-1]["traceback"] = tb
        return {
            "success": False,
            "error": f"Failed to generate diagram: {e}",
            "error_detail": tb,
            "trace": trace
        }
    
    # Step 4: Save spec files
    trace.append({"step": 3, "action": "save_files", "status": "starting"})
    
    # Save spec JSON
    spec_path = output_dir / f"{output_name}.json"
    with open(spec_path, 'w') as f:
        json.dump(spec, f, indent=2)
    
    trace[-1]["status"] = "success"
    trace[-1]["files"] = [str(png_path), str(spec_path)]
    
    # Complete session and get trace file path
    trace_path = None
    if session_id:
        from auto_trace_logger import get_logger
        trace_logger = get_logger()
        trace_path = trace_logger.get_session_file_path(session_id)
        session_data = complete_session(session_id=session_id, success=True, lessons="Diagram generated successfully")
    else:
        session_data = {}
    
    # Get trace data for sheets if session exists
    trace_for_sheets = None
    if session_id:
        trace_for_sheets = get_session_for_sheets(session_id)
    
    return {
        "success": True,
        "image_path": str(png_path),
        "spec_path": str(spec_path),
        "trace_path": str(trace_path) if trace_path else None,
        "trace": trace,
        "session_id": session_id,
        "total_tool_calls": len(session_data.get("tool_calls", [])),
        "trace_data": trace_for_sheets,
        "upload_ready": trace_for_sheets is not None
    }

# ============================================================================
# TOOL 8: MAP POSITION TO COORDINATES
# ============================================================================

@mcp.tool("map_position_to_coordinates")
@trace_tool
def map_position_to_coordinates(position: str, zone: Optional[str] = "offensive", reference_positions: Optional[Dict[str, List[float]]] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Map natural language position to exact coordinates.
    
    Args:
        position: Natural language position (e.g., "left faceoff dot", "behind net", "high slot")
                 or relative position (e.g., "5 units left of F1", "between F1 and F2")
        zone: Context zone - "offensive", "defensive", or "neutral" (default: offensive)
        reference_positions: Optional dict of existing positions for relative positioning
                           Format: {"F1": [x, y], "F2": [x, y]}
        
    Returns:
        Exact coordinates and confidence level
    """
    logger.info(f"📍 [MAP POSITION] '{position}' in {zone} zone")
    
    # Get zone-specific positions
    if zone == "offensive":
        zone_positions = OFFENSIVE_POSITIONS
    elif zone == "defensive":
        zone_positions = DEFENSIVE_POSITIONS
    else:
        zone_positions = NEUTRAL_POSITIONS
    
    # 1. Try exact match first (fastest path)
    position_lower = position.lower().strip()
    if position_lower in zone_positions:
        x, y = zone_positions[position_lower]
        return {
            "success": True,
            "position": position,
            "zone": zone,
            "coordinates": {"x": x, "y": y},
            "positioning_type": "exact",
            "confidence": 1.0,
            "match_type": "exact"
        }
    
    # 2. Use LLM for intelligent matching (if available)
    if client and position_lower not in zone_positions:
        try:
            # Build comprehensive context
            import json
            
            # Common position aliases
            aliases = {
                "c": "center", "rw": "right wing", "lw": "left wing",
                "rd": "right defense", "ld": "left defense", "g": "goalie",
                "rhd": "right defense", "lhd": "left defense",
                "center ice": "center", "centre": "center"
            }
            
            # Format reference positions if provided
            ref_pos_tuples = {}
            if reference_positions:
                for name, coords in reference_positions.items():
                    if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                        ref_pos_tuples[name] = (coords[0], coords[1])
            
            # Build prompt with context - organize positions by category
            positions_list = [f"{k}: ({v[0]}, {v[1]})" for k, v in zone_positions.items()]
            
            # Categorize and prioritize positions for LLM
            # Priority 1: Non-faceoff positions (most commonly used)
            priority_positions = {
                "Slot (all)": [p for p in positions_list if "slot" in p.lower()],  # ~13 positions
                "Point (all)": [p for p in positions_list if "point" in p.lower()],  # ~6 positions
                "Net/Crease": [p for p in positions_list if any(x in p.lower() for x in ["net", "crease", "goalie", "post"])],  # ~8 positions
                "Corners/Walls": [p for p in positions_list if any(x in p.lower() for x in ["corner", "wall"])],  # ~7 positions
                "Key Spots": [p for p in positions_list if any(x in p.lower() for x in ["hash", "dot", "blue line"]) and "faceoff" not in p.lower()],  # ~6 positions
            }
            
            # Priority 2: Key faceoff positions only (not all 22)
            faceoff_positions = [p for p in positions_list if "faceoff" in p.lower()]
            key_faceoffs = [p for p in faceoff_positions if any(x in p for x in ["center", "left wing", "right wing"]) and not "defense" in p][:10]
            if key_faceoffs:
                priority_positions["Faceoff (key)"] = key_faceoffs
            
            # Build position list - should total ~50-55 positions, all important ones
            positions_display = []
            for category, positions in priority_positions.items():
                if positions:
                    positions_display.append(f"\n{category}:")
                    positions_display.extend(positions)  # Show ALL in priority categories
            
            prompt = f"""You are a hockey positioning expert. Map this position request to exact coordinates.

Position request: "{position}"
Current zone: {zone.upper()} ZONE
Reference positions: {json.dumps(ref_pos_tuples) if ref_pos_tuples else "none"}

{zone.upper()} ZONE positions (showing {len([p for cat in priority_positions.values() for p in cat])} of {len(zone_positions)} total):{''.join(positions_display)}

Note: These are {zone} zone coordinates. Offensive zone is positive x (right side), defensive zone is negative x (left side).
Full position list has {len(zone_positions)} positions including all faceoff formations and variations.

Common aliases: {json.dumps(aliases)}

Handle these cases:
1. Position aliases (RW→right wing, C→center)
2. Relative positions ("5 units left of F1", "between F1 and F2")
3. Face-off positions ("center ice faceoff right wing")
4. Contextual descriptions ("weak side winger", "strong side D")

If relative position, calculate exact coordinates.
If unknown position, find closest match.

Output ONLY in format: x|y|confidence|reasoning
Example: -69|22.5|0.95|Matched "left dot" to left faceoff dot"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a hockey positioning expert. Be precise with coordinates."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            parts = result.split("|")
            
            if len(parts) >= 3:
                try:
                    x = float(parts[0])
                    y = float(parts[1])
                    confidence = float(parts[2]) if len(parts) > 2 else 0.8
                    reasoning = parts[3] if len(parts) > 3 else "LLM match"
                    
                    return {
                        "success": True,
                        "position": position,
                        "zone": zone,
                        "coordinates": {"x": x, "y": y},
                        "positioning_type": "llm",
                        "confidence": confidence,
                        "match_type": "llm",
                        "reasoning": reasoning
                    }
                except (ValueError, IndexError):
                    logger.warning(f"Failed to parse LLM response: {result}")
                    
        except Exception as e:
            logger.warning(f"LLM position mapping failed: {e}")
    
    # 3. Try relative positioning without LLM
    if reference_positions:
        ref_pos_tuples = {}
        for name, coords in reference_positions.items():
            if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                ref_pos_tuples[name] = (coords[0], coords[1])
        
        relative_coords = parse_relative_position(position, ref_pos_tuples)
        if relative_coords:
            x, y = relative_coords
            return {
                "success": True,
                "position": position,
                "zone": zone,
                "coordinates": {"x": x, "y": y},
                "positioning_type": "relative",
                "reference_positions": reference_positions,
                "confidence": 0.9,
                "match_type": "relative"
            }
    
    # 4. Try fuzzy substring matching as last resort
    for key, (x, y) in zone_positions.items():
        if position_lower in key or key in position_lower:
            return {
                "success": True,
                "position": position,
                "zone": zone,
                "coordinates": {"x": x, "y": y},
                "positioning_type": "fuzzy",
                "confidence": 0.7,
                "match_type": "fuzzy",
                "matched_to": key
            }
    
    # 5. No match found - return helpful error with suggestions
    suggestions = list(zone_positions.keys())[:15]
    
    # Add specific faceoff suggestions if that's what they're looking for
    if "faceoff" in position_lower or "face-off" in position_lower:
        faceoff_positions = [k for k in zone_positions.keys() if "faceoff" in k]
        suggestions = faceoff_positions[:5] + suggestions[:10]
    
    return {
        "success": False,
        "position": position,
        "zone": zone,
        "error": f"Could not map position '{position}' to coordinates",
        "suggestions": suggestions
    }

# ============================================================================
# TOOL 9: MAP MOVEMENT TO COORDINATES
# ============================================================================

@mcp.tool("map_movement_to_coordinates")
@trace_tool
def map_movement_to_coordinates(
    from_position: str,
    to_position: str,
    movement_type: str = "skate",
    pattern: Optional[str] = "auto",
    zone: Optional[str] = "offensive",
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Generate complete movement specification with waypoints for curves.
    
    Args:
        from_position: Starting position in natural language
        to_position: Ending position in natural language
        movement_type: Type of movement - "skate", "pass", "shot", "carry"
        pattern: Movement pattern - "auto", "drive", "cross_ice", "cycle", "weave", "direct"
        zone: Context zone for position mapping
        
    Returns:
        Complete movement specification with coordinates and waypoints
    """
    logger.info(f"🏒 [MAP MOVEMENT] {movement_type}: '{from_position}' → '{to_position}'")
    
    # Normalize pattern descriptions to standard names
    pattern_aliases = {
        "rim the puck": "rim",
        "dump and chase": "dump", 
        "dump in": "dump",
        "sauce pass": "sauce",
        "saucer pass": "sauce",
        "chip and chase": "chip",
        "wrap around": "wrap",
        "wraparound": "wrap",
        "bank pass": "bank",
        "stretch pass": "stretch",
        "outlet pass": "stretch",
        "button hook": "button_hook",
        "curl back": "button_hook",
        "cross-ice": "cross_ice",
        "cross ice": "cross_ice"
    }
    
    # Check if pattern matches any alias
    if pattern and pattern.lower() in pattern_aliases:
        pattern = pattern_aliases[pattern.lower()]
        logger.info(f"📝 Normalized pattern to: {pattern}")
    
    # Map positions to coordinates
    from_result = map_position_to_coordinates(from_position, zone)
    to_result = map_position_to_coordinates(to_position, zone)
    
    if not from_result["success"] or not to_result["success"]:
        return {
            "success": False,
            "error": "Could not map positions to coordinates",
            "from_result": from_result,
            "to_result": to_result
        }
    
    from_coords = from_result["coordinates"]
    to_coords = to_result["coordinates"]
    
    # Calculate movement metrics
    dx = to_coords["x"] - from_coords["x"]
    dy = to_coords["y"] - from_coords["y"]
    distance = (dx**2 + dy**2)**0.5
    
    # Try LLM interpretation ONLY for auto pattern detection
    # If user specified a pattern, respect it and skip LLM
    llm_waypoints = None
    if pattern == "auto" and client:
            try:
                # Build context for LLM
                movement_context = f"{movement_type} from {from_position} to {to_position}"
                
                prompt = f"""You are a hockey tactics expert. Analyze this movement and suggest the best pattern.

Movement: {movement_context}
Type: {movement_type}
Zone: {zone.upper()} ZONE
From: {from_coords} 
To: {to_coords}
Distance: {round(distance, 1)} units

HOCKEY MOVEMENT PATTERNS:
- direct: Straight line (passes, shots)
- curve: Gentle curve (standard skating)
- cross_ice: S-curve across ice (40+ Y-axis change)
- drive: Drive to net with curve around defenders
- cycle: Along boards, corner work
- rush: Long fast movement (60+ units)
- rim: Along boards behind net (puck movement)
- dump: High off glass/boards (dump and chase)
- chip: Quick advance past defender (small arc)
- sauce: Over obstacle (elevated pass)
- wrap: Behind net to opposite side
- bank: Off boards to teammate
- stretch: Long outlet pass through zones
- button_hook: Curl back to maintain possession
- weave: Serpentine through traffic

Special considerations:
- "rim the puck" = rim pattern along boards
- "dump it in" = dump pattern from neutral zone
- "sauce pass" = sauce pattern with arc
- "chip and chase" = chip pattern
- "wrap around" = wrap pattern behind net
- "bank pass" = bank pattern off boards
- "stretch pass" = stretch pattern (long distance)
- "button hook" = button_hook pattern (curl back)

Based on the movement description and context, determine:
1. The most appropriate pattern
2. Any special waypoints needed

Output ONLY in format: pattern|waypoint1_x,waypoint1_y|waypoint2_x,waypoint2_y
If no special waypoints needed beyond standard pattern, just output: pattern|standard
Example: rim|89,-20|89,0|89,20
Example: sauce|50,10|standard
Example: drive|standard"""

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a hockey movement pattern expert. Be precise and concise."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=100
                )
                
                result = response.choices[0].message.content.strip()
                parts = result.split("|")
                
                if parts:
                    llm_pattern = parts[0].strip()
                    
                    # Validate pattern name
                    valid_patterns = ["direct", "curve", "cross_ice", "drive", "cycle", "rush", 
                                    "rim", "dump", "chip", "sauce", "wrap", "bank", "stretch", 
                                    "button_hook", "weave"]
                    
                    if llm_pattern in valid_patterns:
                        pattern = llm_pattern
                        logger.info(f"🤖 LLM suggested pattern: {pattern}")
                        
                        # Check for custom waypoints from LLM
                        if len(parts) > 1 and parts[1] != "standard":
                            custom_waypoints = []
                            for waypoint_str in parts[1:]:
                                if "," in waypoint_str:
                                    try:
                                        wx, wy = waypoint_str.split(",")
                                        custom_waypoints.append([float(wx), float(wy)])
                                    except:
                                        pass
                            
                            if custom_waypoints:
                                # Store LLM waypoints to use later
                                llm_waypoints = custom_waypoints
                                logger.info(f"🤖 Using LLM waypoints: {llm_waypoints}")
                    
            except Exception as e:
                logger.warning(f"LLM movement pattern suggestion failed: {e}")
                # Fall back to rule-based detection
        
    # Rule-based pattern detection if LLM didn't set it
    if pattern == "auto":
        if abs(dy) > 40:
            pattern = "cross_ice"
        elif "corner" in from_position.lower() and "net" in to_position.lower():
            pattern = "drive"
        elif "corner" in from_position.lower() and "corner" in to_position.lower():
            pattern = "cycle"
        elif distance > 60:
            pattern = "rush"
        elif movement_type in ["pass", "shot"]:
            pattern = "direct"
        else:
            pattern = "curve"
    
    # Use modular waypoint calculator (unless LLM already provided waypoints)
    from_tuple = (from_coords["x"], from_coords["y"])
    to_tuple = (to_coords["x"], to_coords["y"])
    
    # Use LLM waypoints if provided, otherwise calculate based on pattern
    if llm_waypoints:
        waypoints = llm_waypoints
    else:
        waypoints = calculate_waypoints(from_tuple, to_tuple, pattern)
    
    # Determine style based on movement type
    style_map = {
        "skate": "solid",
        "pass": "dotted",
        "shot": "dashed",
        "carry": "wavy"
    }
    
    movement_spec = {
        "type": movement_type,
        "from_pos": from_coords,
        "to_pos": to_coords,
        "style": style_map.get(movement_type, "solid"),
    }
    
    # Only add waypoints if they exist
    if waypoints:
        movement_spec["waypoints"] = waypoints
    
    return {
        "success": True,
        "movement_spec": movement_spec,
        "pattern_used": pattern,
        "distance": round(distance, 1),
        "from_position": {
            "natural": from_position,
            "coordinates": from_coords,
            "confidence": from_result["confidence"]
        },
        "to_position": {
            "natural": to_position,
            "coordinates": to_coords,
            "confidence": to_result["confidence"]
        },
        "usage_hint": "Add this movement_spec directly to your movements array"
    }

# ============================================================================
# TOOL 10: HEALTH CHECK
# ============================================================================

@mcp.tool("tools_health_check")
@trace_tool
def tools_health_check(session_id: Optional[str] = None) -> Dict[str, Any]:
    """Check health and statistics of the MCP server.
    
    Returns:
        Server health, available resources, and debug info
    """
    logger.info("🔧 [HEALTH] Checking system status")
    
    # Check template availability
    finder = DrillTemplateFinder()
    template_count = len(finder.drill_patterns)
    
    # Check trace sessions
    trace_dir = Path(__file__).parent.parent / "trace_logs"
    trace_count = len(list(trace_dir.glob("session_*.json"))) if trace_dir.exists() else 0
    
    # Check output files
    output_dir = Path(__file__).parent.parent / "outputs"
    png_count = len(list(output_dir.glob("*.png"))) if output_dir.exists() else 0
    svg_count = len(list(output_dir.glob("*.svg"))) if output_dir.exists() else 0
    
    return {
        "status": "healthy",
        "version": "2.1",
        "tools_available": 10,
        "templates_available": template_count,
        "template_types": list(finder.drill_patterns.keys()),
        "trace_sessions": trace_count,
        "diagrams_generated": {"png": png_count, "svg": svg_count, "total": png_count + svg_count},
        "landmarks": len(LANDMARKS),
        "llm_validation": "available" if client else "unavailable (no OpenAI key)",
        "paths": {
            "templates": str(finder.template_dir),
            "output": str(output_dir),
            "traces": str(trace_dir)
        }
    }

# ============================================================================
# ATOMIC PIPELINE TOOLS - STAGE 1: QUERY ANALYSIS
# ============================================================================

@mcp.tool("analyze_hockey_query")
@trace_tool
def analyze_hockey_query(query: str, clarifications: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes a hockey drill query and extracts/enriches components needed for diagram spec.
    Uses LLM with hockey intelligence to fill gaps with educated assumptions.
    
    Args:
        query: Natural language drill/play description
        clarifications: Optional user answers to questions (e.g., {"faceoff_location": "right dot"})
        session_id: Optional session ID for tracing
        
    Returns:
        Analysis with explicit info, assumptions, and components aligned to spec sections
    """
    
    # Prepare clarifications text
    clarifications_text = ""
    if clarifications:
        clarifications_text = "\nUser clarifications provided:\n"
        for key, value in clarifications.items():
            clarifications_text += f"- {key}: {value}\n"
    
    # Create the analysis prompt
    prompt = f"""Analyze this hockey drill/play query and extract components needed for a diagram.
    
QUERY: "{query}"
{clarifications_text}

Your task is to analyze this query with hockey expertise and provide a structured JSON response.

For ANY hockey situation, you MUST:
1. Identify what's explicitly stated vs what needs to be assumed
2. Apply hockey knowledge to fill gaps (e.g., faceoffs need 11 players total)
3. Make educated assumptions with confidence levels
4. Generate questions for critical unknowns

Output a JSON object with this EXACT structure:
{{
    "original_query": "the original query",
    "explicit_info": {{
        "situation": "faceoff/drill/play/etc",
        "zone": "offensive/defensive/neutral if mentioned",
        "key_actions": ["list of mentioned actions"],
        // other explicitly mentioned details
    }},
    "components_with_assumptions": {{
        "rink": {{
            "view": "offensive/defensive/full",
            "assumption": "reasoning for this choice",
            "confidence": 0.0-1.0
        }},
        "players": [
            {{
                "id": "C/LW/RW/LD/RD/OC/etc",
                "type": "center/winger/defense/goalie",
                "team": "home/away",
                "position_desc": "natural language position description",
                "assumption": "why this player is needed",
                "confidence": 0.0-1.0
            }}
            // Include ALL players needed for the situation
        ],
        "movements": [
            {{
                "id": "m1/m2/etc",
                "type": "pass/shot/skate/carry",
                "desc": "movement description",
                "from_player": "player ID",
                "to_area": "target area description",
                "assumption": "reasoning for this movement",
                "confidence": 0.0-1.0
            }}
        ],
        "zones": [],
        "annotations": [
            {{
                "text": "title or label text",
                "position_desc": "where to place it",
                "assumption": "why this annotation",
                "confidence": 0.0-1.0
            }}
        ],
        "equipment": []
    }},
    "questions_for_user": [
        {{
            "question": "question text",
            "key": "parameter_key",
            "options": ["option1", "option2"],
            "critical": true/false,
            "confidence": 0.0-1.0
        }}
    ],
    "metadata": {{
        "type": "drill/play",
        "phase": "offensive/defensive/neutral/transition",
        "key_players": ["list of key player IDs"]
    }}
}}

IMPORTANT HOCKEY KNOWLEDGE:
- Faceoffs require both teams: 5v5 plus goalie (11 total) for zone faceoffs
- "Weak side" for right dot = left wing, for left dot = right wing
- "Bump back" = faceoff win technique sending puck backward
- Offensive zone faceoffs: attacking team at points, defending team protecting net
- Always include goalie if there's a shot
- Standard positions: C, LW, RW, LD, RD for home; OC, OW1, OW2, OD1, OD2, G for away

Apply your hockey expertise to provide a complete, realistic analysis."""
    
    # Use LLM to analyze
    if not client:
        logger.warning("OpenAI client not available, returning basic analysis")
        return {
            "error": "OpenAI client not configured",
            "original_query": query,
            "suggestion": "Configure OPENAI_API_KEY to enable LLM analysis"
        }
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use gpt-4o-mini for better hockey understanding
            messages=[
                {"role": "system", "content": "You are a hockey coach and diagram expert. Analyze drills and plays with deep hockey knowledge."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for consistent analysis
            response_format={"type": "json_object"}  # Ensure JSON response
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Apply any clarifications that weren't processed by LLM
        if clarifications:
            result["user_clarifications"] = clarifications
        
        # Log summary
        player_count = len(result.get("components_with_assumptions", {}).get("players", []))
        movement_count = len(result.get("components_with_assumptions", {}).get("movements", []))
        logger.info(f"🔍 Query analysis complete: {player_count} players, {movement_count} movements")
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return {
            "error": "Failed to parse analysis response",
            "original_query": query,
            "raw_response": response.choices[0].message.content if response else None
        }
    except Exception as e:
        logger.error(f"Query analysis failed: {e}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "original_query": query
        }

# ============================================================================
        if zone == "offensive":
            result["components_with_assumptions"]["rink"] = {
                "view": "offensive",
                "assumption": "Focus on offensive zone for offensive zone faceoff",
                "confidence": 0.95
            }
            
            # Build player list for offensive zone faceoff
            is_right_dot = dot_location == "right dot"
            
            # Home team (offensive)
            players = [
                {
                    "id": "C",
                    "type": "center",
                    "team": "home",
                    "position_desc": f"at {dot_location or 'faceoff dot'} (taking draw)",
                    "assumption": "Center takes the faceoff",
                    "confidence": 1.0
                },
                {
                    "id": "LW",
                    "type": "winger",
                    "team": "home",
                    "position_desc": f"left wing position on circle {'(weak side)' if is_right_dot else '(strong side)'}",
                    "assumption": "Standard offensive zone faceoff formation",
                    "confidence": 0.9
                },
                {
                    "id": "RW",
                    "type": "winger",
                    "team": "home",
                    "position_desc": f"right wing position on circle {'(strong side)' if is_right_dot else '(weak side)'}",
                    "assumption": "Standard offensive zone faceoff formation",
                    "confidence": 0.9
                },
                {
                    "id": "LD",
                    "type": "defense",
                    "team": "home",
                    "position_desc": "left point position",
                    "assumption": "Left D at point for offensive zone faceoff",
                    "confidence": 0.9
                },
                {
                    "id": "RD",
                    "type": "defense",
                    "team": "home",
                    "position_desc": "right point position",
                    "assumption": "Right D at point for offensive zone faceoff",
                    "confidence": 0.9
                }
            ]
            
            # Away team (defensive)
            if not clarifications or clarifications.get("show_opposing", "all") == "all":
                players.extend([
                    {
                        "id": "OC",
                        "type": "center",
                        "team": "away",
                        "position_desc": f"opposing center at {dot_location or 'faceoff dot'}",
                        "assumption": "Opposing center for faceoff",
                        "confidence": 1.0
                    },
                    {
                        "id": "OW1",
                        "type": "winger",
                        "team": "away",
                        "position_desc": "opposing winger on strong side",
                        "assumption": "Defensive faceoff formation",
                        "confidence": 0.8
                    },
                    {
                        "id": "OW2",
                        "type": "winger",
                        "team": "away",
                        "position_desc": "opposing winger on weak side",
                        "assumption": "Defensive faceoff formation",
                        "confidence": 0.8
                    },
                    {
                        "id": "OD1",
                        "type": "defense",
                        "team": "away",
                        "position_desc": "opposing defense protecting net (strong side)",
                        "assumption": "Defensive positioning",
                        "confidence": 0.85
                    },
                    {
                        "id": "OD2",
                        "type": "defense",
                        "team": "away",
                        "position_desc": "opposing defense protecting net (weak side)",
                        "assumption": "Defensive positioning",
                        "confidence": 0.85
                    }
                ])
            
            # Add goalie if shot is mentioned
            if "shot" in query.lower() or "shoot" in query.lower():
                players.append({
                    "id": "G",
                    "type": "goalie",
                    "team": "away",
                    "position_desc": "in net",
                    "assumption": "Goalie present for shot scenario",
                    "confidence": 1.0
                })
            
            result["components_with_assumptions"]["players"] = players
    
    # Parse movements from query
    movements = []
    
    # Look for bump/win back
    if "bump" in query.lower() and "back" in query.lower():
        movements.append({
            "id": "m1",
            "type": "pass",
            "desc": "Center bumps puck back",
            "from_player": "C",
            "to_area": "behind faceoff circle",
            "assumption": "Bump back is a faceoff win technique",
            "confidence": 0.95
        })
    
    # Look for swing/move over
    if "swing" in query.lower() or "swings over" in query.lower():
        # Determine which winger based on weak/strong side
        winger = None
        if "weak side" in query.lower():
            if result["explicit_info"].get("faceoff_location") == "right dot":
                winger = "LW"  # Left wing is weak side for right dot
            elif result["explicit_info"].get("faceoff_location") == "left dot":
                winger = "RW"  # Right wing is weak side for left dot
        
        if winger:
            movements.append({
                "id": "m2",
                "type": "skate",
                "desc": f"{winger} swings over to get puck",
                "from_player": winger,
                "to_area": "behind faceoff circle",
                "assumption": "Winger retrieves bumped puck",
                "confidence": 0.9
            })
            
            # Add carry to shooting position
            shot_location = clarifications.get("shot_location", "shooting position") if clarifications else "shooting position"
            if "slot" in shot_location:
                movements.append({
                    "id": "m3",
                    "type": "carry",
                    "desc": f"{winger} carries puck to slot",
                    "from_player": winger,
                    "to_area": "slot",
                    "assumption": "Move to slot for shot",
                    "confidence": 0.95
                })
    
    # Look for shot
    if "shot" in query.lower() or "shoot" in query.lower():
        shooter = None
        for m in movements:
            if "carry" in m.get("type", "") or "skate" in m.get("type", ""):
                shooter = m.get("from_player")
        
        if shooter:
            movements.append({
                "id": f"m{len(movements)+1}",
                "type": "shot",
                "desc": f"{shooter} shoots on net",
                "from_player": shooter,
                "to_area": "net",
                "assumption": "Final play action is shot",
                "confidence": 1.0
            })
    
    result["components_with_assumptions"]["movements"] = movements
    
    # Add annotations
    result["components_with_assumptions"]["annotations"] = [
        {
            "text": "Offensive Zone Faceoff Play",
            "position_desc": "title",
            "assumption": "Title describes the play",
            "confidence": 0.9
        }
    ]
    
    # Detect drill vs play
    if any(word in query.lower() for word in ["drill", "practice", "exercise"]):
        result["metadata"]["type"] = "drill"
    else:
        result["metadata"]["type"] = "play"
    
    # Generate questions for unclear elements
    if "faceoff_location" not in result["explicit_info"] and not clarifications:
        result["questions_for_user"].append({
            "question": "Which faceoff dot - left or right?",
            "key": "faceoff_location",
            "options": ["left dot", "right dot"],
            "critical": True,
            "confidence": 0.5
        })
    
    # Add metadata
    result["metadata"]["phase"] = result["explicit_info"].get("faceoff_zone", "unknown")
    result["metadata"]["key_players"] = list(set([m.get("from_player") for m in movements if m.get("from_player")]))
    
    logger.info(f"🔍 Query analysis complete: {len(result['components_with_assumptions']['players'])} players, {len(movements)} movements")
    
    return result

# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

def main():
    """Main entry point for the Hockey Diagram MCP server v2."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hockey Diagram MCP Server v2")
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
        
        logger.info("🏒 Starting Hockey Diagram MCP Server v2 (stdio mode)")
        try:
            asyncio.run(run_stdio())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
    else:
        # SSE/HTTP mode
        logger.info(f"🏒 Starting Hockey Diagram MCP Server v2 at http://{args.host}:{args.port}")
        mcp.run(transport="sse", host=args.host, port=args.port)

if __name__ == "__main__":
    main()