# Commit Prep Command

Pre-commit checklist to ensure code quality and functionality before git commits.

## Code Quality Checks

### Web App
```bash
cd web_app

# Install dependencies if needed
npm install

# ESLint - Check for code quality issues
npm run lint

# TypeScript - Check for type errors  
npm run type-check

# Production build test - Ensure no build errors
npm run build

# Return to root
cd ..
```

### Python Components
```bash
# Activate environment
source ../spacy_env/bin/activate

# Run relevant tests
python -m pytest tests/test_fastmcp_client.py -v
python -m pytest tests/test_age_group.py -v

# Test POC components
cd servers/poc
python test_mcp_connection.py
python test_agent_cli.py
cd ../..
```

## Service Health Validation

```bash
# Check all services are running and healthy
curl http://localhost:8000/health      # MCP Server
curl http://localhost:8002             # Agent HTTP Server (if running)
curl http://localhost:3000             # Web App (if running)
curl http://localhost:3003/api/mcp     # Direct API (if running)
```

## Functional Testing

### Quick Integration Test
```bash
# Test complete pipeline if services running
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What are good U10 skating drills?"}' \
  http://localhost:3000/api/agent-test

# Expected: Hockey-specific response in ~5-15 seconds
```

### MCP Tool Validation
```bash
cd servers/poc
/Users/liammckendry/spacy_env/bin/python -c "
import asyncio
from poc_agents.web_native_mcp_agent import run_web_mcp_agent_with_logging

async def test():
    try:
        response = await run_web_mcp_agent_with_logging('Test commit validation')
        print('✅ MCP integration working')
        return True
    except Exception as e:
        print(f'❌ MCP integration error: {e}')
        return False

result = asyncio.run(test())
"
cd ../..
```

## Documentation Validation

### Check CLAUDE.md Updates
- [ ] New commands documented
- [ ] Environment setup current
- [ ] Testing instructions accurate
- [ ] File locations updated

### Check Project Documentation
- [ ] README.md reflects current state
- [ ] POC documentation updated if relevant
- [ ] Technical design docs current

## Git Status Review

```bash
# Review what will be committed
git status

# Review specific changes
git diff --staged

# Check for sensitive information
git diff --staged | grep -i -E "(api_key|password|secret|token)"
```

## Pre-Commit Checklist

- [ ] **Code Quality**: ESLint and TypeScript checks pass
- [ ] **Tests**: Relevant tests pass
- [ ] **Services**: Core services healthy
- [ ] **Integration**: Basic functionality works
- [ ] **Documentation**: Updated as needed
- [ ] **Security**: No sensitive data in commits
- [ ] **Commit Message**: Clear and descriptive

## Commit Message Format

Use this format for consistency:
```
<type>: <description>

- Specific change 1
- Specific change 2
- Specific change 3

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Post-Commit Actions

After successful commit:
```bash
# Optional: Push to remote (only if requested)
# git push origin <branch-name>

# Optional: Create pull request
# gh pr create --title "Description" --body "Details"
```

## Emergency Rollback

If issues discovered after commit:
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - USE CAREFULLY
git reset --hard HEAD~1
```

## Success Criteria
- ✅ All quality checks pass
- ✅ Core functionality verified
- ✅ Documentation current
- ✅ No sensitive data in commit
- ✅ Clear commit message
- ✅ Services remain operational post-commit