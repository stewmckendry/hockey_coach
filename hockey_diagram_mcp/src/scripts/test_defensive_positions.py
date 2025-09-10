#!/usr/bin/env python3
"""
Test defensive zone positions with diagram generation.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "servers"))
sys.path.append(str(Path(__file__).parent / "src"))

from hockey_diagram_builder import DiagramBuilder
from spec_converter import dict_to_diagram_spec
from position_mapper import map_position

def create_player(player_type, position_name, team, label, zone="defensive"):
    """Helper to create player with coordinates from position name."""
    coords = map_position(position_name, zone)
    return {
        "type": player_type,
        "position": position_name,
        "coordinates": {"x": coords[0], "y": coords[1]},
        "team": team,
        "label": label
    }

def test_defensive_faceoff():
    """Test defensive zone face-off with all 10 players."""
    builder = DiagramBuilder()
    
    # Create spec for left dot face-off
    spec_dict = {
        "players": [
            # Home team (5 players) - defending
            create_player("forward", "defensive left faceoff home center", "home", "HC"),
            create_player("forward", "defensive left faceoff home left wing", "home", "HLW"),
            create_player("forward", "defensive left faceoff home right wing", "home", "HRW"),
            create_player("defense", "defensive left faceoff home left defense", "home", "HLD"),
            create_player("defense", "defensive left faceoff home right defense", "home", "HRD"),
            
            # Away team (5 players) - attacking
            create_player("forward", "defensive left faceoff away center", "away", "AC"),
            create_player("forward", "defensive left faceoff away left wing", "away", "ALW"),
            create_player("forward", "defensive left faceoff away right wing", "away", "ARW"),
            create_player("defense", "defensive left faceoff away left defense", "away", "ALD"),
            create_player("defense", "defensive left faceoff away right defense", "away", "ARD"),
        ],
        "rink": {"view": "defensive"},
        "zones": [
            # Highlight the faceoff circle
            {"type": "circle", "position": {"x": -69, "y": 22.5}, "radius": 15, "style": {"fill": "none", "stroke": "#FF0000", "strokeWidth": 2}},
        ],
        "annotations": [
            {"text": "Defensive Zone Left Dot Face-off", "position": {"x": -69, "y": -38}, "anchor": "middle"},
            {"text": "HOME (defending): HC, HRW, HLW, HRD, HLD", "position": {"x": -69, "y": 38}, "anchor": "middle", "style": {"fontSize": 9, "fill": "#0000FF"}},
            {"text": "AWAY (attacking): AC, ALW, ARW, ALD, ARD", "position": {"x": -69, "y": 40.5}, "anchor": "middle", "style": {"fontSize": 9, "fill": "#FF0000"}}
        ]
    }
    
    # Convert to spec and generate diagram
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_defensive_faceoff.png"
    builder.build(spec, output_path)
    
    print(f"✅ Defensive zone face-off: {output_path}")
    return output_path

def test_defensive_slots_points():
    """Test defensive zone slot and point positions."""
    builder = DiagramBuilder()
    
    spec_dict = {
        "players": [
            # High slot positions
            create_player("forward", "high slot middle", "away", "HSM", "defensive"),
            create_player("forward", "high slot left", "away", "HSL", "defensive"),
            create_player("forward", "high slot right", "away", "HSR", "defensive"),
            
            # Mid slot positions
            create_player("forward", "mid slot middle", "home", "MSM", "defensive"),
            create_player("forward", "mid slot left", "home", "MSL", "defensive"),
            create_player("forward", "mid slot right", "home", "MSR", "defensive"),
            
            # Low slot positions
            create_player("forward", "low slot middle", "away", "LSM", "defensive"),
            create_player("forward", "low slot left", "away", "LSL", "defensive"),
            create_player("forward", "low slot right", "away", "LSR", "defensive"),
            
            # Points
            create_player("defense", "point middle", "home", "PM", "defensive"),
            create_player("defense", "point left", "home", "PL", "defensive"),
            create_player("defense", "point right", "home", "PR", "defensive"),
            create_player("defense", "point left boards", "away", "PLB", "defensive"),
            create_player("defense", "point right boards", "away", "PRB", "defensive"),
            
            # Goalie
            create_player("goalie", "goalie", "home", "G", "defensive"),
        ],
        "rink": {"view": "defensive"},
        "zones": [
            # Show slot area
            {"type": "rectangle", "position": {"x": -69, "y": 0}, "width": 20, "height": 30, 
             "style": {"fill": "rgba(255,0,0,0.1)", "stroke": "#FF0000"}},
        ],
        "annotations": [
            {"text": "Defensive Zone Slot and Point Positions", "position": {"x": -69, "y": -38}, "anchor": "middle"},
            {"text": "Slot Area", "position": {"x": -69, "y": 0}, "anchor": "middle", "style": {"fontSize": 10, "fill": "#FF0000"}},
            {"text": "Blue Line Points", "position": {"x": -25, "y": 0}, "anchor": "middle", "style": {"fontSize": 10, "fill": "#0000FF"}}
        ]
    }
    
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_defensive_slots_points.png"
    builder.build(spec, output_path)
    
    print(f"✅ Defensive slots and points: {output_path}")
    return output_path

def test_defensive_corners_walls():
    """Test defensive zone corner and wall positions."""
    builder = DiagramBuilder()
    
    spec_dict = {
        "players": [
            # Corners
            create_player("forward", "left corner", "home", "LC", "defensive"),
            create_player("forward", "right corner", "home", "RC", "defensive"),
            
            # Half walls
            create_player("forward", "left half wall", "away", "LHW", "defensive"),
            create_player("forward", "right half wall", "away", "RHW", "defensive"),
            
            # Behind net
            create_player("forward", "behind net", "home", "BN", "defensive"),
            
            # Net front
            create_player("forward", "net front", "away", "NF", "defensive"),
            
            # Posts
            create_player("forward", "left post", "away", "LP", "defensive"),
            create_player("forward", "right post", "away", "RP", "defensive"),
        ],
        "rink": {"view": "defensive"},
        "annotations": [
            {"text": "Defensive Zone Corners and Walls", "position": {"x": -69, "y": -38}, "anchor": "middle"},
            {"text": "Corner Play Areas", "position": {"x": -89, "y": 0}, "anchor": "middle", "style": {"fontSize": 10}},
            {"text": "Half-Wall Positions", "position": {"x": -69, "y": 35}, "anchor": "middle", "style": {"fontSize": 10}}
        ]
    }
    
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_defensive_corners_walls.png"
    builder.build(spec, output_path)
    
    print(f"✅ Defensive corners and walls: {output_path}")
    return output_path

if __name__ == "__main__":
    print("\n🏒 TESTING DEFENSIVE ZONE POSITIONS")
    print("="*50)
    
    print("\n1️⃣ Testing defensive zone face-off...")
    test_defensive_faceoff()
    
    print("\n2️⃣ Testing defensive slots and points...")
    test_defensive_slots_points()
    
    print("\n3️⃣ Testing defensive corners and walls...")
    test_defensive_corners_walls()
    
    print("\n✅ All defensive zone tests complete! Check generated PNG files.")