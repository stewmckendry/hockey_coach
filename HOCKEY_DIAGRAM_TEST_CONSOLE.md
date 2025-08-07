# Hockey Diagram Test Console

## Overview
Web-based testing interface for the AI-powered hockey diagram generation system. Provides real-time diagram generation, comprehensive feedback collection, and monitoring capabilities.

## Architecture

### Frontend (`/hockey-diagram-test`)
- **Testing Interface**: Enter prompts and generate diagrams
- **Feedback System**: Star ratings, categories, and detailed comments
- **Technical Details**: View parser specs and agent traces
- **Example Prompts**: Quick access to common formations

### Backend Integration
- **Primary**: Hockey Diagram Agent (port 8002) with intelligent capabilities
- **Fallback**: Direct MCP server (port 8001) for basic generation
- **Logging**: Comprehensive tracking of all generations and feedback

## Usage

### Starting Services
```bash
# Start all services including the diagram agent
python start_services.py

# Or manually start the agent server
cd .. && source spacy_env/bin/activate && cd thunder_playbook
python servers/hockey_diagram_agent_server.py
```

### Testing Workflow
1. Navigate to http://localhost:3000/hockey-diagram-test
2. Enter a hockey formation description
3. Click "Generate Diagram"
4. Review the generated diagram
5. Provide feedback using stars and categories
6. View technical details if needed

### Monitoring
Access the monitoring dashboard at http://localhost:3000/hockey-diagram-test/monitor to:
- View gallery of all generated diagrams
- Review feedback entries
- Analyze performance statistics
- Search and filter results

## Agent Capabilities

### Fast Path (Known Formations)
- Standard formations like "2-1-2 forecheck"
- Preset plays and systems
- ~10-15 seconds generation time

### Research Path (Unknown Concepts)
- Searches hockey tactics database
- Web search for international variations
- ~30-60 seconds generation time

### Iterative Refinement
- Maintains conversation context
- Can adjust previous diagrams
- Example: "Move F1 higher in the zone"

## API Endpoints

### Generation
```
POST /api/hockey-diagram/generate
Body: { "prompt": "2-1-2 forecheck" }
```

### Feedback
```
POST /api/hockey-diagram/feedback
Body: { 
  "logId": "hdt_123...",
  "rating": 5,
  "categories": ["Accuracy", "Clarity"],
  "comment": "Perfect representation"
}
```

### Monitoring
```
GET /api/hockey-diagram/monitor?action=recent
GET /api/hockey-diagram/monitor?action=stats
GET /api/hockey-diagram/monitor?action=search&query=forecheck
```

## Troubleshooting

### 404 Error
If you get a 404 when accessing the test console:
1. Restart the Next.js development server
2. Clear Next.js cache: `rm -rf web_app/.next`
3. Rebuild: `cd web_app && npm run dev`

### Agent Not Available
The system will automatically fall back to direct MCP if the agent is unavailable. To use agent features:
1. Ensure OPENAI_API_KEY is set
2. Start the agent server on port 8002
3. Check health: `curl http://localhost:8002/health`

### Slow Generation
- Fast path: 10-15 seconds (known formations)
- Research path: 30-60 seconds (unknown concepts)
- Timeout: 2 minutes maximum

## Data Collection

All interactions are logged for analysis:
- Generation requests and results
- Processing times and tool usage
- User feedback and ratings
- Error tracking and recovery

Logs are stored in: `web_app/logs/hockey-diagram-test/`