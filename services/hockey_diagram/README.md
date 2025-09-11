# Hockey Diagram Manual Iteration System

A specification-driven hockey diagram generation system that evolves through real coaching scenarios, using sportypy for NHL-regulation rinks and Hockey Canada template standards.

## Quick Start

```bash
# Activate virtual environment
source ../../spacy_env/bin/activate

# System is ready for iteration!
```

## Iteration Flow

### How It Works
1. **You provide** a natural language description of a hockey diagram
2. **Claude analyzes** and creates a spec, builds the diagram
3. **Claude shares** the filepath and spec summary
4. **You review** and provide feedback
5. **Repeat** until diagram meets your needs
6. **Track** in Google Sheets for retrospective

### Example Session
```
You: "Create a 2-1-2 forecheck with F1 pressuring the puck carrier behind the net"
Claude: [Generates diagram] → outputs/diagram_20250127_143022.png
You: "Move F2 to cover the weak side boards"
Claude: [Updates and regenerates]
You: "Perfect!"
Claude: [Records in tracking sheet]
```

## Project Structure

```
hockey_diagram_mcp/
├── spec/
│   └── hockey_diagram_spec.md      # Living specification (v1.0)
├── src/
│   └── diagram_builder.py          # SportyPy-based builder
├── outputs/
│   └── *.png                       # Generated diagrams
├── docs/
│   ├── ITERATION_FLOW.md          # Detailed process documentation
│   └── README.md                   # This file
└── tracking/
    ├── sheet_link.txt              # Google Sheets link
    └── iteration_tracker.csv       # Local backup
```

## Key Features

### Uses SportyPy
- NHL-regulation rink dimensions
- Professional visualization quality
- Multiple view options (full, half, zones)

### Hockey Canada Template Standards
- **Players**: Coach (©), Forwards (○), Defense (△), Goalie (◐), Opponents (X)
- **Movements**: Carry (→), Pass (···>), Shot (--→), Backward (~), Pressure (═══)
- **Zones**: Coverage areas, pressure zones, passing lanes

### Specification-Driven
- Every element defined in `spec/hockey_diagram_spec.md`
- Spec evolves with each new coaching need
- JSON-based for clarity and versioning

## Current Capabilities

✅ **Rink Views**: full, offensive, defensive, neutral, half
✅ **Player Types**: All Hockey Canada standard symbols
✅ **Movement Types**: 8 types per template legend
✅ **Zone Overlays**: Coverage, pressure, lanes
✅ **Annotations**: Text labels, drill markers

## Tracking & Evolution

**Google Sheets**: [Hockey Diagram Manual Iterations](https://docs.google.com/spreadsheets/d/1_RdgMPxluftZfeFl1SXZKYycDVxAV-GrzzhESIOXt24/edit)

Tracks:
- Test cases and descriptions
- Number of iterations needed
- Spec updates made
- Feedback received
- Lessons learned

## Next Steps

Ready to create your first diagram! Just describe what you need in natural language.

Examples to try:
- "Show a power play umbrella formation with passing options"
- "Create a D-to-D breakout with weak side support"
- "Draw a 1-3-1 neutral zone trap"
- "Illustrate a cycle drill in the offensive zone"

The system will learn and improve with each diagram we create together.