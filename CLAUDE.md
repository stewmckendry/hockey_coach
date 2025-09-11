# CLAUDE.md - Thunder Playbook Project

## 🔧 Environment Setup (CRITICAL)
```bash
# ALWAYS activate virtual environment first:
cd .. && source spacy_env/bin/activate && cd thunder_playbook
```

## 🏒 Project Overview
Hockey Coach AI Assistant platform using MCP servers, ChromaDB, and Next.js.

### Core Services
- **MCP Server** (`services/hockey_kb_mcp.py`): Port 8000
- **Hockey Diagram MCP** (`services/hockey_diagram/`): Programmatic tactical diagrams
- **Direct API** (`services/hockey_mcp_direct_api.py`): Port 3003
- **Web App** (`apps/web/`): Next.js, Port 3000
- **ChromaDB**: 8 hockey knowledge collections

### Quick Start
```bash
# Start all services
python start_services.py

# Or individually:
python services/hockey_kb_mcp.py &
python services/hockey_mcp_direct_api.py &
cd apps/web && npm run dev
```

## 📁 Key Locations
- Virtual env: `../spacy_env`
- Data models: `shared/models/`
- Hockey data: `data/loaders/chroma_load/`
- Diagrams: `services/hockey_diagram/`
- Web app: `apps/web/`

## 🧪 Testing
```bash
# Python tests
python -m pytest tests/ -v

# Web app
cd apps/web
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
- **Reorganized**: Project structure for clarity
- **Services**: `services/` for backend services
- **Apps**: `apps/` for frontend applications
- **Shared**: `shared/` for common code