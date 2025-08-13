# ⚠️ IMPORTANT: Path Update Required After Merge

## Current Configuration (Worktree)
The hockey-prompts MCP server is currently configured with **worktree paths** in Claude Desktop:

```json
"hockey-prompts": {
  "command": "/Users/liammckendry/thunder_playbook_worktrees/issue-103/servers/hockey_prompts_mcp/start_server.sh",
  "args": [],
  "env": {}
}
```

## Required Update After Merge
After merging this worktree into main, update the Claude Desktop configuration to use the main repository path:

### File to Update:
`/Users/liammckendry/Library/Application Support/Claude/claude_desktop_config.json`

### Change From (Worktree):
```json
"command": "/Users/liammckendry/thunder_playbook_worktrees/issue-103/servers/hockey_prompts_mcp/start_server.sh"
```

### Change To (Main):
```json
"command": "/Users/liammckendry/thunder_playbook/servers/hockey_prompts_mcp/start_server.sh"
```

## Update Steps:
1. After merging PR into main
2. Open Claude Desktop config: `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Find the `hockey-prompts` section
4. Update the path from `thunder_playbook_worktrees/issue-103` to `thunder_playbook`
5. Save the file
6. Restart Claude Desktop

## Alternative: Use Claude Code CLI
If you're using Claude Code CLI, update with:
```bash
# Remove old worktree config
claude mcp remove hockey-prompts

# Add with main repo path
claude mcp add hockey-prompts /Users/liammckendry/thunder_playbook/servers/hockey_prompts_mcp/start_server.sh
```

## Verification
After updating, verify the server connects:
```bash
claude mcp list | grep hockey-prompts
```

Should show: `hockey-prompts: ... - ✓ Connected`

---

**Note**: This is a temporary configuration using the worktree path for testing. The production path should point to the main repository.