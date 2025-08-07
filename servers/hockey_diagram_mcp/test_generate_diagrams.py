#!/usr/bin/env python
"""Generate test diagrams with updated formations."""

import asyncio
from generator import HockeyDiagramGenerator, Player, Movement, CoverageZone
from elements import FORMATIONS
from PIL import Image
import io
import base64
from pathlib import Path
import json

async def test_generate_diagrams():
    generator = HockeyDiagramGenerator()
    output_dir = Path("test_diagrams")
    output_dir.mkdir(exist_ok=True)
    
    print("Generating test diagrams with updated formations...\n")
    
    # Test formations to generate
    test_formations = [
        ('2-1-2_forecheck', '2-1-2 Forecheck - Updated'),
        ('1-3-1_powerplay', '1-3-1 Power Play'),
        ('box_penalty_kill', 'Box Penalty Kill'),
        ('defensive_zone_coverage', 'Defensive Zone Coverage'),
        ('diamond_penalty_kill', 'Diamond Penalty Kill')
    ]
    
    for formation_name, title in test_formations:
        print(f"Generating {formation_name}...")
        
        # Get formation from elements
        formation = FORMATIONS.get(formation_name)
        if not formation:
            print(f"  ✗ Formation not found: {formation_name}")
            continue
            
        # Create diagram spec
        spec = {
            "type": "tactical",
            "title": title,
            "description": formation['description'],
            "players": formation['players'],
            "movements": formation.get('movements', []),
            "zones": formation.get('zones', []),
            "annotations": []
        }
        
        try:
            # Convert dicts to dataclass objects
            player_objects = [Player(**p) for p in formation['players']]
            
            movement_objects = []
            for m in formation.get('movements', []):
                movement_objects.append(Movement(**m))
            
            zone_objects = []
            for z in formation.get('zones', []):
                # Include all required attributes
                zone_obj = CoverageZone(
                    zone_type=z.get('zone_type', 'coverage'),
                    area=z.get('area', []),
                    team=z.get('team', 'home'),
                    opacity=z.get('opacity', 0.2)
                )
                zone_objects.append(zone_obj)
            
            # Generate diagram
            diagram_base64 = generator.generate_diagram(
                players=player_objects,
                movements=movement_objects,
                zones=zone_objects,
                title=title,
                output_format='png'
            )
            
            if diagram_base64:
                # Save the diagram
                img_data = base64.b64decode(diagram_base64)
                output_path = output_dir / f"{formation_name}.png"
                
                with open(output_path, 'wb') as f:
                    f.write(img_data)
                
                print(f"  ✓ Saved to: {output_path}")
                print(f"  ✓ Description: {formation['description']}")
                
                # Also save the spec for reference
                spec_path = output_dir / f"{formation_name}_spec.json"
                with open(spec_path, 'w') as f:
                    json.dump(spec, f, indent=2)
                    
            else:
                print(f"  ✗ Generation failed: No diagram returned")
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    print(f"\n✅ Test diagrams saved to: {output_dir}")
    print("\nPlease review the generated diagrams to validate:")
    print("1. 2-1-2 Forecheck: Both forwards deep, defense inside blue line")
    print("2. 1-3-1 Power Play: Proper umbrella formation")
    print("3. Box Penalty Kill: Compact box structure")
    print("4. Defensive Zone Coverage: Wingers covering points")
    print("5. Diamond Penalty Kill: Diamond shape with proper spacing")


if __name__ == "__main__":
    asyncio.run(test_generate_diagrams())