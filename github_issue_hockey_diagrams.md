# Replace Stability AI with Programmatic Hockey Diagram Generation via MCP Server

## Problem Statement
The current Stability AI approach for generating hockey tactical diagrams is failing because:
- AI image generation is designed for artistic creation, not precise technical diagrams
- Each iterative edit introduces more errors rather than improvements
- Lack of precision control for exact measurements and standardized layouts
- The AI doesn't understand hockey rink specifications
- Resulting diagrams fail basic accuracy requirements (missing nets, wrong line colors, incorrect face-off dots)

## Current Issues with Generated Diagrams
- Goal lines not red
- Missing goal nets
- Goal creases not blue with red outline
- Face-off dots shown as + symbols instead of dots
- Missing neutral zone dots
- Inconsistent proportions
- Each iteration makes the image worse, not better

## Proposed Solution
Create an MCP server that combines natural language understanding with programmatic diagram generation:
1. **Natural Language Input**: Claude Code calls MCP tool with coaching instructions
2. **LLM Parsing**: Use GPT-4 to convert instructions to structured specifications
3. **Programmatic Generation**: Use sportypy to create precise diagrams
4. **MCP Resource Output**: Return diagrams as MCP resources for immediate use

## Architecture Overview

### MCP Server Flow
```
Claude Code → MCP Tool Call → LLM Parser → Diagram Spec → Sportypy → Image → MCP Resource
     ↓              ↓              ↓             ↓            ↓          ↓
"2-1-2       generate_hockey   Parse to    {players:[],   Generate   Return
forecheck"    _diagram tool     JSON spec    movements:[]} NHL rink   PNG/SVG
```

### Example MCP Tool Implementation
```python
# hockey_diagram_mcp_server.py
from fastmcp import FastMCP
from sportypy.surfaces import NHLRink
import openai
import json

mcp = FastMCP("Hockey Diagram Generator")

@mcp.tool()
async def generate_hockey_diagram(prompt: str, diagram_type: str = "tactical") -> str:
    """
    Generate a hockey diagram from natural language instructions.
    
    Args:
        prompt: Natural language description (e.g., "2-1-2 forecheck with center 
                pressuring puck carrier")
        diagram_type: Type of diagram (tactical, drill, system)
    
    Returns:
        Path to generated diagram image
    """
    
    # Step 1: Use LLM to parse natural language
    diagram_spec = await parse_hockey_prompt(prompt)
    
    # Step 2: Generate diagram programmatically
    diagram_path = await create_diagram_from_spec(diagram_spec)
    
    return diagram_path

async def parse_hockey_prompt(prompt: str) -> dict:
    """Convert natural language to structured diagram specification"""
    
    system_prompt = """You are a hockey tactics parser. Convert natural language 
    hockey instructions into structured JSON for diagram generation.
    
    Output format:
    {
        "players": [
            {"position": "C", "x": 0, "y": 0, "team": "home"},
            {"position": "RW", "x": 50, "y": -20, "team": "home"}
        ],
        "opponents": [
            {"label": "X1", "x": 0, "y": 100, "has_puck": true}
        ],
        "movements": [
            {"from": "C", "to": [0, 50], "type": "skating"},
            {"from": "RW", "to": "X1", "type": "forecheck"}
        ],
        "zones": [
            {"type": "coverage", "area": "slot", "team": "home"}
        ],
        "view": "full_rink"
    }"""
    
    response = await openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    
    return json.loads(response.choices[0].message.content)
```

## Implementation Plan

### Phase 1: Core Programmatic Generation
1. Install dependencies: `pip install sportypy matplotlib fastmcp openai`
2. Create base diagram generation functions
3. Implement NHL regulation rink with proper specifications
4. Test basic player and movement rendering

### Phase 2: MCP Server Development
1. Create FastMCP server for hockey diagrams
2. Implement LLM prompt parsing system
3. Build translation layer between parsed specs and sportypy
4. Add error handling and validation

### Phase 3: Tactical Elements Library
Build comprehensive element library:
- **Players**: All positions with team colors
- **Movements**: Skating paths, passes, shots
- **Zones**: Coverage areas, pressure zones
- **Annotations**: Play names, coaching notes
- **Presets**: Common formations (2-1-2, 1-3-1, etc.)

### Phase 4: Integration
1. Deploy MCP server
2. Update `/generate-image` to use MCP for tactical diagrams
3. Keep Stability AI for other image types
4. Update documentation

### Phase 5: Advanced Features
- **Iterative Refinement**: Modify existing diagrams
- **Animation Support**: Generate play sequences
- **Multiple Views**: Full rink, zones, detailed areas
- **Export Options**: PNG, SVG, PDF, animated GIF

## Example Usage

### Basic Tactical Diagram
```python
# From Claude Code
result = await mcp.call_tool(
    "generate_hockey_diagram",
    prompt="Create a 2-1-2 forecheck with F1 pressuring behind the net, "
           "F2 covering the strong side, and F3 staying high in the slot"
)
```

### Power Play Setup
```python
result = await mcp.call_tool(
    "generate_hockey_diagram",
    prompt="Show 1-3-1 power play formation with movement options from "
           "the half-wall to the slot",
    diagram_type="system"
)
```

### Drill Diagram
```python
result = await mcp.call_tool(
    "generate_hockey_diagram",
    prompt="3v2 rush drill starting from the blue line with D1 and D2 "
           "defending and forwards attacking with speed",
    diagram_type="drill"
)
```

## Technical Requirements

### Dependencies
```python
# Core libraries
sportypy>=0.1.0
matplotlib>=3.5.0
fastmcp>=0.3.0
openai>=1.0.0

# Additional utilities
pillow>=9.0.0  # Image processing
svgwrite>=1.4.0  # SVG manipulation
numpy>=1.20.0  # Coordinate calculations
```

### File Structure
```
thunder_playbook/
├── servers/
│   └── hockey_diagram_mcp/
│       ├── __init__.py
│       ├── server.py           # FastMCP server
│       ├── parser.py           # LLM prompt parsing
│       ├── generator.py        # Diagram generation
│       ├── elements.py         # Tactical elements
│       └── presets/            # Common formations
│           ├── forecheck_2_1_2.json
│           ├── powerplay_umbrella.json
│           └── penalty_kill_box.json
```

## Benefits of MCP Wrapper Approach

1. **Natural Language Interface**: Coaches describe plays in their own words
2. **Intelligent Parsing**: LLM understands hockey terminology and context
3. **Precise Output**: Programmatic generation ensures accuracy
4. **Seamless Integration**: Works within existing Claude Code workflow
5. **Extensibility**: Easy to add new play types and features
6. **Cost Efficiency**: One-time LLM parse + free diagram generation

## Success Criteria
- [ ] MCP server successfully parses natural language hockey instructions
- [ ] Generated diagrams have 100% accurate rink dimensions
- [ ] All standard plays can be described and generated
- [ ] Integration with `/generate-image` command works seamlessly
- [ ] Performance: <2 seconds for diagram generation
- [ ] Support for at least 20 common tactical patterns
- [ ] Export in PNG and SVG formats
- [ ] Clear documentation for coaches

## Future Enhancements
- Voice input for coaching instructions
- Real-time collaborative diagram editing
- Integration with video analysis tools
- Machine learning for play recognition
- 3D visualization options
- Mobile app companion

## Migration Strategy
1. Develop MCP server in parallel with existing system
2. Test with comprehensive set of tactical scenarios
3. Gradual rollout: tactical diagrams first, then drills
4. Maintain Stability AI for non-diagram images
5. Gather coach feedback and iterate

## Cost Analysis
- **Current**: ~$0.03 per Stability AI generation (often requires multiple attempts)
- **Proposed**: ~$0.002 per LLM parse + $0 for diagram generation
- **Savings**: ~93% cost reduction with better quality results

## References
- [sportypy documentation](https://sportypy.sportsdataverse.org/)
- [FastMCP documentation](https://github.com/jlowin/fastmcp)
- [NHL Official Rink Dimensions](https://www.nhl.com/info/hockey-rink)
- [OpenAI API documentation](https://platform.openai.com/docs)