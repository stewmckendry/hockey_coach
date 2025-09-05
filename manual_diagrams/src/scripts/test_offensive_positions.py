#!/usr/bin/env python3
"""
Test offensive zone positions with diagram generation.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "servers"))
sys.path.append(str(Path(__file__).parent / "src"))

from hockey_diagram_builder import DiagramBuilder
from spec_converter import dict_to_diagram_spec
from position_mapper import map_position

def create_player(player_type, position_name, team, label, zone="offensive"):
    """Helper to create player with coordinates from position name."""
    coords = map_position(position_name, zone)
    return {
        "type": player_type,
        "position": position_name,
        "coordinates": {"x": coords[0], "y": coords[1]},
        "team": team,
        "label": label
    }

def test_offensive_faceoff():
    """Test offensive zone face-off with all 10 players."""
    builder = DiagramBuilder()
    
    # Create spec for left dot face-off
    spec_dict = {
        "players": [
            # Home team (5 players) - attacking
            create_player("forward", "offensive left faceoff home center", "home", "HC"),
            create_player("forward", "offensive left faceoff home left wing", "home", "HLW"),
            create_player("forward", "offensive left faceoff home right wing", "home", "HRW"),
            create_player("defense", "offensive left faceoff home left defense", "home", "HLD"),
            create_player("defense", "offensive left faceoff home right defense", "home", "HRD"),
            
            # Away team (5 players) - defending
            create_player("forward", "offensive left faceoff away center", "away", "AC"),
            create_player("forward", "offensive left faceoff away left wing", "away", "ALW"),
            create_player("forward", "offensive left faceoff away right wing", "away", "ARW"),
            create_player("defense", "offensive left faceoff away left defense", "away", "ALD"),
            create_player("defense", "offensive left faceoff away right defense", "away", "ARD"),
        ],
        "rink": {"view": "offensive"},
        "zones": [
            # Highlight the faceoff circle
            {"type": "circle", "position": {"x": 69, "y": 22.5}, "radius": 15, "style": {"fill": "none", "stroke": "#FF0000", "strokeWidth": 2}},
        ],
        "annotations": [
            {"text": "Offensive Zone Left Dot Face-off", "position": {"x": 69, "y": -38}, "anchor": "middle"},
            {"text": "HOME: HC, HLW, HRW, HLD, HRD", "position": {"x": 69, "y": 38}, "anchor": "middle", "style": {"fontSize": 9, "fill": "#0000FF"}},
            {"text": "AWAY: AC, ALW, ARW, ALD, ARD", "position": {"x": 69, "y": 40.5}, "anchor": "middle", "style": {"fontSize": 9, "fill": "#FF0000"}}
        ]
    }
    
    # Convert to spec and generate diagram
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_offensive_faceoff.png"
    builder.build(spec, output_path)
    
    print(f"✅ Offensive zone face-off: {output_path}")
    return output_path

def test_net_area_positions():
    """Test net area positions."""
    builder = DiagramBuilder()
    
    spec_dict = {
        "players": [
            create_player("forward", "net front", "home", "NF"),
            create_player("forward", "behind net", "home", "BN"),
            create_player("forward", "left post", "away", "LP"),
            create_player("forward", "right post", "away", "RP"),
            create_player("goalie", "crease", "away", "G"),
        ],
        "rink": {"view": "offensive"},
        "annotations": [
            {"text": "Net Area Positions", "position": {"x": 69, "y": -38}, "anchor": "middle"},
            {"text": "Key positions around the net", "position": {"x": 69, "y": 38}, "anchor": "middle", "style": {"fontSize": 10}}
        ]
    }
    
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_net_area.png"
    builder.build(spec, output_path)
    
    print(f"✅ Net area positions: {output_path}")
    return output_path

def test_slot_and_points():
    """Test slot area and point positions."""
    builder = DiagramBuilder()
    
    spec_dict = {
        "players": [
            # High slot positions
            create_player("forward", "high slot middle", "home", "HSM"),
            create_player("forward", "high slot left", "home", "HSL"),
            create_player("forward", "high slot right", "home", "HSR"),
            
            # Mid slot positions
            create_player("forward", "mid slot middle", "away", "MSM"),
            create_player("forward", "mid slot left", "away", "MSL"),
            create_player("forward", "mid slot right", "away", "MSR"),
            
            # Low slot positions
            create_player("forward", "low slot middle", "home", "LSM"),
            create_player("forward", "low slot left", "home", "LSL"),
            create_player("forward", "low slot right", "home", "LSR"),
            
            # Points
            create_player("defense", "point middle", "away", "PM"),
            create_player("defense", "point left", "away", "PL"),
            create_player("defense", "point right", "away", "PR"),
            create_player("defense", "point left boards", "home", "PLB"),
            create_player("defense", "point right boards", "home", "PRB"),
            
            # Goalie
            create_player("goalie", "goalie", "away", "G"),
        ],
        "rink": {"view": "offensive"},
        "zones": [
            # Show slot area
            {"type": "rectangle", "position": {"x": 69, "y": 0}, "width": 20, "height": 30, 
             "style": {"fill": "rgba(255,0,0,0.1)", "stroke": "#FF0000"}},
        ],
        "annotations": [
            {"text": "Slot and Point Positions", "position": {"x": 69, "y": -38}, "anchor": "middle"},
            {"text": "Slot Area", "position": {"x": 69, "y": 0}, "anchor": "middle", "style": {"fontSize": 10, "fill": "#FF0000"}},
            {"text": "Blue Line Points", "position": {"x": 25, "y": 0}, "anchor": "middle", "style": {"fontSize": 10, "fill": "#0000FF"}}
        ]
    }
    
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_slot_points.png"
    builder.build(spec, output_path)
    
    print(f"✅ Slot and points: {output_path}")
    return output_path

def test_corners_halfwall():
    """Test corner and half-wall positions."""
    builder = DiagramBuilder()
    
    spec_dict = {
        "players": [
            # Corners
            create_player("forward", "left corner", "home", "LC"),
            create_player("forward", "right corner", "home", "RC"),
            
            # Half walls
            create_player("forward", "left half wall", "away", "LHW"),
            create_player("forward", "right half wall", "away", "RHW"),
            
            # Corner queues
            create_player("forward", "corner queue left", "home", "QL"),
            create_player("forward", "corner queue right", "home", "QR"),
        ],
        "rink": {"view": "offensive"},
        "annotations": [
            {"text": "Corners and Half-Wall Positions", "position": {"x": 69, "y": -38}, "anchor": "middle"},
            {"text": "Corner Play Areas", "position": {"x": 89, "y": 0}, "anchor": "middle", "style": {"fontSize": 10}},
            {"text": "Half-Wall Positions", "position": {"x": 69, "y": 35}, "anchor": "middle", "style": {"fontSize": 10}}
        ]
    }
    
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_corners_halfwall.png"
    builder.build(spec, output_path)
    
    print(f"✅ Corners and half-wall: {output_path}")
    return output_path

if __name__ == "__main__":
    print("\n🏒 TESTING OFFENSIVE ZONE POSITIONS")
    print("="*50)
    
    print("\n1️⃣ Testing offensive zone face-off...")
    test_offensive_faceoff()
    
    print("\n2️⃣ Testing net area positions...")
    test_net_area_positions()
    
    print("\n3️⃣ Testing slot and point positions...")
    test_slot_and_points()
    
    print("\n4️⃣ Testing corners and half-wall...")
    test_corners_halfwall()
    
    print("\n✅ All tests complete! Check generated PNG files.")