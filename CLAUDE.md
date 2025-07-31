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
- **Direct API Server** (`servers/hockey_mcp_direct_api.py`): API wrapper for MCP server (port 3003) 
- **Next.js Web App** (`web_app/`): Frontend with server-side AI integration using OpenAI Responses API
- **Vector Database**: ChromaDB with 8 hockey knowledge collections (1000+ items)
- **AI Image Generation** (`image_gen/`): Two-agent system for hockey diagrams
- **Notion MCP Integration**: User-level MCP server for hockey coaching documentation management

### Data Flow
1. Raw hockey data → ChromaDB processing → Vector embeddings
2. User queries → MCP tools → Semantic search → AI-powered responses
3. Web app uses both MCP server AND OpenAI Responses API for different features
4. Claude Code integrates with Notion for documentation management via MCP

## MCP Server Integrations

### Notion MCP Integration

#### Overview
The Notion MCP server enables Claude Code to directly manage hockey coaching documentation in Notion workspaces. This integration provides seamless content creation, updates, and search capabilities.

#### Setup Requirements
1. **Notion Integration**: Create internal integration at https://www.notion.so/profile/integrations
2. **API Token**: Copy integration token (format: `ntn_****`)
3. **Workspace Permissions**: Connect integration to specific pages or grant workspace access
4. **Claude Code Configuration**: User-level MCP server setup

#### Installation
```bash
# Install Notion MCP server (user-level scope)
claude mcp add notion -s user -- npx -y @notionhq/notion-mcp-server

# Verify installation
claude mcp list
```

#### Configuration
**File Location**: `~/.claude.json`
```json
{
  "mcpServers": {
    "notion": {
      "type": "stdio", 
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_TOKEN": "ntn_****"
      }
    }
  }
}
```

#### Available Tools
- **Search**: `mcp__notion-remote__search` - Search workspace content
- **Fetch**: `mcp__notion-remote__fetch` - Retrieve specific pages/databases
- **Create Pages**: `mcp__notion-remote__create-pages` - Create new pages
- **Update Pages**: `mcp__notion-remote__update-page` - Modify existing content
- **Create Databases**: `mcp__notion-remote__create-database` - Create new databases
- **Comments**: `mcp__notion-remote__create-comment` - Add page comments

#### Hockey Coaching Use Cases
```bash
# Example workflows available through Claude Code:

# 1. Create practice plan documentation
"Create a new Notion page titled 'U12 Passing Practice Plan'"

# 2. Update coaching notes
"Update the page 'Team Strategy Notes' with power play formations"

# 3. Search existing content
"Search for all skating drill pages in the workspace"

# 4. Create player tracking database
"Create a database for tracking player development goals"
```

### Exa MCP Integration

#### Overview
The Exa MCP server provides AI-powered web search capabilities for development workflows, offering fast, controllable, and accurate web search specifically designed for AI applications.

#### Setup Requirements
1. **Exa API Key**: Obtain from https://dashboard.exa.ai/api-keys
2. **Node.js**: Required for NPX execution
3. **Claude Code CLI**: For MCP server management

#### Installation
```bash
# Install Exa MCP server (user-level scope)
claude mcp add exa npx -- -y exa-mcp-server --scope user

# Verify installation
claude mcp list
```

#### Configuration
**File Location**: `~/.claude.json`
```json
{
  "mcpServers": {
    "exa": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": {
        "EXA_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Available Tools
- **Web Search**: `mcp__exa__web_search_exa` - AI-optimized web searches
- **Company Research**: `mcp__exa__company_research_exa` - Deep company analysis
- **URL Crawling**: `mcp__exa__crawling_exa` - Extract content from specific URLs
- **LinkedIn Search**: `mcp__exa__linkedin_search_exa` - Search LinkedIn profiles/companies
- **Deep Research**: `mcp__exa__deep_researcher_start/check` - AI-powered research workflows

#### Hockey Coaching Use Cases
```bash
# Example workflows available through Claude Code:

# 1. Research training techniques
"What are the best youth hockey training drills for improving skating speed?"

# 2. Equipment research
"Find recent reviews of the CCM Jetspeed FT6 Pro hockey stick"

# 3. Industry analysis
"Research Bauer Hockey's latest equipment innovations"

# 4. Content extraction
"Extract the practice plan from https://www.usahockey.com/news_article/show/1234567"
```

#### Cost Monitoring
Exa API usage is metered. Typical costs:
- Web search: ~$0.005 per query
- Company research: ~$0.008 per query  
- URL crawling: ~$0.001 per page
- Monitor usage through API response `costDollars` field

### Semgrep MCP Integration

#### Overview
The Semgrep MCP server enables Claude Code to perform comprehensive security analysis and code quality scanning directly through conversational interface. Semgrep is a fast, deterministic static analysis tool with over 5,000 built-in rules supporting many programming languages.

#### Setup Requirements
1. **Python Environment**: Python 3.8+ (uses project's existing virtual environment)
2. **Optional Semgrep Token**: For advanced features via Semgrep AppSec Platform
3. **Claude Code CLI**: For MCP server management

#### Installation
```bash
# Install Semgrep MCP server (user-level scope)
claude mcp add semgrep uvx semgrep-mcp

# Verify installation
claude mcp list
```

#### Configuration
**File Location**: `~/.claude.json`

**Basic Configuration (Local Scanning Only):**
```json
{
  "mcpServers": {
    "semgrep": {
      "command": "uvx",
      "args": ["semgrep-mcp"]
    }
  }
}
```

**Advanced Configuration (with Semgrep AppSec Platform):**
```json
{
  "mcpServers": {
    "semgrep": {
      "command": "uvx", 
      "args": ["semgrep-mcp"],
      "env": {
        "SEMGREP_APP_TOKEN": "your-token-here"
      }
    }
  }
}
```

#### Available Tools
- **security_check**: Scan code for security vulnerabilities
- **semgrep_scan**: Scan code files with specific config
- **semgrep_scan_with_custom_rule**: Use custom Semgrep rules
- **get_abstract_syntax_tree**: Generate AST for code analysis
- **supported_languages**: List supported programming languages
- **semgrep_rule_schema**: Get rule schema for custom rule creation
- **semgrep_findings**: Fetch findings from Semgrep AppSec Platform (requires token)

#### Hockey Coaching Security Use Cases
```bash
# Example workflows for hockey coaching platform security:

# 1. Scan Python MCP servers for vulnerabilities
"Scan the hockey_mcp.py file for security vulnerabilities"

# 2. Check web app for common security issues
"Run security analysis on the Next.js web application"

# 3. Validate API endpoint security
"Check the chat API route for potential security risks"

# 4. Custom rule for hockey data validation
"Create a custom Semgrep rule to detect insecure player data handling"

# 5. AST analysis for code understanding
"Generate abstract syntax tree for the coaching recommendation function"
```

#### Multi-Language Support
Semgrep supports analysis of:
- **Python**: MCP servers, data processing scripts
- **TypeScript/JavaScript**: Next.js web application, API routes
- **JSON**: Configuration files, data schemas
- **YAML**: Docker configs, CI/CD pipelines
- **And many more**: See `supported_languages` tool for full list

#### Custom Rule Creation
```bash
# Example: Create rule for detecting hardcoded API keys
"Create a Semgrep rule to detect hardcoded OpenAI API keys in Python files"

# Example: Rule for insecure data handling
"Write a custom rule to identify potential SQL injection in hockey statistics queries"
```

### Ref-tools MCP Integration

#### Overview
The Ref-tools MCP server provides token-efficient, smart documentation search capabilities across all development projects. Ref-tools prevents AI hallucinations by providing accurate, up-to-date documentation with intelligent chunking and session-aware search, specifically tuned for technical documentation.

#### Setup Requirements
1. **Ref-tools API Key**: Obtain from https://ref.tools (sign up and generate from dashboard)
2. **Node.js**: Required for NPX execution
3. **Claude Code CLI**: For MCP server management
4. **Internet Connection**: Required for documentation searches

#### Installation
```bash
# Install Ref-tools MCP server (user-level scope)
claude mcp add ref-tools -s user -e REF_API_KEY=your_api_key -- npx ref-tools-mcp@latest

# Verify installation
claude mcp list
```

#### Configuration
**File Location**: `~/.claude.json`

**Option A: HTTP Transport (Recommended):**
```json
{
  "mcpServers": {
    "ref-tools": {
      "type": "http",
      "url": "https://api.ref.tools/mcp?apiKey=${REF_API_KEY}"
    }
  }
}
```

**Option B: Local STDIO Server:**
```json
{
  "mcpServers": {
    "ref-tools": {
      "type": "stdio",
      "command": "npx",
      "args": ["ref-tools-mcp@latest"],
      "env": {
        "REF_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Available Tools
- **Documentation Search**: `ref_search_documentation` - Token-efficient search across technical docs
- **URL Reading**: `ref_read_url` - Fetch webpage content and convert to markdown
- **Web Search**: `ref_search_web` - Optional fallback web search tool

#### Hockey Coaching Development Use Cases
```bash
# Example workflows for Thunder Playbook development:

# 1. API Integration Research
"Search FastMCP documentation for server configuration parameters"

# 2. Library Implementation Details
"Find ChromaDB client API methods for vector similarity search"

# 3. Framework-Specific Examples  
"Search Pydantic documentation for model validation examples"

# 4. Troubleshooting Documentation
"Find Next.js API route error handling best practices"

# 5. Hockey Domain Research
"Search USA Hockey coaching documentation for skill development frameworks"
```

#### Token Efficiency & Performance
- **Smart Filtering**: Returns only most relevant ~200 tokens from 80k+ token documents
- **Session Tracking**: Minimizes redundant searches through search history awareness
- **Content Chunking**: Pre-processed content optimized for AI consumption
- **P95 Latency**: ~1.7 seconds for documentation searches
- **Coverage**: Thousands of public GitHub repositories and major platform docs

#### Session Awareness Examples
```bash
# Initial broad search
"Find OpenAI API rate limiting documentation"

# Session-aware follow-up automatically avoids duplicate results
"Show specific rate limits for GPT-4 model usage"

# Refined search builds on previous context
"What happens when rate limits are exceeded?"
```

#### Security Considerations
- **Third-party Risk**: Use third-party MCP servers at your own risk
- **Internet Access**: Server requires internet access for documentation searches
- **API Key Security**: Store API keys securely in environment variables
- **Data Privacy**: Review ref.tools data handling policies before use

### Playwright MCP Integration

#### Overview
The Playwright MCP server enables Claude Code to perform comprehensive browser automation and testing directly through conversational interface. Playwright provides cross-browser automation capabilities for end-to-end testing, web scraping, and automated quality assurance with an accessibility-first approach.

#### Setup Requirements
1. **Node.js**: Version 18 or newer (LTS recommended)
2. **Claude Code CLI**: For MCP server management
3. **System Resources**: 4GB+ RAM recommended for browser automation
4. **Browser Drivers**: Automatically installed with Playwright

#### Installation
```bash
# Install Playwright MCP server (user-level scope)
claude mcp add playwright npx @playwright/mcp@latest

# Verify installation
claude mcp list
```

#### Configuration
**File Location**: `~/.claude.json`

**Basic Configuration:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**Advanced Configuration with Browser Options:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--browser", "chromium",
        "--isolated"
      ]
    }
  }
}
```

**Device Emulation Configuration:**
```json
{
  "mcpServers": {
    "playwright-mobile": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--device", "iPhone 15",
        "--isolated"
      ]
    }
  }
}
```

#### Available Capabilities
- **Navigation**: Visit web pages and handle URL routing
- **Element Interaction**: Click elements, type text, interact with forms
- **Visual Capture**: Take screenshots and capture page states
- **Dialog Handling**: Manage alerts, prompts, and confirmations
- **JavaScript Execution**: Run custom JavaScript code on pages
- **Network Monitoring**: Monitor and analyze network requests/responses
- **Multi-tab Management**: Handle multiple browser tabs and windows
- **API Testing**: HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **Cross-Browser Testing**: Support for Chromium, Firefox, WebKit, Edge

#### Hockey Coaching Development Use Cases
```bash
# Example workflows for Thunder Playbook development:

# 1. End-to-End Testing
"Test the hockey drill search functionality across different browsers"

# 2. Web App Validation
"Navigate to localhost:3000, test the chat interface, and take screenshots"

# 3. Responsive Design Testing
"Test the coaching interface on mobile device emulation"

# 4. Form Interaction Testing
"Fill out the practice plan form and verify submission works"

# 5. Performance Monitoring
"Load the main page and check for network requests taking longer than 2 seconds"

# 6. Cross-Browser Compatibility
"Test the same user journey in both Chrome and Firefox"

# 7. API Endpoint Testing
"Navigate to the MCP API endpoint and validate the response structure"

# 8. Visual Regression Testing
"Take screenshots of key pages and compare with previous versions"
```

#### Advanced Features
- **Accessibility-First**: Uses Playwright's accessibility tree for reliable element selection
- **Deterministic Actions**: Avoids pixel-based interactions that can be unreliable
- **Structured Data**: Provides accessibility snapshots without requiring vision models
- **Session Management**: Persistent browser profiles and authentication state
- **Security Controls**: Origin filtering and request blocking capabilities

#### Browser Configuration Options
```bash
# Command-line configuration options:
--browser <browser>          # Choose browser (chrome, firefox, webkit, msedge)
--device <device>            # Emulate specific devices (e.g., "iPhone 15")
--isolated                   # Keep browser profile in memory only
--storage-state <path>       # Persist authentication state
--allowed-origins <origins>  # Control allowed request origins
--blocked-origins <origins>  # Block specific origins
--caps <caps>               # Enable additional capabilities (vision, pdf)
```

#### Performance Considerations
- **Memory Usage**: Browser instances consume significant memory (1-2GB per instance)
- **Parallel Testing**: Multiple browsers may impact system performance
- **Network Bandwidth**: Page load testing accuracy depends on stable internet
- **Resource Requirements**: Multi-core processor recommended for parallel execution

#### Integration with Thunder Playbook Testing
```bash
# Practical testing examples for hockey coaching platform:

# 1. Complete User Journey Testing
"Navigate to the app, search for skating drills, create a practice plan, and verify results"

# 2. MCP Server Integration Testing  
"Test the connection between the web app and hockey MCP server endpoints"

# 3. ChatBot Interface Testing
"Interact with the hockey coaching chatbot and verify responses are generated"

# 4. Database Integration Testing
"Search for hockey knowledge and verify ChromaDB integration works correctly"

# 5. Responsive Layout Testing
"Test the coaching interface across desktop, tablet, and mobile viewports"

# 6. Authentication Flow Testing
"Test user login/logout workflows if authentication is implemented"
```

#### Security and Session Management
- **Authentication Handling**: Manual login capability for sites requiring authentication
- **Persistent Sessions**: Browser profiles maintain login state during sessions
- **Isolated Environments**: Clean testing environments for consistent results
- **Network Security**: Firewall settings and request filtering capabilities
- **Origin Control**: Restrict or allow specific domains for security

#### Troubleshooting Playwright Integration
- **Browser installation failures**: Run `npx playwright install` manually
- **Permission errors**: Ensure Node.js has proper execution permissions
- **Memory issues**: Close unused browser instances, increase system RAM
- **Network timeouts**: Check internet connection and target site availability
- **Element selection failures**: Use accessibility tree selectors instead of CSS
- **Screenshot failures**: Verify target page is fully loaded before capture

### MCP Troubleshooting
- **401 Unauthorized**: Verify API keys and workspace permissions  
- **Tools not available**: Restart Claude Code after configuration changes
- **Connection issues**: Check `claude mcp list` for server status
- **Permission errors**: Ensure proper API key scope and permissions
- **Semgrep installation errors**: Ensure `uvx` is installed (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Semgrep dependency issues**: Run `uvx semgrep-mcp --help` to test installation
- **Path scanning errors**: Ensure target files/directories exist and are readable
- **Custom rule syntax errors**: Validate rule syntax with `semgrep_rule_schema` tool
- **Ref-tools API errors**: Verify REF_API_KEY is valid and not expired
- **Documentation not found**: Check if target documentation is in ref.tools coverage
- **HTTP transport issues**: Switch to STDIO server if HTTP endpoint is unreachable
- **Token efficiency concerns**: Use specific search terms rather than broad queries
- **Playwright browser installation**: Run `npx playwright install` if browsers not found
- **Playwright memory issues**: Close unused browser instances, increase system RAM allocation
- **Playwright network timeouts**: Check internet connection and verify target site availability
- **Playwright element selection**: Use accessibility selectors instead of unreliable CSS selectors

**⚠️ Important**: After modifying MCP server configuration, restart Claude Code for changes to take effect.

## Essential Development Commands

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

# Test specific MCP tools
# Notion examples
"Search Notion for hockey practice plans"
"Create a Notion page for team meeting notes"

# Ref-tools examples  
"Search FastMCP documentation for server setup"
"Find ChromaDB client API usage examples"

# Exa examples
"Research latest hockey training methodologies"

# Semgrep examples
"Scan this Python file for security vulnerabilities"

# Playwright examples
"Navigate to localhost:3000 and take a screenshot"
"Test the hockey drill search functionality"
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

## MCP Workflow Integration Patterns

### Research → Implementation
```bash
# 1. Use Ref-tools for accurate API documentation
"Search FastMCP documentation for async client patterns"

# 2. Use Exa for broader context and examples  
"Find examples of FastMCP servers in production"

# 3. Use Semgrep for security validation
"Scan the new MCP client code for security issues"

# 4. Use Notion for documentation storage
"Create a Notion page documenting the MCP integration approach"
```

### Documentation → Development → Testing
```bash
# 1. Research official documentation with Ref-tools
"Find Pydantic v2 migration guide for data models"

# 2. Store findings in Notion for team access
"Create a Notion database for tracking API migration tasks"

# 3. Implement changes following documented patterns
# (Use standard development tools)

# 4. Validate implementation with security tools
"Run Semgrep analysis on updated data models"

# 5. Research additional context if needed
"Search for Pydantic performance optimization examples"
```

### Multi-Server Development Workflow
```bash
# Typical development session combining all MCP servers:

# Start with documentation research
"Search Next.js documentation for API route middleware patterns"

# Expand research if needed  
"Find real-world examples of Next.js middleware implementations"

# Document findings for team
"Create a Notion page with middleware implementation guidelines"

# Implement the solution
# (Standard coding)

# Security validation
"Scan the new middleware code for potential vulnerabilities"

# Integration testing research
"Find testing patterns for Next.js API middleware"
```

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