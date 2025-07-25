# Multi-Claude Setup Command

Set up complete Git worktree infrastructure and coordination files for parallel development batch.

**Usage**: Planning Claude only - before launching Worker Claude instances

---

## Git Worktree Creation

### Create Worktrees for Task Batch
```bash
# Navigate to main repository
cd /Users/liammckendry/thunder_playbook

# Verify clean main branch state
git status
git pull origin main  # If needed

# Create worktrees for current task batch
# Task 1.4: Season Planning Specialist Agent
git worktree add ../thunder_playbook_task_1_4 -b task-1.4-season-planning-agent

# Task 1.5: Team Assessment Tool  
git worktree add ../thunder_playbook_task_1_5 -b task-1.5-team-assessment-tool

# Task 1.6: Artifact Generation
git worktree add ../thunder_playbook_task_1_6 -b task-1.6-artifact-generation

# Verify worktree creation
git worktree list
```

### Worktree Structure Validation
```bash
# Expected output from 'git worktree list':
# /Users/liammckendry/thunder_playbook           [main]
# /Users/liammckendry/thunder_playbook_task_1_4  [task-1.4-season-planning-agent]  
# /Users/liammckendry/thunder_playbook_task_1_5  [task-1.5-team-assessment-tool]
# /Users/liammckendry/thunder_playbook_task_1_6  [task-1.6-artifact-generation]

echo "✅ Git worktrees created successfully"
```

---

## Coordination Files Initialization

### Create Communication Infrastructure
```bash
# Ensure coordination directory exists
mkdir -p coordination

# Initialize core coordination files if not present
touch coordination/planning_scratchpad.md
touch coordination/shared_status.md  
touch coordination/integration_queue.md

# Initialize task-specific scratchpads
touch coordination/task_1_4_scratchpad.md
touch coordination/task_1_5_scratchpad.md
touch coordination/task_1_6_scratchpad.md

# Initialize task assignments (if not already present)
touch coordination/task_assignment_1_4.md
touch coordination/task_assignment_1_5.md
touch coordination/task_assignment_1_6.md

echo "✅ Coordination files initialized"
```

### Update Shared Status Dashboard
```bash
# Update shared_status.md with current batch information
cat > coordination/shared_status.md << 'EOF'
# Shared Status Dashboard  
## Multi-Claude Development Coordination

**Last Updated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Update Frequency**: Real-time (as tasks progress)

---

## Task Status Matrix

| Task | Worker | Status | Progress | Branch | Blockers | ETA |
|------|--------|--------|----------|--------|----------|-----|
| 1.4 Season Planning Agent | Worker-1 | PENDING_ASSIGNMENT | 0% | task-1.4-season-planning-agent | None | TBD |
| 1.5 Team Assessment Tool | Worker-2 | PENDING_ASSIGNMENT | 0% | task-1.5-team-assessment-tool | None | TBD |
| 1.6 Artifact Generation | Worker-3 | PENDING_ASSIGNMENT | 0% | task-1.6-artifact-generation | None | TBD |

---

## Environment Status

### Core Services
- **MCP Server** (port 8000): ✅ RUNNING
- **Web App** (port 3000): ✅ RUNNING  
- **ChromaDB**: ✅ AVAILABLE
- **Git Repository**: ✅ CLEAN (main branch)

### Worker Claude Readiness
- **Worker Claude 1**: 🟡 PREPARING (worktree ready)
- **Worker Claude 2**: 🟡 PREPARING (worktree ready)  
- **Worker Claude 3**: 🟡 PREPARING (worktree ready)

---

## Communication Health

**Scratchpad Status**:
- ✅ planning_scratchpad.md: Active (Planning Claude)
- 🟡 task_1_4_scratchpad.md: Initialized (awaiting Worker Claude 1)
- 🟡 task_1_5_scratchpad.md: Initialized (awaiting Worker Claude 2)
- 🟡 task_1_6_scratchpad.md: Initialized (awaiting Worker Claude 3)
- ✅ shared_status.md: Active (this file)
- ✅ integration_queue.md: Active (empty - no completed tasks yet)

**Update Frequency Target**: Every 2 hours during active development

---

## Current Blockers

**No Active Blockers** 🎉

---

*This file is automatically updated by all Claude instances for cross-coordination*
EOF

echo "✅ Shared status dashboard updated"
```

---

## Service Health Validation

### Core Services Check
```bash
echo "🔍 Validating core services..."

# Check MCP Server
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ MCP Server (port 8000): HEALTHY"
else
    echo "❌ MCP Server (port 8000): DOWN - Run /hockey-setup first"
    exit 1
fi

# Check Web App (if running)
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Web App (port 3000): HEALTHY"
else
    echo "🟡 Web App (port 3000): NOT RUNNING - Start with 'cd web_app && npm run dev'"
fi

# Check Agent HTTP Server (if running)
if curl -s http://localhost:8002 > /dev/null; then
    echo "✅ Agent HTTP Server (port 8002): HEALTHY"
else
    echo "🟡 Agent HTTP Server (port 8002): NOT RUNNING - Start with POC agent server if needed"
fi

# Check Direct API (if running)
if curl -s http://localhost:3003/api/mcp > /dev/null; then
    echo "✅ Direct API (port 3003): HEALTHY"
else
    echo "🟡 Direct API (port 3003): NOT RUNNING - Start if needed for testing"
fi

echo "✅ Service health validation complete"
```

### ChromaDB Connectivity
```bash
echo "🔍 Testing ChromaDB connectivity..."

# Test ChromaDB access via MCP server
python3 << 'EOF'
try:
    import sys
    sys.path.append('/Users/liammckendry/thunder_playbook')
    from utils.chroma_utils import get_chroma_collection
    
    # Test connection
    collection = get_chroma_collection('drill-source1')
    count = collection.count()
    print(f"✅ ChromaDB: Connected successfully ({count} items in drill-source1)")
    
except Exception as e:
    print(f"❌ ChromaDB: Connection failed - {e}")
    exit(1)
EOF

echo "✅ ChromaDB connectivity validated"
```

---

## Final Validation

### Commit Coordination Infrastructure
```bash
# Add coordination files to git
git add coordination/

# Commit infrastructure setup
git commit -m "Initialize multi-Claude coordination infrastructure for batch 1

- Set up Git worktrees for Tasks 1.4, 1.5, 1.6
- Initialize communication scratchpad files
- Update shared status dashboard
- Ready for Worker Claude instance launch

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ Coordination infrastructure committed"
```

### Generate Launch Instructions
```bash
echo ""
echo "🚀 MULTI-CLAUDE SETUP COMPLETE!"
echo ""
echo "Ready to launch Worker Claude instances:"
echo ""
echo "Worker Claude 1:"
echo "  Directory: cd /Users/liammckendry/thunder_playbook_task_1_4"
echo "  Task: Season Planning Specialist Agent"
echo "  Assignment: coordination/task_assignment_1_4.md"
echo ""
echo "Worker Claude 2:"  
echo "  Directory: cd /Users/liammckendry/thunder_playbook_task_1_5"
echo "  Task: Team Assessment Tool"
echo "  Assignment: coordination/task_assignment_1_5.md"
echo ""
echo "Worker Claude 3:"
echo "  Directory: cd /Users/liammckendry/thunder_playbook_task_1_6" 
echo "  Task: Artifact Generation"
echo "  Assignment: coordination/task_assignment_1_6.md"
echo ""
echo "Next Steps:"
echo "1. Open 3 new Claude Code terminal sessions"
echo "2. Navigate each to its assigned worktree directory"
echo "3. Provide each with its task assignment file"
echo "4. Monitor progress via coordination/shared_status.md"
echo ""
```

---

## Success Criteria

- ✅ All Git worktrees created successfully
- ✅ All coordination files initialized and configured
- ✅ Shared status dashboard updated with current batch
- ✅ Core services validated and healthy
- ✅ ChromaDB connectivity confirmed
- ✅ Infrastructure changes committed to git
- ✅ Launch instructions generated

## Troubleshooting

### Worktree Creation Fails
```bash
# Clean up failed worktree
git worktree remove ../thunder_playbook_task_X_Y --force

# Remove branch if needed
git branch -D task-X.Y-description

# Retry creation
git worktree add ../thunder_playbook_task_X_Y -b task-X.Y-description
```

### Service Health Issues
```bash
# If MCP server down, restart it
python servers/hockey_mcp.py &

# If web app needed, start it
cd web_app && npm run dev &

# Wait for services to be ready
sleep 5
```

### ChromaDB Issues
```bash
# Check ChromaDB status
python -c "
from utils.chroma_utils import get_chroma_collection
try:
    collection = get_chroma_collection('drill-source1')
    print('ChromaDB OK')
except Exception as e:
    print(f'ChromaDB Error: {e}')
"
```

Multi-Claude parallel development infrastructure is now ready for Worker Claude deployment!