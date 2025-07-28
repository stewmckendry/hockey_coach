# Checkpoint Report Command

Generate standardized progress reports for Worker Claude instances at key development checkpoints.

**Usage**: Worker Claude instances - at Draft+Questions and Testing Ready checkpoints

---

## Checkpoint Type Detection

### Determine Checkpoint Phase
```bash
echo "🔍 Determining checkpoint phase..."

# Detect current phase based on context and user input
CHECKPOINT_TYPE=""

# If user specifies checkpoint type, use it
if [ ! -z "$1" ]; then
    CHECKPOINT_TYPE="$1"
    echo "📋 Checkpoint type specified: $CHECKPOINT_TYPE"
else
    # Auto-detect based on current progress
    echo "🤖 Auto-detecting checkpoint phase..."
    
    # Check git status for clues
    if git diff --quiet && git diff --staged --quiet; then
        CHECKPOINT_TYPE="draft-questions"
        echo "📝 Detected: draft-questions (no code changes yet)"
    elif git diff --name-only HEAD | wc -l | grep -q "[1-9]"; then
        CHECKPOINT_TYPE="testing-ready"  
        echo "🧪 Detected: testing-ready (code changes present)"
    else
        CHECKPOINT_TYPE="draft-questions"
        echo "📝 Defaulted to: draft-questions"
    fi
fi

# Validate checkpoint type
case "$CHECKPOINT_TYPE" in
    "draft-questions"|"testing-ready"|"progress-update")
        echo "✅ Checkpoint type: $CHECKPOINT_TYPE"
        ;;
    *)
        echo "❌ Invalid checkpoint type: $CHECKPOINT_TYPE"
        echo "Valid types: draft-questions, testing-ready, progress-update"
        exit 1
        ;;
esac
```

### Determine Worker Context
```bash
echo "🔍 Determining worker context..."

# Get task information from current directory
CURRENT_DIR=$(pwd)
TASK_NUMBER=""
TASK_NAME=""
WORKER_ID=""
SCRATCHPAD_FILE=""

case "$CURRENT_DIR" in
    *"task_1_4") 
        TASK_NUMBER="1.4"
        TASK_NAME="Season Planning Specialist Agent"
        WORKER_ID="Worker-1"
        SCRATCHPAD_FILE="coordination/task_1_4_scratchpad.md"
        ;;
    *"task_1_5") 
        TASK_NUMBER="1.5"
        TASK_NAME="Team Assessment Tool"
        WORKER_ID="Worker-2"
        SCRATCHPAD_FILE="coordination/task_1_5_scratchpad.md"
        ;;
    *"task_1_6") 
        TASK_NUMBER="1.6"
        TASK_NAME="Artifact Generation"
        WORKER_ID="Worker-3"
        SCRATCHPAD_FILE="coordination/task_1_6_scratchpad.md"
        ;;
    *)
        echo "❌ Unknown task directory: $CURRENT_DIR"
        echo "Run this command from a task worktree directory"
        exit 1
        ;;
esac

echo "✅ Worker context identified:"
echo "  📋 Task: $TASK_NUMBER - $TASK_NAME"
echo "  🆔 Worker: $WORKER_ID"
echo "  📝 Scratchpad: $SCRATCHPAD_FILE"
```

---

## Draft + Questions Checkpoint

### Generate Draft + Questions Report
```bash
if [ "$CHECKPOINT_TYPE" = "draft-questions" ]; then
    echo "📝 Generating Draft + Questions checkpoint report..."
    
    # Calculate completion percentage for exploration phase
    COMPLETION_PERCENT="75"  # Typically 75% after exploration/planning
    
    # Generate checkpoint report
    cat >> "$SCRATCHPAD_FILE" << EOF

---

## CHECKPOINT: DRAFT + QUESTIONS - $(date -u +%Y-%m-%dT%H:%M:%SZ)

**Phase**: EXPLORE + PLAN COMPLETE
**Status**: AWAITING_HUMAN_FEEDBACK  
**Completion**: ${COMPLETION_PERCENT}%
**Worker**: $WORKER_ID

### DRAFT: Complete Implementation Plan

#### User-Agent Experience Design
[PLACEHOLDER - Worker Claude should replace this section with actual UX design findings]
- Conversation flow mapping
- Key agent questions identified
- Response patterns defined
- User experience entry/exit points

#### Technical Design & System Alignment  
[PLACEHOLDER - Worker Claude should replace this section with technical approach]
- Architecture integration approach
- Code reuse strategy identified
- MCP tool integration plan
- System evolution considerations

#### OpenAI Agents SDK Integration
[PLACEHOLDER - Worker Claude should replace this section with SDK research]
- Native SDK features to leverage
- Implementation pattern selected
- Custom vs native decisions documented

### QUESTIONS FOR HUMAN FEEDBACK:

1. **UX Design Question**: [PLACEHOLDER - Replace with specific UX assumption question]

2. **Technical Approach Question**: [PLACEHOLDER - Replace with specific technical question]

3. **SDK Integration Question**: [PLACEHOLDER - Replace with specific SDK question]

4. **System Integration Question**: [PLACEHOLDER - Replace with integration question]

5. **Scope/Priority Question**: [PLACEHOLDER - Replace with scope clarification question]

### ITERATION STATUS:
- [ ] Draft covers all research areas comprehensively
- [ ] Questions highlight key assumptions requiring validation
- [ ] Ready for human feedback and iteration cycle
- [ ] All exploration objectives completed

**NEXT REQUIRED ACTION**: Human review and feedback on draft + questions
**AWAITING**: Iteration cycle until approved to proceed to BUILD phase

---

EOF

    echo "✅ Draft + Questions report: Added to scratchpad"
    echo ""
    echo "📋 Template sections added - replace PLACEHOLDER content with:"
    echo "  1. Your actual UX design findings and conversation flow"
    echo "  2. Your technical approach and system integration plan"  
    echo "  3. Your SDK research and implementation decisions"
    echo "  4. Your specific questions about key assumptions"
    echo ""
    echo "🔄 Next step: Present draft + questions for human feedback"
fi
```

---

## Testing Ready Checkpoint

### Generate Testing Ready Report
```bash
if [ "$CHECKPOINT_TYPE" = "testing-ready" ]; then
    echo "🧪 Generating Testing Ready checkpoint report..."
    
    # Calculate completion percentage for build phase
    COMPLETION_PERCENT="95"  # Typically 95% after build completion
    
    # Analyze implemented changes
    FILES_MODIFIED=$(git diff origin/main --name-only | wc -l | tr -d ' ')
    COMMITS_MADE=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
    
    # Generate checkpoint report
    cat >> "$SCRATCHPAD_FILE" << EOF

---

## CHECKPOINT: TESTING READY - $(date -u +%Y-%m-%dT%H:%M:%SZ)

**Phase**: BUILD COMPLETE
**Status**: READY_FOR_HUMAN_TESTING
**Completion**: ${COMPLETION_PERCENT}%
**Worker**: $WORKER_ID

### IMPLEMENTATION COMPLETED:

#### Files Created/Modified: $FILES_MODIFIED
$(git diff origin/main --name-only | sed 's/^/- /')

#### Commits Made: $COMMITS_MADE
$(git log --oneline origin/main..HEAD 2>/dev/null | sed 's/^/- /' || echo "- No commits yet")

#### Integration Points Tested:
- [ ] MCP server connectivity validated
- [ ] Agent integration functional  
- [ ] CLI testing completed
- [ ] Service health confirmed

### READY FOR HUMAN TESTING:

#### Testing Scenarios to Validate:
[PLACEHOLDER - Worker Claude should replace with specific test scenarios]
1. **Primary functionality test**: [Describe main feature test]
2. **Integration test**: [Describe system integration test]  
3. **Edge case test**: [Describe edge case validation]
4. **Performance test**: [Describe performance validation]

#### How to Test the Implementation:
[PLACEHOLDER - Worker Claude should replace with testing instructions]
\`\`\`bash
# Step 1: [Testing step]
# Step 2: [Testing step]  
# Step 3: [Testing step]
\`\`\`

#### Expected Behavior to Verify:
[PLACEHOLDER - Worker Claude should replace with expected outcomes]
- **Functional expectation**: [What should work]
- **Performance expectation**: [How fast/reliable]
- **Integration expectation**: [How it works with system]

### IMPLEMENTATION NOTES:

#### Build Phase Summary:
- **Approach**: [PLACEHOLDER - Describe implementation approach used]
- **Challenges**: [PLACEHOLDER - Any challenges encountered and resolved]
- **Deviations**: [PLACEHOLDER - Any changes from original plan]

#### Quality Assurance Completed:
- [ ] Code follows existing patterns and conventions
- [ ] Error handling implemented appropriately  
- [ ] Documentation updated for new functionality
- [ ] No breaking changes to existing system

### QUESTIONS (if any):
[PLACEHOLDER - Replace with any remaining questions or concerns]
1. **Implementation question**: [Any implementation concerns]
2. **Testing question**: [Any testing approach questions]
3. **Integration question**: [Any integration concerns]

**NEXT REQUIRED ACTION**: Human testing and validation of implementation
**AWAITING**: Green light to proceed to SUBMIT WORK phase

---

EOF

    echo "✅ Testing Ready report: Added to scratchpad"
    echo ""
    echo "📋 Template sections added - replace PLACEHOLDER content with:"
    echo "  1. Specific testing scenarios for your implementation"
    echo "  2. Clear testing instructions for human validation"
    echo "  3. Expected behavior and outcomes to verify"
    echo "  4. Summary of your build approach and any challenges"
    echo ""
    echo "🧪 Next step: Present for human testing validation"
fi
```

---

## Progress Update Checkpoint

### Generate Progress Update Report
```bash
if [ "$CHECKPOINT_TYPE" = "progress-update" ]; then
    echo "📊 Generating progress update checkpoint report..."
    
    # Determine current phase based on activity
    CURRENT_PHASE="UNKNOWN"
    if [ ! -d ".git" ]; then
        CURRENT_PHASE="SETUP"
    elif [ "$(git rev-list --count HEAD 2>/dev/null || echo 0)" -eq 0 ]; then
        CURRENT_PHASE="EXPLORE_PLAN"
    elif git diff --quiet && git diff --staged --quiet; then
        CURRENT_PHASE="PLANNING"
    else
        CURRENT_PHASE="BUILD"
    fi
    
    # Calculate rough completion percentage
    case "$CURRENT_PHASE" in
        "SETUP") COMPLETION_PERCENT="10" ;;
        "EXPLORE_PLAN") COMPLETION_PERCENT="30" ;;
        "PLANNING") COMPLETION_PERCENT="50" ;;
        "BUILD") COMPLETION_PERCENT="80" ;;
        *) COMPLETION_PERCENT="0" ;;
    esac
    
    # Generate progress update
    cat >> "$SCRATCHPAD_FILE" << EOF

---

## PROGRESS UPDATE - $(date -u +%Y-%m-%dT%H:%M:%SZ)

**Phase**: $CURRENT_PHASE
**Status**: IN_PROGRESS
**Completion**: ${COMPLETION_PERCENT}%
**Worker**: $WORKER_ID

### Current Activity:
[PLACEHOLDER - Worker Claude should describe current work]

### Progress Since Last Update:
[PLACEHOLDER - Worker Claude should describe recent progress]
- Completed: [What was finished]
- In Progress: [What is currently being worked on]
- Next: [What comes next]

### Files Being Modified:
$(if git diff --name-only HEAD 2>/dev/null | grep -q .; then git diff --name-only HEAD | sed 's/^/- /'; else echo "- No files currently modified"; fi)

### Blockers/Questions:
[PLACEHOLDER - Worker Claude should note any blockers]
- Blocker 1: [Description and status]
- Question 1: [Question needing clarification]
- None currently

### Timeline Status:
- **On Track**: [Yes/No with explanation]
- **Expected Next Checkpoint**: [When and what type]
- **Estimated Completion**: [Time estimate for current phase]

### Communication Notes:
- **Last Human Interaction**: [When and outcome]
- **Escalation Needed**: [Yes/No with details]
- **Coordination Required**: [Any cross-task dependencies]

---

EOF

    echo "✅ Progress update report: Added to scratchpad"
    echo ""
    echo "📋 Template sections added - replace PLACEHOLDER content with:"
    echo "  1. Your current specific activity and focus"
    echo "  2. Concrete progress made since last update"
    echo "  3. Any blockers or questions requiring attention"
    echo "  4. Timeline and communication status"
fi
```

---

## Shared Status Dashboard Update

### Update Cross-Instance Status
```bash
echo "🔄 Updating shared status dashboard..."

# Update shared status with checkpoint information
python -c "
import re
from datetime import datetime

# Read current shared status
with open('coordination/shared_status.md', 'r') as f:
    content = f.read()

# Update task status based on checkpoint type
status_map = {
    'draft-questions': 'AWAITING_FEEDBACK',
    'testing-ready': 'READY_FOR_TESTING', 
    'progress-update': 'IN_PROGRESS'
}

new_status = status_map.get('$CHECKPOINT_TYPE', 'IN_PROGRESS')
progress = '$COMPLETION_PERCENT'

# Update task row in status table
task_pattern = r'(\| $TASK_NUMBER .*?\| $WORKER_ID \|) [^|]+ (\| )\d+(%\s*\|)'
replacement = r'\1 ' + new_status + r' \2' + progress + r'\3'

updated_content = re.sub(task_pattern.replace('$TASK_NUMBER', '$TASK_NUMBER').replace('$WORKER_ID', '$WORKER_ID'), replacement, content)

# Update timestamp
timestamp_pattern = r'(\*\*Last Updated\*\*: )[^\\n]+'
new_timestamp = r'\1' + datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
updated_content = re.sub(timestamp_pattern, new_timestamp, updated_content)

# Write updated content
with open('coordination/shared_status.md', 'w') as f:
    f.write(updated_content)

print('✅ Shared status updated: Task $TASK_NUMBER status changed to ' + new_status)
"

echo "✅ Shared status dashboard: Updated with checkpoint information"
```

---

## Checkpoint Summary

### Generate Checkpoint Summary
```bash
echo ""
echo "📋 CHECKPOINT REPORT COMPLETE!"
echo ""
echo "Checkpoint Details:"
echo "  📊 Type: $CHECKPOINT_TYPE"
echo "  📋 Task: $TASK_NUMBER - $TASK_NAME"
echo "  🆔 Worker: $WORKER_ID"
echo "  📈 Progress: ${COMPLETION_PERCENT}%"
echo "  ⏰ Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""
echo "Updates Made:"
echo "  📝 Scratchpad: $SCRATCHPAD_FILE updated"
echo "  📊 Shared Status: Dashboard updated with checkpoint status"
echo "  🔄 Communication: Standardized report format applied"
echo ""

case "$CHECKPOINT_TYPE" in
    "draft-questions")
        echo "Next Steps:"
        echo "  1. Complete PLACEHOLDER sections in scratchpad"
        echo "  2. Present draft + questions to human for feedback"
        echo "  3. Iterate based on feedback until approved"
        echo "  4. Proceed to BUILD phase after approval"
        ;;
    "testing-ready")
        echo "Next Steps:"
        echo "  1. Complete PLACEHOLDER sections in scratchpad"
        echo "  2. Present implementation for human testing"
        echo "  3. Address any issues found during testing"
        echo "  4. Proceed to SUBMIT WORK phase after green light"
        ;;
    "progress-update")
        echo "Next Steps:"
        echo "  1. Complete PLACEHOLDER sections in scratchpad"
        echo "  2. Continue with current development phase"
        echo "  3. Address any blockers or questions noted"
        echo "  4. Provide next progress update as needed"
        ;;
esac
echo ""
```

---

## Success Criteria

- ✅ Checkpoint type determined correctly
- ✅ Worker context identified from directory
- ✅ Standardized report generated in scratchpad
- ✅ Shared status dashboard updated
- ✅ Template sections provided for completion
- ✅ Next steps clearly defined

## Usage Examples

```bash
# Auto-detect checkpoint type
/checkpoint-report

# Specify checkpoint type explicitly  
/checkpoint-report draft-questions
/checkpoint-report testing-ready
/checkpoint-report progress-update
```

## Troubleshooting

### Wrong Directory
```bash
# Must be run from task worktree directory
cd /Users/liammckendry/thunder_playbook_task_1_X
/checkpoint-report
```

### Missing Scratchpad File
```bash
# Check coordination directory
ls -la coordination/task_*_scratchpad.md

# Contact Planning Claude if missing
```

### Shared Status Update Fails
```bash
# Check shared status file exists and is writable
ls -la coordination/shared_status.md

# Manual update if script fails
vim coordination/shared_status.md
```

Standardized checkpoint reporting system is now active for consistent multi-Claude communication!