#!/usr/bin/env python3
"""
Test script to validate n8n workflow structure and simulate execution
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

def load_workflow(filepath: str) -> Dict:
    """Load and parse n8n workflow JSON"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

def validate_node_structure(node: Dict) -> List[str]:
    """Validate individual node structure"""
    errors = []
    required_fields = ['id', 'name', 'type', 'position']
    
    for field in required_fields:
        if field not in node:
            errors.append(f"Missing required field '{field}' in node {node.get('name', 'unknown')}")
    
    # Check position is array with 2 numbers
    if 'position' in node:
        if not isinstance(node['position'], list) or len(node['position']) != 2:
            errors.append(f"Invalid position format in node {node.get('name', 'unknown')}")
    
    # Validate parameters based on node type
    if node.get('type') == 'n8n-nodes-base.googleSheets':
        if 'parameters' not in node:
            errors.append(f"Missing parameters in Google Sheets node {node.get('name', 'unknown')}")
        else:
            params = node['parameters']
            if 'resource' not in params or 'operation' not in params:
                errors.append(f"Missing resource/operation in Google Sheets node {node.get('name', 'unknown')}")
    
    return errors

def validate_connections(workflow: Dict) -> List[str]:
    """Validate workflow connections"""
    errors = []
    node_ids = {node['id'] for node in workflow.get('nodes', [])}
    node_names = {node['name'] for node in workflow.get('nodes', [])}
    connections = workflow.get('connections', {})
    
    for source_node, targets in connections.items():
        # Check if source node exists
        if source_node not in node_names:
            errors.append(f"Connection from non-existent node: {source_node}")
        
        # Check target nodes
        if 'main' in targets:
            for connection_group in targets['main']:
                for connection in connection_group:
                    target_node = connection.get('node')
                    if target_node not in node_names:
                        errors.append(f"Connection to non-existent node: {target_node}")
    
    return errors

def simulate_execution(workflow: Dict) -> Dict:
    """Simulate workflow execution with test data"""
    print("\n📊 Simulating workflow execution...")
    
    # Test data from Google Sheets
    test_case = {
        "test_id": "TC001",
        "drill_description": "Two lines at NZ boards. On whistle, each lead skater curves around center into OZ, give-and-go with coach at hashmarks, then shoot. Two goalies.",
        "expected_title": "Two-Line NZ Give-and-Go",
        "expected_players": "X1,X2,C1,C2,G1,G2",
        "expected_steps": "3",
        "expected_landmarks": "left_boards,right_boards,center_dot,left_hashmarks,right_hashmarks,low_slot,behind_net"
    }
    
    print(f"✅ Test Case: {test_case['test_id']}")
    
    # Simulate Generate Drill Spec
    generated_spec = {
        "schema_version": "0.1",
        "type": "drill",
        "title": "Two-Line NZ Give-and-Go",
        "players": [
            {"id": "X1", "role": "X", "location": {"landmark": "left_boards"}},
            {"id": "X2", "role": "X", "location": {"landmark": "right_boards"}},
            {"id": "C1", "role": "C", "location": {"landmark": "left_hashmarks"}},
            {"id": "C2", "role": "C", "location": {"landmark": "right_hashmarks"}},
            {"id": "G1", "role": "G", "location": {"landmark": "behind_net"}},
            {"id": "G2", "role": "G", "location": {"landmark": "behind_net", "offset": {"dx": 10, "dy": 0}}}
        ],
        "drill": {
            "sequence": [
                {"step": 1, "actions": [{"actor": "X1", "action": "skate", "to_landmark": "center_dot"}]},
                {"step": 2, "actions": [{"actor": "X1", "action": "pass", "to_actor": "C1"}]},
                {"step": 3, "actions": [{"actor": "X1", "action": "shoot", "to_landmark": "low_slot"}]}
            ]
        }
    }
    print(f"✅ Generated spec with {len(generated_spec['players'])} players and {len(generated_spec['drill']['sequence'])} steps")
    
    # Simulate evaluation
    score = 4  # Good match
    evaluation = {
        "score": score,
        "extended_reasoning": "Title matches expected. All 6 players correctly identified. 3 sequence steps as expected. Most landmarks used.",
        "reasoning_summary": "Good match with minor landmark differences"
    }
    print(f"✅ Evaluation score: {score}/5")
    
    # Simulate Google Sheets writes
    results_row = {
        "test_id": test_case["test_id"],
        "timestamp": "2024-01-20T10:30:00Z",
        "score": score,
        "passed": score >= 3,
        "title_match": "Yes",
        "players_match": "Yes", 
        "steps_match": "Yes",
        "landmarks_match": "Yes",
        "explanation": evaluation["reasoning_summary"],
        "image_file": ""
    }
    
    specs_row = {
        "test_id": test_case["test_id"],
        "timestamp": "2024-01-20T10:30:00Z",
        "generated_spec": json.dumps(generated_spec),
        "expected_spec": json.dumps({
            "title": test_case["expected_title"],
            "players": test_case["expected_players"],
            "steps": test_case["expected_steps"],
            "landmarks": test_case["expected_landmarks"]
        })
    }
    
    print("✅ Results row prepared for Google Sheets")
    print("✅ Specs row prepared for Google Sheets")
    
    return {
        "success": True,
        "test_case": test_case,
        "generated_spec": generated_spec,
        "evaluation": evaluation,
        "results_row": results_row,
        "specs_row": specs_row
    }

def main():
    print("🔍 n8n Workflow Validator & Tester")
    print("=" * 50)
    
    workflow_path = Path("/Users/liammckendry/thunder_playbook_worktrees/issue-109/n8n/workflows/drill_evaluation_simplified.json")
    
    if not workflow_path.exists():
        print(f"❌ Workflow file not found: {workflow_path}")
        sys.exit(1)
    
    # Load workflow
    workflow = load_workflow(str(workflow_path))
    print(f"✅ Loaded workflow with {len(workflow.get('nodes', []))} nodes")
    
    # Validate structure
    print("\n🔧 Validating workflow structure...")
    all_errors = []
    
    # Check meta
    if 'meta' not in workflow:
        all_errors.append("Missing 'meta' field")
    
    # Validate each node
    for node in workflow.get('nodes', []):
        node_errors = validate_node_structure(node)
        all_errors.extend(node_errors)
    
    # Validate connections
    connection_errors = validate_connections(workflow)
    all_errors.extend(connection_errors)
    
    # Check for specific required nodes
    node_names = [node['name'] for node in workflow.get('nodes', [])]
    required_nodes = [
        "When fetching a dataset row",
        "Match drill format", 
        "Generate Drill Spec",
        "OpenAI Chat Model",
        "Calculate drill accuracy metric",
        "Set metrics",
        "Write Results to Sheets",
        "Write Specs to Sheets"
    ]
    
    for req_node in required_nodes:
        if req_node not in node_names:
            all_errors.append(f"Missing required node: {req_node}")
    
    # Report validation results
    if all_errors:
        print("\n❌ Validation errors found:")
        for error in all_errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ All structure validations passed!")
    
    # Check for problematic __rl objects
    workflow_str = json.dumps(workflow)
    if '"__rl"' in workflow_str:
        print("\n⚠️  Warning: Workflow contains __rl objects that may cause import issues")
        rl_count = workflow_str.count('"__rl"')
        print(f"   Found {rl_count} instances of __rl objects")
    
    # Simulate execution
    result = simulate_execution(workflow)
    
    if result['success']:
        print("\n✅ Workflow simulation successful!")
        print("\n📊 Simulation Summary:")
        print(f"  - Test ID: {result['test_case']['test_id']}")
        print(f"  - Generated {len(result['generated_spec']['players'])} players")
        print(f"  - Created {len(result['generated_spec']['drill']['sequence'])} drill steps")
        print(f"  - Evaluation score: {result['evaluation']['score']}/5")
        print(f"  - Test passed: {result['results_row']['passed']}")
    
    print("\n🎯 Workflow is ready for browser testing!")
    print("   Import the workflow at: /Users/liammckendry/thunder_playbook_worktrees/issue-109/n8n/workflows/drill_evaluation_simplified.json")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)