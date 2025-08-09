---
description: "Show available commands and recommended workflows for Claude Code"
argument-hint: "[category]"
allowed-tools: ["Read"]
---

# Help - Claude Code Command Guide

Display available commands and recommended workflows. This is the starting point for any Claude Code instance.

**Usage**: `/help [category]` - Optional category: workflow, diagnostic, documentation, git, all

---

## 🚀 QUICK START WORKFLOW

### For New Claude Code Instances:
```bash
# First time on this project?
/help                    # You are here! See all commands
/preflight-check         # Verify environment is ready

# Starting work on an issue?
/start-issue <github-url>    # Complete setup in one command

# Finishing work?
/finish-issue <github-url>   # Document, commit, and create PR

# After PR approval?
/merge-worktree <issue-url> <pr-url>  # Merge and cleanup
```

### Continuing After Context Handoff:
```bash
# 1. Check for handoff documentation
cat coordination/context_handoff_*.md  # Read previous state

# 2. Continue with existing work
/onboard-feature <feature-name>        # Read feature docs
/preflight-check                       # Verify environment

# 3. Or start the issue fresh
/start-issue <github-url>              # Fresh setup
```

---

## 📋 COMMAND CATEGORIES

### 🎯 Primary Workflow Commands (USE THESE FIRST)
```
/start-issue <url>       - Begin work: worktree, env, checks, docs
/finish-issue <url>      - Complete work: test, document, commit, PR  
/merge-worktree          - Finalize after PR approval
```

### 🔍 Diagnostic Commands (When Issues Arise)
```
/preflight-check         - Comprehensive environment validation
/debug-mcp [port]        - Debug MCP endpoints (common 30-40% time loss!)
/trace-check             - Verify OpenAI API traces
/hockey-system-test      - Test hockey-specific systems
/web-validate            - Validate web app functionality
```

### 🔄 Context Management (When Running Out of Space)
```
/context-handoff         - Commit everything and prepare for new Claude
/context-handoff --emergency  - Rapid handoff when context critical
```

### 📚 Documentation Commands (Knowledge Transfer)
```
/document-feature        - Create/update feature documentation
/onboard-feature         - Read existing docs and get up to speed
/checkpoint-report       - Generate progress report
/task-handoff            - Planning Claude integration (multi-Claude)
```

### 🌿 Git Workflow Commands
```
/worktree-issue          - Create git worktree for issue
/commit-worktree         - Commit and push changes
/commit-prep             - Prepare commit message
/integration-ready       - Check if ready for integration
```

### 🏒 Hockey-Specific Commands
```
/hockey-setup            - Initialize hockey coaching environment
/plan-practice           - Create practice plans
/research-hockey         - Search hockey knowledge base
/generate-image          - Create hockey diagrams
/search-hockey-videos    - Find instructional videos
```

### 🎤 Voice & Configuration Commands
```
/start-voice-mode        - Enable voice interaction
/configure-voice         - Setup voice preferences
/reconnect               - Reconnect to services
/activate                - Activate services and environments
```

### 📊 Planning & Tracking Commands
```
/implement-feature       - Comprehensive feature implementation
/review-open-issues      - Review GitHub issues
/sync-issues             - Sync issue status
/multi-claude-setup      - Setup parallel development
/review-notion-tracker   - Check Notion documentation
```

---

## ⚠️ COMMON PITFALLS TO AVOID

### 1. Missing MCP Endpoints (30-40% time loss!)
```bash
# ALWAYS check MCP endpoints first:
/debug-mcp               # Run this if MCP tools fail
/preflight-check         # Or run comprehensive check
```

### 2. Virtual Environment Not Activated
```bash
# CRITICAL - Always activate first:
cd .. && source spacy_env/bin/activate && cd thunder_playbook
# Or use: /activate
```

### 3. Empty Query Errors
- OpenAI embeddings fail with empty queries
- Solution: Use list functions instead of search with empty string

### 4. Schema Mismatches
- Old cached data may have different structure
- Run /preflight-check to detect

---

## 📖 DETAILED HELP

### Get Help on Specific Category:
```bash
/help workflow      # Show workflow commands
/help diagnostic    # Show diagnostic tools
/help documentation # Show docs commands
/help git          # Show git commands
/help hockey       # Show hockey commands
/help all          # Show everything
```

### Get Help on Specific Command:
```bash
# Just run the command without arguments:
/start-issue        # Shows usage
/debug-mcp          # Shows usage
```

---

## 🎓 LEARNING PATH FOR NEW CLAUDE

1. **Start Here**: `/help` (you're here!)
2. **Check Environment**: `/preflight-check`
3. **Fix Any Issues**: `/debug-mcp --fix`
4. **Start Fresh Work**: `/start-issue <github-url>`
5. **Or Continue Existing**: `/onboard-feature <feature-name>` (reads docs)
6. **When Done**: `/finish-issue <github-url>`
7. **If Context Full**: `/context-handoff` (saves everything)

---

## 💡 PRO TIPS

1. **Always run /preflight-check before starting work**
2. **Use /debug-mcp immediately if MCP tools fail**
3. **Document issues with /document-feature for next Claude**
4. **Run /start-issue instead of manual setup**
5. **Check /help whenever unsure about commands**
6. **Watch for context exhaustion signs (slowness, repetition)**
7. **Use /context-handoff BEFORE context runs out**

---

## 🆘 STILL STUCK?

If you need more help:
1. Check CLAUDE.md for project-specific guidance
2. Run /preflight-check for system diagnosis
3. Use /debug-mcp for MCP-specific issues
4. Review existing documentation with /onboard-feature

Remember: The meta-commands (/start-issue, /finish-issue) handle most complexity for you!