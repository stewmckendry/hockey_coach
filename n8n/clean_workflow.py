#!/usr/bin/env python3
"""
Clean n8n workflow by removing __rl objects and fixing known issues
"""

import json
import sys
from pathlib import Path

def clean_rl_objects(obj):
    """Recursively clean __rl objects from workflow"""
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            if key == "__rl":
                continue  # Skip __rl keys
            elif isinstance(value, dict) and "__rl" in value:
                # Replace __rl structure with direct value
                if "value" in value:
                    cleaned[key] = value["value"]
                else:
                    cleaned[key] = clean_rl_objects(value)
            else:
                cleaned[key] = clean_rl_objects(value)
        return cleaned
    elif isinstance(obj, list):
        return [clean_rl_objects(item) for item in obj]
    else:
        return obj

def fix_model_names(workflow):
    """Fix model names that might cause issues"""
    workflow_str = json.dumps(workflow)
    # Replace gpt-5 with gpt-4o-mini (gpt-5 doesn't exist)
    workflow_str = workflow_str.replace('"gpt-5"', '"gpt-4o-mini"')
    return json.loads(workflow_str)

def main():
    input_file = Path("/Users/liammckendry/thunder_playbook_worktrees/issue-109/n8n/workflows/drill_evaluation_simplified.json")
    output_file = Path("/Users/liammckendry/thunder_playbook_worktrees/issue-109/n8n/workflows/drill_evaluation_clean.json")
    
    print("🧹 Cleaning n8n workflow...")
    
    # Load workflow
    with open(input_file, 'r') as f:
        workflow = json.load(f)
    
    print(f"✅ Loaded workflow with {len(workflow.get('nodes', []))} nodes")
    
    # Clean __rl objects
    workflow = clean_rl_objects(workflow)
    print("✅ Removed __rl objects")
    
    # Fix model names
    workflow = fix_model_names(workflow)
    print("✅ Fixed model names")
    
    # Ensure proper structure
    if "meta" not in workflow:
        workflow["meta"] = {
            "instanceId": "drill-eval-clean-v1",
            "templateCredsSetupCompleted": True
        }
    
    # Save cleaned workflow
    with open(output_file, 'w') as f:
        json.dump(workflow, f, indent=2)
    
    print(f"\n✅ Cleaned workflow saved to: {output_file}")
    
    # Verify no __rl remains
    with open(output_file, 'r') as f:
        content = f.read()
        if "__rl" in content:
            print("⚠️  Warning: Some __rl objects may still remain")
        else:
            print("✅ All __rl objects successfully removed")
    
    print("\n📋 Import Instructions:")
    print("1. Open n8n at http://localhost:5678")
    print("2. Go to Workflows > Import from File")
    print(f"3. Select: {output_file}")
    print("4. Configure Google Sheets credentials if needed")
    print("5. Click 'Execute Workflow' to test")

if __name__ == "__main__":
    main()