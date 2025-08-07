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

# Add current directory to path for local imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generator import HockeyDiagramGenerator, Player, Movement, CoverageZone as Zone
from parser import HockeyPromptParser, DiagramSpec
from enhanced_parser import EnhancedHockeyParser
from two_stage_parser import TwoStageHockeyParser
from elements import FORMATIONS, get_formation, list_available_elements
from diagram_cache import DiagramCacheManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Hockey Diagram Generator")

# Initialize components
diagram_generator = HockeyDiagramGenerator()
cache_manager = DiagramCacheManager()

# Lazy initialization for parsers to ensure env vars are loaded
_prompt_parser = None
_enhanced_parser = None
_two_stage_parser = None

def get_prompt_parser():
    global _prompt_parser
    if _prompt_parser is None:
        _prompt_parser = HockeyPromptParser()
    return _prompt_parser

def get_enhanced_parser():
    global _enhanced_parser
    if _enhanced_parser is None:
        _enhanced_parser = EnhancedHockeyParser()
    return _enhanced_parser

def get_two_stage_parser():
    global _two_stage_parser
    if _two_stage_parser is None:
        _two_stage_parser = TwoStageHockeyParser()
    return _two_stage_parser

# Storage directory for generated diagrams - use absolute path to avoid nesting
DIAGRAM_DIR = Path(__file__).parent / "generated_diagrams"
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
            diagram_spec = await get_two_stage_parser().parse_prompt(prompt, context)
            logger.info("Using two-stage parser for maximum accuracy")
        except Exception as two_stage_error:
            logger.warning(f"Two-stage parser failed: {two_stage_error}, falling back to enhanced parser")
            # Fallback to enhanced parser
            try:
                diagram_spec = await get_enhanced_parser().parse_prompt(prompt, context)
                logger.info("Using enhanced parser")
            except Exception as enhanced_error:
                logger.warning(f"Enhanced parser failed: {enhanced_error}, falling back to preset parser")
                # Final fallback to preset-based parser
                diagram_spec = await get_prompt_parser().parse_with_presets(prompt, FORMATIONS)
        
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

async def parse_hockey_formation(
    prompt: str,
    return_structured: bool = True
) -> Dict[str, Any]:
    """
    Parse a hockey formation using the two-stage parser.
    Returns structured data ready for diagram generation.
    
    Args:
        prompt: Natural language description of the hockey formation/play
        return_structured: Whether to return structured format (default: True)
    
    Returns:
        Dictionary containing parsed formation data or error information
    """
    start_time = datetime.now()
    logger.info(f"Parsing hockey formation: {prompt[:50]}...")
    
    try:
        # Use two-stage parser for maximum accuracy
        diagram_spec = await get_two_stage_parser().parse_prompt(prompt)
        
        if return_structured:
            return {
                "success": True,
                "formation": diagram_spec.diagram_type,
                "players": [p.dict() for p in diagram_spec.players],
                "movements": [m.dict() for m in diagram_spec.movements] if diagram_spec.movements else [],
                "zones": [z.dict() for z in diagram_spec.zones] if diagram_spec.zones else [],
                "view": diagram_spec.view,
                "title": diagram_spec.title,
                "parsing_time": (datetime.now() - start_time).total_seconds()
            }
        else:
            return {
                "success": True,
                "raw_spec": diagram_spec.dict(),
                "parsing_time": (datetime.now() - start_time).total_seconds()
            }
    except Exception as e:
        logger.error(f"Error parsing formation: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "parsing_time": (datetime.now() - start_time).total_seconds()
        }

async def generate_diagram_from_spec(
    diagram_spec: Dict[str, Any],
    output_format: str = "png"
) -> Dict[str, Any]:
    """
    Generate a diagram from a parsed specification.
    Separates parsing from generation for agent flexibility.
    
    Args:
        diagram_spec: Parsed diagram specification (from parse_hockey_formation)
        output_format: Output format - 'png' or 'svg' (default: png)
    
    Returns:
        Dictionary containing diagram path and generation details
    """
    start_time = datetime.now()
    logger.info("Generating diagram from pre-parsed specification...")
    
    # Log input specification details
    logger.info(f"DIAGRAM GENERATION INPUT - Players: {len(diagram_spec.get('players', []))}")
    logger.info(f"DIAGRAM GENERATION INPUT - Movements: {len(diagram_spec.get('movements', []))}")
    logger.info(f"DIAGRAM GENERATION INPUT - Zones: {len(diagram_spec.get('zones', []))}")
    logger.info(f"DIAGRAM GENERATION INPUT - Output format: {output_format}")
    
    try:
        # Reconstruct DiagramSpec from dict
        from parser import DiagramSpec
        
        # Convert dictionary back to proper objects
        spec_dict = diagram_spec.copy()
        
        # Convert players
        players = []
        for p_dict in spec_dict.get('players', []):
            players.append(Player(
                position=p_dict['position'],
                x=p_dict['x'],
                y=p_dict['y'],
                team=p_dict['team'],
                has_puck=p_dict.get('has_puck', False)
            ))
        
        # Convert movements if present
        movements = None
        if spec_dict.get('movements'):
            movements = []
            for m_dict in spec_dict['movements']:
                to_pos = m_dict['to_position']
                if isinstance(to_pos, list):
                    to_pos = tuple(to_pos)
                movements.append(Movement(
                    from_position=m_dict['from_position'],
                    to_position=to_pos,
                    movement_type=m_dict['movement_type']
                ))
        
        # Convert zones if present
        zones = None
        if spec_dict.get('zones'):
            zones = []
            for z_dict in spec_dict['zones']:
                area = z_dict['area']
                if isinstance(area, list):
                    area = tuple(area)
                zones.append(Zone(
                    zone_type=z_dict['zone_type'],
                    area=area,
                    team=z_dict['team'],
                    opacity=z_dict.get('opacity', 0.2)
                ))
        
        # Generate the diagram
        base64_image = diagram_generator.generate_diagram(
            players=players,
            movements=movements,
            zones=zones,
            view=spec_dict.get('view', 'full'),
            title=spec_dict.get('title'),
            output_format=output_format
        )
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hockey_diagram_from_spec_{timestamp}.{output_format}"
        filepath = DIAGRAM_DIR / filename
        
        diagram_generator.save_to_file(base64_image, str(filepath), output_format)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # Log generation output details
        logger.info(f"DIAGRAM GENERATION OUTPUT - File saved: {filepath}")
        logger.info(f"DIAGRAM GENERATION OUTPUT - File size: {filepath.stat().st_size if filepath.exists() else 0} bytes")
        logger.info(f"DIAGRAM GENERATION PERFORMANCE - Total time: {generation_time:.3f}s")
        logger.info(f"Successfully generated diagram from spec: {filepath}")
        
        return {
            "success": True,
            "diagram_path": str(filepath),
            "message": f"Diagram generated from specification: {filepath}",
            "generation_time": generation_time
        }
        
    except Exception as e:
        logger.error(f"Error generating diagram from spec: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "generation_time": (datetime.now() - start_time).total_seconds()
        }

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

@mcp.tool()
async def create_hockey_diagram(
    request: str,
    context: Optional[str] = None,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create intelligent hockey diagrams from natural language descriptions.
    
    This tool provides enhanced capabilities including:
    - Automatic research of unknown formations and systems
    - Iterative refinement based on feedback
    - Conversation memory within sessions
    - Natural language understanding of hockey concepts
    
    Args:
        request: Natural language description of the formation/play/drill
        context: Optional context or previous conversation reference
        conversation_id: Optional conversation ID for maintaining context
    
    Returns:
        Dictionary containing diagram path, tactical explanation, and metadata
    """
    start_time = datetime.now()
    logger.info(f"🤖 Agent-based generation: {request[:50]}...")
    
    try:
        # Log environment state
        logger.info(f"OPENAI_API_KEY set: {'OPENAI_API_KEY' in os.environ}")
        logger.info(f"EXA_API_KEY set: {'EXA_API_KEY' in os.environ}")
        
        # Import agent (lazy loading to avoid circular imports)
        logger.info("Importing hockey_diagram_agent module...")
        from hockey_diagram_agent import get_agent
        
        # Get or create agent instance with timeout
        logger.info("Getting agent instance...")
        try:
            agent = await asyncio.wait_for(get_agent(), timeout=10.0)
            logger.info("Agent instance obtained successfully")
        except asyncio.TimeoutError:
            logger.error("Timeout getting agent instance")
            raise Exception("Agent initialization timed out after 10 seconds")
        
        # Prepare context if provided
        agent_context = None
        if context:
            try:
                import json
                agent_context = json.loads(context) if isinstance(context, str) else context
            except (json.JSONDecodeError, TypeError):
                agent_context = {"notes": context}
        
        # Generate diagram using agent with timeout
        if conversation_id:
            # Continue existing conversation
            logger.info(f"📞 Continuing conversation {conversation_id}")
            result = await asyncio.wait_for(agent.continue_conversation(request), timeout=90.0)
        else:
            # Start new generation
            logger.info(f"Generating diagram with agent...")
            result = await asyncio.wait_for(agent.generate_diagram(request, agent_context), timeout=90.0)
        
        # Add server metadata
        result.update({
            "agent_used": True,
            "server_timestamp": datetime.now().isoformat(),
            "total_time": (datetime.now() - start_time).total_seconds()
        })
        
        logger.info(f"✅ Agent generation completed: {result.get('success', False)}")
        return result
        
    except ImportError as e:
        logger.error(f"Agent not available: {e}")
        return {
            "success": False,
            "error": "Agent system not available - falling back to direct generation",
            "error_type": "agent_unavailable",
            "fallback_suggestion": "Use generate_hockey_diagram tool instead"
        }
    except Exception as e:
        logger.error(f"Agent generation error: {e}, trying simple agent fallback")
        
        # Try simple agent as fallback
        try:
            from simple_hockey_agent import generate_with_simple_agent
            logger.info("Using simple agent fallback...")
            result = await generate_with_simple_agent(request)
            result.update({
                "agent_used": True,
                "fallback_used": True,
                "server_timestamp": datetime.now().isoformat(),
                "total_time": (datetime.now() - start_time).total_seconds()
            })
            return result
        except Exception as fallback_error:
            logger.error(f"Simple agent also failed: {fallback_error}")
            
        return {
            "success": False,
            "error": f"Agent generation failed: {str(e)}",
            "error_type": type(e).__name__,
            "generation_time": (datetime.now() - start_time).total_seconds(),
            "fallback_suggestion": "Try using generate_hockey_diagram for direct generation"
        }

@mcp.tool()
async def get_agent_status() -> Dict[str, Any]:
    """
    Get status and capabilities of the hockey diagram agent.
    
    Returns:
        Dictionary containing agent availability, capabilities, and server status
    """
    try:
        from hockey_diagram_agent import get_agent
        
        agent = await get_agent()
        capabilities = await agent.get_agent_capabilities()
        
        return {
            "agent_available": True,
            "agent_initialized": True,
            "capabilities": capabilities,
            "status": "operational"
        }
        
    except ImportError:
        return {
            "agent_available": False,
            "agent_initialized": False,
            "status": "not_available",
            "message": "Agent system dependencies not installed"
        }
    except Exception as e:
        return {
            "agent_available": False,
            "agent_initialized": False,
            "status": "error",
            "error": str(e),
            "message": "Agent system encountered an error"
        }

async def clear_agent_conversation() -> Dict[str, Any]:
    """
    Clear the agent's conversation history and reset context.
    
    Returns:
        Dictionary confirming the conversation reset
    """
    try:
        from hockey_diagram_agent import get_agent
        
        agent = await get_agent()
        agent.clear_conversation()
        
        return {
            "success": True,
            "message": "Agent conversation history cleared",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to clear agent conversation"
        }

# Cache Management Tools

@mcp.tool()
async def save_diagram_to_cache(
    prompt: str,
    spec: Dict[str, Any],
    parser_type: str = "unknown",
    tags: Optional[List[str]] = None,
    author: Optional[str] = None
) -> Dict[str, Any]:
    """
    Save a diagram specification to the cache for reuse.
    
    Args:
        prompt: Original user prompt used to generate the diagram
        spec: The parsed diagram specification (from parse_hockey_formation)
        parser_type: Type of parser used (two_stage, enhanced, basic)
        tags: Optional list of tags for categorization
        author: Optional author name
    
    Returns:
        Dictionary with cache ID and success status
    """
    try:
        metadata = {}
        if tags:
            metadata['tags'] = tags
        if author:
            metadata['author'] = author
            
        diagram_id = cache_manager.save_diagram(
            prompt=prompt,
            spec=spec,
            parser_type=parser_type,
            metadata=metadata
        )
        
        return {
            "success": True,
            "diagram_id": diagram_id,
            "message": f"Diagram saved to cache with ID: {diagram_id}"
        }
    except Exception as e:
        logger.error(f"Error saving diagram to cache: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def search_cached_diagrams(
    query: str,
    limit: int = 10,
    min_similarity: float = 0.7
) -> Dict[str, Any]:
    """
    Search for similar cached diagrams using semantic similarity.
    
    Args:
        query: Search query (typically a prompt or description)
        limit: Maximum number of results to return
        min_similarity: Minimum similarity score (0-1) for results
    
    Returns:
        Dictionary with matching diagrams and their similarity scores
    """
    try:
        diagrams = cache_manager.search_diagrams(
            query=query,
            limit=limit,
            min_similarity=min_similarity
        )
        
        return {
            "success": True,
            "count": len(diagrams),
            "diagrams": diagrams,
            "query": query
        }
    except Exception as e:
        logger.error(f"Error searching cached diagrams: {e}")
        return {
            "success": False,
            "error": str(e),
            "diagrams": []
        }

@mcp.tool()
async def get_cached_diagram(
    diagram_id: str,
    regenerate: bool = False
) -> Dict[str, Any]:
    """
    Retrieve a specific cached diagram by ID.
    
    Args:
        diagram_id: Unique identifier of the cached diagram
        regenerate: If True, regenerates the diagram image from the spec
    
    Returns:
        Dictionary with diagram spec and optionally the regenerated image
    """
    try:
        diagram = cache_manager.get_diagram(diagram_id)
        
        if not diagram:
            return {
                "success": False,
                "error": f"Diagram {diagram_id} not found"
            }
        
        result = {
            "success": True,
            "diagram": diagram
        }
        
        # Regenerate image if requested
        if regenerate and diagram.get('spec'):
            spec = diagram['spec']
            # Convert spec dict to DiagramSpec object
            diagram_spec = DiagramSpec(**spec)
            
            # Generate diagram using existing logic
            players = []
            if diagram_spec.players:
                for p in diagram_spec.players:
                    players.append(
                        Player(
                            position=p.position,
                            coordinates=tuple(p.coordinates) if p.coordinates else None,
                            label=p.label,
                            team=p.team,
                            number=p.number
                        )
                    )
            
            movements = []
            if diagram_spec.movements:
                for m in diagram_spec.movements:
                    movements.append(
                        Movement(
                            from_position=tuple(m.from_position),
                            to_position=tuple(m.to_position),
                            movement_type=m.movement_type
                        )
                    )
            
            zones = []
            if diagram_spec.zones:
                for z in diagram_spec.zones:
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
                output_format='png'
            )
            
            result['image_base64'] = base64_image
            
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving cached diagram: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def update_cached_diagram(
    diagram_id: str,
    spec: Optional[Dict[str, Any]] = None,
    validated: Optional[bool] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update a cached diagram's specification or metadata.
    
    Args:
        diagram_id: Unique identifier of the cached diagram
        spec: Updated diagram specification (optional)
        validated: Mark diagram as validated/reviewed (optional)
        tags: Updated tags for categorization (optional)
    
    Returns:
        Dictionary with update status
    """
    try:
        metadata = {}
        if validated is not None:
            metadata['validated'] = validated
        if tags is not None:
            metadata['tags'] = tags
            
        success = cache_manager.update_diagram(
            diagram_id=diagram_id,
            spec=spec,
            metadata=metadata if metadata else None
        )
        
        return {
            "success": success,
            "message": f"Diagram {diagram_id} updated" if success else f"Failed to update diagram {diagram_id}"
        }
        
    except Exception as e:
        logger.error(f"Error updating cached diagram: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def delete_cached_diagram(
    diagram_id: str
) -> Dict[str, Any]:
    """
    Delete a cached diagram from the cache.
    
    Args:
        diagram_id: Unique identifier of the cached diagram
    
    Returns:
        Dictionary with deletion status
    """
    try:
        success = cache_manager.delete_diagram(diagram_id)
        
        return {
            "success": success,
            "message": f"Diagram {diagram_id} deleted" if success else f"Failed to delete diagram {diagram_id}"
        }
        
    except Exception as e:
        logger.error(f"Error deleting cached diagram: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_cache_statistics() -> Dict[str, Any]:
    """
    Get statistics about the diagram cache.
    
    Returns:
        Dictionary with cache statistics including counts, popular diagrams, etc.
    """
    try:
        stats = cache_manager.get_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting cache statistics: {e}")
        return {
            "success": False,
            "error": str(e)
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