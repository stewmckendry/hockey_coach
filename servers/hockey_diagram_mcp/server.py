"""
FastMCP server for generating precise hockey tactical diagrams.
Provides natural language interface for creating NHL-regulation hockey diagrams.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from servers.hockey_diagram_mcp.generator import HockeyDiagramGenerator, Player, Movement, Zone
from servers.hockey_diagram_mcp.parser import HockeyPromptParser, DiagramSpec
from servers.hockey_diagram_mcp.enhanced_parser import EnhancedHockeyParser
from servers.hockey_diagram_mcp.two_stage_parser import TwoStageHockeyParser
from servers.hockey_diagram_mcp.elements import FORMATIONS, get_formation, list_available_elements

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Hockey Diagram Generator")

# Initialize components
diagram_generator = HockeyDiagramGenerator()
prompt_parser = HockeyPromptParser()
enhanced_parser = EnhancedHockeyParser()
two_stage_parser = TwoStageHockeyParser()

# Storage directory for generated diagrams
DIAGRAM_DIR = Path("servers/hockey_diagram_mcp/generated_diagrams")
DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)

def _filter_players_by_view(diagram_spec, view: str):
    """
    Filter players based on view boundaries to improve diagram clarity.
    Removes players that are outside the specified view area.
    """
    if view == "full":
        return diagram_spec  # No filtering needed for full view
    
    # Define view boundaries (expanded for better tactical visibility)
    # NOTE: Some formations may have coordinate mapping issues - these boundaries are more permissive to debug
    view_bounds = {
        "offensive": {"x_min": 15, "x_max": 100, "y_min": -42.5, "y_max": 42.5},  # Include defenders pinching at blue line
        "defensive": {"x_min": -100, "x_max": 100, "y_min": -42.5, "y_max": 42.5},  # TEMP: Allow all X coords to debug coordinate mapping issue
        "neutral": {"x_min": -35, "x_max": 35, "y_min": -42.5, "y_max": 42.5}  # Allow drill progressions beyond center
    }
    
    if view not in view_bounds:
        return diagram_spec
    
    bounds = view_bounds[view]
    filtered_players = []
    
    for player in diagram_spec.players:
        # Check if player is within view boundaries
        if (bounds["x_min"] <= player.x <= bounds["x_max"] and 
            bounds["y_min"] <= player.y <= bounds["y_max"]):
            filtered_players.append(player)
        else:
            logger.info(f"Filtered out {player.position} at ({player.x}, {player.y}) - outside {view} view")
    
    # Update diagram spec with filtered players
    diagram_spec.players = filtered_players
    
    # Also filter movements that reference removed players
    if diagram_spec.movements:
        player_positions = {p.position for p in filtered_players}
        filtered_movements = []
        
        for movement in diagram_spec.movements:
            # Keep movement if both from and to positions are still present
            from_pos = movement.from_position
            to_pos = movement.to_position
            
            # Handle to_position being coordinates vs player position
            if isinstance(to_pos, list):
                to_pos_in_bounds = (bounds["x_min"] <= to_pos[0] <= bounds["x_max"] and 
                                  bounds["y_min"] <= to_pos[1] <= bounds["y_max"])
            else:
                to_pos_in_bounds = to_pos in player_positions
            
            if from_pos in player_positions and to_pos_in_bounds:
                filtered_movements.append(movement)
            else:
                logger.info(f"Filtered out movement {from_pos} → {to_pos} - player not in {view} view")
        
        diagram_spec.movements = filtered_movements
    
    return diagram_spec

@mcp.tool()
async def generate_hockey_diagram(
    prompt: str,
    diagram_type: Optional[str] = "tactical",
    view: Optional[str] = "full",
    output_format: Optional[str] = "png"
) -> Dict[str, Any]:
    """
    Generate a hockey diagram from natural language instructions.
    
    Args:
        prompt: Natural language description (e.g., "2-1-2 forecheck with center pressuring puck carrier")
        diagram_type: Type of diagram - 'tactical', 'drill', or 'system' (default: tactical)
        view: Rink view - 'full', 'offensive', 'defensive', or 'neutral' (default: full)
        output_format: Output format - 'png' or 'svg' (default: png)
    
    Returns:
        Dictionary containing:
        - diagram_path: Path to saved diagram file
        - base64_image: Base64 encoded image data
        - diagram_spec: Parsed specification used to generate diagram
        - generation_time: Time taken to generate
    """
    start_time = datetime.now()
    logger.info(f"Generating hockey diagram: {prompt[:50]}...")
    
    try:
        # Parse the natural language prompt
        context = {
            "diagram_type": diagram_type,
            "requested_view": view
        }
        
        # Try two-stage parser first for best accuracy
        try:
            diagram_spec = await two_stage_parser.parse_prompt(prompt, context)
            logger.info("Using two-stage parser for maximum accuracy")
        except Exception as two_stage_error:
            logger.warning(f"Two-stage parser failed: {two_stage_error}, falling back to enhanced parser")
            # Fallback to enhanced parser
            try:
                diagram_spec = await enhanced_parser.parse_prompt(prompt, context)
                logger.info("Using enhanced parser")
            except Exception as enhanced_error:
                logger.warning(f"Enhanced parser failed: {enhanced_error}, falling back to preset parser")
                # Final fallback to preset-based parser
                diagram_spec = await prompt_parser.parse_with_presets(prompt, FORMATIONS)
        
        # Override view if specified
        if view != "full":
            diagram_spec.view = view
            
        # Apply view filtering to remove players outside view boundaries
        diagram_spec = _filter_players_by_view(diagram_spec, view)
            
        # Convert parsed spec to generator objects
        players = [
            Player(
                position=p.position,
                x=p.x,
                y=p.y,
                team=p.team,
                has_puck=p.has_puck
            ) for p in diagram_spec.players
        ]
        
        movements = None
        if diagram_spec.movements:
            movements = []
            for m in diagram_spec.movements:
                # Handle both string and list to_position
                to_pos = m.to_position
                if isinstance(to_pos, list):
                    to_pos = tuple(to_pos)
                movements.append(
                    Movement(
                        from_position=m.from_position,
                        to_position=to_pos,
                        movement_type=m.movement_type
                    )
                )
        
        zones = None
        if diagram_spec.zones:
            zones = []
            for z in diagram_spec.zones:
                # Handle both string and list area
                area = z.area
                if isinstance(area, list):
                    area = tuple(area)
                zones.append(
                    Zone(
                        zone_type=z.zone_type,
                        area=area,
                        team=z.team,
                        opacity=getattr(z, 'opacity', 0.2)
                    )
                )
        
        # Generate the diagram
        base64_image = diagram_generator.generate_diagram(
            players=players,
            movements=movements,
            zones=zones,
            view=diagram_spec.view,
            title=diagram_spec.title,
            output_format=output_format
        )
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hockey_diagram_{timestamp}.{output_format}"
        filepath = DIAGRAM_DIR / filename
        
        diagram_generator.save_to_file(base64_image, str(filepath), output_format)
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Successfully generated diagram: {filepath}")
        
        # Always return file path only to avoid token limit issues
        return {
            "diagram_path": str(filepath),
            "message": f"Diagram successfully generated and saved to {filepath}",
            "diagram_spec": diagram_spec.dict(),
            "generation_time": generation_time,
            "success": True
        }
        
    except ValueError as e:
        logger.error(f"Validation error in diagram generation: {e}")
        return {
            "error": f"Invalid input: {str(e)}",
            "success": False,
            "generation_time": (datetime.now() - start_time).total_seconds(),
            "error_type": "validation"
        }
    except ConnectionError as e:
        logger.error(f"Connection error (likely OpenAI API): {e}")
        return {
            "error": "Failed to connect to AI service. Please check your API key and connection.",
            "success": False,
            "generation_time": (datetime.now() - start_time).total_seconds(),
            "error_type": "connection"
        }
    except Exception as e:
        logger.error(f"Unexpected error generating diagram: {e}", exc_info=True)
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "success": False,
            "generation_time": (datetime.now() - start_time).total_seconds(),
            "error_type": "unknown",
            "fallback_used": False
        }

@mcp.tool()
async def list_hockey_formations() -> Dict[str, List[str]]:
    """
    List all available preset hockey formations and tactical elements.
    
    Returns:
        Dictionary containing available formations, zones, and patterns
    """
    return list_available_elements()

@mcp.tool()
async def get_formation_details(formation_name: str) -> Dict[str, Any]:
    """
    Get detailed specification for a specific formation.
    
    Args:
        formation_name: Name of the formation (e.g., '2-1-2_forecheck', '1-3-1_powerplay')
    
    Returns:
        Formation specification including player positions and movements
    """
    try:
        if not formation_name:
            return {
                "error": "Formation name is required",
                "success": False,
                "available_formations": list(FORMATIONS.keys())
            }
        
        formation = get_formation(formation_name)
        if not formation:
            # Try to find similar formations
            similar = [f for f in FORMATIONS.keys() if formation_name.lower() in f.lower()]
            return {
                "error": f"Formation '{formation_name}' not found",
                "success": False,
                "available_formations": list(FORMATIONS.keys()),
                "suggestions": similar if similar else None
            }
        
        return {
            "formation": formation,
            "success": True
        }
    except Exception as e:
        logger.error(f"Error getting formation details: {e}")
        return {
            "error": f"Failed to retrieve formation: {str(e)}",
            "success": False
        }

@mcp.resource("hockey://diagram_examples")
async def get_diagram_examples() -> str:
    """
    Get example prompts for generating hockey diagrams.
    """
    examples = """
# Hockey Diagram Generation Examples

## Basic Formations
- "Create a 2-1-2 forecheck with F1 pressuring behind the net"
- "Show 1-3-1 power play umbrella formation"
- "Draw box penalty kill formation in defensive zone"
- "Illustrate neutral zone trap with 1-3-1 setup"

## Plays with Movement
- "2-1-2 forecheck with weak side winger rotating to support"
- "Breakout play with D-to-D pass and winger support"
- "Offensive zone cycle with low forward rotation"
- "Power play entry with drop pass at blue line"

## Drills
- "3v2 rush drill starting from neutral zone"
- "Corner battle drill with 2v2 in offensive zone"
- "Defensive zone coverage drill with 3v3"
- "Passing drill with figure-8 pattern"

## Zone Views
- "Offensive zone face-off play" (with view='offensive')
- "Defensive zone coverage" (with view='defensive')
- "Neutral zone regroup" (with view='neutral')

## Advanced Specifications
- "Power play with overload on left side, movement from half-wall to slot"
- "Penalty kill with aggressive pressure on puck carrier, box rotation"
- "Breakout with reverse behind net, center swing support"
"""
    return examples

@mcp.resource("hockey://generated_diagrams")
async def list_generated_diagrams() -> str:
    """
    List all previously generated diagrams.
    """
    diagrams = []
    for file in DIAGRAM_DIR.glob("hockey_diagram_*.png"):
        diagrams.append(str(file.name))
    
    return json.dumps({
        "diagram_count": len(diagrams),
        "diagrams": diagrams[-20:]  # Last 20 diagrams
    }, indent=2)

# Health check endpoint
@mcp.resource("hockey://health")
async def health_check() -> str:
    """Check if the hockey diagram MCP server is running."""
    return json.dumps({
        "status": "healthy",
        "service": "Hockey Diagram MCP Server",
        "version": "1.0.0",
        "components": {
            "generator": "operational",
            "parser": "operational",
            "formations": len(FORMATIONS)
        }
    })

def main():
    """Run the MCP server."""
    logger.info("Starting Hockey Diagram MCP Server...")
    logger.info(f"Diagram storage directory: {DIAGRAM_DIR}")
    logger.info(f"Available formations: {len(FORMATIONS)}")
    
    # FastMCP handles stdio transport automatically
    mcp.run()

if __name__ == "__main__":
    main()