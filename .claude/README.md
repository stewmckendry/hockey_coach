# Claude Code Project Settings

This directory contains project-specific Claude Code configuration.

## Setup Instructions

1. Copy the template file to create your local settings:
   ```bash
   cp settings.local.json.template settings.local.json
   ```

2. The local settings file (`settings.local.json`) is gitignored and won't be committed.

## Auto-Accept Permissions

The template includes full auto-accept permissions for all tools including MCP servers:
- All standard Claude Code tools (Read, Write, Edit, Bash, etc.)
- All configured MCP servers (notion, exa, ref-tools, hockey-diagram, etc.)

This allows Claude Code to run in auto-accept edits mode without requiring manual approval for each tool use.

## MCP Server Configuration

The project currently enables:
- `hockey-diagram`: Hockey tactical diagram generation

Additional MCP servers are configured at the user level in `~/.claude.json`.