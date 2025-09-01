#!/usr/bin/env python3
"""Test script for the new net element visualization."""

from src.hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation

def test_net_element():
    """Test the net element in various positions."""
    builder = DiagramBuilder()
    
    # Test 1: Net in different positions
    players = [
        Player(type="net", position="net1", coordinates={"x": 30, "y": 20}, label=""),
        Player(type="net", position="net2", coordinates={"x": -30, "y": 40}, label=""),
        Player(type="net", position="net3", coordinates={"x": 0, "y": -30}, label=""),
        
        # Add some players for context
        Player(type="forward", position="F1", coordinates={"x": 20, "y": 30}, team="home", label="F1"),
        Player(type="forward", position="F2", coordinates={"x": -20, "y": 35}, team="home", label="F2"),
        Player(type="defense", position="D1", coordinates={"x": 0, "y": -20}, team="home", label="D1"),
    ]
    
    # Add some movements to show interaction with nets
    movements = [
        Movement(from_pos="F1", to_pos={"x": 30, "y": 20}, type="shot", label="Shot on net"),
        Movement(from_pos="F2", to_pos={"x": -30, "y": 40}, type="pass", label="Pass to net"),
    ]
    
    # Add annotation
    annotations = [
        Annotation(text="Net Placement Test", position={"x": 0, "y": 45}, size="large", style="bold"),
        Annotation(text="Multiple nets for practice", position={"x": 0, "y": -45}, size="medium"),
    ]
    
    spec = DiagramSpec(
        title="Net Element Test - Various Positions",
        rink={"type": "full", "zone": "offensive"},
        players=players,
        movements=movements,
        zones=[],
        annotations=annotations,
        metadata={"created_by": "test_script", "version": "1.0"}
    )
    
    # Save the test diagram
    output_path = "outputs/test_net_element.png"
    result = builder.build(spec, output_path)
    print(f"Saved net element test to {result}")
    
    # Test 2: Net with shooting drill
    builder2 = DiagramBuilder()
    
    players2 = [
        # Place net at top of slot
        Player(type="net", position="net1", coordinates={"x": 0, "y": 35}, label=""),
        
        # Shooters
        Player(type="forward", position="S1", coordinates={"x": -20, "y": 10}, team="home", label="1"),
        Player(type="forward", position="S2", coordinates={"x": 0, "y": 10}, team="home", label="2"),
        Player(type="forward", position="S3", coordinates={"x": 20, "y": 10}, team="home", label="3"),
        
        # Pucks
        Player(type="puck", position="p1", coordinates={"x": -20, "y": 8}),
        Player(type="puck", position="p2", coordinates={"x": 0, "y": 8}),
        Player(type="puck", position="p3", coordinates={"x": 20, "y": 8}),
    ]
    
    movements2 = [
        Movement(from_pos="S1", to_pos={"x": 0, "y": 35}, type="shot"),
        Movement(from_pos="S2", to_pos={"x": 0, "y": 35}, type="shot"),
        Movement(from_pos="S3", to_pos={"x": 0, "y": 35}, type="shot"),
    ]
    
    annotations2 = [
        Annotation(text="SHOOTING DRILL", position={"x": 0, "y": 45}, size="large", style="bold"),
        Annotation(text="Rapid Fire", position={"x": 0, "y": -40}, size="medium"),
    ]
    
    spec2 = DiagramSpec(
        title="Shooting Drill with Net",
        rink={"type": "full", "zone": "offensive"},
        players=players2,
        movements=movements2,
        zones=[],
        annotations=annotations2,
        metadata={"created_by": "test_script", "version": "1.0"}
    )
    
    output_path2 = "outputs/test_net_shooting_drill.png"
    result2 = builder2.build(spec2, output_path2)
    print(f"Saved shooting drill test to {result2}")

if __name__ == "__main__":
    test_net_element()