#!/usr/bin/env python3
"""
Test script to compare effectiveness of different research tools for hockey diagram prompts.
Tests search_hockey_tactics, search_hockey_drills, and web_search_exa tools.
"""

import asyncio
import json
import time
from typing import Dict, List, Any

# Test prompts covering different categories
TEST_PROMPTS = [
    # Standard NHL systems
    "1-3-1 power play formation",
    "2-1-2 forecheck system", 
    "diamond penalty kill",
    
    # International/less common systems
    "Swedish torpedo forecheck",
    "Finnish box+1 system",
    "Russian 5-man cycle",
    
    # Modern/advanced tactics
    "stretch pass breakout",
    "middle lane drive",
    "low cycle support",
    
    # Specific drills
    "3v2 continuous drill",
    "breakout under pressure drill", 
    "cross-ice passing drill",
    
    # Youth-specific concepts
    "U10 cross-ice scrimmage",
    "novice station rotation drill",
    "atom defensive positioning"
]

class ToolTester:
    def __init__(self):
        self.results = {}
        
    async def test_hockey_tactics(self, prompt: str) -> Dict[str, Any]:
        """Test search_hockey_tactics tool."""
        try:
            # Import the MCP tool
            import sys
            sys.path.append('/Users/liammckendry/thunder_playbook')
            
            start_time = time.time()
            
            # Use the hockey coaching MCP tool
            result = await self.call_hockey_tactics_tool(prompt)
            
            end_time = time.time()
            
            return {
                "success": True,
                "response_time": end_time - start_time,
                "content": result,
                "content_length": len(str(result)),
                "has_positioning": "position" in str(result).lower() or "zone" in str(result).lower(),
                "has_movement": "move" in str(result).lower() or "pass" in str(result).lower(),
                "specificity_score": self.calculate_specificity(result)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0,
                "content": "",
                "content_length": 0,
                "has_positioning": False,
                "has_movement": False,
                "specificity_score": 0
            }
    
    async def call_hockey_tactics_tool(self, prompt: str):
        """Call the hockey tactics MCP tool."""
        # This would normally use MCP, but for testing we'll simulate
        # We'll use the actual MCP call through the coaching tools
        return f"Hockey tactics search result for: {prompt}"
    
    async def test_hockey_drills(self, prompt: str) -> Dict[str, Any]:
        """Test search_hockey_drills tool."""
        try:
            start_time = time.time()
            
            # Use the hockey drills MCP tool
            result = await self.call_hockey_drills_tool(prompt)
            
            end_time = time.time()
            
            return {
                "success": True, 
                "response_time": end_time - start_time,
                "content": result,
                "content_length": len(str(result)),
                "has_positioning": "position" in str(result).lower() or "zone" in str(result).lower(),
                "has_movement": "move" in str(result).lower() or "pass" in str(result).lower(),
                "specificity_score": self.calculate_specificity(result)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0,
                "content": "",
                "content_length": 0,
                "has_positioning": False,
                "has_movement": False,
                "specificity_score": 0
            }
    
    async def call_hockey_drills_tool(self, prompt: str):
        """Call the hockey drills MCP tool."""
        return f"Hockey drills search result for: {prompt}"
    
    async def test_web_search_exa(self, prompt: str) -> Dict[str, Any]:
        """Test web_search_exa tool."""
        try:
            start_time = time.time()
            
            # Use Exa web search with hockey-specific query
            hockey_query = f"hockey {prompt} formation positioning tactics"
            result = await self.call_exa_tool(hockey_query)
            
            end_time = time.time()
            
            return {
                "success": True,
                "response_time": end_time - start_time, 
                "content": result,
                "content_length": len(str(result)),
                "has_positioning": "position" in str(result).lower() or "zone" in str(result).lower(),
                "has_movement": "move" in str(result).lower() or "pass" in str(result).lower(),
                "specificity_score": self.calculate_specificity(result)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0,
                "content": "",
                "content_length": 0,
                "has_positioning": False,
                "has_movement": False,
                "specificity_score": 0
            }
    
    async def call_exa_tool(self, query: str):
        """Call the Exa web search tool."""
        return f"Exa web search result for: {query}"
    
    def calculate_specificity(self, content: str) -> int:
        """Calculate a specificity score based on hockey-specific terms."""
        hockey_terms = [
            "forecheck", "backcheck", "cycle", "breakout", "regroup",
            "slot", "point", "corner", "crease", "boards", "hash",
            "winger", "center", "defense", "defenseman", "forward",
            "pass", "shot", "screen", "tip", "one-timer", "wrap",
            "zone", "neutral", "offensive", "defensive", "power play",
            "penalty kill", "face-off", "draw", "pressure", "support"
        ]
        
        content_lower = content.lower()
        score = sum(1 for term in hockey_terms if term in content_lower)
        return score
    
    async def run_comprehensive_test(self):
        """Run tests on all prompts with all tools."""
        print("🏒 Starting Hockey Research Tools Comparison Test")
        print("=" * 60)
        
        for i, prompt in enumerate(TEST_PROMPTS):
            print(f"\nTest {i+1}/{len(TEST_PROMPTS)}: {prompt}")
            print("-" * 40)
            
            # Test each tool
            tactics_result = await self.test_hockey_tactics(prompt)
            drills_result = await self.test_hockey_drills(prompt) 
            exa_result = await self.test_web_search_exa(prompt)
            
            # Store results
            self.results[prompt] = {
                "hockey_tactics": tactics_result,
                "hockey_drills": drills_result,
                "web_search_exa": exa_result
            }
            
            # Print summary
            print(f"  Hockey Tactics: {'✅' if tactics_result['success'] else '❌'} "
                  f"({tactics_result.get('response_time', 0):.2f}s, "
                  f"score: {tactics_result.get('specificity_score', 0)})")
            
            print(f"  Hockey Drills:  {'✅' if drills_result['success'] else '❌'} "
                  f"({drills_result.get('response_time', 0):.2f}s, "
                  f"score: {drills_result.get('specificity_score', 0)})")
            
            print(f"  Web Search Exa: {'✅' if exa_result['success'] else '❌'} "
                  f"({exa_result.get('response_time', 0):.2f}s, "
                  f"score: {exa_result.get('specificity_score', 0)})")
    
    def analyze_results(self):
        """Analyze test results and provide recommendations."""
        print("\n🔍 ANALYSIS RESULTS")
        print("=" * 60)
        
        # Calculate aggregate metrics
        tool_stats = {
            "hockey_tactics": {"success": 0, "avg_time": 0, "avg_score": 0, "positioning": 0, "movement": 0},
            "hockey_drills": {"success": 0, "avg_time": 0, "avg_score": 0, "positioning": 0, "movement": 0},
            "web_search_exa": {"success": 0, "avg_time": 0, "avg_score": 0, "positioning": 0, "movement": 0}
        }
        
        for prompt, results in self.results.items():
            for tool, result in results.items():
                if result["success"]:
                    tool_stats[tool]["success"] += 1
                    tool_stats[tool]["avg_time"] += result["response_time"]
                    tool_stats[tool]["avg_score"] += result["specificity_score"]
                    if result["has_positioning"]:
                        tool_stats[tool]["positioning"] += 1
                    if result["has_movement"]:
                        tool_stats[tool]["movement"] += 1
        
        # Calculate averages
        total_tests = len(TEST_PROMPTS)
        for tool in tool_stats:
            if tool_stats[tool]["success"] > 0:
                tool_stats[tool]["avg_time"] /= tool_stats[tool]["success"]
                tool_stats[tool]["avg_score"] /= tool_stats[tool]["success"]
        
        # Print detailed analysis
        for tool, stats in tool_stats.items():
            print(f"\n{tool.upper().replace('_', ' ')}")
            print(f"  Success Rate: {stats['success']}/{total_tests} ({stats['success']/total_tests*100:.1f}%)")
            print(f"  Avg Response Time: {stats['avg_time']:.2f}s")
            print(f"  Avg Specificity Score: {stats['avg_score']:.1f}")
            print(f"  Positioning Info: {stats['positioning']}/{total_tests} ({stats['positioning']/total_tests*100:.1f}%)")
            print(f"  Movement Info: {stats['movement']}/{total_tests} ({stats['movement']/total_tests*100:.1f}%)")
        
        return tool_stats
    
    def generate_recommendations(self, tool_stats: Dict):
        """Generate recommendations based on analysis."""
        print("\n📋 RECOMMENDATIONS")
        print("=" * 60)
        
        # Rank tools by different criteria
        by_success = sorted(tool_stats.items(), key=lambda x: x[1]["success"], reverse=True)
        by_specificity = sorted(tool_stats.items(), key=lambda x: x[1]["avg_score"], reverse=True)
        by_speed = sorted(tool_stats.items(), key=lambda x: x[1]["avg_time"])
        
        print("Ranking by Success Rate:")
        for i, (tool, stats) in enumerate(by_success, 1):
            print(f"  {i}. {tool}: {stats['success']}/{len(TEST_PROMPTS)} ({stats['success']/len(TEST_PROMPTS)*100:.1f}%)")
        
        print("\nRanking by Hockey Specificity:")
        for i, (tool, stats) in enumerate(by_specificity, 1):
            print(f"  {i}. {tool}: {stats['avg_score']:.1f} avg score")
        
        print("\nRanking by Speed:")
        for i, (tool, stats) in enumerate(by_speed, 1):
            print(f"  {i}. {tool}: {stats['avg_time']:.2f}s avg")
        
        # Generate final recommendation
        print("\n🎯 OPTIMAL PECKING ORDER RECOMMENDATION:")
        print("Based on comprehensive analysis:")
        print("1. First choice: [To be determined based on actual results]")
        print("2. Second choice: [To be determined based on actual results]")
        print("3. Fallback: [To be determined based on actual results]")

async def main():
    """Run the comprehensive test."""
    tester = ToolTester()
    
    # Run tests  
    await tester.run_comprehensive_test()
    
    # Analyze results
    tool_stats = tester.analyze_results()
    
    # Generate recommendations
    tester.generate_recommendations(tool_stats)
    
    # Save results to file
    with open("research_tools_test_results.json", "w") as f:
        json.dump({
            "test_prompts": TEST_PROMPTS,
            "detailed_results": tester.results,
            "summary_stats": tool_stats
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to research_tools_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())