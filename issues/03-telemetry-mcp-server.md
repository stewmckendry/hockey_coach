# Issue 3: Telemetry MCP Server for Claude Code Analytics

## Overview
Implement a FastMCP server that provides Claude Code with tools to query, analyze, and retrieve telemetry data collected by the logging hook system. This server will enable Claude Code to access development workflow analytics and generate insights directly through conversational interface.

## Problem Statement
While the logging hook system captures comprehensive telemetry data, there's no easy way for Claude Code to access and analyze this data. Users need a seamless interface to query logs, retrieve metrics, and understand development patterns without manual log file analysis.

## Solution Approach
Create a FastMCP server integrated with the Thunder Playbook architecture that provides structured tools for telemetry data access, querying, and analysis. The server will offer both raw data access and computed analytics.

## Technical Requirements

### Core Functionality
- **FastMCP Integration**: Compatible with existing Thunder Playbook MCP architecture
- **Data Access Tools**: Query telemetry data by various criteria
- **Metrics Computation**: Calculate development workflow KPIs
- **Error Analysis**: Identify and analyze error patterns
- **Performance Analytics**: Tool usage and execution time analysis
- **Session Management**: Track and compare development sessions

### MCP Tools Specification

| Tool Name | Purpose | Input Parameters | Output Format |
|-----------|---------|------------------|---------------|
| `get_usage_metrics` | Tool usage statistics | time_range, tool_filter | Aggregated metrics JSON |
| `get_session_logs` | Session history data | session_id, date_range | Detailed session logs |
| `search_telemetry` | Query logs by criteria | query, filters, limit | Filtered log entries |
| `get_error_analysis` | Error patterns and trends | time_range, error_type | Error analysis report |
| `get_performance_metrics` | Performance analytics | metric_type, aggregation | Performance data |
| `get_workflow_insights` | Development patterns | analysis_type, period | Computed insights |

## Implementation Specifications

### File Structure
```
thunder_playbook/
├── servers/
│   └── telemetry_mcp_server.py      # Main MCP server
├── telemetry/
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── tools.py                 # MCP tool implementations
│   │   ├── analytics.py             # Analytics computation
│   │   ├── queries.py               # Data query logic
│   │   └── models.py                # Response models
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── log_reader.py            # Log file access
│   │   ├── indexer.py               # Search indexing
│   │   └── aggregator.py            # Metrics aggregation
│   └── config.py                    # Configuration
├── tests/
│   └── test_telemetry_mcp.py        # MCP server tests
└── docs/
    └── TELEMETRY_MCP_API.md         # API documentation
```

### 1. FastMCP Server Implementation
```python
# servers/telemetry_mcp_server.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from telemetry.mcp.tools import TelemetryTools
from telemetry.config import TelemetryConfig

# Initialize FastMCP server
mcp = FastMCP("Thunder Playbook Telemetry Server")

# Initialize telemetry tools
config = TelemetryConfig()
telemetry_tools = TelemetryTools(config)

@mcp.tool()
async def get_usage_metrics(
    time_range: str = "7d",
    tool_filter: Optional[str] = None,
    aggregation: str = "daily"
) -> Dict[str, Any]:
    """
    Get tool usage statistics and metrics.
    
    Args:
        time_range: Time period (1d, 7d, 30d, or YYYY-MM-DD to YYYY-MM-DD)
        tool_filter: Specific tool name or pattern to filter
        aggregation: Aggregation level (hourly, daily, weekly)
    
    Returns:
        Dict containing usage metrics, success rates, and performance data
    """
    try:
        return await telemetry_tools.get_usage_metrics(
            time_range=time_range,
            tool_filter=tool_filter,
            aggregation=aggregation
        )
    except Exception as e:
        logging.error(f"Error getting usage metrics: {e}")
        return {"error": str(e), "metrics": {}}

@mcp.tool()
async def get_session_logs(
    session_id: Optional[str] = None,
    date_range: str = "1d",
    limit: int = 100
) -> Dict[str, Any]:
    """
    Retrieve detailed session logs and events.
    
    Args:
        session_id: Specific session ID to retrieve
        date_range: Date range for session search
        limit: Maximum number of sessions to return
    
    Returns:
        Dict containing session data, events, and metadata
    """
    try:
        return await telemetry_tools.get_session_logs(
            session_id=session_id,
            date_range=date_range,
            limit=limit
        )
    except Exception as e:
        logging.error(f"Error getting session logs: {e}")
        return {"error": str(e), "sessions": []}

@mcp.tool()
async def search_telemetry(
    query: str,
    event_types: Optional[List[str]] = None,
    time_range: str = "7d",
    limit: int = 50
) -> Dict[str, Any]:
    """
    Search telemetry logs by text query and filters.
    
    Args:
        query: Search query (tool names, error messages, file paths)
        event_types: Filter by event types (SessionStart, ToolUse, etc.)
        time_range: Time period to search within
        limit: Maximum results to return
    
    Returns:
        Dict containing matching log entries and search metadata
    """
    try:
        return await telemetry_tools.search_telemetry(
            query=query,
            event_types=event_types,
            time_range=time_range,
            limit=limit
        )
    except Exception as e:
        logging.error(f"Error searching telemetry: {e}")
        return {"error": str(e), "results": []}

@mcp.tool()
async def get_error_analysis(
    time_range: str = "7d",
    error_type: Optional[str] = None,
    group_by: str = "tool"
) -> Dict[str, Any]:
    """
    Analyze error patterns and failure trends.
    
    Args:
        time_range: Time period for error analysis
        error_type: Specific error type to analyze
        group_by: Group errors by tool, session, or time
    
    Returns:
        Dict containing error analysis, patterns, and recommendations
    """
    try:
        return await telemetry_tools.get_error_analysis(
            time_range=time_range,
            error_type=error_type,
            group_by=group_by
        )
    except Exception as e:
        logging.error(f"Error analyzing errors: {e}")
        return {"error": str(e), "analysis": {}}

@mcp.tool()
async def get_performance_metrics(
    metric_type: str = "tool_duration",
    time_range: str = "7d",
    percentiles: List[int] = [50, 90, 95, 99]
) -> Dict[str, Any]:
    """
    Get performance metrics and timing analysis.
    
    Args:
        metric_type: Type of metric (tool_duration, session_length, etc.)
        time_range: Time period for analysis
        percentiles: Percentile values to calculate
    
    Returns:
        Dict containing performance metrics and statistical analysis
    """
    try:
        return await telemetry_tools.get_performance_metrics(
            metric_type=metric_type,
            time_range=time_range,
            percentiles=percentiles
        )
    except Exception as e:
        logging.error(f"Error getting performance metrics: {e}")
        return {"error": str(e), "metrics": {}}

@mcp.tool()
async def get_workflow_insights(
    analysis_type: str = "productivity",
    time_period: str = "7d",
    comparison_period: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate workflow insights and optimization recommendations.
    
    Args:
        analysis_type: Type of analysis (productivity, efficiency, patterns)
        time_period: Period to analyze
        comparison_period: Period to compare against (optional)
    
    Returns:
        Dict containing insights, trends, and actionable recommendations
    """
    try:
        return await telemetry_tools.get_workflow_insights(
            analysis_type=analysis_type,  
            time_period=time_period,
            comparison_period=comparison_period
        )
    except Exception as e:
        logging.error(f"Error generating workflow insights: {e}")
        return {"error": str(e), "insights": {}}

if __name__ == "__main__":
    # Start the MCP server
    asyncio.run(mcp.run(transport="stdio"))
```

### 2. Telemetry Tools Implementation
```python
# telemetry/mcp/tools.py
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..storage.log_reader import LogReader
from ..storage.aggregator import MetricsAggregator
from ..storage.indexer import SearchIndexer
from .analytics import WorkflowAnalytics

class TelemetryTools:
    def __init__(self, config):
        self.config = config
        self.log_reader = LogReader(config)
        self.aggregator = MetricsAggregator(config)
        self.indexer = SearchIndexer(config)
        self.analytics = WorkflowAnalytics(config)
        
    async def get_usage_metrics(
        self, 
        time_range: str,
        tool_filter: Optional[str],
        aggregation: str
    ) -> Dict[str, Any]:
        """Compute tool usage metrics"""
        
        # Parse time range
        start_date, end_date = self._parse_time_range(time_range)
        
        # Load relevant log data
        logs = await self.log_reader.get_tool_logs(
            start_date=start_date,
            end_date=end_date,
            tool_filter=tool_filter
        )
        
        # Aggregate metrics
        metrics = await self.aggregator.compute_usage_metrics(
            logs=logs,
            aggregation=aggregation
        )
        
        return {
            "time_range": f"{start_date} to {end_date}",
            "total_tools_used": len([log for log in logs if log.get("tool_name")]),
            "unique_tools": len(set(log.get("tool_name") for log in logs if log.get("tool_name"))),
            "success_rate": metrics.get("success_rate", 0),
            "average_duration_ms": metrics.get("avg_duration", 0),
            "tool_breakdown": metrics.get("tool_breakdown", {}),
            "usage_by_time": metrics.get("usage_by_time", {}),
            "performance_trends": metrics.get("performance_trends", {})
        }
    
    async def get_session_logs(
        self,
        session_id: Optional[str],
        date_range: str,
        limit: int
    ) -> Dict[str, Any]:
        """Retrieve session logs and events"""
        
        if session_id:
            # Get specific session
            session_data = await self.log_reader.get_session_by_id(session_id)
            sessions = [session_data] if session_data else []
        else:
            # Get sessions by date range
            start_date, end_date = self._parse_time_range(date_range)
            sessions = await self.log_reader.get_sessions_by_date(
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
        
        # Enrich session data with computed metrics
        enriched_sessions = []
        for session in sessions:
            enriched_session = await self._enrich_session_data(session)
            enriched_sessions.append(enriched_session)
        
        return {
            "total_sessions": len(enriched_sessions),
            "sessions": enriched_sessions,
            "summary": await self._compute_session_summary(enriched_sessions)
        }
    
    async def search_telemetry(
        self,
        query: str,
        event_types: Optional[List[str]],
        time_range: str,
        limit: int
    ) -> Dict[str, Any]:
        """Search telemetry logs"""
        
        start_date, end_date = self._parse_time_range(time_range)
        
        # Perform search using indexer
        results = await self.indexer.search(
            query=query,
            event_types=event_types,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return {
            "query": query,
            "total_results": len(results),
            "results": results,
            "search_time_ms": results.get("search_time_ms", 0),
            "filters_applied": {
                "event_types": event_types,
                "time_range": time_range
            }
        }
```

### 3. Analytics Engine
```python
# telemetry/mcp/analytics.py
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import statistics
from collections import defaultdict, Counter

class WorkflowAnalytics:
    def __init__(self, config):
        self.config = config
    
    async def analyze_productivity_trends(
        self,
        sessions: List[Dict[str, Any]],
        comparison_period: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Analyze productivity patterns and trends"""
        
        # Calculate key productivity metrics
        metrics = {
            "average_session_duration": self._calc_average_duration(sessions),
            "tools_per_session": self._calc_tools_per_session(sessions),
            "success_rate_trend": self._calc_success_rate_trend(sessions),
            "peak_productivity_hours": self._identify_peak_hours(sessions),
            "most_efficient_tools": self._identify_efficient_tools(sessions),
        }
        
        # Generate insights and recommendations
        insights = self._generate_productivity_insights(metrics, comparison_period)
        
        return {
            "analysis_type": "productivity",
            "metrics": metrics,
            "insights": insights,
            "recommendations": self._generate_recommendations(insights)
        }
    
    def _generate_productivity_insights(
        self,
        metrics: Dict[str, Any],
        comparison: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Generate actionable productivity insights"""
        
        insights = []
        
        # Session duration insights
        avg_duration = metrics["average_session_duration"]
        if avg_duration > 3600:  # > 1 hour
            insights.append({
                "type": "session_length",
                "severity": "medium",
                "title": "Long Development Sessions",
                "description": f"Average session length is {avg_duration/60:.1f} minutes. Consider breaking into shorter focused sessions.",
                "actionable": True
            })
        
        # Tool efficiency insights  
        efficient_tools = metrics["most_efficient_tools"]
        if efficient_tools:
            insights.append({
                "type": "tool_efficiency",
                "severity": "low",
                "title": "High-Efficiency Tools Identified",
                "description": f"Tools with best success/time ratio: {', '.join(efficient_tools[:3])}",
                "actionable": True
            })
        
        return insights
```

### 4. Data Storage and Indexing
```python
# telemetry/storage/log_reader.py
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class LogReader:
    def __init__(self, config):
        self.config = config
        self.logs_dir = Path(config.logs_dir)
    
    async def get_tool_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        tool_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Read tool usage logs within date range"""
        
        logs = []
        
        # Read from daily log files
        current_date = start_date.date()
        while current_date <= end_date.date():
            daily_file = self.logs_dir / f"daily_{current_date.strftime('%Y%m%d')}.jsonl"
            if daily_file.exists():
                async with asyncio.open(daily_file, 'r') as f:
                    async for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            
                            # Filter by tool if specified
                            if tool_filter and log_entry.get("tool_name") != tool_filter:
                                continue
                                
                            # Filter by date range
                            log_time = datetime.fromisoformat(log_entry["timestamp"])
                            if start_date <= log_time <= end_date:
                                logs.append(log_entry)
                                
                        except json.JSONDecodeError:
                            continue
            
            current_date += timedelta(days=1)
        
        return logs
```

## Integration with Thunder Playbook

### MCP Server Registration
Add to existing MCP server configuration:
```python
# servers/hockey_mcp.py - Add telemetry tools
from telemetry_mcp_server import mcp as telemetry_mcp

# Register telemetry tools with main hockey MCP server
hockey_mcp = FastMCP("Hockey Coaching Assistant")

# Import telemetry tools
@hockey_mcp.tool()
async def get_development_metrics(*args, **kwargs):
    return await telemetry_mcp.get_usage_metrics(*args, **kwargs)

# ... other integrations
```

### Service Startup Integration
```python
# start_services.py - Add telemetry MCP server
def start_telemetry_mcp_server():
    """Start the telemetry MCP server"""
    return subprocess.Popen([
        "python", "servers/telemetry_mcp_server.py"
    ], cwd=PROJECT_ROOT)

if __name__ == "__main__":
    services = [
        start_hockey_mcp_server(),
        start_direct_api_server(), 
        start_telemetry_mcp_server(),  # Add telemetry server
        start_web_app()
    ]
```

## Testing Strategy

### Unit Tests
- **Tool Functions**: Test each MCP tool with mock data
- **Data Processing**: Verify log parsing and aggregation logic
- **Analytics**: Test insight generation and metric calculations
- **Error Handling**: Test failure scenarios and recovery

### Integration Tests
- **MCP Protocol**: Test FastMCP server communication
- **Data Pipeline**: Test end-to-end data flow from logs to insights
- **Performance**: Test response times with large datasets
- **Cross-Session**: Test multi-session analysis capabilities

### Load Tests
- **Concurrent Queries**: Test multiple simultaneous telemetry requests
- **Large Datasets**: Test performance with extensive log history
- **Memory Usage**: Monitor memory consumption during analysis
- **Response Times**: Ensure sub-second response for typical queries

## Success Criteria
- ✅ All 6 MCP tools respond within 2 seconds for typical queries
- ✅ Successfully processes logs from all 8 hook events
- ✅ Generates meaningful insights with >90% accuracy
- ✅ Handles concurrent requests without performance degradation
- ✅ Integrates seamlessly with existing Thunder Playbook MCP architecture
- ✅ Provides actionable recommendations for workflow optimization

## Implementation Timeline
- **Day 1-2**: Core MCP server and basic tools implementation
- **Day 3-4**: Analytics engine and insight generation
- **Day 5-6**: Data storage optimization and indexing
- **Day 7-8**: Integration testing and performance optimization

## Dependencies
- **FastMCP**: Python FastMCP library for MCP server implementation
- **Telemetry Logs**: Data from logging hook system (Issue #2)
- **Python 3.8+**: For async/await and type hints
- **Thunder Playbook Environment**: Integration with existing MCP architecture

## Future Enhancements
- **Real-time Analytics**: Stream processing for live insights
- **Machine Learning**: Predictive analytics and anomaly detection
- **Custom Dashboards**: Web interface for visual analytics
- **Team Collaboration**: Multi-user analytics and benchmarking
- **Export Capabilities**: Integration with external analytics platforms