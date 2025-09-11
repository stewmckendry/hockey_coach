# Hockey Practice Planning MCP Prompt Library

A Model Context Protocol (MCP) server that provides reusable prompts for hockey practice planning and team management workflows.

## Overview

This MCP server delivers structured, interactive prompts that guide coaches through practice planning and review workflows. The prompts are stored as easily editable markdown files and integrate with existing MCP tools like Airtable, Hockey MCP, and Notion.

## Features

- **Interactive Workflows**: Step-by-step guidance with coach checkpoints
- **Markdown-Based**: Prompts stored as `.md` files for easy editing
- **Tool Integration**: Works with Airtable, Hockey MCP, Hockey Diagram MCP, and Notion
- **Age-Appropriate**: Tailored content for different age groups (U8-U14+)

## Available Prompts

### 1. `plan_next_practice`
Interactive 5-step workflow for comprehensive practice planning:
- Review previous practice feedback
- Analyze skill coverage gaps
- Smart drill selection
- Generate structured practice plan
- Update tracking systems

### 2. `post_practice_review`
4-step post-practice workflow:
- Create session log with feedback
- Rate drill effectiveness
- Verify automatic tracking updates
- Generate next practice recommendations

### 3. `practice_template`
Standard practice plan template with age-specific adjustments

### 4. `list_hockey_skills`
Comprehensive skill library organized by category and age group

### 5. `quick_drill_search`
Guide for searching drills using the Hockey MCP tools

## Installation

### Prerequisites
- Python 3.8+
- MCP SDK (`pip install mcp`)
- Access to required MCP servers (Airtable, Hockey MCP)

### Setup Steps

1. **Clone/Navigate to the server directory:**
```bash
cd servers/hockey_prompts_mcp
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Make startup script executable:**
```bash
chmod +x start_server.sh
```

## Configuration

### For Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hockey-prompts": {
      "command": "python",
      "args": ["/full/path/to/servers/hockey_prompts_mcp/server.py"]
    }
  }
}
```

### For Claude Code CLI

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "hockey-prompts": {
      "type": "stdio",
      "command": "/full/path/to/servers/hockey_prompts_mcp/start_server.sh",
      "args": []
    }
  }
}
```

## Usage

### In Claude Desktop

1. Open Claude Desktop
2. The prompts will appear in the prompt library
3. Select a prompt (e.g., "Plan Next Practice")
4. Claude will guide you through the interactive workflow
5. Respond to checkpoints as prompted

### In Claude Code CLI

```bash
# Start a practice planning session
claude "Use the plan_next_practice prompt to help me plan tomorrow's U10 practice"

# Run post-practice review
claude "Use the post_practice_review prompt for today's practice"
```

## How It Works

1. **Prompt Storage**: All prompts are stored as markdown files in `prompts/`
2. **Dynamic Loading**: Server loads prompts on-demand from markdown
3. **Tool Instructions**: Prompts include specific MCP tool calls for the LLM
4. **Interactive Checkpoints**: Clear pause points for coach input
5. **Integration**: Seamlessly works with existing MCP tools

## Editing Prompts

To modify prompts:

1. Navigate to `prompts/` directory
2. Edit the relevant `.md` file
3. No server restart needed - changes load on next prompt use
4. Follow the existing format for consistency

### Prompt Structure

Each prompt markdown file includes:
- **Overview**: Purpose and workflow summary
- **Parameters**: Input parameters (if any)
- **Steps**: Detailed workflow with tool calls
- **Checkpoints**: Coach input requirements
- **Output Format**: Expected results

## Required MCP Tools

The prompts reference these MCP tools (must be configured separately):

- **Airtable MCP**: Database operations
  - `mcp__airtable__list_records`
  - `mcp__airtable__create_record`
  - `mcp__airtable__update_records`

- **Hockey MCP**: Drill searches
  - `search_hockey_drills`
  - `search_hockey_tactics`

- **Hockey Diagram MCP**: Visual diagrams (optional)
  - `generate_hockey_diagram`

- **Notion MCP**: Documentation export (optional)
  - `mcp__notion-remote__notion-create-pages`

## Troubleshooting

### Server won't start
- Check Python version (3.8+ required)
- Verify MCP package installed: `pip install mcp`
- Check file permissions on `start_server.sh`

### Prompts not loading
- Verify prompt files exist in `prompts/` directory
- Check file permissions on markdown files
- Review server logs for errors

### Tool calls failing
- Ensure required MCP servers are configured
- Verify Airtable API access and table structure
- Check Hockey MCP server is running

## Development

### Adding New Prompts

1. Create new markdown file in `prompts/`
2. Add prompt registration in `server.py`:
```python
@mcp.prompt(
    name="your_prompt_name",
    title="Your Prompt Title",
    description="Brief description"
)
async def your_prompt_name() -> str:
    return load_prompt("your_prompt_file.md")
```

### Testing Prompts

```bash
# Test server startup
./start_server.sh

# Test prompt loading
python -c "from server import load_prompt; print(load_prompt('plan_next_practice.md')[:100])"
```

## License

Part of the Thunder Playbook hockey coaching platform.

## Support

For issues or questions:
- Check existing documentation in `docs/`
- Review `HOCKEY_PRACTICE_WORKFLOWS.md` for workflow details
- Open an issue in the main repository