"""
Comprehensive test suite for enhanced hockey diagram parsing accuracy.

Tests all major diagram types:
1. Base NHL rink with different focus areas
2. Position areas and zone coverage
3. Drill sequences and progressions  
4. Faceoff setups and responsibilities
5. Tactical plays (breakouts, forechecks, etc.)
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from servers.hockey_diagram_mcp.enhanced_parser import EnhancedHockeyParser
from servers.hockey_diagram_mcp.generator import HockeyDiagramGenerator

async def test_base_rink_views():
    """Test base NHL rink generation with different focus areas."""
    print("🏒 Testing Base NHL Rink Views...")
    
    parser = EnhancedHockeyParser()
    generator = HockeyDiagramGenerator()
    
    test_cases = [
        ("Full rink overview", "full"),
        ("Offensive zone focus", "offensive"), 
        ("Defensive zone focus", "defensive"),
        ("Neutral zone focus", "neutral"),
    ]
    
    for description, view in test_cases:
        try:
            spec = await parser.parse_prompt(f"Show {description} with basic player positions", 
                                           {"diagram_type": "formation"})
            spec.view = view  # Override view
            
            # Generate diagram
            base64_img = generator.generate_diagram(
                players=spec.players,
                movements=spec.movements, 
                zones=spec.zones,
                view=view,
                title=description,
                output_format="png"
            )
            
            # Save to file
            filename = f"test_base_rink_{view}.png"
            generator.save_to_file(base64_img, filename, "png")
            print(f"✅ {description}: {filename}")
            
        except Exception as e:
            print(f"❌ {description}: {e}")

async def test_position_areas():
    """Test position area recognition and zone shading."""
    print("\n🎯 Testing Position Areas...")
    
    parser = EnhancedHockeyParser()
    generator = HockeyDiagramGenerator()
    
    test_cases = [
        "Show defensive coverage in the slot area",
        "Highlight left point position for power play",
        "Mark the high slot for screening positions", 
        "Show corner coverage responsibilities",
        "Display neutral zone trap positioning",
    ]
    
    for i, prompt in enumerate(test_cases):
        try:
            spec = await parser.parse_prompt(prompt, {"diagram_type": "formation"})
            
            base64_img = generator.generate_diagram(
                players=spec.players,
                movements=spec.movements,
                zones=spec.zones,
                view="full",
                title=prompt,
                output_format="png"
            )
            
            filename = f"test_position_area_{i+1}.png"
            generator.save_to_file(base64_img, filename, "png")
            print(f"✅ Position Area {i+1}: {filename}")
            
        except Exception as e:
            print(f"❌ Position Area {i+1}: {e}")

async def test_drill_sequences():
    """Test drill pattern parsing and sequence visualization."""
    print("\n🥅 Testing Drill Sequences...")
    
    parser = EnhancedHockeyParser()
    generator = HockeyDiagramGenerator()
    
    test_cases = [
        "3 player passing drill: Step 1 - triangle formation, Step 2 - pass clockwise, Step 3 - follow pass",
        "2-on-1 drill: Forwards start at blue line, pass between cones, attack goal",
        "Breakout drill: D1 retrieves puck behind net, passes to C at half wall, C passes to winger",
        "Figure 8 skating drill with cone weaving",
        "Power play entry drill: Point pass to half wall, cycle to slot"
    ]
    
    for i, prompt in enumerate(test_cases):
        try:
            spec = await parser.parse_prompt(prompt, {"diagram_type": "drill"})
            
            base64_img = generator.generate_diagram(
                players=spec.players,
                movements=spec.movements,
                zones=spec.zones,
                view="full", 
                title=f"Drill {i+1}",
                output_format="png"
            )
            
            filename = f"test_drill_sequence_{i+1}.png"
            generator.save_to_file(base64_img, filename, "png")
            print(f"✅ Drill {i+1}: {filename}")
            
        except Exception as e:
            print(f"❌ Drill {i+1}: {e}")

async def test_faceoff_setups():
    """Test faceoff position parsing and coverage."""
    print("\n⚪ Testing Faceoff Setups...")
    
    parser = EnhancedHockeyParser()
    generator = HockeyDiagramGenerator()
    
    test_cases = [
        "Defensive zone faceoff left dot: center vs center, wingers on boards, defense cover points",
        "Offensive zone faceoff right dot: power play setup with umbrella formation",
        "Neutral zone faceoff: standard coverage with center ice positioning",
        "Penalty kill faceoff: box formation defensive setup"
    ]
    
    for i, prompt in enumerate(test_cases):
        try:
            spec = await parser.parse_prompt(prompt, {"diagram_type": "faceoff"})
            
            base64_img = generator.generate_diagram(
                players=spec.players,
                movements=spec.movements,
                zones=spec.zones,
                view="full",
                title=f"Faceoff {i+1}",
                output_format="png"
            )
            
            filename = f"test_faceoff_{i+1}.png"
            generator.save_to_file(base64_img, filename, "png")
            print(f"✅ Faceoff {i+1}: {filename}")
            
        except Exception as e:
            print(f"❌ Faceoff {i+1}: {e}")

async def test_tactical_plays():
    """Test tactical play parsing and flow visualization.""" 
    print("\n⚡ Testing Tactical Plays...")
    
    parser = EnhancedHockeyParser()
    generator = HockeyDiagramGenerator()
    
    test_cases = [
        "2-1-2 forecheck: F1 pressures behind net, F2 supports high, F3 covers middle",
        "Breakout play: reverse behind net, center swings to support, quick up to winger",
        "Zone entry: drop pass at blue line, trailer carries wide, support from center",
        "Power play cycle: boards to corner, behind net, out to point",
        "Penalty kill box: compact formation, pressure puck carrier, cover passing lanes"
    ]
    
    for i, prompt in enumerate(test_cases):
        try:
            spec = await parser.parse_prompt(prompt, {"diagram_type": "play"})
            
            base64_img = generator.generate_diagram(
                players=spec.players,
                movements=spec.movements,
                zones=spec.zones,
                view="full",
                title=f"Play {i+1}", 
                output_format="png"
            )
            
            filename = f"test_tactical_play_{i+1}.png"
            generator.save_to_file(base64_img, filename, "png")
            print(f"✅ Tactical Play {i+1}: {filename}")
            
        except Exception as e:
            print(f"❌ Tactical Play {i+1}: {e}")

async def test_preset_comparison():
    """Compare enhanced parsing with preset formations."""
    print("\n🔄 Testing Preset vs Enhanced Parsing...")
    
    parser = EnhancedHockeyParser()
    generator = HockeyDiagramGenerator()
    
    # Test same formation as preset
    try:
        spec = await parser.parse_prompt("2-1-2 forecheck formation with F1 and F2 pressuring high", 
                                       {"diagram_type": "formation"})
        
        base64_img = generator.generate_diagram(
            players=spec.players,
            movements=spec.movements,
            zones=spec.zones,
            view="full",
            title="Enhanced Parser 2-1-2",
            output_format="png"
        )
        
        filename = "test_enhanced_vs_preset.png"
        generator.save_to_file(base64_img, filename, "png")
        print(f"✅ Enhanced vs Preset: {filename}")
        
    except Exception as e:
        print(f"❌ Enhanced vs Preset: {e}")

async def run_all_tests():
    """Run comprehensive test suite."""
    print("🚀 Starting Enhanced Hockey Diagram Parser Tests\n" + "="*60)
    
    await test_base_rink_views()
    await test_position_areas() 
    await test_drill_sequences()
    await test_faceoff_setups()
    await test_tactical_plays()
    await test_preset_comparison()
    
    print("\n" + "="*60)
    print("✅ Enhanced parsing tests complete! Check generated images.")

if __name__ == "__main__":
    asyncio.run(run_all_tests())