"""
Core diagram generation tools that can be used by both MCP server and agent.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import json

from two_stage_parser import TwoStageHockeyParser
from generator import HockeyDiagramGenerator
from elements import FORMATIONS

logger = logging.getLogger(__name__)

async def parse_hockey_formation_core(
    prompt: str,
    parser_type: str = "two_stage"
) -> Dict[str, Any]:
    """
    Core parsing function without MCP decoration.
    """
    logger.info(f"🎯 Parsing: {prompt[:50]}...")
    
    try:
        if parser_type == "two_stage":
            from two_stage_parser import TwoStageHockeyParser
            parser = TwoStageHockeyParser()
            diagram_spec = await parser.parse_prompt(prompt)
        else:
            # Fallback to basic parser
            from parser import HockeyPromptParser
            parser = HockeyPromptParser()
            diagram_spec = await parser.parse_prompt(prompt)
        
        # Convert to dict for JSON serialization
        spec_dict = diagram_spec.dict() if hasattr(diagram_spec, 'dict') else diagram_spec
        
        # Extract traces if available
        traces = getattr(diagram_spec, '_traces', {})
        
        return {
            "success": True,
            "parsed_data": spec_dict,
            "parser_used": parser_type,
            "timestamp": datetime.now().isoformat(),
            "traces": traces  # Include parser stage traces
        }
        
    except Exception as e:
        logger.error(f"Parsing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "parser_attempted": parser_type
        }

async def generate_diagram_from_spec_core(
    diagram_spec: Dict[str, Any],
    output_format: str = "png"
) -> Dict[str, Any]:
    """
    Core generation function without MCP decoration.
    """
    logger.info("🎨 Generating diagram from specification...")
    
    try:
        generator = HockeyDiagramGenerator()
        
        # Extract components from spec
        players = diagram_spec.get('players', [])
        movements = diagram_spec.get('movements', [])
        zones = diagram_spec.get('zones', [])
        view = diagram_spec.get('view', 'full')
        title = diagram_spec.get('title', 'Hockey Formation')
        
        # Apply offsets to prevent overlapping players
        from player_offset_system import apply_player_offsets
        diagram_spec = apply_player_offsets(diagram_spec)
        
        # Re-extract players after offset application
        players = diagram_spec.get('players', [])
        
        # Convert player dicts to Player objects if needed
        from generator import Player, Movement, CoverageZone
        
        logger.info(f"Players before conversion: {type(players)}, length: {len(players) if players else 0}")
        if players:
            logger.info(f"First player type: {type(players[0])}")
            if isinstance(players[0], str):
                logger.error(f"ERROR: Players is a list of strings, not dicts! First player: {players[0]}")
            else:
                logger.info(f"First player data: {players[0]}")
        
        if players and isinstance(players[0], dict):
            players = [
                Player(
                    position=p.get('position'),
                    x=p.get('x'),
                    y=p.get('y'),
                    team=p.get('team', 'home'),
                    has_puck=p.get('has_puck', False)
                ) for p in players
            ]
            logger.info(f"Converted {len(players)} players to Player objects")
        
        # Convert movement dicts to Movement objects if needed
        if movements and isinstance(movements[0], dict):
            movements = [
                Movement(
                    from_position=m.get('from_position', (m.get('from_x'), m.get('from_y')) if 'from_x' in m else None),
                    to_position=m.get('to_position', (m.get('to_x'), m.get('to_y')) if 'to_x' in m else None),
                    movement_type=m.get('movement_type', 'skating')
                ) for m in movements if m.get('from_position') or 'from_x' in m
            ]
        
        # Convert zone dicts to CoverageZone objects if needed
        if zones and isinstance(zones[0], dict):
            zones = [
                CoverageZone(
                    zone_type=z.get('zone_type', 'coverage'),
                    area=(z.get('x_start'), z.get('y_start'), z.get('x_end'), z.get('y_end')) if 'x_start' in z else z.get('area', 'slot'),
                    team=z.get('team', 'home'),
                    opacity=z.get('opacity', 0.2)
                ) for z in zones
            ]
        
        # Generate the diagram
        result = generator.generate_diagram(
            players=players,
            movements=movements,
            zones=zones,
            view=view,
            title=title,
            output_format=output_format
        )
        
        # Save if successful
        if isinstance(result, dict) and result.get('success'):
            # Ensure directory exists
            output_dir = Path("generated_diagrams")
            output_dir.mkdir(exist_ok=True)
            
            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hockey_diagram_{timestamp}.{output_format}"
            filepath = output_dir / filename
            
            # Save base64 data
            if output_format == "png":
                import base64
                image_data = base64.b64decode(result['base64_data'])
                with open(filepath, 'wb') as f:
                    f.write(image_data)
            
            return {
                "success": True,
                "diagram_path": str(filepath),
                "filename": filename,
                "base64_data": result['base64_data'],
                "message": f"Diagram generated: {filepath}"
            }
        else:
            # Handle string result (base64 data directly)
            if isinstance(result, str):
                output_dir = Path("generated_diagrams")
                output_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"hockey_diagram_{timestamp}.{output_format}"
                filepath = output_dir / filename
                
                import base64
                image_data = base64.b64decode(result)
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                return {
                    "success": True,
                    "diagram_path": str(filepath),
                    "filename": filename,
                    "base64_data": result,
                    "message": f"Diagram generated: {filepath}"
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Unknown generation error')
                }
                
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

def list_formations_core() -> Dict[str, Any]:
    """
    Core function to list available formations.
    """
    formations_by_category = {}
    total_count = 0
    
    for category, formations in FORMATIONS.items():
        formations_by_category[category] = list(formations.keys())
        total_count += len(formations)
    
    return {
        "success": True,
        "formations": formations_by_category,
        "total": total_count,
        "categories": list(FORMATIONS.keys())
    }