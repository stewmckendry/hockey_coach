# Worker Ready Check Command

Comprehensive environment validation for Worker Claude instances before beginning task execution.

**Usage**: Worker Claude instances only - upon assignment to worktree

---

## Worktree Environment Validation

### Verify Worktree Setup
```bash
# Check current directory and branch
echo "🔍 Validating worktree environment..."
echo "Current directory: $(pwd)"
echo "Current branch: $(git branch --show-current)"
echo "Git status:"
git status --porcelain

# Verify we're in the correct worktree
EXPECTED_DIRS=(
    "/Users/liammckendry/thunder_playbook_task_1_4"
    "/Users/liammckendry/thunder_playbook_task_1_5" 
    "/Users/liammckendry/thunder_playbook_task_1_6"
)

CURRENT_DIR=$(pwd)
if [[ " ${EXPECTED_DIRS[@]} " =~ " ${CURRENT_DIR} " ]]; then
    echo "✅ Worktree directory: CORRECT"
else
    echo "❌ Worktree directory: INCORRECT - Expected one of: ${EXPECTED_DIRS[@]}"
    echo "Navigate to your assigned worktree directory first"
    exit 1
fi

# Verify branch name matches directory
EXPECTED_BRANCH=""
case "$CURRENT_DIR" in
    *"task_1_4") EXPECTED_BRANCH="task-1.4-season-planning-agent" ;;
    *"task_1_5") EXPECTED_BRANCH="task-1.5-team-assessment-tool" ;;
    *"task_1_6") EXPECTED_BRANCH="task-1.6-artifact-generation" ;;
esac

CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "$EXPECTED_BRANCH" ]; then
    echo "✅ Git branch: CORRECT ($CURRENT_BRANCH)"
else
    echo "❌ Git branch: INCORRECT - Expected: $EXPECTED_BRANCH, Got: $CURRENT_BRANCH"
    exit 1
fi
```

### Python Environment Validation
```bash
echo "🔍 Validating Python environment..."

# Check if spacy_env is activated
if [[ "$VIRTUAL_ENV" == *"spacy_env"* ]]; then
    echo "✅ Python environment: spacy_env activated"
    echo "Python path: $VIRTUAL_ENV"
else
    echo "🟡 Python environment: spacy_env not activated"
    echo "Activating spacy_env..."
    source /Users/liammckendry/spacy_env/bin/activate
    
    if [[ "$VIRTUAL_ENV" == *"spacy_env"* ]]; then
        echo "✅ Python environment: spacy_env activated successfully"
    else
        echo "❌ Python environment: Failed to activate spacy_env"
        exit 1
    fi
fi

# Verify Python version and key packages
echo "Python version: $(python --version)"
echo "Python path: $(which python)"

# Test key package imports
python -c "
import sys
import os
sys.path.append('/Users/liammckendry/thunder_playbook')

try:
    # Test core imports
    import openai
    print('✅ OpenAI package: Available')
    
    import chromadb  
    print('✅ ChromaDB package: Available')
    
    from fastmcp import FastMCP
    print('✅ FastMCP package: Available')
    
    from utils.chroma_utils import get_chroma_collection
    print('✅ Project utilities: Available')
    
except ImportError as e:
    print(f'❌ Package import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies: All required packages available"
else
    echo "❌ Python dependencies: Missing required packages"
    exit 1
fi
```

---

## Service Connectivity Testing

### Core Services Health Check
```bash
echo "🔍 Testing service connectivity..."

# Test MCP Server
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo "✅ MCP Server (port 8000): CONNECTED"
    
    # Test specific MCP tools
    echo "Testing MCP tools availability..."
    python -c "
import sys
sys.path.append('/Users/liammckendry/thunder_playbook')
import requests
import json

try:
    # Test MCP server tools endpoint
    response = requests.get('http://localhost:8000/mcp/list_tools', timeout=5)
    if response.status_code == 200:
        tools = response.json()
        expected_tools = ['search_hockey_knowledge', 'get_coaching_recommendations', 
                         'create_practice_plan', 'analyze_player_development']
        
        available_tools = [tool.get('name', '') for tool in tools.get('tools', [])]
        
        for tool in expected_tools:
            if tool in available_tools:
                print(f'✅ MCP Tool: {tool} available')
            else:
                print(f'❌ MCP Tool: {tool} missing')
                
    else:
        print(f'❌ MCP Tools: Server responded with status {response.status_code}')
        
except Exception as e:
    print(f'❌ MCP Tools: Connection error - {e}')
"
else
    echo "❌ MCP Server (port 8000): UNREACHABLE"
    echo "Run /hockey-setup to start core services"
    exit 1
fi

# Test Web App (optional)
if curl -s -f http://localhost:3000 > /dev/null; then
    echo "✅ Web App (port 3000): CONNECTED"
else
    echo "🟡 Web App (port 3000): NOT RUNNING (optional for development)"
fi

# Test Agent HTTP Server (optional)
if curl -s -f http://localhost:8002 > /dev/null; then
    echo "✅ Agent HTTP Server (port 8002): CONNECTED"
else
    echo "🟡 Agent HTTP Server (port 8002): NOT RUNNING (optional for testing)"
fi
```

### ChromaDB Connectivity Test
```bash
echo "🔍 Testing ChromaDB connectivity..."

python -c "
import sys
sys.path.append('/Users/liammckendry/thunder_playbook')

try:
    from utils.chroma_utils import get_chroma_collection
    
    # Test access to key collections
    test_collections = ['drill-source1', 'ltad-source1', 'tactics-source1']
    
    for collection_name in test_collections:
        try:
            collection = get_chroma_collection(collection_name)
            count = collection.count()
            print(f'✅ ChromaDB Collection: {collection_name} ({count} items)')
        except Exception as e:
            print(f'❌ ChromaDB Collection: {collection_name} - {e}')
            
except Exception as e:
    print(f'❌ ChromaDB: Connection failed - {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ ChromaDB: All test collections accessible"
else
    echo "❌ ChromaDB: Connectivity issues detected"
    exit 1
fi
```

---

## Task Assignment Validation

### Load and Validate Task Assignment
```bash
echo "🔍 Validating task assignment..."

# Determine task assignment file based on directory
TASK_FILE=""
case "$CURRENT_DIR" in
    *"task_1_4") TASK_FILE="coordination/task_assignment_1_4.md" ;;
    *"task_1_5") TASK_FILE="coordination/task_assignment_1_5.md" ;;
    *"task_1_6") TASK_FILE="coordination/task_assignment_1_6.md" ;;
esac

if [ -f "$TASK_FILE" ]; then
    echo "✅ Task assignment file: Found ($TASK_FILE)"
    
    # Extract task title
    TASK_TITLE=$(grep "^**Task**:" "$TASK_FILE" | sed 's/\*\*Task\*\*: //')
    echo "📋 Task: $TASK_TITLE"
    
    # Check for required sections
    REQUIRED_SECTIONS=("Context" "Technical Requirements" "Success Criteria" "Workflow Approach")
    
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if grep -q "### $section" "$TASK_FILE" || grep -q "## $section" "$TASK_FILE"; then
            echo "✅ Task section: $section present"
        else
            echo "❌ Task section: $section missing"
        fi
    done
    
else
    echo "❌ Task assignment file: NOT FOUND ($TASK_FILE)"
    echo "Contact Planning Claude for task assignment"
    exit 1
fi
```

### Determine Scratchpad File
```bash
echo "🔍 Identifying scratchpad file..."

# Determine scratchpad file based on directory
SCRATCHPAD_FILE=""
case "$CURRENT_DIR" in
    *"task_1_4") SCRATCHPAD_FILE="coordination/task_1_4_scratchpad.md" ;;
    *"task_1_5") SCRATCHPAD_FILE="coordination/task_1_5_scratchpad.md" ;;
    *"task_1_6") SCRATCHPAD_FILE="coordination/task_1_6_scratchpad.md" ;;
esac

if [ -f "$SCRATCHPAD_FILE" ]; then
    echo "✅ Scratchpad file: Found ($SCRATCHPAD_FILE)"
else
    echo "❌ Scratchpad file: NOT FOUND ($SCRATCHPAD_FILE)"
    echo "Contact Planning Claude for scratchpad initialization"
    exit 1
fi
```

---

## Task Acknowledgment

### Acknowledge Task Assignment
```bash
echo "🔍 Acknowledging task assignment..."

# Add acknowledgment to scratchpad
cat >> "$SCRATCHPAD_FILE" << EOF

---

## WORKER CLAUDE READY CHECK - $(date -u +%Y-%m-%dT%H:%M:%SZ)

**Environment Validation**: ✅ COMPLETE
- Worktree setup: CORRECT
- Git branch: CORRECT  
- Python environment: spacy_env activated
- Service connectivity: MCP server reachable
- ChromaDB access: All collections available
- Task assignment: Loaded and validated

**Task Acknowledgment**: ✅ ACKNOWLEDGED
**Status**: READY_TO_BEGIN_EXPLORATION
**Worker Claude**: ACTIVE

**Next Phase**: Beginning exploration phase
- Research user-agent experience design
- Study technical system alignment  
- Research OpenAI Agents SDK patterns
- Synthesize into implementation plan

**Communication Protocol**: ESTABLISHED
- Progress updates: Every phase transition
- Escalation path: Via scratchpad to Planning Claude
- Completion notice: Via integration queue

---

EOF

echo "✅ Task acknowledgment: Added to scratchpad"
```

### Update Shared Status
```bash
echo "🔍 Updating shared status dashboard..."

# Determine worker ID and task name
WORKER_ID=""
TASK_NAME=""
case "$CURRENT_DIR" in
    *"task_1_4") 
        WORKER_ID="Worker-1"
        TASK_NAME="Season Planning Agent"
        ;;
    *"task_1_5") 
        WORKER_ID="Worker-2"
        TASK_NAME="Team Assessment Tool"
        ;;
    *"task_1_6") 
        WORKER_ID="Worker-3"
        TASK_NAME="Artifact Generation"
        ;;
esac

# Update shared status with ready status
python -c "
import sys
import re

# Read current shared status
with open('coordination/shared_status.md', 'r') as f:
    content = f.read()

# Update worker status to ACTIVE
worker_pattern = r'(\*\*$WORKER_ID\*\*: )🟡 PREPARING.*'
replacement = r'\1✅ ACTIVE (exploration phase starting)'

updated_content = re.sub(worker_pattern.replace('$WORKER_ID', '$WORKER_ID'), replacement, content)

# Write updated content
with open('coordination/shared_status.md', 'w') as f:
    f.write(updated_content)

print('✅ Shared status updated: $WORKER_ID marked as ACTIVE')
"

echo "✅ Shared status: Updated with ready status"
```

---

## Final Readiness Report

### Generate Readiness Summary
```bash
echo ""
echo "🎉 WORKER CLAUDE READY CHECK COMPLETE!"
echo ""
echo "Worker Environment Summary:"
echo "  🆔 Worker ID: $WORKER_ID"
echo "  📋 Task: $TASK_NAME"
echo "  📁 Directory: $CURRENT_DIR"
echo "  🌿 Branch: $CURRENT_BRANCH"
echo "  🐍 Python: spacy_env activated"
echo "  🔧 Services: MCP server connected"
echo "  💾 Data: ChromaDB accessible"
echo "  📝 Assignment: Loaded and acknowledged"
echo "  📊 Status: Updated in coordination files"
echo ""
echo "Ready to begin autonomous Explore + Plan phase!"
echo ""
echo "Next steps:"
echo "1. Study task assignment thoroughly: $TASK_FILE"
echo "2. Begin exploration phase research"
echo "3. Update progress in scratchpad: $SCRATCHPAD_FILE"
echo "4. Present Draft + Questions when exploration complete"
echo ""
```

---

## Success Criteria

- ✅ Worktree directory and branch validated
- ✅ Python environment (spacy_env) activated and tested
- ✅ All required Python packages available
- ✅ MCP server connectivity confirmed
- ✅ ChromaDB collections accessible
- ✅ Task assignment file loaded and validated
- ✅ Scratchpad file identified and accessible  
- ✅ Task acknowledgment added to scratchpad
- ✅ Shared status dashboard updated
- ✅ Communication protocol established

## Troubleshooting

### Wrong Directory/Branch
```bash
# Check assigned worktree
git worktree list

# Navigate to correct directory
cd /Users/liammckendry/thunder_playbook_task_1_X
```

### Python Environment Issues
```bash
# Activate spacy_env
source /Users/liammckendry/spacy_env/bin/activate

# Verify activation
echo $VIRTUAL_ENV
```

### Service Connectivity Issues  
```bash
# Check service status
curl http://localhost:8000/health

# If services down, run setup
/hockey-setup
```

### Missing Task Files
```bash
# Check coordination directory
ls -la coordination/

# Contact Planning Claude if files missing
echo "❌ Missing coordination files - contact Planning Claude"
```

Worker Claude is now validated and ready for autonomous task execution!