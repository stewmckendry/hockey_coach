# Hockey Diagram Caching System

## Overview
The Hockey Diagram Caching System provides semantic caching and retrieval of hockey tactical diagram specifications using ChromaDB. This system enables reuse of validated diagrams, reduces generation time for similar queries, and builds a library of hockey formations and plays.

## Architecture

### Core Components

1. **DiagramCacheManager** (`diagram_cache.py`)
   - Manages ChromaDB collection for diagram specs
   - Provides semantic search using OpenAI embeddings
   - Tracks usage statistics and validation status

2. **MCP Tools** (in `server.py`)
   - `save_diagram_to_cache`: Save diagram specs with metadata
   - `search_cached_diagrams`: Semantic similarity search
   - `get_cached_diagram`: Retrieve specific diagram with optional regeneration
   - `update_cached_diagram`: Update specs or metadata
   - `delete_cached_diagram`: Remove from cache
   - `get_cache_statistics`: Usage analytics

3. **Web API** (`web_app/app/api/hockey-diagram/cache/route.ts`)
   - REST API wrapper for MCP tools
   - Supports both GET and POST methods
   - Handles all cache operations

4. **Web UI** (`web_app/app/hockey-diagram-test/page.tsx`)
   - Save button for generated diagrams
   - Library view with search and load functionality
   - Visual indicators for validation and usage

## Features

### Semantic Search
- Uses OpenAI embeddings for similarity matching
- Configurable similarity threshold (0-1)
- Returns similarity scores for ranking

### Metadata Tracking
- Parser type (two_stage, enhanced, basic)
- Usage count and last used timestamp
- Validation status
- Custom tags for categorization
- Author attribution

### Performance Optimization
- Stores only specs, not images (regenerate on demand)
- Automatic usage tracking for popular diagrams
- <2 second response time for cached diagrams

## Usage

### Via MCP Tools (Claude Code, CLI)

```python
# Save a diagram
mcp__hockey-diagram__save_diagram_to_cache(
    prompt="2-1-2 forecheck",
    spec={...},
    parser_type="two_stage",
    tags=["forecheck", "defensive"],
    author="coach_smith"
)

# Search for similar diagrams
mcp__hockey-diagram__search_cached_diagrams(
    query="power play formation",
    limit=10,
    min_similarity=0.7
)

# Get and regenerate a diagram
mcp__hockey-diagram__get_cached_diagram(
    diagram_id="diagram_abc123",
    regenerate=True
)
```

### Via Web Interface

1. Generate a diagram using the test interface
2. Click "Save" button to cache the diagram
3. Click "Library" to browse saved diagrams
4. Click any diagram in library to load and regenerate

### Via API

```javascript
// Save diagram
fetch('/api/hockey-diagram/cache', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'save',
    data: {
      prompt: '2-1-2 forecheck',
      spec: diagramSpec,
      parserType: 'two_stage',
      tags: ['forecheck'],
      author: 'web-user'
    }
  })
})

// Search diagrams
fetch('/api/hockey-diagram/cache?action=search&query=power+play&limit=10')

// Get specific diagram
fetch('/api/hockey-diagram/cache?action=get&id=diagram_abc123&regenerate=true')
```

## Storage Structure

### ChromaDB Collection
- **Name**: `hockey_diagram_specs`
- **Documents**: Original prompts (searchable text)
- **Metadata**: JSON containing:
  - `spec`: Full diagram specification
  - `prompt`: Original prompt text
  - `parser_type`: Parser used
  - `created_at`: ISO timestamp
  - `usage_count`: Number of retrievals
  - `validated`: Boolean flag
  - `tags`: Array of strings
  - `author`: Creator identifier

## Testing

### Unit Tests
```bash
python test_cache_tools.py
```

### Integration Tests
```bash
python test_integration_cache.py
```

### Manual Testing
1. Start the MCP server: `python server.py`
2. Start the web app: `cd web_app && npm run dev`
3. Navigate to http://localhost:3000/hockey-diagram-test
4. Generate, save, and retrieve diagrams

## Performance Metrics

### Target Goals (from Issue #101)
- >70% cache hit rate after 1 month
- 100+ validated specs in 3 months
- <2 second cached diagram response
- 3+ iterations per user session

### Current Performance
- Semantic search: ~500ms
- Diagram regeneration: ~1000ms
- Total cached response: <2 seconds
- Storage: ~2KB per diagram spec

## Future Enhancements

### Phase 3 - Advanced Features (Pending)
- Spec variations tracking
- Community sharing features
- Advanced filtering and search
- Bulk operations

### Phase 4 - Optimization (Pending)
- Performance monitoring dashboard
- Cache warming strategies
- Distributed caching support

## Dependencies

- ChromaDB: Vector database for semantic search
- OpenAI API: Embeddings for similarity matching
- FastMCP: MCP server framework
- Next.js: Web application framework

## Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_api_key

# Optional (defaults shown)
CHROMA_HOST=localhost
CHROMA_PORT=8000
HOCKEY_DIAGRAM_MCP_URL=http://localhost:8001
```

## Troubleshooting

### Common Issues

1. **ChromaDB Connection Failed**
   - Ensure ChromaDB server is running: `chroma run --host localhost --port 8000`
   - Check firewall/network settings

2. **No Embeddings Available**
   - Verify OPENAI_API_KEY is set
   - Falls back to default embeddings if API key missing

3. **Cache Not Persisting**
   - Check write permissions for `./chroma_diagram_cache`
   - Verify ChromaDB persistence settings

4. **Poor Search Results**
   - Adjust `min_similarity` threshold (lower = more results)
   - Use more specific search queries
   - Ensure diagrams have descriptive prompts

## Contributing

When adding new features:
1. Update MCP tools in `server.py`
2. Add corresponding API routes
3. Update UI components as needed
4. Add tests for new functionality
5. Update this documentation