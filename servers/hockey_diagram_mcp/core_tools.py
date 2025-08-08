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
        
        # Convert player dicts to Player objects - HANDLE ALL COORDINATE CONVERSION HERE
        from generator import Player, Movement, CoverageZone
        from coordinate_mapper import coordinate_mapper
        
        logger.info(f"Players before conversion: {type(players)}, length: {len(players) if players else 0}")
        if players:
            logger.info(f"First player type: {type(players[0])}")
            if isinstance(players[0], str):
                logger.error(f"ERROR: Players is a list of strings, not dicts! First player: {players[0]}")
            else:
                logger.info(f"First player data: {players[0]}")
        
        if players and isinstance(players[0], dict):
            converted_players = []
            for i, p in enumerate(players):
                logger.info(f"Processing player {i}: type={type(p)}, value={p}")
                
                # Skip if this became a string somehow
                if isinstance(p, str):
                    logger.error(f"Player {i} is a string, skipping: {p}")
                    continue
                
                # ALL COORDINATE CONVERSION HAPPENS HERE (programmatically)
                x, y = None, None
                
                # Check if already has coordinates (from legacy systems)
                if 'x' in p and 'y' in p:
                    x, y = p.get('x'), p.get('y')
                    logger.info(f"Using existing coordinates: ({x}, {y})")
                
                # Convert zone-based data to coordinates (this is THE coordinate conversion point)
                elif 'zone' in p:
                    zone_name = p.get('zone', '')
                    try:
                        x, y = coordinate_mapper.get_area_coordinate(zone_name)
                        logger.info(f"🎯 CONVERTED zone '{zone_name}' to coordinates ({x}, {y})")
                    except Exception as e:
                        logger.warning(f"Failed to convert zone '{zone_name}': {e}")
                        # Fallback to center
                        x, y = 0, 0
                
                # Final fallback
                if x is None or y is None:
                    logger.warning(f"No coordinates found for player {p}, using center (0, 0)")
                    x, y = 0, 0
                
                # Create Player object with converted coordinates
                try:
                    player_obj = Player(
                        position=p.get('position', p.get('role', 'F1')),
                        x=x,
                        y=y,
                        team=p.get('team', 'home'),
                        has_puck=p.get('has_puck', False)
                    )
                    converted_players.append(player_obj)
                    logger.info(f"✅ Created Player object: {player_obj}")
                except Exception as e:
                    logger.error(f"Error creating Player object from {p}: {e}")
                    continue
            
            players = converted_players
            logger.info(f"✅ Converted {len(players)} players to Player objects")
            
            # Now apply offsets AFTER coordinate conversion
            from player_offset_system import PlayerOffsetCalculator
            calculator = PlayerOffsetCalculator()
            
            # Convert Player objects to dicts for offset calculation
            player_dicts = [
                {
                    'x': p.x,
                    'y': p.y,
                    'position': p.position,
                    'team': p.team,
                    'has_puck': p.has_puck
                }
                for p in players
            ]
            
            # Apply offsets
            offset_players = calculator.calculate_offsets(player_dicts)
            
            # Convert back to Player objects
            players = [
                Player(
                    position=p['position'],
                    x=p['x'],
                    y=p['y'],
                    team=p['team'],
                    has_puck=p['has_puck']
                )
                for p in offset_players
            ]
            logger.info(f"✅ Applied offsets to {len(players)} players")
        
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
        try:
            logger.info(f"About to call generator.generate_diagram with {len(players)} players")
            for i, player in enumerate(players):
                logger.info(f"Player {i}: {type(player)} - {player}")
            
            result = generator.generate_diagram(
                players=players,
                movements=movements,
                zones=zones,
                view=view,
                title=title,
                output_format=output_format
            )
        except Exception as e:
            logger.error(f"Generator error details: {type(e).__name__}: {e}")
            logger.error(f"Players passed to generator: {[type(p) for p in players]}")
            raise
        
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