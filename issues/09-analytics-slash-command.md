# Issue 4: Analytics Slash Command for Development Workflow Insights

## Overview
Implement a custom slash command `/analyze-workflow` for Claude Code that leverages the telemetry MCP server to gather development data and generates AI-powered insights and optimization recommendations for improving development workflow efficiency.

## Problem Statement
While telemetry data is captured and accessible through MCP tools, users need a simple, conversational way to request workflow analysis and receive actionable insights. Manual querying of telemetry data and interpretation requires technical expertise and time.

## Solution Approach
Create a custom Claude Code slash command that automatically gathers relevant telemetry data, applies AI analysis using templated prompts, and presents comprehensive workflow insights with specific improvement recommendations.

## Technical Requirements

### Core Functionality
- **Slash Command Integration**: Register `/analyze-workflow` with Claude Code
- **Telemetry Data Collection**: Automatically query relevant metrics via MCP server
- **AI-Powered Analysis**: Use structured prompts for insight generation
- **Actionable Recommendations**: Provide specific, implementable suggestions
- **Customizable Analysis**: Support different analysis types and time periods
- **Progress Tracking**: Show data collection and analysis progress

### Command Syntax and Options
```bash
/analyze-workflow [type] [period] [options]

# Examples:
/analyze-workflow                           # Default: productivity analysis, 7 days
/analyze-workflow productivity 30d          # Productivity analysis, 30 days
/analyze-workflow efficiency 7d --compare-to=30d  # With comparison period
/analyze-workflow errors 24h               # Error pattern analysis
/analyze-workflow tools 7d --filter=Edit   # Tool-specific analysis
/analyze-workflow full 14d                 # Comprehensive analysis
```

### Analysis Types
| Type | Focus | Key Metrics | Output |
|------|-------|-------------|--------|
| `productivity` | Overall efficiency | Session duration, tool usage, success rates | Productivity insights and recommendations |
| `efficiency` | Speed and optimization | Tool performance, error rates, repetitive patterns | Efficiency improvement suggestions |
| `errors` | Error patterns | Failure analysis, error types, recovery patterns | Error prevention strategies |
| `tools` | Tool usage analysis | Tool frequency, success rates, performance | Tool optimization recommendations |
| `sessions` | Session patterns | Session characteristics, workflow patterns | Session management insights |
| `full` | Comprehensive analysis | All metrics combined | Complete workflow assessment |

## Implementation Specifications

### File Structure
```
thunder_playbook/
├── .claude/
│   ├── commands/
│   │   └── analyze-workflow.py         # Slash command implementation
│   └── settings.json                   # Command registration
├── telemetry/
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── prompts.py                  # Analysis prompt templates
│   │   ├── insights.py                 # Insight generation logic
│   │   └── recommendations.py          # Recommendation engine
│   └── visualization/
│       ├── __init__.py
│       ├── charts.py                   # Simple text-based charts
│       └── reports.py                  # Report formatting
├── docs/
│   └── ANALYTICS_COMMAND_GUIDE.md      # User guide
└── tests/
    └── test_analytics_command.py       # Command tests
```

### 1. Slash Command Registration
```json
// .claude/settings.json - Add command registration
{
  "commands": {
    "analyze-workflow": {
      "description": "Analyze development workflow and generate optimization insights",
      "script": ".claude/commands/analyze-workflow.py",
      "usage": "/analyze-workflow [type] [period] [options]"
    }
  }
}
```

### 2. Main Command Implementation
```python
#!/usr/bin/env python3
# .claude/commands/analyze-workflow.py

import sys
import asyncio
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from telemetry.analysis.insights import WorkflowAnalyzer
from telemetry.analysis.prompts import AnalysisPrompts
from telemetry.mcp.tools import TelemetryTools
from telemetry.config import TelemetryConfig

class AnalyzeWorkflowCommand:
    def __init__(self):
        self.config = TelemetryConfig()
        self.telemetry_tools = TelemetryTools(self.config)
        self.analyzer = WorkflowAnalyzer(self.config)
        self.prompts = AnalysisPrompts()
    
    async def execute(self, args: List[str]) -> str:
        """Main command execution"""
        
        # Parse command arguments
        parsed_args = self._parse_arguments(args)
        
        # Show progress indicator
        print("🔍 Analyzing development workflow...")
        print(f"📊 Analysis type: {parsed_args.type}")
        print(f"📅 Time period: {parsed_args.period}")
        print()
        
        try:
            # Step 1: Collect telemetry data
            print("📈 Collecting telemetry data...")
            telemetry_data = await self._collect_telemetry_data(parsed_args)
            
            if not telemetry_data or self._is_insufficient_data(telemetry_data):
                return self._format_insufficient_data_response(parsed_args)
            
            # Step 2: Generate AI analysis
            print("🤖 Generating AI-powered insights...")
            analysis_prompt = self._build_analysis_prompt(parsed_args, telemetry_data)
            
            # Step 3: Format and return results
            print("📋 Formatting results...")
            return self._format_analysis_results(
                analysis_type=parsed_args.type,
                period=parsed_args.period,
                telemetry_data=telemetry_data,
                analysis_prompt=analysis_prompt
            )
            
        except Exception as e:
            return self._format_error_response(str(e))
    
    async def _collect_telemetry_data(self, args) -> Dict[str, Any]:
        """Collect relevant telemetry data based on analysis type"""
        
        data = {}
        
        # Always collect basic usage metrics
        data["usage_metrics"] = await self.telemetry_tools.get_usage_metrics(
            time_range=args.period,
            tool_filter=args.filter if hasattr(args, 'filter') else None,
            aggregation="daily"
        )
        
        # Collect additional data based on analysis type
        if args.type in ["productivity", "full"]:
            data["session_logs"] = await self.telemetry_tools.get_session_logs(
                date_range=args.period,
                limit=50
            )
            data["performance_metrics"] = await self.telemetry_tools.get_performance_metrics(
                metric_type="tool_duration",
                time_range=args.period
            )
        
        if args.type in ["errors", "full"]:
            data["error_analysis"] = await self.telemetry_tools.get_error_analysis(
                time_range=args.period,
                group_by="tool"
            )
        
        if args.type in ["efficiency", "tools", "full"]:
            data["workflow_insights"] = await self.telemetry_tools.get_workflow_insights(
                analysis_type="efficiency",
                time_period=args.period,
                comparison_period=args.compare_to if hasattr(args, 'compare_to') else None
            )
        
        return data
    
    def _build_analysis_prompt(self, args, telemetry_data: Dict[str, Any]) -> str:
        """Build AI analysis prompt based on collected data"""
        
        # Get base prompt template for analysis type
        base_prompt = self.prompts.get_analysis_prompt(args.type)
        
        # Add telemetry data context
        data_context = self._format_telemetry_data_for_prompt(telemetry_data)
        
        # Build complete prompt
        full_prompt = f"""
{base_prompt}

## Telemetry Data Analysis

{data_context}

## Analysis Instructions

Please analyze the above telemetry data and provide:

1. **Key Insights**: 3-5 most important findings about the development workflow
2. **Performance Patterns**: Trends in tool usage, session duration, and success rates  
3. **Bottlenecks Identified**: Specific areas where efficiency could be improved
4. **Actionable Recommendations**: Concrete steps to optimize the workflow
5. **Priority Actions**: Top 3 recommendations to implement first

Focus on practical, implementable suggestions that will have measurable impact on development productivity.

**Analysis Period**: {args.period}
**Analysis Type**: {args.type}
**Current Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        return full_prompt
    
    def _format_analysis_results(
        self,
        analysis_type: str,
        period: str, 
        telemetry_data: Dict[str, Any],
        analysis_prompt: str
    ) -> str:
        """Format the complete analysis results"""
        
        # Create executive summary
        summary = self._create_executive_summary(telemetry_data)
        
        # Return formatted response that Claude will process
        return f"""
# 📊 Development Workflow Analysis Report

**Analysis Type**: {analysis_type.title()}  
**Time Period**: {period}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📈 Executive Summary

{summary}

## 🤖 AI Analysis Request

I've collected comprehensive telemetry data about your development workflow. Please analyze this data and provide insights:

{analysis_prompt}

---

*This analysis is based on {self._get_data_point_count(telemetry_data)} telemetry data points collected from your Claude Code usage.*
"""
    
    def _create_executive_summary(self, data: Dict[str, Any]) -> str:
        """Create high-level summary of key metrics"""
        
        summary_parts = []
        
        # Usage metrics summary
        if "usage_metrics" in data:
            metrics = data["usage_metrics"]
            total_tools = metrics.get("total_tools_used", 0)
            success_rate = metrics.get("success_rate", 0)
            avg_duration = metrics.get("average_duration_ms", 0)
            
            summary_parts.append(f"• **Tools Used**: {total_tools} total executions")
            summary_parts.append(f"• **Success Rate**: {success_rate:.1%}")
            if avg_duration > 0:
                summary_parts.append(f"• **Average Tool Duration**: {avg_duration/1000:.1f}s")
        
        # Session summary
        if "session_logs" in data:
            sessions = data["session_logs"].get("sessions", [])
            if sessions:
                avg_session_length = sum(s.get("duration_ms", 0) for s in sessions) / len(sessions)
                summary_parts.append(f"• **Sessions Analyzed**: {len(sessions)}")
                summary_parts.append(f"• **Average Session Length**: {avg_session_length/60000:.1f} minutes")
        
        # Error summary
        if "error_analysis" in data:
            errors = data["error_analysis"]
            error_count = errors.get("total_errors", 0)
            if error_count > 0:
                summary_parts.append(f"• **Errors Detected**: {error_count} issues found")
        
        return "\n".join(summary_parts) if summary_parts else "No significant activity detected in the specified period."

    def _parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments"""
        
        parser = argparse.ArgumentParser(description="Analyze development workflow")
        parser.add_argument("type", nargs="?", default="productivity",
                          choices=["productivity", "efficiency", "errors", "tools", "sessions", "full"],
                          help="Type of analysis to perform")
        parser.add_argument("period", nargs="?", default="7d",
                          help="Time period to analyze (1d, 7d, 30d)")
        parser.add_argument("--compare-to", help="Comparison period")
        parser.add_argument("--filter", help="Filter by specific tool or pattern")
        parser.add_argument("--limit", type=int, default=100, help="Limit results")
        
        return parser.parse_args(args)

async def main():
    """Command entry point"""
    command = AnalyzeWorkflowCommand()
    result = await command.execute(sys.argv[1:])
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Analysis Prompt Templates
```python
# telemetry/analysis/prompts.py

class AnalysisPrompts:
    def __init__(self):
        self.prompts = {
            "productivity": self._productivity_prompt(),
            "efficiency": self._efficiency_prompt(), 
            "errors": self._error_analysis_prompt(),
            "tools": self._tool_analysis_prompt(),
            "sessions": self._session_analysis_prompt(),
            "full": self._comprehensive_prompt()
        }
    
    def get_analysis_prompt(self, analysis_type: str) -> str:
        return self.prompts.get(analysis_type, self.prompts["productivity"])
    
    def _productivity_prompt(self) -> str:
        return """
# Development Productivity Analysis

You are an expert development workflow analyst. Analyze the provided telemetry data to identify productivity patterns and optimization opportunities.

## Focus Areas:
- **Time Management**: Session durations, work patterns, peak productivity periods
- **Tool Effectiveness**: Success rates, execution times, tool selection patterns  
- **Workflow Efficiency**: Repetitive tasks, automation opportunities, bottlenecks
- **Development Velocity**: Code output, task completion rates, iteration cycles

## Key Questions to Address:
1. What are the most productive development patterns observed?
2. Which tools/approaches yield the highest success rates?
3. What time patterns show peak productivity vs. inefficiency?
4. What workflow changes would have the highest impact on productivity?
5. Are there signs of context switching, multitasking, or focus issues?
"""

    def _efficiency_prompt(self) -> str:
        return """
# Development Efficiency Analysis

Analyze the telemetry data to identify efficiency bottlenecks and optimization opportunities in the development workflow.

## Focus Areas:
- **Performance Bottlenecks**: Slow tools, long-running operations, timeout issues
- **Repetitive Patterns**: Tasks that could be automated or streamlined
- **Error Recovery**: Time spent on error resolution and debugging
- **Resource Utilization**: Effective use of available tools and capabilities

## Key Questions to Address:
1. Which tools or operations consume disproportionate time?
2. What repetitive patterns suggest automation opportunities?
3. How much time is spent on error recovery vs. productive work?
4. What workflow changes would eliminate the biggest inefficiencies?
5. Are there underutilized tools that could improve efficiency?
"""

    def _error_analysis_prompt(self) -> str:
        return """
# Error Pattern Analysis

Analyze error patterns and failure modes to identify prevention strategies and workflow improvements.

## Focus Areas:
- **Error Frequency**: Most common failure types and their impact
- **Error Recovery**: Time and effort spent resolving issues
- **Root Causes**: Underlying patterns that lead to errors
- **Prevention Strategies**: Workflow changes to reduce error rates

## Key Questions to Address:
1. What are the most frequent types of errors or failures?
2. Which tools or operations have the highest failure rates?
3. What patterns precede errors (time of day, session length, complexity)?
4. How can the workflow be modified to prevent common errors?
5. What additional tooling or practices would improve reliability?
"""

    def _comprehensive_prompt(self) -> str:
        return """
# Comprehensive Development Workflow Analysis

Perform a holistic analysis of the development workflow covering productivity, efficiency, error patterns, and tool usage.

## Analysis Scope:
- **Productivity Assessment**: Overall effectiveness and output quality
- **Efficiency Optimization**: Speed and resource utilization improvements
- **Error Prevention**: Reliability and failure reduction strategies  
- **Tool Utilization**: Effectiveness of current toolchain and missing capabilities
- **Workflow Patterns**: Session management and work organization

## Deliverables:
1. **Workflow Health Score**: Overall assessment with key metrics
2. **Top Improvement Opportunities**: Highest-impact optimization areas
3. **Implementation Roadmap**: Prioritized action plan with timeline
4. **Success Metrics**: KPIs to track improvement over time
5. **Risk Assessment**: Potential negative impacts of proposed changes
"""
```

### 4. Command Integration with Claude Code

The command integrates with Claude Code through the slash command system and returns a formatted response that Claude processes as a user prompt, triggering AI analysis of the telemetry data.

## User Experience Flow

### 1. Command Execution
```bash
User: /analyze-workflow productivity 14d
```

### 2. Data Collection Progress
```
🔍 Analyzing development workflow...
📊 Analysis type: productivity
📅 Time period: 14d

📈 Collecting telemetry data...
📊 Usage metrics: ✅ 1,247 tool executions found
📝 Session logs: ✅ 23 sessions analyzed  
⚡ Performance data: ✅ Metrics computed

🤖 Generating AI-powered insights...
📋 Formatting results...
```

### 3. Claude AI Analysis
Claude receives the formatted telemetry data and analysis prompt, then provides insights like:

```markdown
# 📊 Development Workflow Analysis Results

Based on your 14-day telemetry data, here are the key insights:

## 🎯 Key Findings

1. **High Tool Usage Efficiency**: 94.2% success rate across 1,247 tool executions
2. **Session Length Optimization Needed**: Average 78-minute sessions exceed optimal focus periods
3. **Peak Productivity Window**: 9-11 AM shows 40% higher success rates

## 🚀 Top Recommendations

1. **Break Long Sessions**: Implement 45-minute focused work blocks with breaks
2. **Morning Schedule Optimization**: Schedule complex tasks during 9-11 AM peak hours
3. **Tool Chain Enhancement**: Consider adding automated formatting hooks (saves ~12 min/day)

## 📈 Expected Impact
- **20% productivity increase** through session length optimization
- **15% error reduction** by scheduling complex work during peak hours
- **12 minutes saved daily** through automation improvements
```

## Testing Strategy

### Unit Tests
- **Argument Parsing**: Test all command syntax variations
- **Data Collection**: Mock MCP server responses and verify data gathering
- **Prompt Generation**: Test prompt template assembly with various data scenarios
- **Error Handling**: Test failure modes and error responses

### Integration Tests
- **MCP Integration**: Test with actual telemetry MCP server
- **Claude Code Integration**: Test slash command registration and execution
- **End-to-End Flow**: Complete command execution with real telemetry data
- **Performance**: Measure command execution time and response quality

### User Acceptance Tests
- **Ease of Use**: Verify command syntax is intuitive and discoverable
- **Insight Quality**: Validate that generated insights are actionable and accurate
- **Response Time**: Ensure command completes within acceptable timeframe (< 30 seconds)
- **Error Messages**: Test that error messages are clear and helpful

## Success Criteria
- ✅ Command completes analysis within 30 seconds for typical datasets
- ✅ Generates 3-5 actionable insights per analysis
- ✅ 90% of recommendations are implementable and specific
- ✅ Supports all 6 analysis types with appropriate depth
- ✅ Handles edge cases gracefully (insufficient data, errors)
- ✅ Integrates seamlessly with Claude Code slash command system

## Implementation Timeline
- **Day 1-2**: Core command structure and argument parsing
- **Day 3-4**: Telemetry data collection and prompt generation
- **Day 5-6**: Analysis templates and formatting logic
- **Day 7-8**: Integration testing and user experience polish

## Dependencies
- **Telemetry MCP Server**: Data access through MCP tools (Issue #3)
- **Claude Code**: Slash command support and MCP integration
- **Telemetry Logs**: Historical data from logging hooks (Issue #2)
- **Python 3.8+**: For async data collection and processing

## Future Enhancements
- **Interactive Analysis**: Follow-up questions and deeper dives
- **Comparison Analysis**: Compare periods, teams, or projects
- **Custom Metrics**: User-defined KPIs and tracking goals
- **Automated Scheduling**: Regular analysis reports and monitoring
- **Integration with Goals**: Track progress toward specific productivity targets
- **Export Capabilities**: Save reports in various formats (PDF, markdown, JSON)