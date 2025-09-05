"""
Interactive hockey diagram builder.
Interprets natural language descriptions to create hockey diagrams.
"""

from hockey_rink import HockeyRink
from typing import Dict, List, Tuple, Optional
import re

class DiagramBuilder:
    """Builds hockey diagrams from natural language descriptions."""
    
    def __init__(self):
        self.rink = None
        self.player_positions = {}
        self.formation_presets = {
            '2-1-2': {
                'description': 'Standard breakout formation',
                'positions': {
                    'D1': (-80, 20), 'D2': (-80, -20),
                    'C': (-40, 0),
                    'LW': (-30, 30), 'RW': (-30, -30)
                }
            },
            '1-2-2': {
                'description': 'Neutral zone trap',
                'positions': {
                    'F1': (30, 0),
                    'F2': (10, 15), 'F3': (10, -15),
                    'D1': (-10, 20), 'D2': (-10, -20)
                }
            },
            'umbrella': {
                'description': 'Power play umbrella',
                'positions': {
                    'C': (140, 0),
                    'D1': (155, 22), 'D2': (155, -22),
                    'LW': (175, 15), 'RW': (175, -15)
                }
            },
            'overload': {
                'description': 'Power play overload',
                'positions': {
                    'D1': (155, 20), 'D2': (140, -5),
                    'F1': (175, -25), 'F2': (160, -15), 'F3': (150, 0)
                }
            }
        }
        
    def parse_description(self, description: str) -> Dict:
        """
        Parse natural language description into diagram instructions.
        
        Returns dict with:
        - rink_type: 'full', 'half', or 'zone'
        - formation: recognized formation name or None
        - players: list of player positions
        - actions: movements, passes, etc.
        """
        desc_lower = description.lower()
        
        # Determine rink type
        if 'full' in desc_lower or 'neutral zone' in desc_lower or 'rush' in desc_lower:
            rink_type = 'full'
        elif 'half' in desc_lower or 'breakout' in desc_lower:
            rink_type = 'half'
        elif 'zone' in desc_lower or 'power play' in desc_lower or 'pp' in desc_lower:
            rink_type = 'zone'
        else:
            rink_type = 'full'  # default
            
        # Check for formations
        formation = None
        for form_name, form_data in self.formation_presets.items():
            if form_name in desc_lower or form_data['description'].lower() in desc_lower:
                formation = form_name
                break
                
        # Parse player positions
        players = []
        position_patterns = [
            r'(\w+) (?:at|in|on) (?:the )?([\w\s]+)',
            r'place (\w+) (?:at|in|on) ([\w\s]+)',
            r'(\w+) positioned? (?:at|in|on) ([\w\s]+)'
        ]
        
        for pattern in position_patterns:
            matches = re.findall(pattern, desc_lower)
            for match in matches:
                players.append({'label': match[0].upper(), 'location': match[1]})
                
        # Parse actions
        actions = []
        if 'pass' in desc_lower:
            pass_matches = re.findall(r'pass (?:from |the puck from )?(\w+) to (\w+)', desc_lower)
            for match in pass_matches:
                actions.append({'type': 'pass', 'from': match[0].upper(), 'to': match[1].upper()})
                
        if 'move' in desc_lower or 'skate' in desc_lower:
            move_matches = re.findall(r'(\w+) (?:moves?|skates?) (?:to |towards? )?([\w\s]+)', desc_lower)
            for match in move_matches:
                actions.append({'type': 'movement', 'player': match[0].upper(), 'to': match[1]})
                
        return {
            'rink_type': rink_type,
            'formation': formation,
            'players': players,
            'actions': actions,
            'has_puck': 'puck' in desc_lower
        }
        
    def location_to_coords(self, location: str, rink_type: str) -> Tuple[float, float]:
        """Convert location description to coordinates."""
        loc = location.lower().strip()
        
        # Zone-based locations
        zone_locations = {
            'center': (0, 0),
            'center ice': (0, 0),
            'left wing': (-30, 30),
            'right wing': (-30, -30),
            'left point': (155, 22),
            'right point': (155, -22),
            'high slot': (150, 0),
            'low slot': (170, 0),
            'left corner': (185, -30),
            'right corner': (185, 30),
            'behind net': (190, 0),
            'net front': (180, 0),
            'left boards': (0, 42),
            'right boards': (0, -42),
            'blue line': (136, 0),
            'goal line': (189, 0),
            'left circle': (169, 22),
            'right circle': (169, -22),
            'half wall': (160, -15),
            'left half wall': (160, 15),
            'right half wall': (160, -15)
        }
        
        # Check for exact matches
        if loc in zone_locations:
            return zone_locations[loc]
            
        # Check for partial matches
        for key, coords in zone_locations.items():
            if key in loc or loc in key:
                return coords
                
        # Default to center if can't parse
        return (0, 0)
        
    def build_diagram(self, description: str) -> HockeyRink:
        """Build a complete diagram from natural language description."""
        parsed = self.parse_description(description)
        
        # Create rink
        self.rink = HockeyRink(rink_type=parsed['rink_type'])
        
        # Apply formation if recognized
        if parsed['formation']:
            preset = self.formation_presets[parsed['formation']]
            for label, pos in preset['positions'].items():
                self.rink.add_player(pos[0], pos[1], label, team='home')
                self.player_positions[label] = pos
                
        # Add custom players
        for player in parsed['players']:
            coords = self.location_to_coords(player['location'], parsed['rink_type'])
            self.rink.add_player(coords[0], coords[1], player['label'], team='home')
            self.player_positions[player['label']] = coords
            
        # Add puck at first player position or center
        if parsed['has_puck'] and self.player_positions:
            first_player = list(self.player_positions.values())[0]
            self.rink.add_puck(first_player[0], first_player[1])
            
        # Add actions
        for action in parsed['actions']:
            if action['type'] == 'pass':
                if action['from'] in self.player_positions and action['to'] in self.player_positions:
                    start = self.player_positions[action['from']]
                    end = self.player_positions[action['to']]
                    self.rink.add_pass(start, end)
                    
            elif action['type'] == 'movement':
                if action['player'] in self.player_positions:
                    start = self.player_positions[action['player']]
                    end = self.location_to_coords(action['to'], parsed['rink_type'])
                    self.rink.add_movement(start, end)
                    
        return self.rink


def interactive_mode():
    """Run the diagram builder in interactive mode."""
    print("\n🏒 Hockey Diagram Builder - Interactive Mode")
    print("=" * 50)
    print("\nDescribe your hockey diagram in natural language.")
    print("Examples:")
    print("  - 'Show a 2-1-2 breakout with D1 passing to the right wing'")
    print("  - 'Power play umbrella formation in the offensive zone'")
    print("  - 'Create a 3-on-2 rush with the center carrying the puck'")
    print("\nType 'quit' to exit, 'help' for more commands\n")
    
    builder = DiagramBuilder()
    diagram_count = 0
    
    while True:
        description = input("\n📝 Describe your diagram: ").strip()
        
        if description.lower() == 'quit':
            print("Thanks for using Hockey Diagram Builder!")
            break
            
        elif description.lower() == 'help':
            print("\nAvailable commands:")
            print("  - Describe any hockey play, formation, or drill")
            print("  - Mention 'full rink', 'half ice', or 'offensive zone'")
            print("  - Include player positions: 'D1 at the blue line'")
            print("  - Add movements: 'center moves to the slot'")
            print("  - Add passes: 'pass from D1 to the center'")
            print("\nPreset formations: 2-1-2, 1-2-2, umbrella, overload")
            continue
            
        elif description.lower() == 'list':
            print("\nAvailable formations:")
            for name, data in builder.formation_presets.items():
                print(f"  - {name}: {data['description']}")
            continue
            
        try:
            print(f"\n🎨 Building diagram...")
            rink = builder.build_diagram(description)
            
            diagram_count += 1
            filename = f"diagram_{diagram_count}.png"
            rink.save(filename)
            print(f"✅ Diagram saved as {filename}")
            
        except Exception as e:
            print(f"❌ Error creating diagram: {e}")
            print("Try being more specific or use one of the example formats.")


if __name__ == "__main__":
    interactive_mode()