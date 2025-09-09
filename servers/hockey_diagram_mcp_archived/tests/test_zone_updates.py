#!/usr/bin/env python
"""Test zone grid updates and formation positioning."""

from zone_grid_hockey_names import hockey_zone_grid
from elements import FORMATIONS
import json


def test_zone_updates():
    print("Testing Zone Grid Updates and Formation Positioning\n")
    print("=" * 60)
    
    # Test 1: Hockey-friendly zone names
    print("\n1. Testing Hockey-Friendly Zone Names:")
    print("-" * 40)
    test_zones = [
        'o-slot-high',
        'o-slot-low', 
        'o-point-left',
        'o-point-right',
        'd-corner-left-high',
        'neutral-left-wing-high'
    ]
    
    for zone in test_zones:
        coords = hockey_zone_grid.get_zone_position(zone)
        info = hockey_zone_grid.get_zone_info(zone)
        if info:
            print(f"✓ {zone}: ({coords[0]}, {coords[1]}) - {info.description}")
        else:
            print(f"✗ {zone}: NOT FOUND")
    
    # Test 2: Backward compatibility
    print("\n\n2. Testing Backward Compatibility:")
    print("-" * 40)
    old_zones = ['off-center-right-mid-high', 'def-left-high', 'neu-left-mid-low']
    
    for old_zone in old_zones:
        new_name = hockey_zone_grid.convert_technical_to_hockey(old_zone)
        coords = hockey_zone_grid.get_zone_position(old_zone)
        print(f"✓ {old_zone} → {new_name}: ({coords[0]}, {coords[1]})")
    
    # Test 3: Updated formations
    print("\n\n3. Testing Updated Formations:")
    print("-" * 40)
    
    test_formations = ['2-1-2_forecheck', '1-3-1_powerplay', 'box_penalty_kill', 
                      'defensive_zone_coverage', 'diamond_penalty_kill']
    
    for formation_name in test_formations:
        formation = FORMATIONS.get(formation_name)
        if formation:
            print(f"\n✓ {formation_name}:")
            print(f"  Description: {formation['description']}")
            print(f"  Players ({len(formation['players'])}):")
            
            # Show player positions and their zones
            for player in formation['players'][:5]:  # First 5 players
                x, y = player['x'], player['y']
                zone = hockey_zone_grid.get_zone_by_position(x, y)
                pos = player['position']
                print(f"    - {pos}: ({x}, {y}) → {zone}")
        else:
            print(f"\n✗ {formation_name}: NOT FOUND")
    
    # Test 4: Key hockey areas
    print("\n\n4. Testing Key Hockey Areas:")
    print("-" * 40)
    areas = hockey_zone_grid.get_key_hockey_areas()
    
    for area_name, zones in areas.items():
        print(f"\n{area_name.upper()}:")
        for zone in zones[:3]:  # First 3 zones
            coords = hockey_zone_grid.get_zone_position(zone)
            print(f"  - {zone}: ({coords[0]}, {coords[1]})")
    
    # Test 5: Validate 2-1-2 forecheck specifically
    print("\n\n5. Validating 2-1-2 Forecheck Corrections:")
    print("-" * 40)
    formation = FORMATIONS.get('2-1-2_forecheck')
    if formation:
        print("Player positions:")
        for player in formation['players']:
            if player['position'] in ['LW', 'RW', 'C', 'LD', 'RD']:
                x, y = player['x'], player['y']
                zone = hockey_zone_grid.get_zone_by_position(x, y)
                print(f"  {player['position']}: x={x}, y={y} → {zone}")
                
                # Validate positioning
                if player['position'] in ['LW', 'RW'] and player.get('team') == 'home':
                    if x > 70:
                        print(f"    ✓ Forward deep (x={x} > 70)")
                    else:
                        print(f"    ✗ Forward not deep enough (x={x} <= 70)")
                
                if player['position'] in ['LD', 'RD']:
                    if 25 <= x <= 35:
                        print(f"    ✓ Defense inside blue line (25 <= x={x} <= 35)")
                    else:
                        print(f"    ✗ Defense positioning incorrect (x={x})")


if __name__ == "__main__":
    test_zone_updates()