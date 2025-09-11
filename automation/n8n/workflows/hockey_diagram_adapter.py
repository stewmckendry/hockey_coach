#!/usr/bin/env python3
"""
Minimal Hockey Diagram Adapter for n8n
Provides HTTP endpoints for generating hockey diagrams from specifications.
"""

import os
import sys
import json
import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add hockey_diagram_mcp to path
hockey_diagram_path = Path(__file__).parent.parent.parent / "servers" / "hockey_diagram_mcp"
sys.path.insert(0, str(hockey_diagram_path))

from generator import HockeyDiagramGenerator, Player, Movement, CoverageZone

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize diagram generator
diagram_generator = HockeyDiagramGenerator()

def convert_zone_location_to_coordinates(zone: str, location: str, view: str = 'full') -> tuple:
    """
    Convert zone and location to x/y coordinates.
    
    Args:
        zone: Ice zone (offensive/neutral/defensive)
        location: Specific location within the zone
        view: Rink view (full/offensive/defensive/neutral)
    
    Returns:
        Tuple of (x, y) coordinates
    """
    # Coordinate mappings for full rink view
    # X-axis: -100 (defensive) to 100 (offensive)
    # Y-axis: -42.5 (left) to 42.5 (right)
    
    coordinate_map = {
        # Offensive zone locations
        ('offensive', 'slot'): (70, 0),
        ('offensive', 'high_slot'): (55, 0),
        ('offensive', 'low_slot'): (80, 0),
        ('offensive', 'point'): (35, 0),
        ('offensive', 'left_point'): (35, -25),
        ('offensive', 'right_point'): (35, 25),
        ('offensive', 'left_circle'): (69, -22),
        ('offensive', 'right_circle'): (69, 22),
        ('offensive', 'behind_net'): (89, 0),
        ('offensive', 'net_front'): (85, 0),
        ('offensive', 'crease'): (87, 0),
        ('offensive', 'left_corner'): (89, -37),
        ('offensive', 'right_corner'): (89, 37),
        ('offensive', 'left_half_wall'): (75, -35),
        ('offensive', 'right_half_wall'): (75, 35),
        ('offensive', 'left_boards'): (50, -40),
        ('offensive', 'right_boards'): (50, 40),
        
        # Neutral zone locations
        ('neutral', 'center_ice'): (0, 0),
        ('neutral', 'left_wall'): (0, -40),
        ('neutral', 'right_wall'): (0, 40),
        ('neutral', 'center_lane'): (0, 0),
        
        # Defensive zone locations
        ('defensive', 'slot'): (-70, 0),
        ('defensive', 'defensive_slot'): (-70, 0),
        ('defensive', 'high_slot'): (-55, 0),
        ('defensive', 'defensive_high_slot'): (-55, 0),
        ('defensive', 'low_slot'): (-80, 0),
        ('defensive', 'defensive_low_slot'): (-80, 0),
        ('defensive', 'point'): (-35, 0),
        ('defensive', 'left_point'): (-35, -25),
        ('defensive', 'right_point'): (-35, 25),
        ('defensive', 'left_circle'): (-69, -22),
        ('defensive', 'defensive_left_circle'): (-69, -22),
        ('defensive', 'right_circle'): (-69, 22),
        ('defensive', 'defensive_right_circle'): (-69, 22),
        ('defensive', 'behind_net'): (-89, 0),
        ('defensive', 'defensive_behind_net'): (-89, 0),
        ('defensive', 'net_front'): (-85, 0),
        ('defensive', 'defensive_net_front'): (-85, 0),
        ('defensive', 'crease'): (-87, 0),
        ('defensive', 'left_corner'): (-89, -37),
        ('defensive', 'defensive_left_corner'): (-89, -37),
        ('defensive', 'right_corner'): (-89, 37),
        ('defensive', 'defensive_right_corner'): (-89, 37),
        ('defensive', 'left_half_wall'): (-75, -35),
        ('defensive', 'defensive_left_half_wall'): (-75, -35),
        ('defensive', 'right_half_wall'): (-75, 35),
        ('defensive', 'defensive_right_half_wall'): (-75, 35),
        ('defensive', 'left_boards'): (-50, -40),
        ('defensive', 'right_boards'): (-50, 40),
        
        # Special locations
        ('neutral', 'bench'): (0, -42),
        ('neutral', 'penalty_box'): (0, 42),
    }
    
    # Get coordinates from map, default to center if not found
    coords = coordinate_map.get((zone, location), (0, 0))
    
    # Adjust for different views
    if view == 'offensive':
        # Shift defensive zone positions closer for offensive view
        if zone == 'defensive':
            coords = (-25, coords[1])
    elif view == 'defensive':
        # Shift offensive zone positions closer for defensive view
        if zone == 'offensive':
            coords = (25, coords[1])
    
    return coords

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "hockey-diagram-adapter"})

@app.route('/generate', methods=['POST'])
def generate_diagram():
    """
    Generate hockey diagram from specification.
    
    Expected JSON payload:
    {
        "players": [
            {"position": "C", "x": 0, "y": 0, "team": "home", "has_puck": true},
            ...
        ],
        "movements": [
            {"from_position": "C", "to_position": "RW", "movement_type": "pass"},
            ...
        ],
        "zones": [
            {"zone_type": "coverage", "area": "slot", "team": "home", "opacity": 0.2},
            ...
        ],
        "view": "full",
        "title": "2-1-2 Forecheck"
    }
    """
    try:
        data = request.get_json()
        
        # Parse players
        players = []
        for p in data.get('players', []):
            # Convert zone/location to x/y coordinates
            x, y = convert_zone_location_to_coordinates(
                p.get('zone'),
                p.get('location'),
                data.get('view', 'full')
            )
            
            player = Player(
                position=p['position'],
                x=x,
                y=y,
                team=p['team'],
                has_puck=p.get('has_puck', False),
                label=p.get('label'),
                zone=p.get('zone')
            )
            players.append(player)
        
        # Parse movements
        movements = []
        for m in data.get('movements', []):
            movement = Movement(
                from_position=m['from_position'],
                to_position=m.get('to_position', m['from_position']),
                movement_type=m.get('movement_type', 'skating'),
                label=m.get('label')
            )
            movements.append(movement)
        
        # Parse zones
        zones = []
        for z in data.get('zones', []):
            # Build area string from zone and location
            area = f"{z.get('zone', '')}_{z.get('location', '')}".strip('_')
            
            zone = CoverageZone(
                zone_type=z['zone_type'],
                area=area,
                team=z['team'],
                opacity=z.get('opacity', 0.2)
            )
            zones.append(zone)
        
        # Generate diagram
        view = data.get('view', 'full')
        title = data.get('title', '')
        
        base64_image = diagram_generator.generate_diagram(
            players=players,
            movements=movements if movements else None,
            zones=zones if zones else None,
            view=view,
            title=title,
            output_format='png'
        )
        
        return jsonify({
            "success": True,
            "image": base64_image,
            "format": "png",
            "title": title
        })
        
    except Exception as e:
        logger.error(f"Error generating diagram: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/parse', methods=['POST'])
def parse_prompt():
    """
    Parse natural language prompt to diagram specification using OpenAI.
    
    Expected JSON payload:
    {
        "prompt": "2-1-2 forecheck with F1 pressuring behind net"
    }
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({
                "success": False,
                "error": "No prompt provided"
            }), 400
        
        # For minimal implementation, return a basic spec structure
        # In production, this would call the two-stage parser
        spec = {
            "players": [],
            "movements": [],
            "zones": [],
            "view": "full",
            "title": prompt[:50]  # Use first 50 chars as title
        }
        
        # Add some basic player positions for common formations
        if "2-1-2" in prompt.lower():
            spec["players"] = [
                {"position": "F1", "zone": "offensive", "location": "behind_net", "team": "home", "has_puck": False},
                {"position": "F2", "zone": "offensive", "location": "left_corner", "team": "home", "has_puck": False},
                {"position": "F3", "zone": "offensive", "location": "right_corner", "team": "home", "has_puck": False},
                {"position": "D1", "zone": "offensive", "location": "left_point", "team": "home", "has_puck": False},
                {"position": "D2", "zone": "offensive", "location": "right_point", "team": "home", "has_puck": False}
            ]
            spec["title"] = "2-1-2 Forecheck"
            spec["view"] = "offensive"
        elif "power play" in prompt.lower():
            spec["players"] = [
                {"position": "C", "zone": "offensive", "location": "slot", "team": "home", "has_puck": True},
                {"position": "LW", "zone": "offensive", "location": "left_circle", "team": "home", "has_puck": False},
                {"position": "RW", "zone": "offensive", "location": "right_circle", "team": "home", "has_puck": False},
                {"position": "LD", "zone": "offensive", "location": "left_point", "team": "home", "has_puck": False},
                {"position": "RD", "zone": "offensive", "location": "right_point", "team": "home", "has_puck": False}
            ]
            spec["title"] = "Power Play Formation"
            spec["view"] = "offensive"
        
        return jsonify({
            "success": True,
            "spec": spec
        })
        
    except Exception as e:
        logger.error(f"Error parsing prompt: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)