# Hockey Diagram Caching and Editing System - Technical Specification

## Overview

This specification outlines the next evolution of the hockey diagram generation system, building on the clean architecture implemented in Issue #97. The system will add intelligent caching with semantic search and interactive editing capabilities, transforming one-shot diagram generation into an iterative, collaborative process.

## System Architecture

### Core Components

1. **Semantic Cache Layer** - ChromaDB-based storage with embeddings for fuzzy matching
2. **Feedback Processing Agent** - LLM-powered interpretation of user editing requests
3. **Interactive Web UI** - Browser-based diagram review and editing interface
4. **Persistence Layer** - Dual storage (vector DB + filesystem) for reliability
5. **Enhanced MCP Tools** - Extended hockey diagram tools with caching support

## Technical Implementation

### 1. Cache Structure

```python
# Cached Spec Format (zone labels only - leverages clean architecture from Issue #97)
{
    "id": "wheel_breakout_v1",
    "title": "Wheel Breakout - Standard", 
    "description": "Defensive zone breakout with wheel behind net",
    "spec": {
        "players": [
            {"position": "D1", "zone": "behind_net", "team": "home", "has_puck": True},
            {"position": "RW", "zone": "right_half_wall", "team": "home"},
            {"position": "LW", "zone": "left_point", "team": "home"}
        ],
        "movements": [...],
        "view": "defensive"
    },
    "metadata": {
        "created": "2025-01-07",
        "usage_count": 15,
        "tags": ["breakout", "defensive", "wheel"],
        "embedding": [0.1, 0.2, ...], # For semantic search
        "variations": ["wheel_breakout_reverse", "wheel_breakout_stretch"]
    }
}
```

### 2. Semantic Search Implementation

```python
class DiagramSpecCache:
    def __init__(self):
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection("diagram_specs")
    
    async def semantic_search(self, query: str, n_results: int = 5):
        """Search for similar cached specs using embeddings"""
        embedding = await self.embed_query(query)
        
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=['metadatas', 'documents', 'distances']
        )
        
        return [
            {
                "id": result['id'],
                "title": result['metadata']['title'],
                "similarity": 1 - result['distance'],
                "description": result['metadata']['description'],
                "usage_count": result['metadata']['usage_count']
            }
            for result in results
        ]
```

### 3. Enhanced Agent Flow

```python
async def generate_diagram_with_cache(user_request: str, conversation_id: str = None):
    """Main entry point with caching and editing support"""
    
    # Step 1: Semantic cache search
    cache_results = await spec_cache.semantic_search(user_request)
    
    if cache_results and cache_results[0]['similarity'] > 0.8:
        # Present cache options to user
        return {
            "type": "cache_results", 
            "matches": cache_results,
            "message": "Found similar diagrams. Choose one or generate new:",
            "options": ["use_cached", "generate_new"]
        }
    
    # No good match, generate new using existing clean architecture
    spec_result = await parse_hockey_formation_core(user_request)
    diagram_result = await generate_diagram_from_spec_core(spec_result['parsed_data'])
    
    return {
        "type": "new_diagram",
        "spec": spec_result['parsed_data'],  # Zone labels only
        "diagram_path": diagram_result['diagram_path'],
        "spec_id": None  # Not saved yet
    }
```

### 4. Feedback Processing Agent

```python
class FeedbackProcessingAgent:
    async def process_feedback(self, current_spec: dict, feedback: str) -> dict:
        """Interpret feedback and modify spec accordingly"""
        
        prompt = f"""
        Current hockey diagram spec:
        {json.dumps(current_spec, indent=2)}
        
        User feedback: "{feedback}"
        
        Modify the spec based on feedback. Only change zone assignments,
        positions, or add/remove players. Return updated spec.
        
        Available zones: slot, high_slot, left_corner, right_corner, left_point,
        right_point, left_half_wall, right_half_wall, behind_net, etc.
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        modified_spec = self.extract_json(response.choices[0].message.content)
        return self.validate_spec(modified_spec)
```

## User Experience Flow

### Complete User Journey

1. **Initial Request**: User asks for "wheel breakout"

2. **Cache Search**: Agent searches semantically for similar cached specs
   - Found 3 matches with similarities: 0.92, 0.87, 0.81
   - Present options: "Use cached", "Generate new", or "Browse library"

3. **Spec Generation**: If no cache hit or user chooses "Generate new"
   - Uses existing clean architecture: research → parse → generate
   - LLM classification outputs zone labels only
   - Programmatic conversion generates coordinates and diagram

4. **Interactive Review**: Web interface displays:
   - Generated diagram image
   - Editable spec showing player positions in user-friendly format
   - Feedback text area for natural language changes

5. **Iterative Editing**: 
   - User: "Move left wing from point to slot"
   - Agent processes feedback, modifies spec (zone labels only)
   - System regenerates diagram with updated coordinates
   - User reviews updated version

6. **Save & Reuse**:
   - User satisfied: "Save to library" 
   - Spec stored with metadata, tags, and embeddings
   - Next user requesting similar gets instant cache hit

### Web UI Components

```html
<div class="diagram-review">
    <div class="diagram-display">
        <img src="/diagram/path" alt="Hockey Diagram" />
    </div>
    
    <div class="spec-editor">
        <h3>Player Positions</h3>
        <div class="player-grid">
            <div class="player">
                <span>F1 (Center):</span>
                <select class="zone-selector">
                    <option selected>high_slot</option>
                    <option>low_slot</option>
                    <option>left_circle</option>
                </select>
            </div>
            <!-- Repeat for each player -->
        </div>
        
        <div class="feedback-area">
            <textarea placeholder="Describe changes (e.g., 'move left wing to slot')"></textarea>
            <button onclick="processFeedback()">Update Diagram</button>
        </div>
    </div>
    
    <div class="actions">
        <button onclick="saveSpec()">Save to Library</button>
        <button onclick="downloadDiagram()">Download Image</button>
        <button onclick="shareSpec()">Share Spec</button>
    </div>
</div>
```

## MCP Tool Extensions

### New Tools

```python
@mcp.tool()
async def generate_diagram_with_cache_support(
    request: str,
    use_cached_spec: Optional[str] = None,
    feedback: Optional[str] = None,
    conversation_id: Optional[str] = None
) -> str:
    """Enhanced diagram generation with caching and editing"""

@mcp.tool()
async def search_cached_specs(query: str, limit: int = 5) -> str:
    """Semantic search of cached diagram specs"""

@mcp.tool()
async def save_diagram_spec(spec: dict, title: str, tags: list) -> str:
    """Save current spec to cache library"""

@mcp.tool()
async def get_spec_variations(base_spec_id: str) -> str:
    """Get variations of a cached spec"""

@mcp.tool()
async def process_spec_feedback(spec: dict, feedback: str) -> str:
    """Process natural language feedback to modify spec"""
```

## Data Storage

### ChromaDB Collections

- **`diagram_specs`**: Core spec storage with embeddings
- **`spec_variations`**: Tracks relationships between similar specs  
- **`usage_analytics`**: Track popularity and success metrics

### File System Structure

```
cached_specs/
├── specs/
│   ├── wheel_breakout_v1.json
│   ├── powerplay_umbrella_v2.json
│   └── ...
├── images/
│   ├── wheel_breakout_v1.png
│   └── ...
└── metadata/
    ├── tags.json
    ├── analytics.json
    └── relationships.json
```

## Benefits & Impact

### Performance Benefits
- **90% faster diagram generation** for cached specs
- **Reduced API costs** by reusing expensive research/parsing
- **Improved accuracy** through community-validated specs

### User Experience Benefits
- **Interactive editing** with visual feedback
- **Progressive refinement** instead of starting over
- **Library building** creates shared knowledge base
- **Natural language feedback** - no technical knowledge required

### System Benefits
- **Scalable architecture** that improves over time  
- **Clean separation** leverages Issue #97 foundation
- **Extensible design** supports future enhancements
- **Community-driven** spec library grows organically

## Implementation Phases

### Phase 1: Core Caching (Week 1-2)
- Set up ChromaDB collection
- Implement semantic search
- Create basic cache persistence
- Add cache-aware MCP tools

### Phase 2: Web Interface (Week 3-4)  
- Build diagram review UI
- Add spec editing interface
- Implement feedback processing
- Create save/download functionality

### Phase 3: Advanced Features (Week 5-6)
- Spec variations tracking
- Usage analytics
- Batch operations
- Export/import capabilities

### Phase 4: Polish & Scale (Week 7-8)
- Performance optimization
- Advanced search filters
- Community features
- Documentation and tutorials

## Dependencies

### Technical Requirements
- **ChromaDB**: Vector storage and semantic search
- **OpenAI Embeddings**: For query vectorization  
- **Enhanced Web UI**: React/Next.js components
- **Feedback Agent**: GPT-4 for natural language processing

### Builds On
- **Issue #97 Clean Architecture**: Zone-label specs enable easy caching/editing
- **Existing MCP Tools**: hockey_tactics search, formation research
- **Current Web App**: Next.js foundation for UI extensions

## Success Metrics

- **Cache Hit Rate**: >70% of requests served from cache after 1 month
- **User Engagement**: Average 3+ iterations per diagram session  
- **Library Growth**: 100+ validated specs after 3 months
- **Performance**: <2 second response time for cached specs
- **User Satisfaction**: Positive feedback on editing experience

---

This specification transforms hockey diagram generation from a one-shot process into an intelligent, collaborative system that learns and improves over time while maintaining the clean architectural principles established in Issue #97.