---
description: "Generate or update comprehensive documentation for a feature to enable smooth handoff between Claude Code instances"
argument-hint: "<feature-name> [related-issue-urls...]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebFetch", "TodoWrite", "Task"]
---

# Document Feature for Handoff

Generate or update comprehensive documentation about a feature to help another Claude Code instance understand the technical implementation, context, and setup requirements.

**Behavior**: 
- If documentation already exists for the feature, it will be **updated** with new information
- Existing documentation is backed up before updates
- Shows what changed since last documentation (commits, files)
- Preserves version history for tracking documentation evolution

**Usage**: `$ARGUMENTS` - Feature name and optionally related GitHub issue URLs

---

## Phase 1: Feature Analysis

### Parse Arguments and Context
```bash
# Extract feature name and optional issue URLs from arguments
FEATURE_NAME=$(echo "$ARGUMENTS" | awk '{print $1}')
ISSUE_URLS=$(echo "$ARGUMENTS" | cut -d' ' -f2-)

echo "📝 Documenting feature: $FEATURE_NAME"
echo "🔗 Related issues: $ISSUE_URLS"

# Determine if we're in main repo or worktree
CURRENT_DIR=$(pwd)
if [[ "$CURRENT_DIR" == *"worktree"* ]]; then
    echo "📍 Working in worktree: $CURRENT_DIR"
    WORKTREE_MODE=true
else
    echo "📍 Working in main repository"
    WORKTREE_MODE=false
fi

# Check git status and branch
echo ""
echo "🌿 Git Status:"
git status --short
echo "📌 Current branch: $(git branch --show-current)"
echo "📊 Uncommitted changes: $(git status --porcelain | wc -l)"

# Check for existing documentation
DOCS_DIR="coordination/feature_docs"
mkdir -p "$DOCS_DIR"

# Look for existing documentation for this feature
EXISTING_DOC=$(ls -t "$DOCS_DIR"/${FEATURE_NAME}_handoff_*.md 2>/dev/null | head -1)

if [ -n "$EXISTING_DOC" ]; then
    echo ""
    echo "📄 Found existing documentation: $EXISTING_DOC"
    echo "📝 Will update existing documentation instead of creating new"
    
    # Create backup of existing documentation
    BACKUP_FILE="${EXISTING_DOC}.backup_$(date +%Y%m%d_%H%M%S)"
    cp "$EXISTING_DOC" "$BACKUP_FILE"
    echo "💾 Backup created: $BACKUP_FILE"
    
    # Extract last documented branch and commit from existing doc
    LAST_BRANCH=$(grep "^\*\*Branch\*\*:" "$EXISTING_DOC" | head -1 | sed 's/.*Branch\*\*: *//' | awk '{print $1}')
    LAST_COMMIT=$(grep "Last commit:" "$EXISTING_DOC" | tail -1 | sed 's/.*Last commit: *//')
    
    if [ -n "$LAST_BRANCH" ]; then
        echo "📌 Last documented branch: $LAST_BRANCH"
    fi
    if [ -n "$LAST_COMMIT" ]; then
        echo "📝 Last documented commit: $LAST_COMMIT"
    fi
    
    FEATURE_DOC="$EXISTING_DOC"
    UPDATE_MODE=true
    export UPDATE_MODE=true
    export BACKUP_FILE="$BACKUP_FILE"
else
    echo ""
    echo "📄 No existing documentation found"
    echo "📝 Creating new documentation file"
    
    FEATURE_DOC="$DOCS_DIR/${FEATURE_NAME}_handoff_$(date +%Y%m%d_%H%M%S).md"
    UPDATE_MODE=false
fi

echo ""
```

### Fetch GitHub Issue Context (if URLs provided)
```python
import re
import json
from datetime import datetime

issue_urls = "$ISSUE_URLS".strip().split() if "$ISSUE_URLS".strip() else []
issue_data = []

for url in issue_urls:
    if 'github.com' in url:
        print(f"📥 Fetching issue: {url}")
        # Use WebFetch to get issue details
        # Parse issue title, description, comments, and linked PRs
        # Extract technical decisions and implementation notes
        issue_data.append({
            'url': url,
            'fetched': datetime.now().isoformat()
        })

if issue_data:
    with open('/tmp/feature_issues.json', 'w') as f:
        json.dump(issue_data, f, indent=2)
    print(f"✅ Fetched {len(issue_data)} related issues")
```

---

## Phase 2: Technical Discovery

### Identify Feature Components
```bash
echo "🔍 Discovering feature components..."

# Handle documentation creation/update
if [ "$UPDATE_MODE" = true ]; then
    # For updates, preserve existing content and add update header
    echo "" >> "$FEATURE_DOC"
    echo "---" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
    echo "## Documentation Update: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$FEATURE_DOC"
    echo "**Branch**: $(git branch --show-current)" >> "$FEATURE_DOC"
    echo "**Location**: $(pwd)" >> "$FEATURE_DOC"
    echo "**Changes Since Last Update**: $(git status --porcelain | wc -l) uncommitted changes" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
    
    # Add what changed since last documentation
    echo "### What Changed Since Last Documentation" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
    
    # Show git commits since last documented commit if available
    if [ -n "$LAST_COMMIT" ]; then
        LAST_COMMIT_SHA=$(echo "$LAST_COMMIT" | awk '{print $1}')
        echo "#### New Commits Since $LAST_COMMIT_SHA:" >> "$FEATURE_DOC"
        echo '```' >> "$FEATURE_DOC"
        git log --oneline ${LAST_COMMIT_SHA}..HEAD 2>/dev/null | head -10 >> "$FEATURE_DOC" || echo "No new commits found" >> "$FEATURE_DOC"
        echo '```' >> "$FEATURE_DOC"
        echo "" >> "$FEATURE_DOC"
        
        echo "#### Files Changed Since Last Documentation:" >> "$FEATURE_DOC"
        echo '```' >> "$FEATURE_DOC"
        git diff --name-status ${LAST_COMMIT_SHA}..HEAD 2>/dev/null | head -20 >> "$FEATURE_DOC" || echo "Unable to determine file changes" >> "$FEATURE_DOC"
        echo '```' >> "$FEATURE_DOC"
    else
        echo "Unable to determine changes (no previous commit reference found)" >> "$FEATURE_DOC"
    fi
    echo "" >> "$FEATURE_DOC"
    
    # Add marker for where new content begins
    echo "### Updates in This Version" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
else
    # For new documentation, create full header
    cat > "$FEATURE_DOC" << EOF
# Feature Documentation: $FEATURE_NAME
**Generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Branch**: $(git branch --show-current)
**Location**: $(pwd)

---

## Quick Start
EOF
fi

# Continue with service dependency checks
echo "" >> "$FEATURE_DOC"
echo "### Service Dependencies" >> "$FEATURE_DOC"

### Virtual Environment Activation
\`\`\`bash
# CRITICAL: Always activate the virtual environment first
cd .. && source spacy_env/bin/activate && cd thunder_playbook
\`\`\`

### Service Dependencies
EOF

# Check which services are required
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "- **MCP Server**: Running on port 8000 ✅" >> "$FEATURE_DOC"
else
    echo "- **MCP Server**: Required (start with: python servers/hockey_mcp.py &)" >> "$FEATURE_DOC"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "- **Web App**: Running on port 3000 ✅" >> "$FEATURE_DOC"
else
    echo "- **Web App**: May be required (start with: cd web_app && npm run dev)" >> "$FEATURE_DOC"
fi

if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "- **ChromaDB**: Available ✅" >> "$FEATURE_DOC"
else
    echo "- **ChromaDB**: May be required (start with: chroma run --host localhost --port 8000 --no-auth &)" >> "$FEATURE_DOC"
fi
```

### Map File Structure
```python
import os
import glob

# Find all files modified for this feature
print("📂 Analyzing file structure...")

# Use git to find modified files if in git context
modified_files = []
new_files = []
deleted_files = []

try:
    # Get git diff information
    import subprocess
    
    # Files changed in current branch vs main
    diff_output = subprocess.run(
        ['git', 'diff', '--name-status', 'origin/main...HEAD'],
        capture_output=True, text=True
    ).stdout
    
    for line in diff_output.strip().split('\n'):
        if line:
            status, *paths = line.split('\t')
            path = paths[0] if paths else ''
            
            if status == 'M':
                modified_files.append(path)
            elif status == 'A':
                new_files.append(path)
            elif status == 'D':
                deleted_files.append(path)
                
except Exception as e:
    print(f"⚠️ Could not get git diff: {e}")

# Group files by category
file_categories = {
    'Core Implementation': [],
    'Tests': [],
    'Configuration': [],
    'Documentation': [],
    'Web Components': [],
    'API Routes': [],
    'Database/Models': [],
    'Utilities': []
}

all_files = modified_files + new_files

for file in all_files:
    if 'test' in file.lower() or 'spec' in file.lower():
        file_categories['Tests'].append(file)
    elif file.endswith(('.md', '.txt', 'README')):
        file_categories['Documentation'].append(file)
    elif file.endswith(('.json', '.yaml', '.yml', '.env', '.config.js')):
        file_categories['Configuration'].append(file)
    elif 'web_app/components' in file:
        file_categories['Web Components'].append(file)
    elif 'web_app/app/api' in file or 'api/' in file:
        file_categories['API Routes'].append(file)
    elif 'models/' in file or 'schema' in file:
        file_categories['Database/Models'].append(file)
    elif 'utils/' in file or 'lib/' in file:
        file_categories['Utilities'].append(file)
    else:
        file_categories['Core Implementation'].append(file)

# Write to documentation
with open(os.environ.get('FEATURE_DOC', '/tmp/feature_doc.md'), 'a') as f:
    # Check if we're updating or creating new
    update_mode = os.environ.get('UPDATE_MODE', 'false') == 'true'
    
    if update_mode:
        f.write("\n### Updated File Structure\n\n")
    else:
        f.write("\n## File Structure\n\n")
    
    for category, files in file_categories.items():
        if files:
            f.write(f"### {category}\n")
            for file in sorted(files):
                f.write(f"- `{file}`\n")
            f.write("\n")
    
    if deleted_files:
        f.write("### Deleted Files\n")
        for file in sorted(deleted_files):
            f.write(f"- ~~`{file}`~~\n")
        f.write("\n")

print(f"✅ Categorized {len(all_files)} files across {sum(1 for v in file_categories.values() if v)} categories")
```

---

## Phase 3: Implementation Details

### Extract Key Functions and Classes
```bash
echo "🔧 Extracting implementation details..."

# Add implementation section to documentation
cat >> "$FEATURE_DOC" << 'EOF'

## Implementation Details

### Key Entry Points
EOF

# Find main entry points for the feature
if [ -n "$FEATURE_NAME" ]; then
    # Search for function/class definitions related to feature
    echo '```python' >> "$FEATURE_DOC"
    grep -r "def.*${FEATURE_NAME}" --include="*.py" . 2>/dev/null | head -10 >> "$FEATURE_DOC"
    grep -r "class.*${FEATURE_NAME}" --include="*.py" . 2>/dev/null | head -10 >> "$FEATURE_DOC"
    echo '```' >> "$FEATURE_DOC"
    
    # TypeScript/JavaScript functions
    echo '```typescript' >> "$FEATURE_DOC"
    grep -r "function.*${FEATURE_NAME}" --include="*.ts" --include="*.tsx" --include="*.js" . 2>/dev/null | head -10 >> "$FEATURE_DOC"
    grep -r "const.*${FEATURE_NAME}" --include="*.ts" --include="*.tsx" --include="*.js" . 2>/dev/null | head -10 >> "$FEATURE_DOC"
    echo '```' >> "$FEATURE_DOC"
fi
```

### Document API Endpoints
```python
# Search for API routes related to the feature
import re
import os

api_endpoints = []
feature_name = os.environ.get('FEATURE_NAME', '').lower()

# Search for Next.js API routes
api_dirs = ['web_app/app/api', 'web_app/pages/api', 'servers']

for api_dir in api_dirs:
    if os.path.exists(api_dir):
        for root, dirs, files in os.walk(api_dir):
            for file in files:
                if file.endswith(('.ts', '.js', '.py')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                            
                        # Look for route definitions
                        if 'route.ts' in file or 'route.js' in file:
                            # Next.js App Router
                            methods = re.findall(r'export\s+async\s+function\s+(GET|POST|PUT|DELETE|PATCH)', content)
                            if methods:
                                route_path = filepath.replace('web_app/app', '').replace('/route.ts', '').replace('/route.js', '')
                                api_endpoints.append({
                                    'path': route_path,
                                    'methods': methods,
                                    'file': filepath
                                })
                        
                        # FastAPI/Flask routes
                        if '.py' in file:
                            routes = re.findall(r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)', content)
                            routes.extend(re.findall(r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)', content))
                            for method, path in routes:
                                api_endpoints.append({
                                    'path': path,
                                    'methods': [method.upper()],
                                    'file': filepath
                                })
                                
                    except Exception as e:
                        pass

# Write API documentation
if api_endpoints:
    with open(os.environ.get('FEATURE_DOC', '/tmp/feature_doc.md'), 'a') as f:
        f.write("\n### API Endpoints\n\n")
        f.write("| Endpoint | Methods | File |\n")
        f.write("|----------|---------|------|\n")
        
        for endpoint in api_endpoints:
            methods_str = ', '.join(endpoint['methods'])
            f.write(f"| `{endpoint['path']}` | {methods_str} | `{endpoint['file']}` |\n")
        
        f.write("\n")
    
    print(f"✅ Documented {len(api_endpoints)} API endpoints")
```

---

## Phase 4: Dependencies and Configuration

### Document Dependencies
```bash
echo "📦 Documenting dependencies..."

cat >> "$FEATURE_DOC" << 'EOF'

## Dependencies and Configuration

### Python Dependencies
EOF

# Check for Python dependencies
if [ -f "requirements.txt" ]; then
    echo '```' >> "$FEATURE_DOC"
    grep -E "(fastmcp|openai|chroma|pydantic|fastapi)" requirements.txt >> "$FEATURE_DOC" 2>/dev/null
    echo '```' >> "$FEATURE_DOC"
fi

echo "" >> "$FEATURE_DOC"
echo "### Node.js Dependencies" >> "$FEATURE_DOC"

# Check for Node dependencies
if [ -f "web_app/package.json" ]; then
    echo '```json' >> "$FEATURE_DOC"
    grep -A 5 '"dependencies"' web_app/package.json >> "$FEATURE_DOC"
    echo '```' >> "$FEATURE_DOC"
fi

echo "" >> "$FEATURE_DOC"
echo "### Environment Variables" >> "$FEATURE_DOC"
echo "Required environment variables for this feature:" >> "$FEATURE_DOC"
echo '```bash' >> "$FEATURE_DOC"

# Search for environment variable usage
grep -r "os.environ\|process.env" --include="*.py" --include="*.ts" --include="*.js" . 2>/dev/null | \
    grep -oE "(os\.environ\.get\(['\"]|os\.environ\[['\"]|process\.env\.)[A-Z_]+" | \
    sed 's/os.environ.get..\|os.environ\[..\|process.env\.//' | \
    sort -u | head -20 >> "$FEATURE_DOC"

echo '```' >> "$FEATURE_DOC"
```

### Document MCP Tools Usage
```python
# Search for MCP tool usage in the feature
import re

mcp_tools = set()
mcp_patterns = [
    r'search_hockey_knowledge',
    r'get_coaching_recommendations',
    r'create_practice_plan',
    r'analyze_player_development',
    r'generate_hockey_diagram',
    r'parse_hockey_formation'
]

# Search Python files
for root, dirs, files in os.walk('.'):
    # Skip node_modules and other large directories
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__']]
    
    for file in files:
        if file.endswith(('.py', '.ts', '.tsx', '.js')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                for pattern in mcp_patterns:
                    if re.search(pattern, content):
                        mcp_tools.add(pattern)
                        
            except Exception:
                pass

if mcp_tools:
    with open(os.environ.get('FEATURE_DOC', '/tmp/feature_doc.md'), 'a') as f:
        f.write("\n### MCP Tools Used\n")
        f.write("This feature uses the following MCP tools:\n\n")
        for tool in sorted(mcp_tools):
            f.write(f"- `{tool}`\n")
        f.write("\n")
    
    print(f"✅ Found {len(mcp_tools)} MCP tool dependencies")
```

---

## Phase 5: Testing and Validation

### Document Test Coverage
```bash
echo "🧪 Documenting tests..."

cat >> "$FEATURE_DOC" << 'EOF'

## Testing

### Test Files
EOF

# Find test files
find . -name "*test*.py" -o -name "*test*.ts" -o -name "*test*.js" -o -name "*spec*.ts" -o -name "*spec*.js" 2>/dev/null | \
    grep -v node_modules | head -20 >> "$FEATURE_DOC"

echo "" >> "$FEATURE_DOC"
echo "### Running Tests" >> "$FEATURE_DOC"
echo '```bash' >> "$FEATURE_DOC"
echo "# Python tests" >> "$FEATURE_DOC"
echo "cd .. && source spacy_env/bin/activate && cd thunder_playbook" >> "$FEATURE_DOC"
echo "python -m pytest tests/ -v" >> "$FEATURE_DOC"
echo "" >> "$FEATURE_DOC"
echo "# TypeScript/JavaScript tests" >> "$FEATURE_DOC"
echo "cd web_app" >> "$FEATURE_DOC"
echo "npm test" >> "$FEATURE_DOC"
echo "npm run lint" >> "$FEATURE_DOC"
echo "npm run type-check" >> "$FEATURE_DOC"
echo '```' >> "$FEATURE_DOC"

echo "" >> "$FEATURE_DOC"
echo "### Manual Testing Checklist" >> "$FEATURE_DOC"
echo "- [ ] Feature works in development environment" >> "$FEATURE_DOC"
echo "- [ ] All API endpoints respond correctly" >> "$FEATURE_DOC"
echo "- [ ] UI components render properly" >> "$FEATURE_DOC"
echo "- [ ] Error handling works as expected" >> "$FEATURE_DOC"
echo "- [ ] Performance is acceptable" >> "$FEATURE_DOC"
echo "- [ ] No console errors or warnings" >> "$FEATURE_DOC"
```

---

## Phase 6: Common Pitfalls and Solutions

### Document Known Issues and Resolutions
```bash
echo "" >> "$FEATURE_DOC"
echo "## Common Pitfalls and Solutions" >> "$FEATURE_DOC"
echo "" >> "$FEATURE_DOC"
echo "### Issues Encountered During Development" >> "$FEATURE_DOC"
echo "" >> "$FEATURE_DOC"

# Check for MCP endpoint issues
echo "#### MCP Endpoint Issues" >> "$FEATURE_DOC"
for port in 8000 8001 8002 3003; do
    if lsof -i :$port > /dev/null 2>&1; then
        ENDPOINT=$([[ $port == 3003 || $port == 8002 ]] && echo "/api/mcp" || echo "/mcp")
        CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port$ENDPOINT 2>/dev/null)
        
        if [ "$CODE" = "404" ]; then
            echo "- **Port $port**: MCP endpoint missing (404) - causes silent failures" >> "$FEATURE_DOC"
            echo "  - **Solution**: Add MCP handler to service's API server" >> "$FEATURE_DOC"
            echo "  - **Impact**: All MCP tool calls fail without clear error" >> "$FEATURE_DOC"
        elif [ "$CODE" = "200" ] || [ "$CODE" = "405" ]; then
            echo "- **Port $port**: MCP endpoint working ✅" >> "$FEATURE_DOC"
        fi
    fi
done
echo "" >> "$FEATURE_DOC"

# Document spec extraction complexity if relevant
if [ -f "web_app/lib/server/diagramSpecExtractor.ts" ]; then
    echo "#### Spec Extraction Complexity" >> "$FEATURE_DOC"
    echo "- **Issue**: Multiple data formats (parserSpec, agentTraces, RunResult)" >> "$FEATURE_DOC"
    echo "- **Solution**: Created unified extraction logic handling all formats" >> "$FEATURE_DOC"
    echo "- **File**: web_app/lib/server/diagramSpecExtractor.ts" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
fi

# Document empty query handling
echo "#### Empty Query Handling" >> "$FEATURE_DOC"
if grep -r "search_cached_diagrams" --include="*.ts" --include="*.py" . > /dev/null 2>&1; then
    echo "- **Issue**: OpenAI embeddings fail with empty queries ('input is invalid')" >> "$FEATURE_DOC"
    echo "- **Solution**: Implement list_all_cached_diagrams for browsing without search" >> "$FEATURE_DOC"
    echo "- **Alternative**: Default to generic query like 'hockey' when empty" >> "$FEATURE_DOC"
else
    echo "- No search functions requiring empty query handling" >> "$FEATURE_DOC"
fi
echo "" >> "$FEATURE_DOC"

# Document CSS truncation issues
echo "#### CSS Truncation Issues" >> "$FEATURE_DOC"
CSS_ISSUES=$(find web_app -name "*.css" -o -name "*.tsx" | xargs grep -l "truncate\|line-clamp" 2>/dev/null | wc -l)
if [ $CSS_ISSUES -gt 0 ]; then
    echo "- **Issue**: Long content truncated with ellipsis in $CSS_ISSUES files" >> "$FEATURE_DOC"
    echo "- **Solution**: Remove truncate/line-clamp classes from detail views" >> "$FEATURE_DOC"
    echo "- **Check**: Technical details, JSON content, error messages" >> "$FEATURE_DOC"
else
    echo "- No CSS truncation patterns detected" >> "$FEATURE_DOC"
fi
echo "" >> "$FEATURE_DOC"

# Document state management complexity
echo "#### State Management Complexity" >> "$FEATURE_DOC"
if [ -f "web_app/components/hockey-diagram/DiagramLibrary.tsx" ]; then
    STATE_COUNT=$(grep -c "useState" web_app/components/hockey-diagram/DiagramLibrary.tsx 2>/dev/null || echo "0")
    if [ $STATE_COUNT -gt 10 ]; then
        echo "- **Issue**: High state complexity ($STATE_COUNT useState calls)" >> "$FEATURE_DOC"
        echo "- **Solution**: Consider consolidating into useReducer or context" >> "$FEATURE_DOC"
        echo "- **Impact**: Difficult to track state changes and debug" >> "$FEATURE_DOC"
    else
        echo "- State management appears manageable ($STATE_COUNT useState calls)" >> "$FEATURE_DOC"
    fi
else
    echo "- Component not found for state analysis" >> "$FEATURE_DOC"
fi
echo "" >> "$FEATURE_DOC"

# Document schema version issues
echo "#### Schema Version Conflicts" >> "$FEATURE_DOC"
echo "- **Issue**: Older cached entries use different schema (zone vs x/y coordinates)" >> "$FEATURE_DOC"
echo "- **Solution**: Implement backward compatibility or migration script" >> "$FEATURE_DOC"
echo "- **Detection**: Check for both 'zone' and 'x/y' fields in specs" >> "$FEATURE_DOC"
echo "" >> "$FEATURE_DOC"

# Add time estimates for common issues
echo "### Time Impact of Common Issues" >> "$FEATURE_DOC"
echo "" >> "$FEATURE_DOC"
echo "Based on experience, these issues typically cause:" >> "$FEATURE_DOC"
echo "- **Missing MCP endpoint**: 30-40% of development time (silent failures)" >> "$FEATURE_DOC"
echo "- **Spec extraction complexity**: 15-20% (multiple iterations)" >> "$FEATURE_DOC"
echo "- **Empty query errors**: 10-15% (API errors, workarounds)" >> "$FEATURE_DOC"
echo "- **CSS truncation**: 5-10% (UI debugging)" >> "$FEATURE_DOC"
echo "- **State management**: 10-15% (refactoring)" >> "$FEATURE_DOC"
echo "- **Schema conflicts**: 5-10% (data validation)" >> "$FEATURE_DOC"
echo "" >> "$FEATURE_DOC"

# Add preventive measures
echo "### Preventive Measures" >> "$FEATURE_DOC"
echo "" >> "$FEATURE_DOC"
echo "To avoid these issues in future development:" >> "$FEATURE_DOC"
echo "1. **Always run /preflight-check before starting**" >> "$FEATURE_DOC"
echo "2. **Test MCP endpoints with /debug-mcp when adding new services**" >> "$FEATURE_DOC"
echo "3. **Handle empty inputs in all search/query functions**" >> "$FEATURE_DOC"
echo "4. **Plan state management architecture upfront**" >> "$FEATURE_DOC"
echo "5. **Version schemas and maintain backward compatibility**" >> "$FEATURE_DOC"
echo "6. **Test with edge cases early (empty, null, malformed data)**" >> "$FEATURE_DOC"
echo "7. **Add comprehensive error logging, not silent catches**" >> "$FEATURE_DOC"
echo "" >> "$FEATURE_DOC"
```

## Phase 7: Knowledge Transfer

### Create Onboarding Guide
```bash
cat >> "$FEATURE_DOC" << 'EOF'

## Onboarding Guide for New Claude Instance

### 1. Initial Setup
```bash
# Navigate to correct directory
cd /Users/liammckendry/thunder_playbook  # or appropriate worktree

# Activate virtual environment (CRITICAL!)
cd .. && source spacy_env/bin/activate && cd thunder_playbook

# Install/update dependencies if needed
pip install -r requirements.txt
cd web_app && npm install && cd ..
```

### 2. Start Required Services
```bash
# Start all services (recommended)
python start_services.py

# Or start individually:
python servers/hockey_mcp.py &           # MCP server
python servers/hockey_mcp_direct_api.py & # Direct API
cd web_app && npm run dev &              # Web app
```

### 3. Key Files to Review
Priority files to understand this feature:
EOF

# List the most important files (top 10 by modification)
echo '```' >> "$FEATURE_DOC"
git diff --name-only origin/main...HEAD 2>/dev/null | head -10 >> "$FEATURE_DOC"
echo '```' >> "$FEATURE_DOC"

cat >> "$FEATURE_DOC" << 'EOF'

### 4. Common Issues and Solutions

#### Virtual Environment Not Activated
**Error**: `ModuleNotFoundError: No module named 'fastmcp'`
**Solution**: 
```bash
cd .. && source spacy_env/bin/activate && cd thunder_playbook
```

#### Port Already in Use
**Error**: `Address already in use`
**Solution**:
```bash
lsof -i :8000  # Find process
kill -9 <PID>  # Kill process
```

#### ChromaDB Connection Failed
**Error**: `Connection refused`
**Solution**:
```bash
chroma run --host localhost --port 8000 --no-auth &
```

### 5. Feature-Specific Context
EOF

# Add any feature-specific notes
if [ -n "$ISSUE_URLS" ]; then
    echo "" >> "$FEATURE_DOC"
    echo "**Related GitHub Issues:**" >> "$FEATURE_DOC"
    for url in $ISSUE_URLS; do
        echo "- $url" >> "$FEATURE_DOC"
    done
fi

echo "" >> "$FEATURE_DOC"
echo "### 6. Contact Points" >> "$FEATURE_DOC"
echo "- **Previous Claude Instance**: Documented this feature on $(date)" >> "$FEATURE_DOC"
echo "- **Git Branch**: $(git branch --show-current)" >> "$FEATURE_DOC"
echo "- **Last Commit**: $(git log -1 --oneline)" >> "$FEATURE_DOC"
```

---

## Phase 7: Generate Summary

### Create Executive Summary
```bash
# Only add executive summary for new documentation
if [ "$UPDATE_MODE" = false ]; then
    echo "" >> "$FEATURE_DOC"
    echo "---" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
    echo "## Executive Summary" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
    echo "**Feature**: $FEATURE_NAME" >> "$FEATURE_DOC"
    echo "**Status**: $(git status --porcelain | wc -l) uncommitted changes" >> "$FEATURE_DOC"
    echo "**Branch**: $(git branch --show-current)" >> "$FEATURE_DOC"
    echo "**Files Modified**: $(git diff --name-only origin/main...HEAD 2>/dev/null | wc -l)" >> "$FEATURE_DOC"
    echo "**Documentation Generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
    echo "This documentation provides everything needed for another Claude Code instance to:" >> "$FEATURE_DOC"
    echo "1. Understand the feature architecture" >> "$FEATURE_DOC"
    echo "2. Set up the development environment" >> "$FEATURE_DOC"
    echo "3. Continue implementation or maintenance" >> "$FEATURE_DOC"
    echo "4. Run tests and validate functionality" >> "$FEATURE_DOC"
    echo "5. Troubleshoot common issues" >> "$FEATURE_DOC"
else
    # For updates, add update summary
    echo "" >> "$FEATURE_DOC"
    echo "---" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
    echo "### Update Summary" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
    echo "**Updated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$FEATURE_DOC"
    echo "**Current Status**: $(git status --porcelain | wc -l) uncommitted changes" >> "$FEATURE_DOC"
    echo "**Branch**: $(git branch --show-current)" >> "$FEATURE_DOC"
    echo "**Total Files Modified**: $(git diff --name-only origin/main...HEAD 2>/dev/null | wc -l)" >> "$FEATURE_DOC"
    echo "" >> "$FEATURE_DOC"
    
    # Add version history entry
    echo "### Version History" >> "$FEATURE_DOC"
    echo "- $(date -u +%Y-%m-%dT%H:%M:%SZ): Documentation updated" >> "$FEATURE_DOC"
    echo "  - Branch: $(git branch --show-current)" >> "$FEATURE_DOC"
    echo "  - Last commit: $(git log -1 --oneline)" >> "$FEATURE_DOC"
fi

echo ""
if [ "$UPDATE_MODE" = true ]; then
    echo "✅ Feature documentation updated!"
    echo "📄 Updated documentation: $FEATURE_DOC"
    echo "💾 Backup saved with timestamp"
else
    echo "✅ Feature documentation complete!"
    echo "📄 Documentation saved to: $FEATURE_DOC"
fi
echo ""
echo "To onboard a new Claude instance, use:"
echo "/onboard-feature $FEATURE_NAME"
```

---

## Success Confirmation

The feature has been fully documented with:
- ✅ Technical implementation details
- ✅ File structure and modifications
- ✅ Dependencies and configuration
- ✅ API endpoints and MCP tools
- ✅ Testing procedures
- ✅ Setup instructions
- ✅ Troubleshooting guide
- ✅ Contact and context information

The documentation is saved in `coordination/feature_docs/` for easy access by the next Claude Code instance.