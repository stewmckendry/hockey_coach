#!/usr/bin/env python3
"""Quick test to see player and movement coordinates from saved spec."""

import json
from pathlib import Path

def show_coordinates(spec_file):
    """Display coordinates from a saved spec file."""
    
    # Load the spec
    with open(spec_file, 'r') as f:
        spec = json.load(f)
    
    print(f"\n{'='*80}")
    print(f"HOCKEY DIAGRAM COORDINATE ANALYSIS")
    print(f"{'='*80}")
    print(f"Title: {spec.get('title', 'Unknown')}")
    print(f"Description: {spec.get('description', 'Unknown')}")
    print(f"{'='*80}\n")
    
    # Show player positions
    players = spec.get("players", [])
    print("PLAYER POSITIONS:")
    print("-" * 60)
    print(f"{'ID':<5} {'Label':<6} {'Team':<6} {'Type':<10} {'X':>7} {'Y':>7}")
    print("-" * 60)
    
    for player in players:
        coords = player.get("coordinates", {})
        print(f"{player['id']:<5} {player.get('label', 'N/A'):<6} {player['team']:<6} {player['type']:<10} {coords.get('x', 0):>7.1f} {coords.get('y', 0):>7.1f}")
    
    # Show movements
    movements = spec.get("movements", [])
    print(f"\n{'='*60}")
    print("MOVEMENTS:")
    print("-" * 60)
    
    for idx, movement in enumerate(movements, 1):
        print(f"\nMovement {idx}: {movement['type'].upper()} (style: {movement.get('style', 'solid')})")
        
        from_pos = movement.get('from_pos', {})
        to_pos = movement.get('to_pos', {})
        
        print(f"  From: ({from_pos.get('x', 0):>6.1f}, {from_pos.get('y', 0):>6.1f})")
        print(f"  To:   ({to_pos.get('x', 0):>6.1f}, {to_pos.get('y', 0):>6.1f})")
        
        # Calculate distance
        dx = to_pos.get('x', 0) - from_pos.get('x', 0)
        dy = to_pos.get('y', 0) - from_pos.get('y', 0)
        distance = (dx**2 + dy**2)**0.5
        print(f"  Distance: {distance:.1f} units")
        print(f"  Direction: X={'→' if dx > 0 else '←' if dx < 0 else '─'} ({dx:+.1f}), Y={'↑' if dy > 0 else '↓' if dy < 0 else '─'} ({dy:+.1f})")
        
        # Check waypoints
        waypoints = movement.get('waypoints', [])
        if waypoints:
            print(f"  Waypoints ({len(waypoints)}):")
            for wp in waypoints:
                print(f"    • ({wp.get('x', 0):>6.1f}, {wp.get('y', 0):>6.1f})")
        
        # Match movement to players
        print(f"  Player Analysis:")
        
        # Find closest player to start
        min_start_dist = float('inf')
        start_player = None
        for player in players:
            coords = player.get("coordinates", {})
            dist = ((from_pos.get('x', 0) - coords.get('x', 0))**2 + 
                   (from_pos.get('y', 0) - coords.get('y', 0))**2)**0.5
            if dist < min_start_dist:
                min_start_dist = dist
                start_player = player
        
        if start_player and min_start_dist < 5:
            print(f"    ✅ Starts from {start_player.get('label', start_player['id'])} (distance: {min_start_dist:.1f})")
        else:
            print(f"    ⚠️  No player at start position (nearest: {start_player.get('label', start_player['id']) if start_player else 'None'} at {min_start_dist:.1f} units)")
        
        # For passes, find closest player to end
        if movement['type'] == 'pass':
            min_end_dist = float('inf')
            end_player = None
            for player in players:
                coords = player.get("coordinates", {})
                dist = ((to_pos.get('x', 0) - coords.get('x', 0))**2 + 
                       (to_pos.get('y', 0) - coords.get('y', 0))**2)**0.5
                if dist < min_end_dist:
                    min_end_dist = dist
                    end_player = player
            
            if end_player and min_end_dist < 5:
                print(f"    ✅ Targets {end_player.get('label', end_player['id'])} (distance: {min_end_dist:.1f})")
            else:
                print(f"    ⚠️  No player at target (nearest: {end_player.get('label', end_player['id']) if end_player else 'None'} at {min_end_dist:.1f} units)")
        
        # For shots, check if it targets the net
        if movement['type'] == 'shot':
            net_dist = abs(to_pos.get('x', 0) - 89)
            if net_dist < 5:
                print(f"    ✅ Shot targets net (distance from net: {net_dist:.1f})")
            else:
                print(f"    ❌ Shot misses net (distance from net: {net_dist:.1f})")
    
    # Overall assessment
    print(f"\n{'='*60}")
    print("HOCKEY SENSE CHECK:")
    print("-" * 60)
    
    issues = []
    
    # Check each movement
    for idx, movement in enumerate(movements, 1):
        from_pos = movement.get('from_pos', {})
        to_pos = movement.get('to_pos', {})
        
        # Check if movement starts from a player
        min_dist = float('inf')
        for player in players:
            coords = player.get("coordinates", {})
            dist = ((from_pos.get('x', 0) - coords.get('x', 0))**2 + 
                   (from_pos.get('y', 0) - coords.get('y', 0))**2)**0.5
            min_dist = min(min_dist, dist)
        
        if min_dist > 5:
            issues.append(f"Movement {idx} doesn't start from any player (gap: {min_dist:.1f})")
        
        # Check shot targets net
        if movement['type'] == 'shot':
            net_dist = abs(to_pos.get('x', 0) - 89)
            if net_dist > 5:
                issues.append(f"Shot {idx} doesn't target net (off by {net_dist:.1f})")
        
        # Check pass targets player
        if movement['type'] == 'pass':
            min_dist = float('inf')
            for player in players:
                coords = player.get("coordinates", {})
                dist = ((to_pos.get('x', 0) - coords.get('x', 0))**2 + 
                       (to_pos.get('y', 0) - coords.get('y', 0))**2)**0.5
                min_dist = min(min_dist, dist)
            if min_dist > 10:
                issues.append(f"Pass {idx} doesn't target any player (gap: {min_dist:.1f})")
    
    if issues:
        print(f"❌ {len(issues)} ISSUES FOUND:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("✅ ALL MOVEMENTS MAKE HOCKEY SENSE!")
        print("  • All movements start from player positions")
        print("  • Passes target players appropriately")
        print("  • Shots target the net")

if __name__ == "__main__":
    # Check for most recent spec file
    outputs_dir = Path(__file__).parent.parent / "outputs"
    
    # Look for test specs
    test_specs = list(outputs_dir.glob("*test*.json"))
    test_specs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    if test_specs:
        spec_file = test_specs[0]
        print(f"Analyzing: {spec_file.name}")
        show_coordinates(spec_file)
    else:
        print("No test spec files found in outputs/")
        print("Run test_single_movement.py first to generate a spec")