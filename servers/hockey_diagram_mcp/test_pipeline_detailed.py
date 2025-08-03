#!/usr/bin/env python3
"""
Detailed pipeline testing framework for hockey diagram generation.
Captures all stages: prompt → entity extraction → coordinate mapping → final diagram
Includes QA analysis and feedback collection.
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Set API key
if len(sys.argv) > 1:
    os.environ['OPENAI_API_KEY'] = sys.argv[1]

from servers.hockey_diagram_mcp.server import generate_hockey_diagram
from servers.hockey_diagram_mcp.two_stage_parser import TwoStageHockeyParser
from servers.hockey_diagram_mcp.generator import HockeyDiagramGenerator

class PipelineTestRunner:
    """Runs detailed tests capturing all pipeline stages."""
    
    def __init__(self):
        self.parser = TwoStageHockeyParser()
        self.generator = HockeyDiagramGenerator()
        self.results_dir = Path("servers/hockey_diagram_mcp/test_results")
        self.results_dir.mkdir(exist_ok=True)
        
    async def test_prompt(self, prompt: str, view: str = "full", test_id: str = None) -> Dict[str, Any]:
        """Test a single prompt through the entire pipeline."""
        
        result = {
            "test_id": test_id or datetime.now().strftime("%Y%m%d_%H%M%S"),
            "prompt": prompt,
            "requested_view": view,
            "stages": {},
            "qa_analysis": {},
            "success": False
        }
        
        try:
            # Stage 1: Two-stage parser
            print(f"\n{'='*60}")
            print(f"Testing: {prompt}")
            print(f"View: {view}")
            print("="*60)
            
            # Run the parser
            context = {"diagram_type": "tactical", "requested_view": view}
            diagram_spec = await self.parser.parse_prompt(prompt, context)
            
            # Capture parser output
            result["stages"]["parser_output"] = {
                "diagram_type": diagram_spec.diagram_type,
                "title": diagram_spec.title,
                "view": diagram_spec.view,
                "players": [p.dict() for p in diagram_spec.players],
                "movements": [m.dict() for m in (diagram_spec.movements or [])],
                "zones": [z.dict() for z in (diagram_spec.zones or [])]
            }
            
            # Stage 2: Generate diagram through MCP
            mcp_result = await generate_hockey_diagram(
                prompt=prompt,
                view=view,
                output_format="png"
            )
            
            result["stages"]["mcp_result"] = {
                "success": mcp_result.get("success"),
                "diagram_path": mcp_result.get("diagram_path"),
                "generation_time": mcp_result.get("generation_time"),
                "file_output": mcp_result.get("file_output", False)
            }
            
            if mcp_result.get("success"):
                result["success"] = True
                result["diagram_path"] = mcp_result.get("diagram_path")
                
                # Perform QA analysis
                result["qa_analysis"] = self._perform_qa_analysis(
                    prompt, 
                    result["stages"]["parser_output"],
                    mcp_result.get("diagram_spec", {})
                )
            
        except Exception as e:
            result["error"] = str(e)
            result["qa_analysis"]["error"] = f"Pipeline failed: {str(e)}"
            
        return result
    
    def _perform_qa_analysis(self, prompt: str, parser_output: Dict, final_spec: Dict) -> Dict[str, Any]:
        """Perform quality analysis on the generation."""
        
        qa = {
            "checks": {},
            "issues": [],
            "suggestions": []
        }
        
        # Check 1: Player count accuracy
        expected_players = self._estimate_expected_players(prompt)
        actual_players = len(parser_output.get("players", []))
        qa["checks"]["player_count"] = {
            "expected": expected_players,
            "actual": actual_players,
            "match": abs(expected_players - actual_players) <= 1  # Allow ±1 for goalie
        }
        
        # Check 2: View consistency
        requested_view = parser_output.get("view", "full")
        qa["checks"]["view_consistency"] = {
            "requested": requested_view,
            "final": final_spec.get("view", "full"),
            "match": requested_view == final_spec.get("view", "full")
        }
        
        # Check 3: Movement validation
        movements = parser_output.get("movements", [])
        qa["checks"]["movements"] = {
            "count": len(movements),
            "has_movements": len(movements) > 0,
            "expected_movements": "pass" in prompt.lower() or "movement" in prompt.lower()
        }
        
        # Check 4: Formation detection
        formation_keywords = ["forecheck", "penalty kill", "power play", "box", "diamond", "umbrella"]
        detected_formation = any(kw in prompt.lower() for kw in formation_keywords)
        qa["checks"]["formation_detection"] = {
            "expected": detected_formation,
            "diagram_type": parser_output.get("diagram_type"),
            "appropriate": detected_formation == (parser_output.get("diagram_type") in ["formation", "system"])
        }
        
        # Check 5: Zone positioning
        if requested_view != "full":
            qa["checks"]["zone_positioning"] = self._check_zone_positioning(
                parser_output.get("players", []), 
                requested_view
            )
        
        # Generate issues and suggestions
        if not qa["checks"]["player_count"]["match"]:
            qa["issues"].append(f"Player count mismatch: expected ~{expected_players}, got {actual_players}")
            
        if not qa["checks"]["view_consistency"]["match"]:
            qa["issues"].append(f"View inconsistency: requested {requested_view}, got {final_spec.get('view')}")
            
        if qa["checks"]["movements"]["expected_movements"] and not qa["checks"]["movements"]["has_movements"]:
            qa["suggestions"].append("Consider adding movement arrows for plays involving passes or player movement")
            
        # Overall assessment
        qa["overall_quality"] = "GOOD" if len(qa["issues"]) == 0 else ("FAIR" if len(qa["issues"]) <= 2 else "NEEDS_IMPROVEMENT")
        
        return qa
    
    def _estimate_expected_players(self, prompt: str) -> int:
        """Estimate expected number of players based on prompt."""
        prompt_lower = prompt.lower()
        
        # Specific formations
        if "3v2" in prompt_lower: return 5
        if "2v1" in prompt_lower: return 3
        if "3v3" in prompt_lower: return 6
        if "box" in prompt_lower and "penalty kill" in prompt_lower: return 4
        if "power play" in prompt_lower: return 5
        if "6v5" in prompt_lower: return 11
        
        # Default
        return 5
    
    def _check_zone_positioning(self, players: List[Dict], view: str) -> Dict[str, Any]:
        """Check if players are positioned correctly for the view."""
        
        zone_check = {
            "correct_zone": True,
            "out_of_bounds": [],
            "percentage_correct": 100.0
        }
        
        for player in players:
            x = player.get("x", 0)
            
            if view == "offensive" and x < 25:
                zone_check["out_of_bounds"].append(f"{player.get('position')} at x={x}")
            elif view == "defensive" and x > -25:
                zone_check["out_of_bounds"].append(f"{player.get('position')} at x={x}")
            elif view == "neutral" and (x < -25 or x > 25):
                zone_check["out_of_bounds"].append(f"{player.get('position')} at x={x}")
        
        if zone_check["out_of_bounds"]:
            zone_check["correct_zone"] = False
            zone_check["percentage_correct"] = (len(players) - len(zone_check["out_of_bounds"])) / len(players) * 100
            
        return zone_check
    
    async def run_batch_tests(self, test_batch: List[Dict[str, str]]) -> Dict[str, Any]:
        """Run a batch of tests and generate summary report."""
        
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_results = {
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(test_batch),
            "tests": [],
            "summary": {}
        }
        
        print(f"\nRunning Test Batch: {batch_id}")
        print(f"Total tests: {len(test_batch)}")
        
        for i, test in enumerate(test_batch, 1):
            test_id = f"{batch_id}_{i:02d}"
            result = await self.test_prompt(
                prompt=test["prompt"],
                view=test.get("view", "full"),
                test_id=test_id
            )
            batch_results["tests"].append(result)
            
            # Brief result
            status = "✅" if result["success"] else "❌"
            quality = result.get("qa_analysis", {}).get("overall_quality", "UNKNOWN")
            print(f"\n{status} Test {i}: {quality}")
            
            if result.get("qa_analysis", {}).get("issues"):
                print(f"   Issues: {', '.join(result['qa_analysis']['issues'])}")
                
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Generate summary
        batch_results["summary"] = self._generate_batch_summary(batch_results["tests"])
        
        # Save detailed results
        self._save_batch_results(batch_results)
        
        return batch_results
    
    def _generate_batch_summary(self, tests: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics for the batch."""
        
        summary = {
            "successful": sum(1 for t in tests if t["success"]),
            "failed": sum(1 for t in tests if not t["success"]),
            "quality_breakdown": {
                "GOOD": sum(1 for t in tests if t.get("qa_analysis", {}).get("overall_quality") == "GOOD"),
                "FAIR": sum(1 for t in tests if t.get("qa_analysis", {}).get("overall_quality") == "FAIR"),
                "NEEDS_IMPROVEMENT": sum(1 for t in tests if t.get("qa_analysis", {}).get("overall_quality") == "NEEDS_IMPROVEMENT")
            },
            "common_issues": {},
            "recommendations": []
        }
        
        # Analyze common issues
        all_issues = []
        for test in tests:
            all_issues.extend(test.get("qa_analysis", {}).get("issues", []))
            
        for issue in all_issues:
            issue_type = issue.split(":")[0]
            summary["common_issues"][issue_type] = summary["common_issues"].get(issue_type, 0) + 1
            
        # Generate recommendations
        if summary["common_issues"].get("Player count mismatch", 0) > 2:
            summary["recommendations"].append("Review player count logic in parser")
            
        if summary["common_issues"].get("View inconsistency", 0) > 0:
            summary["recommendations"].append("Check view override logic in server.py")
            
        return summary
    
    def _save_batch_results(self, batch_results: Dict):
        """Save batch results to file."""
        
        filename = f"batch_results_{batch_results['batch_id']}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(batch_results, f, indent=2)
            
        print(f"\nDetailed results saved to: {filepath}")
        
        # Also generate markdown report
        self._generate_markdown_report(batch_results)
    
    def _generate_markdown_report(self, batch_results: Dict):
        """Generate a markdown report for easy review."""
        
        filename = f"batch_report_{batch_results['batch_id']}.md"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"# Hockey Diagram Test Batch Report\n\n")
            f.write(f"**Batch ID:** {batch_results['batch_id']}\n")
            f.write(f"**Date:** {batch_results['timestamp']}\n")
            f.write(f"**Total Tests:** {batch_results['total_tests']}\n\n")
            
            # Summary
            summary = batch_results['summary']
            f.write("## Summary\n\n")
            f.write(f"- **Successful:** {summary['successful']}/{batch_results['total_tests']}\n")
            f.write(f"- **Failed:** {summary['failed']}/{batch_results['total_tests']}\n\n")
            
            f.write("### Quality Breakdown\n")
            for quality, count in summary['quality_breakdown'].items():
                f.write(f"- **{quality}:** {count}\n")
            
            if summary['common_issues']:
                f.write("\n### Common Issues\n")
                for issue, count in summary['common_issues'].items():
                    f.write(f"- {issue}: {count} occurrences\n")
                    
            if summary['recommendations']:
                f.write("\n### Recommendations\n")
                for rec in summary['recommendations']:
                    f.write(f"- {rec}\n")
            
            # Individual test results
            f.write("\n## Detailed Test Results\n")
            
            for i, test in enumerate(batch_results['tests'], 1):
                f.write(f"\n### Test {i}: {test['prompt']}\n")
                f.write(f"**View:** {test['requested_view']}\n")
                f.write(f"**Status:** {'✅ Success' if test['success'] else '❌ Failed'}\n")
                
                if test['success']:
                    f.write(f"**Diagram:** `{test['diagram_path']}`\n")
                    
                qa = test.get('qa_analysis', {})
                if qa:
                    f.write(f"**Quality:** {qa.get('overall_quality', 'N/A')}\n")
                    
                    if qa.get('issues'):
                        f.write("\n**Issues:**\n")
                        for issue in qa['issues']:
                            f.write(f"- {issue}\n")
                            
                    if qa.get('suggestions'):
                        f.write("\n**Suggestions:**\n")
                        for suggestion in qa['suggestions']:
                            f.write(f"- {suggestion}\n")
                
                # Parser output details
                parser_out = test.get('stages', {}).get('parser_output', {})
                if parser_out:
                    f.write(f"\n**Parser Output:**\n")
                    f.write(f"- Diagram Type: {parser_out.get('diagram_type')}\n")
                    f.write(f"- Players: {len(parser_out.get('players', []))}\n")
                    f.write(f"- Movements: {len(parser_out.get('movements', []))}\n")
                    f.write(f"- View: {parser_out.get('view')}\n")
                    
        print(f"Markdown report saved to: {filepath}")


# Test batches
TEST_BATCHES = {
    "batch_1_views": [
        {"prompt": "5v5 neutral zone setup", "view": "full"},
        {"prompt": "Offensive zone cycle play", "view": "offensive"},
        {"prompt": "Defensive zone coverage", "view": "defensive"},
        {"prompt": "Neutral zone trap 1-3-1", "view": "neutral"},
        {"prompt": "Breakout from defensive zone to offensive rush", "view": "full"}
    ],
    
    "batch_2_formations": [
        {"prompt": "2-1-2 forecheck with F1 behind net", "view": "offensive"},
        {"prompt": "Box penalty kill formation", "view": "defensive"},
        {"prompt": "1-3-1 power play umbrella", "view": "offensive"},
        {"prompt": "Diamond penalty kill aggressive pressure", "view": "defensive"},
        {"prompt": "2-3 forecheck neutral zone pressure", "view": "neutral"}
    ],
    
    "batch_3_drills": [
        {"prompt": "3v2 rush drill from center ice", "view": "full"},
        {"prompt": "Triangle passing drill in neutral zone", "view": "neutral"},
        {"prompt": "2v1 defensive drill starting at blue line", "view": "defensive"},
        {"prompt": "Breakout drill with D-to-D pass behind net", "view": "defensive"},
        {"prompt": "Power play entry drill at offensive blue line", "view": "offensive"}
    ],
    
    "batch_4_plays": [
        {"prompt": "D-to-D breakout with center swinging low", "view": "defensive"},
        {"prompt": "Give and go play through neutral zone", "view": "full"},
        {"prompt": "Cycle play with low-to-high pass for shot", "view": "offensive"},
        {"prompt": "Stretch pass from D to winger for breakaway", "view": "full"},
        {"prompt": "Behind the net play with wrap around attempt", "view": "offensive"}
    ],
    
    "batch_5_special": [
        {"prompt": "6v5 with goalie pulled offensive zone setup", "view": "offensive"},
        {"prompt": "3v3 overtime spread formation", "view": "full"},
        {"prompt": "Faceoff play in defensive zone strong side win", "view": "defensive"},
        {"prompt": "Power play with net front screen and point shot", "view": "offensive"},
        {"prompt": "Penalty kill clear with strong side winger support", "view": "defensive"}
    ]
}


async def main():
    """Run the test framework."""
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not set!")
        print("Usage: python test_pipeline_detailed.py [API_KEY] [batch_name]")
        sys.exit(1)
        
    runner = PipelineTestRunner()
    
    # Get batch name from command line or use default
    batch_name = sys.argv[2] if len(sys.argv) > 2 else "batch_1_views"
    
    if batch_name not in TEST_BATCHES:
        print(f"Error: Unknown batch '{batch_name}'")
        print(f"Available batches: {', '.join(TEST_BATCHES.keys())}")
        sys.exit(1)
        
    print(f"Running test batch: {batch_name}")
    
    # Run the batch
    results = await runner.run_batch_tests(TEST_BATCHES[batch_name])
    
    print(f"\n{'='*60}")
    print("Batch Complete!")
    print(f"{'='*60}")
    print(f"Success rate: {results['summary']['successful']}/{results['total_tests']}")
    print(f"Quality: {results['summary']['quality_breakdown']}")
    
    if results['summary']['recommendations']:
        print("\nRecommendations:")
        for rec in results['summary']['recommendations']:
            print(f"- {rec}")


if __name__ == "__main__":
    asyncio.run(main())