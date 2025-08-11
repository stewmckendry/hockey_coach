# Hockey Diagram Generator Architecture Documentation

## Executive Summary

The hockey diagram generator has been refactored from a complex dual-agent system to a streamlined single-agent orchestrator with a specialized Parser Agent. This architectural change eliminates redundancy, clarifies responsibilities, and creates a clean separation between orchestration and domain expertise.

## Architecture Overview

### Previous Architecture (Complex)
```
Main Agent (hockey_diagram_agent.py)
├── All orchestration logic
├── All research tools (search_hockey_tactics, search_hockey_drills, web_search_exa)
├── Diagram generation tools
└── Parser Agent (parser_agent.py)
    └── NO MCP tools - basic parsing only
```

### New Architecture (Simplified)
```
Main Agent (hockey_diagram_agent.py)
├── Pure orchestrator - only 3 tools
│   ├── parse_hockey_formation (delegates to Parser Agent)
│   ├── generate_diagram_from_spec (creates diagrams)
│   └── list_hockey_formations (lists presets)
└── Parser Agent (parser_agent.py)
    ├── Hockey knowledge expert with ALL research tools
    ├── search_hockey_tactics (hockey MCP)
    ├── search_hockey_drills (hockey MCP)  
    ├── search_hockey_videos (hockey MCP)
    └── web_search_exa (for international variations)
```

## Key Architectural Changes

### 1. Eliminated Tool Redundancy
**Before**: Both agents had identical research tools, creating confusion and inefficiency.
**After**: Parser Agent exclusively owns all hockey knowledge research capabilities.

### 2. Clear Separation of Concerns
- **Main Agent**: Pure orchestrator that decides workflow (parse → generate)
- **Parser Agent**: Hockey domain expert that handles all tactical knowledge

### 3. Simplified Tool Chain
Main Agent tools reduced from 8+ tools to exactly 3 core orchestration tools:
1. `parse_hockey_formation` - Delegates to Parser Agent with research
2. `generate_diagram_from_spec` - Creates visual diagrams
3. `list_hockey_formations` - Lists available presets

## Component Responsibilities

### Main Agent (`hockey_diagram_agent.py`)
| Responsibility | Description |
|----------------|-------------|
| **Orchestration** | Decides when to parse, research, and generate |
| **User Interface** | Handles conversation flow and context |
| **Quality Control** | Validates outputs and manages errors |
| **Workflow Management** | Coordinates between parsing and generation |

**Tools Owned**: 3 orchestration tools only

### Parser Agent (`parser_agent.py`)
| Responsibility | Description |
|----------------|-------------|
| **Hockey Expertise** | Deep knowledge of formations, systems, and tactics |
| **Research Coordination** | Uses all MCP tools to find unknown formations |
| **Knowledge Synthesis** | Converts research into structured specifications |
| **Tactical Validation** | Ensures hockey accuracy in parsed data |

**Tools Owned**: All 4 research tools
- `search_hockey_tactics`
- `search_hockey_drills` 
- `search_hockey_videos`
- `web_search_exa`

## Tool Ownership Matrix

| Tool | Previous Owner | New Owner | Rationale |
|------|---------------|-----------|-----------|
| `parse_hockey_formation` | Main Agent | Main Agent | Orchestration tool that delegates to Parser Agent |
| `generate_diagram_from_spec` | Main Agent | Main Agent | Core generation capability |
| `list_hockey_formations` | Main Agent | Main Agent | Reference tool for available presets |
| `search_hockey_tactics` | Both Agents | Parser Agent Only | Domain expertise belongs with hockey specialist |
| `search_hockey_drills` | Both Agents | Parser Agent Only | Research capability consolidated |
| `search_hockey_videos` | Both Agents | Parser Agent Only | Knowledge gathering centralized |
| `web_search_exa` | Both Agents | Parser Agent Only | International variations research |

## Example Workflows

### Known Formation (Fast Path)
```
User: "Show me a 2-1-2 forecheck"
│
├── Main Agent: parse_hockey_formation("2-1-2 forecheck")
│   └── Parser Agent: Recognizes formation, returns spec immediately
├── Main Agent: generate_diagram_from_spec(parsed_spec)
└── Result: Diagram generated in ~2-3 seconds
```

### Unknown Formation (Research Path)
```
User: "Show me a Swedish torpedo forecheck"
│
├── Main Agent: parse_hockey_formation("Swedish torpedo forecheck")
│   └── Parser Agent: 
│       ├── search_hockey_tactics("Swedish torpedo forecheck")
│       ├── web_search_exa("Swedish hockey torpedo system")
│       └── Synthesizes research into specification
├── Main Agent: generate_diagram_from_spec(researched_spec)
└── Result: Diagram with researched tactical knowledge
```

### Iterative Refinement
```
User: "Make F1 more aggressive behind the net"
│
├── Main Agent: parse_hockey_formation(feedback + context)
│   └── Parser Agent: 
│       ├── Understands positional adjustment
│       └── Updates specification accordingly
├── Main Agent: generate_diagram_from_spec(updated_spec)
└── Result: Modified diagram with requested changes
```

## Benefits of New Architecture

### 1. Performance Improvements
- **Reduced Complexity**: Main Agent focuses purely on orchestration
- **Faster Tool Selection**: No confusion about which agent has which tools
- **Optimized Research**: Parser Agent specialized for hockey knowledge

### 2. Maintainability Gains
- **Single Source of Truth**: Parser Agent is THE hockey expert
- **Clear Debugging**: Tool usage traced to specific responsibilities
- **Simplified Testing**: Each agent has distinct, testable responsibilities

### 3. Scalability Advantages
- **Easy Extension**: Add new research tools only to Parser Agent
- **Modular Design**: Replace Parser Agent without affecting Main Agent
- **Clear Interfaces**: Well-defined contracts between components

### 4. Error Handling
- **Isolated Failures**: Research failures don't affect orchestration
- **Graceful Degradation**: Parser Agent can fall back to simpler methods
- **Better Error Messages**: Clear indication of which component failed

## Implementation Details

### Parser Agent MCP Configuration
```python
# Parser Agent connects to MCP servers for research
mcp_tools = [
    hockey_mcp_server,  # search_hockey_tactics, search_hockey_drills, search_hockey_videos
    exa_server         # web_search_exa for international variations
]

parser_agent = Agent(
    name="Hockey Parser",
    instructions=PARSER_INSTRUCTIONS,  # Deep hockey domain knowledge
    mcp_servers=mcp_tools,
    model="gpt-4o-mini"
)
```

### Main Agent Simplified Configuration
```python
# Main Agent has only core orchestration tools
orchestration_tools = [
    parse_hockey_formation,      # Delegates to Parser Agent
    generate_diagram_from_spec,  # Creates diagrams
    list_hockey_formations       # Lists presets
]

main_agent = Agent(
    name="Hockey Diagram Expert",
    instructions=EXPERT_INSTRUCTIONS,  # Orchestration focus
    tools=orchestration_tools,         # No MCP servers needed
    model="gpt-4o-mini"
)
```

### Communication Flow
```python
@function_tool
async def parse_hockey_formation(prompt: str) -> str:
    """Main Agent tool that delegates to Parser Agent"""
    if parser_type == "agent":
        # Delegate to Parser Agent with full research capabilities
        from parser_agent import parse_with_agent
        result_json = await parse_with_agent(prompt)
        return result_json
```

## Migration Benefits

### Before Refactor Issues
- **Tool Confusion**: Both agents had same research tools
- **Resource Waste**: Duplicate MCP server connections
- **Debugging Difficulty**: Unclear which agent used which tool
- **Maintenance Overhead**: Changes needed in multiple places

### After Refactor Solutions
- **Clear Ownership**: Each tool has single responsible agent
- **Efficient Resources**: Only Parser Agent connects to research MCPs
- **Easy Debugging**: Tool usage maps directly to agent responsibility  
- **Simple Maintenance**: Research tools managed in one location

## Future Extensions

### Adding New Research Capabilities
```python
# Add to Parser Agent only - Main Agent unchanged
new_mcp_server = MCPServerStdio(
    params={"command": "hockey-analytics-mcp"},
    tool_filter=create_static_tool_filter(
        allowed_tool_names=["analyze_team_stats", "get_player_analytics"]
    )
)
```

### Parser Agent Improvements
- Advanced formation recognition
- Video analysis capabilities
- Real-time coaching suggestions
- International rule variations

### Main Agent Enhancements  
- Better conversation memory
- Multi-diagram workflows
- Export capabilities
- Integration with presentation tools

## Monitoring and Observability

### Tool Usage Tracking
```python
# Each agent logs its tool usage separately
logger.info(f"🔍 Parser Agent used research tools: {tools_used}")
logger.info(f"🎯 Main Agent orchestrated: {orchestration_steps}")
```

### Performance Metrics
- **Parser Agent**: Research accuracy, knowledge synthesis quality
- **Main Agent**: Orchestration efficiency, user satisfaction
- **System Overall**: End-to-end generation time, success rate

## Conclusion

The simplified architecture creates a clean separation between orchestration (Main Agent) and domain expertise (Parser Agent). This change eliminates redundancy, improves maintainability, and creates a scalable foundation for future enhancements.

The Parser Agent now serves as the definitive hockey knowledge expert, while the Main Agent focuses purely on coordinating the workflow from user request to final diagram. This architecture better reflects the natural division of responsibilities and creates clearer debugging and extension paths.

## Architecture Diagrams

### High-Level Flow
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Request  │───▶│   Main Agent    │───▶│  Generated      │
│                 │    │  (Orchestrator) │    │  Diagram        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │  Parser Agent   │
                       │ (Hockey Expert) │
                       └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │  MCP Research   │
                       │     Tools       │
                       └─────────────────┘
```

### Tool Distribution
```
Main Agent Tools (3):
├── parse_hockey_formation
├── generate_diagram_from_spec  
└── list_hockey_formations

Parser Agent Tools (4):
├── search_hockey_tactics
├── search_hockey_drills
├── search_hockey_videos
└── web_search_exa
```