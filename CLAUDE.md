# CLAUDE.md - Thunder Playbook Project

## 🔧 Environment Setup (CRITICAL)
```bash
# ALWAYS activate virtual environment first:
cd .. && source spacy_env/bin/activate && cd thunder_playbook
```

## 🏒 Project Overview
Hockey Coach AI Assistant platform using MCP servers, ChromaDB, and Next.js.

### Core Services
- **MCP Server** (`servers/hockey_mcp.py`): Port 8000
- **Hockey Diagram MCP** (`servers/hockey_diagram_mcp/`): Programmatic tactical diagrams
- **Direct API** (`servers/hockey_mcp_direct_api.py`): Port 3003
- **Web App** (`web_app/`): Next.js, Port 3000
- **ChromaDB**: 8 hockey knowledge collections

### Quick Start
```bash
# Start all services
python start_services.py

# Or individually:
python servers/hockey_mcp.py &
python servers/hockey_mcp_direct_api.py &
cd web_app && npm run dev
```

## 📁 Key Locations
- Virtual env: `../spacy_env`
- Data models: `models/`
- Hockey data: `chroma_load/`
- Diagrams: `servers/hockey_diagram_mcp/`
- Web app: `web_app/`

## 🧪 Testing
```bash
# Python tests
python -m pytest tests/ -v

# Web app
cd web_app
npm run lint
npm run type-check
npm run build
```

## 🔍 Common Issues

### Import Errors
**Solution**: Activate virtual environment (see Environment Setup above)

### Port Already in Use
```bash
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it
```

### ChromaDB Connection Refused
```bash
chroma run --host localhost --port 8000 --no-auth &
```

## 💡 Development Tips
1. Use existing code patterns - check neighboring files first
2. Run tests before committing
3. Keep diagrams programmatic (not AI-generated)
4. Follow age-appropriate UX guidelines for hockey content

## 🚀 Custom Commands
- `/worktree-issue <url>` - Start work on GitHub issue
- `/commit-worktree <url>` - Create PR from worktree
- `/merge-worktree <url> <pr>` - Complete workflow

## 📝 Current Work Context
- **Worktree**: issue-109 (n8n workflow for hockey diagrams)
- **Focus**: Token optimization and MCP configuration
- **n8n Workflow ID**: NLSGnPWngNkvkxqs