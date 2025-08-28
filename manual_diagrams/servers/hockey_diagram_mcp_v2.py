#!/usr/bin/env python3
"""
Hockey Diagram MCP Server v2 - Streamlined 8-tool design.
Following n8n pattern for clarity and reduced cognitive load.
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

# OpenAI for LLM validation (lazy load)
try:
    from openai import OpenAI
    client = OpenAI()
except:
    client = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
1. Build spec using schemas from `search_diagram_node`:
   - "players" - Player positions and types
   - "movements" - Skating, passing, shooting patterns
   - "rink" - View and zone configuration
2. Call `validate_diagram_node_minimal` for each section

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
            "search_diagram_node (for each spec section)",
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
def search_diagram_node(node_type: str) -> Dict[str, Any]:
    """Get schema and instructions for a diagram spec node.
    
    Args:
        node_type: Type of node (players|movements|rink|zones|annotations)
        
    Returns:
        Schema, enums, examples, and constraints for the node type
    """
    logger.info(f"📋 [SCHEMA] Getting schema for: {node_type}")
    
    schemas = {
        "players": {
            "description": "Player positions and configurations",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["type", "position", "team", "has_puck", "coordinates"],
                    "properties": {
                        "type": {"enum": ["forward", "defense", "goalie", "coach"]},
                        "position": {"type": "string", "pattern": "^[FDG][0-9]?$|^COACH$"},
                        "team": {"enum": ["home", "away"]},
                        "has_puck": {"type": "boolean"},
                        "coordinates": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number", "minimum": -100, "maximum": 100},
                                "y": {"type": "number", "minimum": -42.5, "maximum": 42.5}
                            }
                        },
                        "label": {"type": "string"}
                    }
                }
            },
            "enums": {
                "type": ["forward", "defense", "goalie", "coach"],
                "team": ["home", "away"],
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
                "offensive_zone": {
                    "left_dot": {"x": -69, "y": 22.5},
                    "right_dot": {"x": -69, "y": -22.5},
                    "slot": {"x": -69, "y": 0},
                    "hash_left": {"x": -75, "y": 22.5},
                    "hash_right": {"x": -75, "y": -22.5},
                    "net_front": {"x": -86, "y": 0},
                    "goal_line": {"x": -89, "y": 0},
                    "left_corner": {"x": -89, "y": 36},
                    "right_corner": {"x": -89, "y": -36}
                },
                "neutral_zone": {
                    "center_ice": {"x": 0, "y": 0},
                    "blue_line_offensive": {"x": -25, "y": 0},
                    "blue_line_defensive": {"x": 25, "y": 0}
                },
                "defensive_zone": {
                    "behind_net": {"x": 89, "y": 0},
                    "left_post": {"x": 89, "y": 6},
                    "right_post": {"x": 89, "y": -6},
                    "left_dot": {"x": 69, "y": 22.5},
                    "right_dot": {"x": 69, "y": -22.5}
                }
            },
            "standard_positions": STANDARD_POSITIONS
        },
        "movements": {
            "description": "Movement patterns (skating, passing, shooting)",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["type", "from_pos", "to_pos", "style"],
                    "properties": {
                        "type": {"enum": ["skate", "pass", "shot", "carry", "pressure"]},
                        "from_pos": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            }
                        },
                        "to_pos": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            }
                        },
                        "style": {"enum": ["solid", "dashed", "dotted", "wavy"]},
                        "waypoints": {"type": "array", "items": {"type": "object"}},
                        "label": {"type": "string"}
                    }
                }
            },
            "enums": {
                "type": ["skate", "pass", "shot", "carry", "pressure"],
                "style": ["solid", "dashed", "dotted", "wavy"]
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
            "schema": {
                "type": "object",
                "properties": {
                    "view": {"enum": ["full", "half", "offensive", "defensive", "neutral"]}
                }
            },
            "enums": {
                "view": ["full", "half", "offensive", "defensive", "neutral"]
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
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"enum": ["cone", "pylon", "tire", "net", "line", "area"]},
                        "coordinates": {"type": "object"},
                        "size": {"type": "number"},
                        "label": {"type": "string"}
                    }
                }
            },
            "enums": {
                "type": ["cone", "pylon", "tire", "net", "line", "area"]
            }
        },
        "annotations": {
            "description": "Text annotations and notes",
            "schema": {
                "type": "array",
                "items": {"type": "string"}
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
    
    return schemas[node_type]

# ============================================================================
# TOOL 3: SEARCH DIAGRAM TEMPLATE
# ============================================================================

@mcp.tool("search_diagram_template")
def search_diagram_template(query: str, template_type: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
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
def fetch_diagram_template(template_name: str) -> Dict[str, Any]:
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
def validate_diagram_node_minimal(node_type: str, node_data: Any) -> Dict[str, Any]:
    """Validate a single node of the diagram spec.
    
    Args:
        node_type: Type of node (players|movements|rink|zones|annotations)
        node_data: The node data to validate
        
    Returns:
        Validation results with issues and fixes
    """
    logger.info(f"✅ [VALIDATE NODE] {node_type}")
    
    issues = []
    warnings = []
    fixes = {}
    
    if node_type == "players":
        if not isinstance(node_data, list):
            issues.append("Players must be a list")
            return {"valid": False, "issues": issues}
        
        has_puck_count = 0
        for i, player in enumerate(node_data):
            # Check required fields
            required = ["type", "position", "team", "has_puck", "coordinates"]
            for field in required:
                if field not in player:
                    issues.append(f"Player {i}: missing '{field}'")
                    fixes[f"player_{i}"] = {field: "default_value"}
            
            # Check has_puck
            if player.get("has_puck", False):
                has_puck_count += 1
        
        if has_puck_count > 1:
            issues.append("Multiple players have puck (only one allowed)")
        elif has_puck_count == 0:
            warnings.append("No player has puck - is this intentional?")
            
    elif node_type == "movements":
        if not isinstance(node_data, list):
            issues.append("Movements must be a list")
            return {"valid": False, "issues": issues}
        
        for i, movement in enumerate(node_data):
            # Check required fields
            required = ["type", "from_pos", "to_pos", "style"]
            for field in required:
                if field not in movement:
                    issues.append(f"Movement {i}: missing '{field}'")
            
            # Check cross-ice
            if movement.get("type") == "skate":
                from_y = movement.get("from_pos", {}).get("y", 0)
                to_y = movement.get("to_pos", {}).get("y", 0)
                if abs(to_y - from_y) > 40:
                    if "waypoints" not in movement:
                        warnings.append(f"Movement {i}: Cross-ice movement should have waypoints for smooth curve")
                        
    elif node_type == "rink":
        if not isinstance(node_data, dict):
            issues.append("Rink must be an object")
            return {"valid": False, "issues": issues}
        
        if "view" not in node_data:
            warnings.append("No view specified, will use 'offensive' by default")
            fixes["rink"] = {"view": "offensive"}
            
    elif node_type == "annotations":
        if not isinstance(node_data, list):
            issues.append("Annotations must be a list")
            return {"valid": False, "issues": issues}
            
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "fixes": fixes if fixes else None
    }

# ============================================================================
# TOOL 6: VALIDATE DIAGRAM SPEC FULL
# ============================================================================

@mcp.tool("validate_diagram_spec_full")
def validate_diagram_spec_full(spec: Dict[str, Any], original_request: Optional[str] = None) -> Dict[str, Any]:
    """Complete validation of entire diagram specification.
    
    Args:
        spec: Complete diagram specification
        original_request: Original drill description for context
        
    Returns:
        Comprehensive validation with structure, spatial, and hockey sense checks
    """
    logger.info(f"🔍 [VALIDATE FULL] Spec with {len(spec.get('players', []))} players")
    
    # Structure validation
    structure_issues = validate_spec_dict(spec)
    structure_valid = len(structure_issues) == 0
    
    # Spatial validation
    spatial_issues = []
    if "players" in spec:
        for i, p1 in enumerate(spec["players"]):
            for j, p2 in enumerate(spec["players"][i+1:], i+1):
                dist = ((p1["coordinates"]["x"] - p2["coordinates"]["x"])**2 + 
                       (p1["coordinates"]["y"] - p2["coordinates"]["y"])**2)**0.5
                if dist < 5:
                    spatial_issues.append(f"Players {p1.get('position', i)} and {p2.get('position', j)} too close ({dist:.1f} units)")
    
    spatial_valid = len(spatial_issues) == 0
    
    # Hockey sense validation (LLM if available)
    hockey_sense_valid = True
    llm_feedback = None
    
    if original_request and client:
        try:
            prompt = f"""
            Drill request: {original_request}
            
            Spec has:
            - {len(spec.get('players', []))} players
            - {len(spec.get('movements', []))} movements
            - View: {spec.get('rink', {}).get('view', 'unknown')}
            
            Does this match the drill request? Respond with:
            1. YES/NO
            2. Brief issue if NO (one line)
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            
            llm_response = response.choices[0].message.content.strip()
            if llm_response.startswith("NO"):
                hockey_sense_valid = False
                llm_feedback = llm_response.split("\n")[1] if "\n" in llm_response else "Doesn't match drill description"
        except:
            pass
    
    # Compile results
    all_issues = structure_issues + spatial_issues
    if llm_feedback:
        all_issues.append(llm_feedback)
    
    suggestions = []
    if "players" in spec and len(spec["players"]) == 1 and "give" in str(original_request).lower():
        suggestions.append("Give-and-go requires 2+ players")
    
    return {
        "valid": structure_valid and spatial_valid and hockey_sense_valid,
        "structure_valid": structure_valid,
        "spatial_valid": spatial_valid, 
        "hockey_sense_valid": hockey_sense_valid,
        "issues": all_issues,
        "suggestions": suggestions,
        "llm_feedback": llm_feedback
    }

# ============================================================================
# TOOL 7: GENERATE DIAGRAM
# ============================================================================

@mcp.tool("generate_diagram")
def generate_diagram(spec: Dict[str, Any], output_name: Optional[str] = None) -> Dict[str, Any]:
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
    diagram_spec = dict_to_diagram_spec(spec)
    if not diagram_spec:
        return {
            "success": False,
            "error": "Failed to convert spec to diagram",
            "trace": trace
        }
    trace[-1]["status"] = "success"
    
    # Step 2: Generate diagram
    trace.append({"step": 2, "action": "generate_svg", "status": "starting"})
    try:
        builder = DiagramBuilder()
        svg_content = builder.build(diagram_spec)
        trace[-1]["status"] = "success"
    except Exception as e:
        trace[-1]["status"] = "failed"
        trace[-1]["error"] = str(e)
        return {
            "success": False,
            "error": f"Failed to generate diagram: {e}",
            "trace": trace
        }
    
    # Step 3: Save files
    trace.append({"step": 3, "action": "save_files", "status": "starting"})
    
    # Generate output name
    if not output_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"diagram_{timestamp}"
    
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Save SVG
    svg_path = output_dir / f"{output_name}.svg"
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    
    # Save spec JSON
    spec_path = output_dir / f"{output_name}.json"
    with open(spec_path, 'w') as f:
        json.dump(spec, f, indent=2)
    
    trace[-1]["status"] = "success"
    trace[-1]["files"] = [str(svg_path), str(spec_path)]
    
    # Complete session
    session_data = complete_session(success=True, lessons="Diagram generated successfully")
    
    return {
        "success": True,
        "image_path": str(svg_path),
        "spec_path": str(spec_path),
        "trace": trace,
        "session_id": session_data.get("session_id"),
        "total_tool_calls": len(session_data.get("tool_calls", [])),
        "upload_instructions": "Use google-sheets MCP tool to upload trace with your reasoning",
        "trace_data": get_session_for_sheets()
    }

# ============================================================================
# TOOL 8: HEALTH CHECK
# ============================================================================

@mcp.tool("tools_health_check")
def tools_health_check() -> Dict[str, Any]:
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
    output_dir = Path(__file__).parent.parent / "output"
    output_count = len(list(output_dir.glob("*.svg"))) if output_dir.exists() else 0
    
    return {
        "status": "healthy",
        "version": "2.0",
        "tools_available": 8,
        "templates_available": template_count,
        "template_types": list(finder.drill_patterns.keys()),
        "trace_sessions": trace_count,
        "diagrams_generated": output_count,
        "standard_positions": len(STANDARD_POSITIONS),
        "landmarks": len(LANDMARKS),
        "llm_validation": "available" if client else "unavailable (no OpenAI key)",
        "paths": {
            "templates": str(finder.template_dir),
            "output": str(output_dir),
            "traces": str(trace_dir)
        }
    }

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