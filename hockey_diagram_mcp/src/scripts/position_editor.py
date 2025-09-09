#!/usr/bin/env python3
"""
Visual Position Editor for Hockey Diagrams
Generates diagrams showing position mappings for visual validation and editing.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

sys.path.append(str(Path(__file__).parent / "servers"))
sys.path.append(str(Path(__file__).parent / "src"))

from position_mapper import OFFENSIVE_POSITIONS, DEFENSIVE_POSITIONS, NEUTRAL_POSITIONS
from hockey_diagram_builder import DiagramBuilder
from spec_converter import dict_to_diagram_spec

class PositionVisualizer:
    def __init__(self):
        self.builder = DiagramBuilder()
        self.output_dir = Path(__file__).parent / "position_reviews"
        self.output_dir.mkdir(exist_ok=True)
        
    def visualize_zone(self, zone: str, positions: Dict[str, Tuple[float, float]], 
                       batch_size: int = 10, highlight: List[str] = None) -> List[str]:
        """Generate diagrams for positions in batches."""
        position_items = list(positions.items())
        num_batches = (len(position_items) + batch_size - 1) // batch_size
        output_files = []
        
        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(position_items))
            batch_positions = position_items[start_idx:end_idx]
            
            # Create players for this batch
            players = []
            annotations = []
            
            for i, (name, (x, y)) in enumerate(batch_positions):
                # Use different colors/types for visual distinction
                player_type = "forward" if i % 3 == 0 else "defense" if i % 3 == 1 else "goalie"
                is_highlighted = highlight and name in highlight
                
                players.append({
                    "type": player_type,
                    "position": f"P{i+1}",
                    "team": "home" if not is_highlighted else "away",  # Use away color for highlights
                    "coordinates": {"x": x, "y": y},
                    "label": f"{i+1}"  # Number label for reference
                })
                
                # Add position name as annotation near the player
                annotations.append({
                    "text": name,
                    "position": {"x": x, "y": y - 4},  # Slightly below player
                    "anchor": "middle",
                    "style": {"fontSize": 10, "fill": "#FF0000" if is_highlighted else "#000000"}
                })
            
            # Determine rink view based on zone
            if zone == "offensive":
                view = "offensive"
            elif zone == "defensive":
                view = "defensive"
            else:
                view = "neutral"
            
            # Add title annotation
            annotations.append({
                "text": f"{zone.upper()} ZONE POSITIONS (Batch {batch_idx+1}/{num_batches})",
                "position": {"x": 0, "y": -38},
                "anchor": "middle",
                "style": {"fontSize": 14, "fontWeight": "bold"}
            })
            
            # Add batch info
            annotations.append({
                "text": f"Positions {start_idx+1}-{end_idx} of {len(position_items)}",
                "position": {"x": 0, "y": 38},
                "anchor": "middle",
                "style": {"fontSize": 12}
            })
            
            # Create diagram spec as dictionary
            spec = {
                "players": players,
                "movements": [],
                "rink": {"view": view},
                "annotations": annotations
            }
            
            # Generate diagram
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{zone}_batch_{batch_idx+1}_{timestamp}.png"
            output_path = self.output_dir / filename
            
            # Convert dict to DiagramSpec
            diagram_spec = dict_to_diagram_spec(spec)
            self.builder.build(diagram_spec, str(output_path))
            output_files.append(str(output_path))
            
            print(f"✅ Generated: {filename}")
            
            # Also save position list for this batch
            list_file = self.output_dir / f"{zone}_batch_{batch_idx+1}_list.txt"
            with open(list_file, 'w') as f:
                f.write(f"{zone.upper()} ZONE - Batch {batch_idx+1}\n")
                f.write("="*50 + "\n\n")
                for i, (name, (x, y)) in enumerate(batch_positions):
                    f.write(f"{i+1:2}. {name:<35} ({x:>6.1f}, {y:>6.1f})\n")
            
        return output_files
    
    def visualize_all_zones(self, batch_size: int = 10):
        """Visualize all zones."""
        print("\n🎨 GENERATING POSITION VISUALIZATIONS")
        print("="*50)
        
        all_files = []
        
        # Offensive zone
        print("\n🔴 Offensive Zone...")
        off_files = self.visualize_zone("offensive", OFFENSIVE_POSITIONS, batch_size)
        all_files.extend(off_files)
        
        # Defensive zone  
        print("\n🔵 Defensive Zone...")
        def_files = self.visualize_zone("defensive", DEFENSIVE_POSITIONS, batch_size)
        all_files.extend(def_files)
        
        # Neutral zone
        print("\n⚪ Neutral Zone...")
        neu_files = self.visualize_zone("neutral", NEUTRAL_POSITIONS, batch_size)
        all_files.extend(neu_files)
        
        # Create index file
        self.create_index_file(all_files)
        
        print("\n" + "="*50)
        print(f"✅ Generated {len(all_files)} diagrams in: {self.output_dir}")
        print("\n📝 REVIEW INSTRUCTIONS:")
        print("1. Open the diagrams in position_reviews/")
        print("2. Review positions visually")
        print("3. Create a feedback file: position_edits.json")
        print("   Format:")
        print('   {')
        print('     "add": [')
        print('       {"zone": "offensive", "name": "bumper", "x": -65, "y": 0}')
        print('     ],')
        print('     "edit": [')
        print('       {"zone": "neutral", "name": "center ice", "new_x": -1, "new_y": 0}')
        print('     ],')
        print('     "delete": [')
        print('       {"zone": "offensive", "name": "duplicate_position"}')
        print('     ]')
        print('   }')
        print("4. Run: python3 position_editor.py --apply-edits")
        
    def create_index_file(self, files: List[str]):
        """Create an HTML index for easy viewing."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Hockey Position Review</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .zone { margin: 20px 0; padding: 10px; border: 1px solid #ccc; }
        .zone h2 { margin-top: 0; }
        img { max-width: 800px; margin: 10px 0; border: 1px solid #ddd; }
        .offensive { background: #ffe0e0; }
        .defensive { background: #e0e0ff; }
        .neutral { background: #f0f0f0; }
    </style>
</head>
<body>
    <h1>Hockey Position Visual Review</h1>
    <p>Review these position mappings and create position_edits.json with your feedback.</p>
"""
        
        # Group files by zone
        for zone in ["offensive", "defensive", "neutral"]:
            zone_files = [f for f in files if zone in f and f.endswith('.png')]
            if zone_files:
                html += f'<div class="zone {zone}">\n'
                html += f'<h2>{zone.upper()} Zone</h2>\n'
                for f in zone_files:
                    filename = Path(f).name
                    html += f'<h3>{filename}</h3>\n'
                    html += f'<img src="{filename}" alt="{filename}"/>\n'
                html += '</div>\n'
        
        html += """
    <div style="margin-top: 40px; padding: 20px; background: #ffffcc;">
        <h2>How to Provide Feedback</h2>
        <p>Create a file called <code>position_edits.json</code> with your changes:</p>
        <pre>
{
  "add": [
    {"zone": "offensive", "name": "new_position", "x": -50, "y": 10}
  ],
  "edit": [
    {"zone": "neutral", "name": "existing_position", "new_x": 0, "new_y": 5}
  ],
  "delete": [
    {"zone": "defensive", "name": "unwanted_position"}
  ]
}
        </pre>
    </div>
</body>
</html>"""
        
        index_path = self.output_dir / "index.html"
        with open(index_path, 'w') as f:
            f.write(html)
        print(f"\n🌐 Open {index_path} in your browser for easy review")

def apply_edits(edits_file: str = "position_edits.json"):
    """Apply edits from JSON file to position_mapper.py."""
    edits_path = Path(edits_file)
    if not edits_path.exists():
        print(f"❌ No edits file found: {edits_file}")
        print("   Create this file with your position changes")
        return
    
    with open(edits_path, 'r') as f:
        edits = json.load(f)
    
    print("\n📝 APPLYING EDITS")
    print("="*50)
    
    # Load current positions
    positions = {
        "offensive": dict(OFFENSIVE_POSITIONS),
        "defensive": dict(DEFENSIVE_POSITIONS),
        "neutral": dict(NEUTRAL_POSITIONS)
    }
    
    # Apply additions
    if "add" in edits:
        for item in edits["add"]:
            zone = item["zone"]
            name = item["name"]
            positions[zone][name] = (item["x"], item["y"])
            print(f"✅ Added: {zone}/{name} at ({item['x']}, {item['y']})")
    
    # Apply edits
    if "edit" in edits:
        for item in edits["edit"]:
            zone = item["zone"]
            name = item["name"]
            if name in positions[zone]:
                old_pos = positions[zone][name]
                positions[zone][name] = (item["new_x"], item["new_y"])
                print(f"✅ Edited: {zone}/{name} from {old_pos} to ({item['new_x']}, {item['new_y']})")
    
    # Apply deletions
    if "delete" in edits:
        for item in edits["delete"]:
            zone = item["zone"]
            name = item["name"]
            if name in positions[zone]:
                del positions[zone][name]
                print(f"✅ Deleted: {zone}/{name}")
    
    # Generate updated position_mapper.py code
    print("\n📄 Updated position_mapper.py code:")
    print("="*50)
    print("\n# Copy this to position_mapper.py:\n")
    
    for zone_name, zone_positions in positions.items():
        var_name = f"{zone_name.upper()}_POSITIONS"
        print(f"{var_name} = {{")
        for name, (x, y) in sorted(zone_positions.items()):
            print(f'    "{name}": ({x}, {y}),')
        print("}\n")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Visual Position Editor")
    parser.add_argument("--batch-size", type=int, default=10, 
                       help="Number of positions per diagram")
    parser.add_argument("--zone", choices=["offensive", "defensive", "neutral"],
                       help="Visualize specific zone only")
    parser.add_argument("--apply-edits", action="store_true",
                       help="Apply edits from position_edits.json")
    parser.add_argument("--edits-file", default="position_edits.json",
                       help="Path to edits JSON file")
    
    args = parser.parse_args()
    
    if args.apply_edits:
        apply_edits(args.edits_file)
    else:
        viz = PositionVisualizer()
        
        if args.zone:
            # Visualize single zone
            if args.zone == "offensive":
                viz.visualize_zone("offensive", OFFENSIVE_POSITIONS, args.batch_size)
            elif args.zone == "defensive":
                viz.visualize_zone("defensive", DEFENSIVE_POSITIONS, args.batch_size)
            else:
                viz.visualize_zone("neutral", NEUTRAL_POSITIONS, args.batch_size)
        else:
            # Visualize all zones
            viz.visualize_all_zones(args.batch_size)

if __name__ == "__main__":
    main()