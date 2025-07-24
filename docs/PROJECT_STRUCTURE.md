# 📁 Project Structure Documentation

## Overview
The Thunder Playbook project has been reorganized into logical folders for better maintainability and clarity.

## Directory Structure

```
thunder_playbook/
├── 📁 servers/                    # All MCP servers and API services
│   ├── hockey_mcp.py             # Main FastMCP hockey knowledge server (port 8000)
│   ├── hockey_mcp_direct_api.py  # Direct API wrapper for web app (port 3003)
│   ├── hockey_mcp_backup.py      # Backup/previous version of main server
│   ├── fastmcp_proxy.py          # FastMCP proxy server (alternative approach)
│   └── off_ice/                  # Off-ice training specific server modules
│
├── 🌐 web_app/                    # Next.js frontend application
│   ├── app/                      # Next.js 13+ app directory
│   ├── components/               # React components
│   ├── lib/                      # Client-side utilities and API clients
│   └── ...                       # Standard Next.js structure
│
├── 🧪 tests/                      # All test files and test data
│   ├── test_age_group.py         # Age group functionality tests
│   ├── test_fastmcp_client.py    # FastMCP client integration tests
│   ├── test_ltad_enrichment.py   # LTAD enrichment tests
│   ├── test_positions.py         # Position-related tests
│   ├── test_single_extraction.py # Single extraction tests
│   └── test_extraction_output.json # Test data and expected outputs
│
├── 📜 scripts/                    # Utility and processing scripts
│   ├── analyze_drills_metadata.py # Drill metadata analysis
│   ├── debug_html_extraction.py  # HTML extraction debugging
│   └── generate_image.py         # Image generation utilities
│
├── 📊 models/                     # Pydantic data models and schemas
│   ├── conduct.py                # Conduct-related models
│   ├── dryland_models.py         # Dryland training models
│   ├── ltad.py                   # Long-term athlete development models
│   └── ...                       # Other domain models
│
├── 🔧 utils/                      # Shared utility functions
│   ├── chroma_utils.py           # ChromaDB interaction utilities
│   ├── datetime_tools.py         # Date/time helper functions
│   └── ...                       # Other utility modules
│
├── 📸 image_gen/                  # AI image generation tools
│   ├── image_agent/              # Image generation agents
│   ├── inputs/                   # Input images and templates
│   ├── outputs/                  # Generated output images
│   └── prompts/                  # Image generation prompts
│
├── 📦 chroma_load/                # Data processing and vector DB
│   ├── raw/                      # Raw source data
│   ├── processed/                # Processed and enriched data
│   ├── indexed/                  # Indexed data for ChromaDB
│   ├── scripts/                  # Data processing scripts
│   └── prompts/                  # Processing prompts
│
├── 📖 docs/                       # Documentation files
│   └── Agents.md                 # Agent architecture documentation
│
├── 🚀 start_services.py           # Convenient startup script for all services
├── 📋 requirements.txt            # Python dependencies
├── 📦 pyproject.toml             # Poetry configuration
├── 🔒 uv.lock                    # UV lock file
├── 🔐 .env                       # Environment variables
└── 📖 README.md                  # Main project documentation
```

## Key Changes Made

### ✅ **Organized by Function**
- **servers/** - All backend services and APIs
- **tests/** - All testing-related files  
- **scripts/** - Utility scripts and tools
- **docs/** - Documentation files

### ✅ **Improved Developer Experience**
- **start_services.py** - Single command to start all services
- **Clear separation** - Frontend, backend, tests, and utilities
- **Logical grouping** - Related files are co-located

### ✅ **Maintained Functionality**
- All import paths updated correctly
- Services start and connect properly
- FastMCP integration still works
- Web app can still access the APIs

## Usage

### Starting the Application
```bash
# Quick start (recommended)
python start_services.py

# Manual start
python servers/hockey_mcp.py &
python servers/hockey_mcp_direct_api.py &
cd web_app && npm run dev
```

### Development Workflow
1. **Backend changes**: Edit files in `servers/`
2. **Frontend changes**: Edit files in `web_app/`
3. **Data processing**: Use scripts in `chroma_load/scripts/`
4. **Testing**: Run tests from `tests/`
5. **Utilities**: Add shared code to `utils/`

## Service Architecture

```
┌─────────────┐    HTTP     ┌──────────────────────┐    FastMCP     ┌─────────────────┐
│   Next.js   │ ────────────→ │ hockey_mcp_direct_api │ ──────────────→ │   hockey_mcp    │
│  Frontend   │             │    (Port 3003)       │  (in-memory)   │  (Port 8000)    │
│ (Port 3000) │             └──────────────────────┘                └─────────────────┘
└─────────────┘                        │                                      │
                                       │                                      │
                               ┌───────▼───────┐                    ┌─────────▼──────────┐
                               │  FastMCP      │                    │    ChromaDB        │
                               │  Client       │                    │ Vector Database    │
                               │ (in-memory)   │                    │ (Hockey Knowledge) │
                               └───────────────┘                    └────────────────────┘
```

This reorganization makes the project more maintainable, easier to navigate, and follows standard software engineering practices for project structure.
