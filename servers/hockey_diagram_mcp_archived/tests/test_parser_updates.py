#!/usr/bin/env python
"""Test parser with updated formations and zone names."""

import asyncio
from two_stage_parser import TwoStageHockeyParser
from zone_grid_hockey_names import hockey_zone_grid
from elements import FORMATIONS
import json


async def test_parser():
    parser = TwoStageHockeyParser()
    
    print('Testing parser with updated formations and hockey-friendly zone names...\n')
    
    # Test cases that should use updated formations
    test_cases = [
        '2-1-2 forecheck with aggressive pressure',
        '1-3-1 power play umbrella formation',
        'box penalty kill formation',
        'defensive zone coverage system',
        'show me a neutral zone trap',
        'diamond penalty kill setup'
    ]
    
    for prompt in test_cases:
        print(f'\n=== Testing: "{prompt}" ===')
        try:
            result = await parser.parse(prompt)
            
            # Check if preset formation was used
            if 'formation_preset' in result:
                print(f'✓ Used preset: {result["formation_preset"]}')
                formation = FORMATIONS.get(result['formation_preset'])
                if formation:
                    print(f'✓ Description: {formation["description"]}')
                    print(f'✓ Players: {len(formation["players"])} positioned')
                    
                    # Show first few player positions
                    for i, player in enumerate(formation['players'][:3]):
                        print(f'  - {player["position"]}: x={player["x"]}, y={player["y"]}')
                else:
                    print('✗ Formation not found in FORMATIONS dict')
            
            # Check zone mappings
            if 'players' in result:
                print(f'\n  Zone mappings:')
                for player in result['players'][:3]:
                    x, y = player['x'], player['y']
                    zone = hockey_zone_grid.get_zone_by_position(x, y)
                    print(f'  - {player["position"]} at ({x},{y}) → Zone: {zone}')
                    
        except Exception as e:
            print(f'✗ Error: {str(e)}')
    
    print('\n\n=== Testing hockey-friendly zone names ===')
    # Test that zone names work
    test_zones = ['o-slot-high', 'o-point-left', 'd-corner-left-high', 'neutral-left-wing-high']
    for zone in test_zones:
        coords = hockey_zone_grid.get_zone_position(zone)
        print(f'{zone}: {coords}')
    
    # Test backward compatibility
    print('\n=== Testing backward compatibility ===')
    old_zones = ['off-center-right-mid-high', 'def-left-high']
    for zone in old_zones:
        coords = hockey_zone_grid.get_zone_position(zone)
        new_name = hockey_zone_grid.convert_technical_to_hockey(zone)
        print(f'{zone} → {new_name}: {coords}')

    # Test key hockey areas
    print('\n=== Testing key hockey areas ===')
    areas = hockey_zone_grid.get_key_hockey_areas()
    for area_name, zones in areas.items():
        print(f'{area_name}: {zones[:2]}...')  # Show first 2 zones


if __name__ == "__main__":
    asyncio.run(test_parser())