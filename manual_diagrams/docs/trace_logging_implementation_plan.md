# Trace Logging Implementation Plan

## Current State
- `auto_trace_logger.py` exists with session management
- `initialize_diagram` returns a session_id
- `generate_diagram` references session data
- **MISSING**: Automatic logging of each tool call

## Required Implementation

### 1. Add session_id Parameter to All Tools
Every tool (except initialize_diagram) needs to accept optional session_id:

```python
@mcp.tool("search_diagram_node")
def search_diagram_node(node_type: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    # Log the tool call
    if session_id:
        log_tool_call(session_id, "search_diagram_node", {"node_type": node_type})
    
    # ... rest of function
```

### 2. Create Tool Call Logger Function
Add to hockey_diagram_mcp_v2.py:

```python
from auto_trace_logger import get_logger

def log_tool_call(session_id: str, tool_name: str, args: Dict[str, Any], result: Any = None):
    """Log a tool call to the session trace."""
    if not session_id:
        return
    
    logger = get_logger()
    logger.log_tool_call(
        session_id=session_id,
        tool_name=tool_name,
        args=args,
        result=result
    )
```

### 3. Add Decorator for Automatic Logging
Create a decorator to wrap all tools:

```python
def trace_tool(func):
    """Decorator to automatically log tool calls."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract session_id if present
        session_id = kwargs.get('session_id')
        tool_name = func.__name__
        
        # Log the call
        if session_id:
            logger = get_logger()
            logger.log_tool_call(
                session_id=session_id,
                tool_name=tool_name,
                args=kwargs,
                result=None  # Will be updated after
            )
        
        # Execute the tool
        result = func(*args, **kwargs)
        
        # Log the result
        if session_id:
            logger.update_last_result(session_id, result)
        
        return result
    return wrapper
```

### 4. Apply to All Tools
Apply decorator to each tool:

```python
@mcp.tool("search_diagram_node")
@trace_tool
def search_diagram_node(node_type: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    # Tool implementation
```

### 5. Return Trace File Path in generate_diagram
The generate_diagram tool should return the trace file path:

```python
def generate_diagram(spec: Dict[str, Any], output_name: Optional[str] = None, session_id: Optional[str] = None):
    # ... generate diagram ...
    
    # Get trace file path
    if session_id:
        logger = get_logger()
        trace_path = logger.get_session_file_path(session_id)
        
        return {
            "success": True,
            "image_path": str(svg_path),
            "spec_path": str(spec_path),
            "trace_path": str(trace_path),  # Add this
            "upload_instructions": "Use google-sheets tool to upload trace_path contents"
        }
```

## Files to Modify

1. **hockey_diagram_mcp_v2.py**:
   - Add session_id parameter to all 9 tools (except initialize)
   - Add trace_tool decorator
   - Apply decorator to all tools
   - Return trace_path in generate_diagram

2. **auto_trace_logger.py**:
   - Add get_logger() singleton function
   - Add get_session_file_path() method
   - Add update_last_result() method

3. **hockey-diagram-expert.md**:
   - Update instructions to pass session_id with every tool call
   - Add instruction to upload trace_path to Google Sheets

## Example Agent Usage

```python
# Step 1: Initialize and get session_id
result = initialize_diagram("2v1 rush drill")
session_id = result["session_id"]

# Step 2: All subsequent tools pass session_id
template = search_diagram_template("2v1 rush", session_id=session_id)
schema = search_diagram_node("players", session_id=session_id)
position = map_position_to_coordinates("left dot", "offensive", session_id=session_id)

# Step 3: Generate returns trace_path
result = generate_diagram(spec, session_id=session_id)
trace_path = result["trace_path"]

# Step 4: Upload trace to sheets
with open(trace_path) as f:
    trace_data = json.load(f)
google_sheets.update_cells(spreadsheet_id, "Traces", trace_data)
```

## Testing
1. Run a simple drill with session tracking
2. Verify trace file is created in trace_logs/
3. Check all tool calls are logged
4. Verify trace can be uploaded to Google Sheets