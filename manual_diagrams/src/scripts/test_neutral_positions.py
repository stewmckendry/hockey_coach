#!/usr/bin/env python3
"""
Test updated neutral zone positions with diagram generation.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "servers"))
sys.path.append(str(Path(__file__).parent / "src"))

from hockey_diagram_builder import DiagramBuilder
from spec_converter import dict_to_diagram_spec
from position_mapper import map_position

def create_player(player_type, position_name, team, label, zone="neutral"):
    """Helper to create player with coordinates from position name."""
    coords = map_position(position_name, zone)
    return {
        "type": player_type,
        "position": position_name,
        "coordinates": {"x": coords[0], "y": coords[1]},
        "team": team,
        "label": label
    }

def test_center_ice_faceoff():
    """Test center ice face-off with home and away teams."""
    builder = DiagramBuilder()
    
    # Create spec for center ice face-off
    spec_dict = {
        "players": [
            # Home team (attacking right)
            create_player("forward", "center faceoff home center", "home", "HC"),
            create_player("forward", "center faceoff home right wing", "home", "HRW"),
            create_player("forward", "center faceoff home left wing", "home", "HLW"),
            create_player("defense", "center faceoff home right defense", "home", "HRD"),
            create_player("defense", "center faceoff home left defense", "home", "HLD"),
            
            # Away team (defending left)
            create_player("forward", "center faceoff away center", "away", "AC"),
            create_player("forward", "center faceoff away right wing", "away", "ARW"),
            create_player("forward", "center faceoff away left wing", "away", "ALW"),
            create_player("defense", "center faceoff away right defense", "away", "ARD"),
            create_player("defense", "center faceoff away left defense", "away", "ALD"),
        ],
        "rink": {"view": "neutral"},
        "annotations": [
            {"text": "Center Ice Face-off", "position": {"x": 0, "y": -38}, "anchor": "middle"}
        ]
    }
    
    # Convert to spec and generate diagram
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_center_ice_faceoff.png"
    builder.build(spec, output_path)
    
    print(f"✅ Center ice face-off: {output_path}")
    return output_path

def test_offside_dot_faceoff():
    """Test offside dot face-offs with all 10 players."""
    builder = DiagramBuilder()
    
    # Create spec for ONE offside dot showing all 10 players
    spec_dict = {
        "players": [
            # Offensive left dot - Home team (5 players)
            create_player("forward", "offside offensive left faceoff home center", "home", "HC"),
            create_player("forward", "offside offensive left faceoff home wing outside", "home", "HWO"),
            create_player("forward", "offside offensive left faceoff home wing inside", "home", "HWI"),
            create_player("defense", "offside offensive left faceoff home defense left", "home", "HD1"),
            create_player("defense", "offside offensive left faceoff home defense right", "home", "HD2"),
            
            # Offensive left dot - Away team (5 players)
            create_player("forward", "offside offensive left faceoff away center", "away", "AC"),
            create_player("forward", "offside offensive left faceoff away wing outside", "away", "AWO"),
            create_player("forward", "offside offensive left faceoff away wing inside", "away", "AWI"),
            create_player("defense", "offside offensive left faceoff away defense left", "away", "AD1"),
            create_player("defense", "offside offensive left faceoff away defense right", "away", "AD2"),
        ],
        "rink": {"view": "full"},
        "zones": [
            # Highlight the dot being shown
            {"type": "circle", "position": {"x": 20, "y": 22.5}, "radius": 3, "style": {"fill": "rgba(255,0,0,0.3)", "stroke": "#FF0000", "strokeWidth": 2}},
        ],
        "annotations": [
            {"text": "Offside Dot Face-off - 10 Players", "position": {"x": 0, "y": -40}, "anchor": "middle"},
            {"text": "Offensive Zone Left Dot", "position": {"x": 20, "y": 12}, "anchor": "middle", "style": {"fontSize": 10}},
            {"text": "HOME: HC, HWO, HWI, HD1, HD2", "position": {"x": 20, "y": 38}, "anchor": "middle", "style": {"fontSize": 9, "fill": "#0000FF"}},
            {"text": "AWAY: AC, AWO, AWI, AD1, AD2", "position": {"x": 20, "y": 40.5}, "anchor": "middle", "style": {"fontSize": 9, "fill": "#FF0000"}}
        ]
    }
    
    # Convert to spec and generate diagram
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_offside_dots.png"
    builder.build(spec, output_path)
    
    print(f"✅ Offside dot face-offs: {output_path}")
    return output_path

def test_all_neutral_dots():
    """Test all 4 offside dots and center ice."""
    builder = DiagramBuilder()
    
    # Create spec showing all dots
    spec_dict = {
        "players": [
            # Mark each dot with a player
            create_player("forward", "offside dot defensive left", "home", "DL"),
            create_player("forward", "offside dot defensive right", "home", "DR"),
            create_player("forward", "center ice", "away", "C"),
            create_player("forward", "offside dot offensive left", "home", "OL"),
            create_player("forward", "offside dot offensive right", "home", "OR"),
        ],
        "rink": {"view": "neutral"},
        "zones": [
            # Draw circles at each face-off dot
            {"type": "circle", "position": {"x": -20, "y": 22.5}, "radius": 2, "style": {"fill": "rgba(0,0,255,0.2)", "stroke": "#0000FF"}},
            {"type": "circle", "position": {"x": -20, "y": -22.5}, "radius": 2, "style": {"fill": "rgba(0,0,255,0.2)", "stroke": "#0000FF"}},
            {"type": "circle", "position": {"x": 0, "y": 0}, "radius": 15, "style": {"fill": "none", "stroke": "#FF0000", "strokeWidth": 2}},
            {"type": "circle", "position": {"x": 20, "y": 22.5}, "radius": 2, "style": {"fill": "rgba(255,0,0,0.2)", "stroke": "#FF0000"}},
            {"type": "circle", "position": {"x": 20, "y": -22.5}, "radius": 2, "style": {"fill": "rgba(255,0,0,0.2)", "stroke": "#FF0000"}},
        ],
        "annotations": [
            {"text": "All Neutral Zone Face-off Locations", "position": {"x": 0, "y": -38}, "anchor": "middle"},
            {"text": "Defensive Zone Dots", "position": {"x": -20, "y": 32}, "anchor": "middle", "style": {"fontSize": 10, "fill": "#0000FF"}},
            {"text": "Offensive Zone Dots", "position": {"x": 20, "y": 32}, "anchor": "middle", "style": {"fontSize": 10, "fill": "#FF0000"}},
            {"text": "Center Ice", "position": {"x": 0, "y": 18}, "anchor": "middle", "style": {"fontSize": 10, "fill": "#FF0000"}}
        ]
    }
    
    # Convert to spec and generate diagram
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_all_neutral_dots.png"
    builder.build(spec, output_path)
    
    print(f"✅ All neutral dots: {output_path}")
    return output_path

def test_blue_line_queues():
    """Test blue line/boards drill queue positions."""
    builder = DiagramBuilder()
    
    # Create spec showing drill queue positions
    spec_dict = {
        "players": [
            # Defensive blue line queues - show lines of 3 players
            create_player("forward", "defensive blue line left boards queue", "home", "1"),
            create_player("forward", "defensive blue line left queue 2", "home", "2"),
            create_player("forward", "defensive blue line left queue 3", "home", "3"),
            create_player("forward", "defensive blue line right boards queue", "home", "1"),
            create_player("forward", "defensive blue line right queue 2", "home", "2"),
            create_player("forward", "defensive blue line right queue 3", "home", "3"),
            
            # Offensive blue line queues - show lines of 3 players
            create_player("forward", "offensive blue line left boards queue", "away", "1"),
            create_player("forward", "offensive blue line left queue 2", "away", "2"),
            create_player("forward", "offensive blue line left queue 3", "away", "3"),
            create_player("forward", "offensive blue line right boards queue", "away", "1"),
            create_player("forward", "offensive blue line right queue 2", "away", "2"),
            create_player("forward", "offensive blue line right queue 3", "away", "3"),
        ],
        "rink": {"view": "full"},  # Changed to full view
        "zones": [
            # Blue lines
            {"type": "line", "start": {"x": -25, "y": -42.5}, "end": {"x": -25, "y": 42.5}, "style": {"stroke": "#0000FF", "strokeWidth": 3}},
            {"type": "line", "start": {"x": 25, "y": -42.5}, "end": {"x": 25, "y": 42.5}, "style": {"stroke": "#0000FF", "strokeWidth": 3}},
        ],
        "annotations": [
            {"text": "Blue Line Drill Queue Positions", "position": {"x": 0, "y": -38}, "anchor": "middle"},
            {"text": "Defensive Queues", "position": {"x": -25, "y": 0}, "anchor": "middle", "style": {"fontSize": 10, "fill": "#0000FF"}},
            {"text": "Offensive Queues", "position": {"x": 25, "y": 0}, "anchor": "middle", "style": {"fontSize": 10, "fill": "#FF0000"}},
            {"text": "Players line up at blue line/boards intersection", "position": {"x": 0, "y": 38}, "anchor": "middle", "style": {"fontSize": 9}}
        ]
    }
    
    # Convert to spec and generate diagram
    spec = dict_to_diagram_spec(spec_dict)
    output_path = "test_blue_line_queues.png"
    builder.build(spec, output_path)
    
    print(f"✅ Blue line drill queues: {output_path}")
    return output_path

if __name__ == "__main__":
    print("\n🏒 TESTING UPDATED NEUTRAL ZONE POSITIONS")
    print("="*50)
    
    print("\n1️⃣ Testing center ice face-off...")
    test_center_ice_faceoff()
    
    print("\n2️⃣ Testing offside dot face-offs...")
    test_offside_dot_faceoff()
    
    print("\n3️⃣ Testing all neutral zone dots...")
    test_all_neutral_dots()
    
    print("\n4️⃣ Testing blue line drill queues...")
    test_blue_line_queues()
    
    print("\n✅ All tests complete! Check generated PNG files.")