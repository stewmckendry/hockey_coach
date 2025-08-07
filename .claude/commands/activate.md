# /activate

## Purpose
Set up persistent virtual environment activation and optionally start hockey servers from the main thunder_playbook repository.

## Arguments
- `[server-type]` (optional) - Specify which servers to activate:
  - `diagram` or `d` - Start hockey diagram API + web testing console (ports 8001, 3000)
  - `coaching` or `c` - Start hockey coaching/IQ servers (ports 8000, 3003, 3000)
  - `all` or `a` - Start all servers
  - (no argument) - Only verify virtual environment without starting servers

## Implementation

The challenge: Each bash command in Claude Code runs in a separate shell session, so `source activate` doesn't persist.

**Solution**: Always prefix Python commands with the full virtual environment path, and optionally start servers from the main repo.

```bash
#!/bin/bash

# Parse arguments
SERVER_TYPE="${1:-none}"
MAIN_REPO="/Users/liammckendry/thunder_playbook"

echo "🐍 Setting up spacy_env virtual environment for Claude Code..."

# Check if virtual environment exists
if [ ! -f "/Users/liammckendry/spacy_env/bin/activate" ]; then
    echo "❌ ERROR: Virtual environment not found at /Users/liammckendry/spacy_env/"
    echo "Please check that the path is correct."
    exit 1
fi

# Test virtual environment
echo "📋 Testing virtual environment..."
/Users/liammckendry/spacy_env/bin/python --version
echo "📍 Virtual environment location: /Users/liammckendry/spacy_env/"
echo "🐍 Python executable: /Users/liammckendry/spacy_env/bin/python"
echo "🏠 Main repository: $MAIN_REPO"

# Check for key packages
echo ""
echo "📋 Checking key dependencies..."
/Users/liammckendry/spacy_env/bin/python -c "
import sys
packages = ['fastmcp', 'openai', 'chromadb', 'numpy', 'spacy']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}: Available')
    except ImportError:
        print(f'❌ {pkg}: Not found')
"

echo ""
echo "✅ Virtual environment verified!"

# Handle server activation based on argument
case "$SERVER_TYPE" in
    diagram|d)
        echo ""
        echo "🎯 Starting Hockey Diagram Services..."
        cd "$MAIN_REPO"
        
        # Note: server.py uses stdio transport for MCP, not HTTP
        # The HTTP API is provided by hockey_diagram_direct_api.py
        source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_diagram_mcp/hockey_diagram_direct_api.py &
        echo "✅ Hockey Diagram Direct API started on port 8001"
        
        # Start Next.js Web App for diagram testing console
        cd "$MAIN_REPO/web_app"
        npm run dev &
        echo "✅ Next.js Web App started on port 3000"
        
        echo ""
        echo "📝 Test endpoints:"
        echo "   - Diagram API: curl http://localhost:8001/health"
        echo "   - Testing Console: http://localhost:3000/hockey-diagram-test"
        echo "   - Monitor Dashboard: http://localhost:3000/hockey-diagram-test/monitor"
        ;;
    
    coaching|c)
        echo ""
        echo "🏒 Starting Hockey Coaching/IQ Servers..."
        cd "$MAIN_REPO"
        
        # Start Hockey MCP Server
        source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_mcp.py &
        echo "✅ Hockey MCP Server started on port 8000"
        
        # Start Direct API Server
        source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_mcp_direct_api.py &
        echo "✅ Hockey Direct API Server started on port 3003"
        
        # Start Next.js Web App
        cd "$MAIN_REPO/web_app"
        npm run dev &
        echo "✅ Next.js Web App started on port 3000"
        
        echo ""
        echo "📝 Test endpoints:"
        echo "   - MCP Server: curl http://localhost:8000/health"
        echo "   - Direct API: curl http://localhost:3003/api/mcp"
        echo "   - Web App: http://localhost:3000"
        ;;
    
    all|a)
        echo ""
        echo "🚀 Starting ALL Hockey Servers..."
        cd "$MAIN_REPO"
        
        # Start Hockey Diagram Direct API
        source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_diagram_mcp/hockey_diagram_direct_api.py &
        echo "✅ Hockey Diagram Direct API started on port 8001"
        
        # Start Hockey MCP Server
        source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_mcp.py &
        echo "✅ Hockey MCP Server started on port 8000"
        
        # Start Direct API Server
        source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_mcp_direct_api.py &
        echo "✅ Hockey Direct API Server started on port 3003"
        
        # Start Next.js Web App
        cd "$MAIN_REPO/web_app"
        npm run dev &
        echo "✅ Next.js Web App started on port 3000"
        
        echo ""
        echo "📝 All servers running:"
        echo "   - Diagram MCP: http://localhost:8001"
        echo "   - Coaching MCP: http://localhost:8000"
        echo "   - Direct API: http://localhost:3003"
        echo "   - Web App: http://localhost:3000"
        ;;
    
    none)
        echo ""
        echo "📝 IMPORTANT: For subsequent bash commands in this Claude Code session:"
        echo "   Use: /Users/liammckendry/spacy_env/bin/python instead of just 'python'"
        echo "   Use: /Users/liammckendry/spacy_env/bin/pip instead of just 'pip'"
        echo ""
        echo "💡 Better solution: Use the compound activation pattern:"
        echo "   source /Users/liammckendry/spacy_env/bin/activate && python your_script.py"
        echo ""
        echo "🔧 Best practice examples:"
        echo "   source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_mcp.py"
        echo "   source /Users/liammckendry/spacy_env/bin/activate && python -m pytest tests/"
        echo "   source /Users/liammckendry/spacy_env/bin/activate && pip install package_name"
        ;;
    
    *)
        echo "❌ Unknown server type: $SERVER_TYPE"
        echo "Valid options: diagram|d, coaching|c, all|a, or no argument for env only"
        exit 1
        ;;
esac

# Always show process management tips
echo ""
echo "💡 Process Management Tips:"
echo "   - View running processes: ps aux | grep python"
echo "   - Kill a process: kill -9 <PID>"
echo "   - Kill all Python processes: pkill -f python"
echo "   - View port usage: lsof -i :8000"
```

## Usage Examples

```bash
# 1. Only verify virtual environment (no servers)
/activate

# 2. Start Hockey Diagram API + Testing Console
/activate diagram
# or shorthand:
/activate d
# Access testing console at: http://localhost:3000/hockey-diagram-test

# 3. Start Hockey Coaching/IQ servers (MCP, API, Web)
/activate coaching
# or shorthand:
/activate c

# 4. Start ALL servers (Diagram + Coaching/IQ)
/activate all
# or shorthand:
/activate a

# After activation, use these patterns for manual commands:

# Method 1: Compound activation (recommended)
source /Users/liammckendry/spacy_env/bin/activate && python servers/hockey_mcp.py
source /Users/liammckendry/spacy_env/bin/activate && python -m pytest tests/
source /Users/liammckendry/spacy_env/bin/activate && pip install new_package

# Method 2: Direct path (alternative)
/Users/liammckendry/spacy_env/bin/python servers/hockey_mcp.py
/Users/liammckendry/spacy_env/bin/python -m pytest tests/
/Users/liammckendry/spacy_env/bin/pip install new_package

# Check server status
curl http://localhost:8001/health  # Diagram API
curl http://localhost:8000/health  # Coaching MCP
curl http://localhost:3003/api/mcp # Coaching API
curl http://localhost:3000         # Web App

# Stop servers
pkill -f "hockey_diagram_direct_api.py"  # Stop diagram API
pkill -f "hockey_mcp.py"                 # Stop coaching MCP
pkill -f "hockey_mcp_direct_api.py"      # Stop coaching API
pkill -f "next dev"                      # Stop Next.js
```

## Expected Output

### Environment Only (`/activate`)
```
🐍 Setting up spacy_env virtual environment for Claude Code...
📋 Testing virtual environment...
Python 3.x.x
📍 Virtual environment location: /Users/liammckendry/spacy_env/
🐍 Python executable: /Users/liammckendry/spacy_env/bin/python
🏠 Main repository: /Users/liammckendry/thunder_playbook

📋 Checking key dependencies...
✅ fastmcp: Available
✅ openai: Available
✅ chromadb: Available
✅ numpy: Available
✅ spacy: Available

✅ Virtual environment verified!

📝 IMPORTANT: For subsequent bash commands...
[usage instructions]

💡 Process Management Tips...
```

### Diagram Server (`/activate diagram`)
```
[environment verification output...]

🎯 Starting Hockey Diagram Services...
✅ Hockey Diagram Direct API started on port 8001
✅ Next.js Web App started on port 3000

📝 Test endpoints:
   - Diagram API: curl http://localhost:8001/health
   - Testing Console: http://localhost:3000/hockey-diagram-test
   - Monitor Dashboard: http://localhost:3000/hockey-diagram-test/monitor

💡 Process Management Tips...
```

### Coaching Servers (`/activate coaching`)
```
[environment verification output...]

🏒 Starting Hockey Coaching/IQ Servers...
✅ Hockey MCP Server started on port 8000
✅ Hockey Direct API Server started on port 3003
✅ Next.js Web App started on port 3000

📝 Test endpoints:
   - MCP Server: curl http://localhost:8000/health
   - Direct API: curl http://localhost:3003/api/mcp
   - Web App: http://localhost:3000

💡 Process Management Tips...
```

### All Servers (`/activate all`)
```
[environment verification output...]

🚀 Starting ALL Hockey Servers...
✅ Hockey Diagram Direct API started on port 8001
✅ Hockey MCP Server started on port 8000
✅ Hockey Direct API Server started on port 3003
✅ Next.js Web App started on port 3000

📝 All servers running:
   - Diagram API: http://localhost:8001
   - Coaching MCP: http://localhost:8000
   - Coaching API: http://localhost:3003
   - Web App: http://localhost:3000

💡 Process Management Tips...
```

## Notes

- **Key Insight**: Claude Code bash commands run in separate shell sessions, so `source activate` doesn't persist
- **Solution**: Use compound commands with `&&` to activate and run in the same shell session
- **Alternative**: Use full paths to the virtual environment Python/pip executables
- **Server Control**: Now supports starting specific servers from the main thunder_playbook repository
- **Port Allocation**:
  - Port 8000: Hockey MCP Server (coaching - stdio/HTTP dual mode)
  - Port 8001: Hockey Diagram Direct API (HTTP API for diagram generation)
  - Port 3003: Hockey Coaching Direct API (HTTP proxy for MCP)
  - Port 3000: Next.js Web App
- **Background Processes**: All servers start in background mode (`&`) allowing concurrent execution
- **Main Repo Path**: Always runs from `/Users/liammckendry/thunder_playbook` (not worktrees)
- The compound activation pattern is recommended for manual commands

## Related Commands

- `/hockey-setup` - Complete development environment setup (includes this activation)
- `/commit-prep` - Pre-commit checks (requires activated environment)
- `/mcp-test` - MCP server testing (requires activated environment)