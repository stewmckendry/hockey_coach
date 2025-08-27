# Token Optimization Guide for Claude Code Sessions

## Current Problem (157k/200k tokens - 79% used)
- **MCP Tools**: 102.5k tokens (51.2%) - 120+ tools loaded
- **Memory Files**: 20.6k tokens (10.3%) - Duplicate CLAUDE.md files
- **Messages**: 18.4k tokens (9.2%)
- **Only 43k tokens remaining** for actual work!

## Immediate Optimization (Save 90k+ tokens)

### 1. Minimal MCP Configuration for n8n Work
Create `~/.claude/configs/n8n.json`:
```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["mcp-google-sheets@latest"],
      "env": {
        "SERVICE_ACCOUNT_PATH": "/path/to/service-account-key.json"
      }
    },
    "ref-tools": {
      "type": "http",
      "url": "https://api.ref.tools/mcp?apiKey=${REF_API_KEY}"
    }
  }
}
```

Only 2 MCP servers needed for n8n work = **~2k tokens** vs 102k!

### 2. Task-Specific MCP Profiles

#### Hockey Development Profile
```bash
# ~/.claude/configs/hockey.json
# Only: hockey-coaching, hockey-diagram, notion
# ~5k tokens
```

#### Security Analysis Profile
```bash
# ~/.claude/configs/security.json  
# Only: semgrep, exa
# ~3k tokens
```

#### Web Development Profile
```bash
# ~/.claude/configs/webdev.json
# Only: playwright, ref-tools
# ~2k tokens
```

### 3. Switch Profiles Before Starting
```bash
# Before starting a session
export CLAUDE_CONFIG_PROFILE=n8n
claude code

# Or manually swap configs
cp ~/.claude/configs/n8n.json ~/.claude.json
claude code
```

## Session Start Checklist

1. **Choose the right profile**:
   - n8n work? Use minimal profile (2k tokens)
   - Hockey development? Use hockey profile (5k tokens)
   - Never use "all MCP servers" profile unless needed

2. **Clean duplicate files**:
   - Remove duplicate CLAUDE.md from parent directories
   - Keep only project-specific version

3. **Use /compact early**:
   - When context reaches 60%, use `/compact` command
   - Removes old conversation while keeping essential context

## Token Budget Guidelines

| Component | Current | Optimized | Savings |
|-----------|---------|-----------|---------|
| MCP Tools | 102.5k | 2-5k | 97k+ |
| Memory Files | 20.6k | 11k | 9.6k |
| **Total Savings** | | | **106k tokens** |

## Quick Wins for Current Session

1. **Restart with minimal config**:
   ```bash
   # Save current work state
   echo "Workflow ID: NLSGnPWngNkvkxqs" > n8n/current_work.txt
   
   # Exit and restart with minimal MCP
   /exit
   # Then edit ~/.claude.json to remove unnecessary MCP servers
   ```

2. **Use focused agents instead of loading all tools**:
   - Use `explorer-agent` to search instead of loading all search MCPs
   - Use `builder-agent` for coding instead of loading all code tools

3. **Batch operations**:
   - Group multiple file reads/writes
   - Use glob patterns instead of multiple reads

## Emergency Recovery (When at 95%+ tokens)

1. Use `/compact` immediately
2. Save critical info to file:
   ```bash
   echo "Critical context" > .session_state.txt
   ```
3. Exit and restart with minimal profile
4. Read .session_state.txt to restore context

## Best Practices Going Forward

### DO:
- ✅ Start with minimal MCP profile
- ✅ Add servers only when needed
- ✅ Use `/compact` proactively at 60%
- ✅ Keep single CLAUDE.md per project
- ✅ Use task-specific profiles

### DON'T:
- ❌ Load all 120+ MCP tools "just in case"  
- ❌ Keep duplicate configuration files
- ❌ Wait until 90%+ to manage tokens
- ❌ Use general profile for specific tasks

## Estimated Impact

With optimizations:
- **Before**: 79% tokens used at session start
- **After**: 15-20% tokens used at session start
- **Available for work**: 160k+ tokens (vs current 43k)
- **4x more productive sessions!**