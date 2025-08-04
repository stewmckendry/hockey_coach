# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL: Virtual Environment Setup

**ALWAYS activate the virtual environment before running any Python commands:**
```bash
# From project root (thunder_playbook/)
cd .. && source spacy_env/bin/activate && cd thunder_playbook
```

**Common issue**: If you see import errors or missing dependencies, you likely forgot to activate the virtual environment. The `spacy_env` is located in the parent directory, not in the project root.

## Project Architecture

This is a Hockey Coach AI Assistant platform with a **hybrid MCP + Responses API architecture**:

### Core Components
- **MCP Server** (`servers/hockey_mcp.py`): FastMCP server providing 4 hockey coaching tools
- **Hockey Diagram MCP Server** (`servers/hockey_diagram_mcp/`): FastMCP server for programmatic hockey tactical diagram generation
- **Direct API Server** (`servers/hockey_mcp_direct_api.py`): API wrapper for MCP server (port 3003) 
- **Next.js Web App** (`web_app/`): Frontend with server-side AI integration using OpenAI Responses API
- **Vector Database**: ChromaDB with 8 hockey knowledge collections (1000+ items)
- **AI Image Generation** (`image_gen/`): Two-agent system for hockey diagrams
- **MCP Integrations**: See user-scope CLAUDE.md for MCP server configurations (Notion, Exa, Semgrep, Ref-tools, Playwright)
- **Hooks System**: See user-scope CLAUDE.md for telemetry and notification hook configurations

### Data Flow
1. Raw hockey data → ChromaDB processing → Vector embeddings
2. User queries → MCP tools → Semantic search → AI-powered responses
3. Web app uses both MCP server AND OpenAI Responses API for different features
4. Claude Code integrates with external services via MCP servers (see user-scope CLAUDE.md)


## UX Guidelines for Hockey Content

**📋 Reference Document**: See `UX_GUIDELINES.md` for comprehensive content creation standards

**Quick Self-Evaluation Checklist** (apply when creating hockey content):
- [ ] **Age-appropriate**: Language and concepts match target age group (U8/U10/U12/U14+)
- [ ] **Visual ratio**: Meets requirements (U8: 80%, U10: 70%, U12: 60%, U14+: 50% visual content)
- [ ] **Terminology**: Uses appropriate hockey vocabulary tier for age group
- [ ] **Safety first**: All safety considerations clearly addressed
- [ ] **Clear structure**: Follows established template format
- [ ] **Engaging tone**: Positive, encouraging, and age-appropriate language

**Hockey Terminology Tiers**:
- **Tier 1 (U8-U10)**: Basic terms with visual support (puck, stick, pass, shot)
- **Tier 2 (U10-U12)**: Intermediate terms with context (forechecking, power play, cycle)  
- **Tier 3 (U12+)**: Advanced terms with strategic context (neutral zone trap, support angles)

When using MCP hockey tools, always specify age group and apply these guidelines to ensure content appropriateness.

## Notion Workspace for Hockey Teams

**🎯 Issue #83 Implementation**: Complete Notion workspace infrastructure for hockey team content management

### Automated Setup Available
Claude Code can automatically create a complete Notion workspace using MCP tools:

```bash
# Quick start command
"Create a complete Notion workspace for [Team Name] [Age Group] hockey team"
```

### What Gets Created Automatically:
- **Team Information Database**: Team details, coach info, practice schedule
- **Content Library Database**: Practice plans, drills, systems, concepts
- **Page Templates**: Ready-to-use templates for all content types
- **Public Publishing**: Configured for community sharing
- **UX Compliance**: Age-appropriate content following established guidelines

### Available Templates:
- **🏒 Team Home**: Central navigation and team overview
- **📋 Practice Plans**: Age-specific templates (U8-U10: 80% visual, U10-U12: 70% visual, U12+: 60% visual)
- **🥅 Drill Instructions**: Comprehensive drill documentation with progressions
- **🎯 Team Systems**: Tactical concepts and system explanations

### Integration with Thunder Playbook:
- Content templates align with existing ChromaDB hockey knowledge
- Supports multi-source content generation workflows
- Ready for slash command integration from Issue #81
- Prepared for content workflow automation from Issue #85

### Usage Examples:
```bash
# Create specific content
"Create a U10 practice plan for skating fundamentals"
"Add a drill for passing under pressure"
"Create a system explanation for 1-2-2 forecheck"

# Customize for team
"Update team information for [Team Name] in [League]"
"Set practice schedule to Tuesday/Thursday 6PM at [Rink]"
```

All content follows UX guidelines with appropriate terminology tiers and visual content ratios.

## Hockey Diagram MCP Server

**🎯 Issue #87 Implementation**: Replaces Stability AI with programmatic hockey diagram generation for 100% accurate tactical diagrams

### Overview
The Hockey Diagram MCP Server provides precise NHL-regulation hockey tactical diagram generation using programmatic rendering instead of AI image generation. This solves the accuracy issues with AI-generated hockey diagrams (missing nets, wrong line colors, + symbols instead of dots) while achieving significant cost reduction.

### Key Benefits
- **100% Accuracy**: Perfect NHL-regulation rinks with correct colors, lines, and face-off dots
- **Cost Effective**: ~93% cost reduction ($0.03 → $0.002 per diagram)
- **Consistent Quality**: No variation in base rink elements
- **Fast Generation**: Instant diagram creation without AI processing time
- **Natural Language**: Accepts coaching instructions in plain English

### Technical Architecture (Two-Stage Parser)
```
Natural Language Input → Stage 1: Entity Extraction → Stage 2: Coordinate Mapping → sportypy Renderer → Base64 PNG Output
```

**Core Components:**
- `generator.py`: Diagram generation using sportypy for NHL-standard rinks  
- `two_stage_parser.py`: Two-stage parsing system for maximum accuracy
  - Stage 1: Extract semantic entities (players, movements, zones)
  - Stage 2: Map entities to precise NHL coordinates
- `parser.py`: Basic LLM parser (fallback)
- `enhanced_parser.py`: Enhanced parser (secondary fallback)
- `elements.py`: Tactical formations library with preset plays
- `server.py`: FastMCP server exposing `generate_hockey_diagram` tool

**Parser Cascade (Priority Order):**
1. Two-stage parser (highest accuracy, comprehensive pick lists)
2. Enhanced parser (good accuracy, direct parsing)
3. Preset parser (basic functionality, template matching)

### Usage Examples
```bash
# Tactical formations
"2-1-2 forecheck with F1 pressuring behind net"
"Power play umbrella formation with movement from half-wall" 
"Defensive zone coverage drill with 3v3"

# Skill drills
"Passing drill with 3 players in triangle formation"
"Breakout drill from defensive zone"
"Face-off setup for offensive zone"
```

### Available Preset Formations
- **Forechecking**: 2-1-2, 1-2-2, 1-3-1
- **Power Play**: 1-3-1 umbrella, overload
- **Penalty Kill**: box, diamond  
- **Breakouts**: strong side, weak side, reverse
- **Neutral Zone**: trap, regroup
- **Offensive Zone**: cycle, overload

### 🤖 AI Agent Integration (Issue #97)

**New Single Agent Architecture**: The Hockey Diagram MCP Server now includes an intelligent AI agent that can research unknown formations, handle iterative feedback, and maintain conversation context.

#### Available Tools

**Core Generation Tools:**
- `generate_hockey_diagram` - Direct programmatic generation (original method)
- `parse_hockey_formation` - Parse formations into structured data  
- `generate_diagram_from_spec` - Generate from parsed specifications

**🚀 NEW: Agent-Enhanced Tools:**
- `generate_with_agent` - **Intelligent generation with research capabilities**
- `get_agent_status` - Check agent availability and capabilities
- `clear_agent_conversation` - Reset conversation context

**Reference Tools:**
- `list_hockey_formations` - List all available preset formations
- `get_formation_details` - Get detailed formation specifications

#### Agent Capabilities

**1. Fast Path (Known Formations)**
```bash
# Instant generation for standard formations
generate_with_agent("2-1-2 forecheck")
# → parse_hockey_formation → generate_diagram_from_spec
```

**2. Research Path (Unknown Concepts)**
```bash  
# Researches unknown formations automatically
generate_with_agent("Swedish torpedo forecheck")
# → search_hockey_tactics → synthesize → generate_hockey_diagram
```

**3. Iterative Refinement**
```bash
# Maintains conversation context for adjustments
generate_with_agent("power play umbrella")
# Then: "make F1 more aggressive behind the net"
# → Agent remembers context and adjusts previous diagram
```

#### Tool Selection Logic
1. **Direct parsing** (fastest) - for standard formations
2. **Hockey-specific search** (most accurate) - search_hockey_tactics, search_hockey_drills
3. **Web search** (broadest coverage) - web_search_exa for international variations  
4. **Fallback interpretation** (always works) - basic hockey principles

#### Agent Dependencies
- **OpenAI Agents SDK**: `pip install openai-agents`
- **OpenAI API Key**: Set `OPENAI_API_KEY` environment variable
- **Optional**: Exa API key for web research capabilities

### Integration with /generate-image Command
The Hockey Diagram MCP Server is automatically used when tactical keywords are detected:
```python
TACTICAL_KEYWORDS = ["drill", "play", "formation", "system", "forecheck", 
                    "powerplay", "penalty kill", "breakout", "cycle", etc.]
```

When these keywords are detected, the `/generate-image` command routes to the Hockey Diagram MCP Server instead of Stability AI, ensuring accurate tactical diagrams.

### MCP Server Registration
The server is registered in Claude Code configuration as:
```json
"hockey-diagram": {
  "type": "stdio", 
  "command": "/Users/liammckendry/thunder_playbook/servers/hockey_diagram_mcp/start_server.sh",
  "args": [],
  "env": {}
}
```

### Starting the Server
```bash
# Automatic startup with other services
python start_services.py

# Manual startup
cd servers/hockey_diagram_mcp
./start_server.sh

# Or directly
cd .. && source spacy_env/bin/activate && cd thunder_playbook
cd servers/hockey_diagram_mcp
python server.py
```

### Testing the Server
```bash
# Test diagram generation
cd servers/hockey_diagram_mcp  
python test_diagram.py

# Verify MCP connection
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### Output Specifications
- **Format**: PNG images in base64 encoding
- **Resolution**: 800x600 pixels (4:3 aspect ratio)
- **Colors**: NHL-standard (red goal lines, blue zone lines, black boards)
- **Elements**: Proper face-off dots, goal nets, creases, and player positions
- **Views**: Full rink, offensive zone, defensive zone, neutral zone

### Error Handling
- **Fallback**: Automatically falls back to Stability AI if MCP server unavailable
- **Validation**: Validates diagram specifications before rendering
- **Logging**: Comprehensive logging for debugging and monitoring

## Practice Planning Workflow

### Natural Language Practice Planning
You can create comprehensive practice plans through natural conversation with Claude Code. No slash commands needed - just describe what you need.

**Example requests:**
- "I need a practice plan for tomorrow's U10 practice. 60 minutes, focus on passing and defensive positioning."
- "Create a 45-minute practice for U12s focusing mainly on skating skills"
- "Help me plan a fun practice for U8s with lots of small games"

### How Practice Planning Works

1. **You describe your needs** - Duration, age group, focus areas, any special considerations
2. **Claude searches for team context** - Looks up your team information in Notion (if available)
3. **Research phase** - Claude uses hockey MCP tools to find appropriate drills, skills, and videos
4. **Plan generation** - Creates structured practice following best practices from PRACTICE_GUIDELINES.md
5. **Visual content** - Generates tactical diagrams and finds instructional videos
6. **Notion creation** - Creates a complete practice plan page in your Notion workspace
7. **Feedback loop** - You can request changes and Claude will update the plan

### Practice Plan Components

Each practice plan includes:
- Warm-up activities
- Skill development stations
- Team concepts/systems work
- Game simulation/scrimmage
- Cool-down activities
- Coaching points and safety reminders
- Visual diagrams for drills
- Video demonstrations
- Time allocations (flexible based on your needs)

### Post-Practice Workflow

After practice, update your plan in Notion with:
- What worked well
- What didn't work
- Player engagement level
- Adjustments for next time

This feedback helps Claude create better plans in the future by learning what works for your team.

### Files Supporting Practice Planning

- `PRACTICE_GUIDELINES.md` - Best practices for structuring practices
- `PRACTICE_PLAN_TEMPLATE.md` - Standard format for practice plans
- `NOTION_PRACTICE_ARCHITECTURE.md` - How practice plans are organized in Notion
- `PRACTICE_PLAN_ARCHITECTURE.md` - Technical implementation details

## Essential Development Commands

### Custom Slash Commands

#### Git Worktree Workflow Commands

These three commands provide a complete git worktree workflow for GitHub issues:

##### `/worktree-issue <github-issue-url>`
**Purpose**: Create a git worktree for working on a GitHub issue with automated branch setup

**Usage**: 
```bash
/worktree-issue https://github.com/stewmckendry/hockey_coach/issues/123
```

**Workflow**:
1. **Issue Validation**: Fetches and validates the GitHub issue
2. **Branch Creation**: Creates branch `issue-{number}-{sanitized-title}`
3. **Worktree Setup**: Creates worktree at `../thunder_playbook_worktrees/issue-{number}`
4. **GitHub Integration**: Comments on issue with branch reference
5. **Instructions**: Provides clear navigation commands

**Output Example**:
```
✅ Worktree Setup Complete!

📍 Issue: #123 - Add user authentication
🌿 Branch: issue-123-add-user-authentication
📂 Worktree: ../thunder_playbook_worktrees/issue-123

To start working:
cd ../thunder_playbook_worktrees/issue-123
```

##### `/commit-worktree <github-issue-url> [branch-name]`
**Purpose**: Commit changes, create PR, and update issue - maintains worktree for PR feedback

**Usage**: 
```bash
/commit-worktree https://github.com/stewmckendry/hockey_coach/issues/123
# or with explicit branch
/commit-worktree https://github.com/stewmckendry/hockey_coach/issues/123 issue-123-auth
```

**Workflow**:
1. **Quality Checks**: Runs tests, linting, and build verification
2. **Commit Changes**: Creates descriptive commit with issue reference
3. **Push Branch**: Pushes to remote with tracking
4. **Create PR**: Uses gh CLI to create PR with template
5. **Update Issue**: Comments on issue with PR link
6. **Keep Worktree**: Maintains worktree for addressing PR feedback

**Quality Gates**:
- Python: `pytest`, type checking
- Web: `npm run lint`, `npm run type-check`, `npm run build`
- Stops on any failures to ensure quality

##### `/merge-worktree <github-issue-url> <pr-url>`
**Purpose**: Complete the workflow by merging PR, cleaning up, and closing issue

**Usage**: 
```bash
/merge-worktree https://github.com/stewmckendry/hockey_coach/issues/123 https://github.com/stewmckendry/hockey_coach/pull/456
```

**Workflow**:
1. **PR Validation**: Checks approval status and CI checks
2. **Conflict Resolution**: Guides through any merge conflicts
3. **Merge PR**: Squash merges by default (configurable)
4. **Cleanup**: Removes worktree and prunes references
5. **Close Issue**: Updates issue with completion summary
6. **Update Main**: Pulls latest changes to main branch

**Complete Workflow Example**:
```bash
# 1. Start work on issue
/worktree-issue https://github.com/stewmckendry/hockey_coach/issues/123

# 2. After implementation
/commit-worktree https://github.com/stewmckendry/hockey_coach/issues/123

# 3. After PR approval
/merge-worktree https://github.com/stewmckendry/hockey_coach/issues/123 https://github.com/stewmckendry/hockey_coach/pull/456
```

**Key Benefits**:
- **Organized**: All worktrees in `../thunder_playbook_worktrees/`
- **Clean History**: Descriptive branches and commits
- **Quality First**: Automated testing before commits
- **Full Lifecycle**: From issue to merged code
- **GitHub Integration**: Automatic updates and linking

#### `/implement-feature <primary-issue-url> [related-issue-url-1] [related-issue-url-2] ...`
**Purpose**: Implement features from GitHub issues with comprehensive planning and validation

**Usage**: 
```bash
# Single issue implementation
/implement-feature https://github.com/user/repo/issues/123

# Multi-issue implementation with related context
/implement-feature https://github.com/user/repo/issues/123 https://github.com/user/repo/issues/124 https://github.com/user/repo/issues/125
```

**Workflow**:
1. **Multi-Issue Analysis**: Fetches primary issue and all related issues for complete context
2. **Cross-Reference Planning**: Identifies dependencies and conflicts across all related issues
3. **Comprehensive Planning**: Creates detailed todo list with all implementation steps
4. **User Validation**: Pauses for user approval before proceeding (MANDATORY)
5. **Implementation**: Follows existing codebase patterns and conventions
6. **Testing**: Writes/runs tests as applicable to project scope
7. **Documentation**: Updates relevant documentation
8. **Quality Check**: Ensures code quality, security, and performance

**Key Features**:
- **Multi-Issue Support**: Analyzes related issues for comprehensive context
- **Cross-Reference Analysis**: Identifies dependencies and conflicts between issues
- **Deep Planning**: Thinks ultra hard about implementation approach before coding
- **User Validation**: Pauses for mandatory user approval before proceeding
- **Scope-Aware**: Applies steps as relevant to issue complexity (not all steps for every issue)  
- **Convention Following**: Maintains consistency with existing codebase patterns
- **Quality Focus**: Comprehensive testing, documentation, and security considerations
- **Dynamic Updates**: Updates CLAUDE.md when applicable

#### `/close-issue [github-issue-url]`
**Purpose**: Close a GitHub issue with comprehensive delivery summary and implementation documentation

**Usage**: 
```bash
# Close issue with explicit URL
/close-issue https://github.com/user/repo/issues/123

# Close issue from current session context (auto-detects issue URL)
/close-issue
```

**Workflow**:
1. **Issue Identification**: Uses provided URL or analyzes session context to find the target issue
2. **Session Analysis**: Reviews conversation history to identify all work completed
3. **Delivery Documentation**: Creates comprehensive markdown summary of all deliverables
4. **User Approval**: Presents summary for user review and confirmation
5. **GitHub Instructions**: Provides clear steps or GitHub CLI commands to post comment and close issue
6. **Archival**: Saves delivery summary in appropriate project location

**Key Features**:
- **Smart Detection**: Auto-identifies GitHub issues from session context when no URL provided
- **Comprehensive Documentation**: Catalogs all code changes, tests, documentation, and configuration
- **Quality Checklist**: Includes testing status, code quality, and documentation completeness
- **GitHub Integration**: Provides exact commands for posting summary and closing issue
- **Professional Output**: Creates delivery summaries suitable for project documentation
- **Session Awareness**: Works best when used in the same session as implementation work

### Starting Services
```bash
# IMPORTANT: First activate virtual environment
cd .. && source spacy_env/bin/activate && cd thunder_playbook

# All services at once (recommended)
python start_services.py

# Or manually:
python servers/hockey_mcp.py &           # MCP server (port 8000)
python servers/hockey_mcp_direct_api.py &  # API wrapper (port 3003)
cd web_app && npm run dev                # Next.js app (port 3000)
```

### Web App Development
```bash
cd web_app
npm install
npm run dev          # Development server
npm run build        # Production build
npm run start        # Production start
npm run lint         # ESLint
npm run type-check   # TypeScript check
```

### MCP Server Management
```bash
# List all configured MCP servers
claude mcp list

# Add new MCP server (user-level)
claude mcp add <name> -s user -- <command>

# Remove MCP server
claude mcp remove <name>

# Note: For MCP server setup and configuration, see user-scope CLAUDE.md
# Available servers: Notion, Exa, Semgrep, Ref-tools, Playwright
```

### Python Testing
```bash
# IMPORTANT: Activate virtual environment first
cd .. && source spacy_env/bin/activate && cd thunder_playbook

# Install pytest if not already installed
pip install pytest

# Run specific tests
python -m pytest tests/test_fastmcp_client.py
python -m pytest tests/test_age_group.py
python -m pytest tests/test_season_planning_cli.py -v

# Run all tests
python -m pytest tests/ -v

# Test MCP server endpoints
curl http://localhost:8000/health
curl http://localhost:3003/api/mcp
```

### ChromaDB Management
```bash
# IMPORTANT: Activate virtual environment first
cd .. && source spacy_env/bin/activate && cd thunder_playbook

# Start ChromaDB server (required before indexing)
chroma run --host localhost --port 8000 --no-auth &

# Index all hockey data (first-time setup)
python chroma_load/scripts/index_drills_chroma.py
python chroma_load/scripts/index_ltad_chroma.py
python chroma_load/scripts/index_tactics.py
python chroma_load/scripts/index_conduct_chroma.py
python chroma_load/scripts/index_nhl_insights_chroma.py
python chroma_load/scripts/index_office_manual_chroma.py
python chroma_load/scripts/index_video_clips_chroma.py
python chroma_load/scripts/index_video_clips_dryland.py
```

## Key Architecture Patterns

### MCP Tools (4 main tools)
- `search_hockey_knowledge`: Semantic search across all collections
- `get_coaching_recommendations`: AI coaching advice
- `create_practice_plan`: Structured practice planning
- `analyze_player_development`: Player skill progression

### Specialized Agents
- **Season Planning Agent** (`servers/hockey_agents/season_planning_agent.py`): Interactive CLI for comprehensive season planning with conversation persistence
- **POC Agents** (`servers/poc/poc_agents/`): Native MCP and web-native MCP agent implementations for testing

### ChromaDB Collections
- `conduct-*`: Rules and ethics
- `drill-*`: On-ice drills  
- `ltad-*`: Skill development
- `tactics-*`: Team systems
- `office-*`: Off-ice training
- `insight-*`: NHL expert knowledge
- `video-*`: Instructional content

### Web App Structure
- `app/api/chat/route.ts`: Chat API using OpenAI Responses API
- `app/api/mcp/route.ts`: MCP server proxy
- `lib/server/hockeyAgent.ts`: Server-side AI agent (OpenAI Responses API)
- `lib/server/responsesAgent.ts`: Responses API implementation
- `components/chat/`: Chat interface components

### Data Models
All Pydantic models in `models/`:
- `ltad.py`: Skill development models
- `conduct.py`: Rules and conduct
- `dryland_models.py`: Off-ice training
- Plus domain-specific models

## Environment Setup

Required environment variables:
```bash
OPENAI_API_KEY=your_key_here
CHROMA_HOST=localhost
CHROMA_PORT=8000
LOG_LEVEL=INFO
```

Virtual environment setup:
```bash
# CRITICAL: The virtual environment is in the PARENT directory
# This is the most common source of errors!
cd ..
source spacy_env/bin/activate  
cd thunder_playbook

# Verify activation - you should see (spacy_env) in your prompt
which python  # Should show path to spacy_env/bin/python
```

## Important File Locations

- `start_services.py`: Unified service startup
- `utils/chroma_utils.py`: ChromaDB connection utilities
- `web_app/hooks/useChat.ts`: Chat state management
- `web_app/lib/types.ts`: TypeScript type definitions
- `image_gen/image_agent/hockey_image_iterative.py`: AI diagram generation
- `servers/hockey_agents/season_planning_agent.py`: Season planning agent implementation
- `servers/poc/`: Proof of concept implementations and testing utilities
- `coordination/`: Task planning and integration documentation

## Service Health Checks

Verify all services are running:
```bash
curl http://localhost:8000/health     # MCP Server
curl http://localhost:3003/api/mcp    # Direct API  
curl http://localhost:3000            # Web App
```

## Testing Patterns

### MCP Server Testing
```bash
# IMPORTANT: Always use the virtual environment Python
cd .. && source spacy_env/bin/activate && cd thunder_playbook

# Test MCP connection and tools
cd servers/poc
python test_mcp_connection.py

# Test agent directly
python test_agent_cli.py

# Validate complete agent setup
python validate_agent_setup.py
```

### Web Integration Testing
```bash
# Test agent HTTP server
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What are good U10 skating drills?","group_id":"test-session"}' \
  http://localhost:8002

# Test complete web API
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"Create a practice plan for U12 passing"}' \
  http://localhost:3000/api/agent-test
```

### Trace Validation
```bash
# IMPORTANT: Activate virtual environment first
cd .. && source spacy_env/bin/activate && cd thunder_playbook

# Direct agent test with trace logging
python -c "
import asyncio
from servers.poc.poc_agents.web_native_mcp_agent import run_web_mcp_agent_with_logging

async def test():
    response = await run_web_mcp_agent_with_logging('Test query', group_id='validation-test')
    print('Response received')

asyncio.run(test())
"

# Check trace URL in logs and verify in OpenAI dashboard
```

## Code Style Guidelines

### Python
- **Formatting**: Use existing patterns, prefer Black-style formatting
- **Type Hints**: Add type hints for function parameters and returns
- **Error Handling**: Use try/except with specific logging
- **Imports**: Group by standard library, third-party, local
- **Logging**: Use module-level loggers with descriptive messages

```python
# Good example
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def process_query(message: str, group_id: Optional[str] = None) -> str:
    """Process hockey coaching query with optional session grouping."""
    try:
        # Implementation
        logger.info(f"Processing query: {message[:50]}...")
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise
```

### TypeScript
- **Formatting**: Use Prettier defaults
- **Strict Mode**: Enable strict TypeScript checking
- **Interfaces**: Define clear interfaces for API contracts
- **Error Handling**: Use proper error types and handling

```typescript
// Good example
interface AgentRequest {
  message: string;
  group_id?: string;
}

interface AgentResponse {
  response: string;
  timestamp: string;
  processingTime: number;
}
```

## Visual Validation

### Screenshot Locations
- Web interface changes: `docs/screenshots/`
- Before/after comparisons for UI updates
- Responsive behavior validation

### Testing Checklist
- [ ] Desktop view (1920x1080)
- [ ] Mobile view (375x667)
- [ ] Chat interface functionality
- [ ] Error state displays
- [ ] Loading indicators

### Browser Compatibility
- Chrome (primary)
- Firefox
- Safari (if available)

## Development Workflow: Explore-Plan-Code-Commit

### 1. Explore Phase
```bash
# Read relevant files first
# Use Read, Glob, Grep tools to understand scope
# Check existing patterns and conventions
```

### 2. Plan Phase
- Create explicit implementation plan
- Identify dependencies and risks
- Define success criteria
- Set course correction checkpoints

### 3. Code Phase
- Implement incrementally
- Test at each stage
- Use TodoWrite for progress tracking
- Take screenshots for UI changes

### 4. Commit Phase
- Run linting and type checking
- Verify all tests pass
- Create descriptive commit messages
- Update documentation as needed

## Course Correction Checkpoints

For complex tasks, pause at these moments:
1. **After exploration**: "Does the scope and approach look right?"
2. **Mid-implementation**: "Are we on the right track technically?"
3. **Before finalization**: "Does this meet the requirements?"

## Pre-Commit Checklist

### Web App
```bash
cd web_app
npm run lint           # ESLint
npm run type-check     # TypeScript
npm run build          # Production build test
```

### Python Components
```bash
# Run relevant tests
python -m pytest tests/test_specific_component.py

# Check MCP server health
curl http://localhost:8000/health
```

## MCP Workflow Integration

For detailed MCP workflow patterns and integration examples, see the user-scope CLAUDE.md file. Available integrations include:
- **Notion**: Documentation and knowledge management
- **Exa**: AI-powered research and web search
- **Semgrep**: Security analysis and code quality
- **Ref-tools**: Technical documentation search
- **Playwright**: Browser automation and testing

## Common Troubleshooting

### Virtual Environment Issues
```bash
# Error: ModuleNotFoundError: No module named 'fastmcp'
# Solution: You forgot to activate the virtual environment
cd .. && source spacy_env/bin/activate && cd thunder_playbook

# Error: -bash: spacy_env/bin/activate: No such file or directory
# Solution: You're in the wrong directory. The venv is in the PARENT directory
cd ..  # Go to parent directory first
source spacy_env/bin/activate
cd thunder_playbook

# Verify correct Python is being used
which python  # Should show: ../spacy_env/bin/python
python --version  # Should show Python 3.x
```

### Service Startup Issues
```bash
# Error: Port already in use
# Solution: Kill existing processes
lsof -i :8000  # Find process using port 8000
kill -9 <PID>  # Kill the process

# Error: ChromaDB connection refused
# Solution: Start ChromaDB first
chroma run --host localhost --port 8000 --no-auth &
```

### Import Errors in Tests
```bash
# Error: ImportError when running tests
# Solution: Run from project root with proper Python path
cd .. && source spacy_env/bin/activate && cd thunder_playbook
PYTHONPATH=$PWD python -m pytest tests/test_file.py
```