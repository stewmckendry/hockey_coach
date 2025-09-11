#!/usr/bin/env python3
"""
Test n8n workflow by executing it via n8n API
Requires n8n instance running locally
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, Optional

class N8NWorkflowTester:
    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """
        Initialize n8n API client
        
        Args:
            base_url: n8n instance URL (default: http://localhost:5678)
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if api_key:
            self.headers["X-N8N-API-KEY"] = api_key
    
    def check_connection(self) -> bool:
        """Check if n8n instance is accessible"""
        try:
            response = requests.get(f"{self.base_url}/rest/workflows", headers=self.headers, timeout=5)
            return response.status_code in [200, 401]  # 401 means auth required but server is up
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to n8n at {self.base_url}: {e}")
            return False
    
    def import_workflow(self, workflow_path: str) -> Optional[str]:
        """
        Import workflow into n8n
        
        Args:
            workflow_path: Path to workflow JSON file
            
        Returns:
            Workflow ID if successful, None otherwise
        """
        try:
            with open(workflow_path, 'r') as f:
                workflow_data = json.load(f)
            
            # Clean up workflow for import
            if 'id' in workflow_data:
                del workflow_data['id']  # Let n8n assign new ID
            
            # Set a unique name to avoid conflicts
            workflow_data['name'] = f"Test Drill Evaluation - {int(time.time())}"
            
            # Create workflow via API
            response = requests.post(
                f"{self.base_url}/rest/workflows",
                headers=self.headers,
                json=workflow_data,
                timeout=10
            )
            
            if response.status_code == 201:
                workflow = response.json()
                print(f"✅ Workflow imported with ID: {workflow['id']}")
                return workflow['id']
            else:
                print(f"❌ Failed to import workflow: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error importing workflow: {e}")
            return None
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow"""
        try:
            response = requests.patch(
                f"{self.base_url}/rest/workflows/{workflow_id}",
                headers=self.headers,
                json={"active": True},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Workflow {workflow_id} activated")
                return True
            else:
                print(f"❌ Failed to activate workflow: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error activating workflow: {e}")
            return False
    
    def execute_workflow(self, workflow_id: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Execute a workflow
        
        Args:
            workflow_id: ID of workflow to execute
            data: Optional input data for workflow
            
        Returns:
            Execution result if successful
        """
        try:
            # Execute workflow
            payload = {"workflowData": {"nodes": [], "connections": {}}}
            if data:
                payload["data"] = data
            
            response = requests.post(
                f"{self.base_url}/rest/workflows/{workflow_id}/execute",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Workflow executed successfully")
                return result
            else:
                print(f"❌ Failed to execute workflow: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error executing workflow: {e}")
            return None
    
    def get_executions(self, workflow_id: str) -> Optional[list]:
        """Get workflow executions"""
        try:
            response = requests.get(
                f"{self.base_url}/rest/executions",
                headers=self.headers,
                params={"workflowId": workflow_id},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                print(f"❌ Failed to get executions: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting executions: {e}")
            return None
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        try:
            response = requests.delete(
                f"{self.base_url}/rest/workflows/{workflow_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ Workflow {workflow_id} deleted")
                return True
            else:
                print(f"⚠️  Could not delete workflow: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️  Error deleting workflow: {e}")
            return False


def test_manual_execution():
    """Test workflow using manual trigger approach"""
    print("\n📋 Manual Execution Test")
    print("=" * 50)
    
    # Test data
    test_data = {
        "test_id": "TC001",
        "drill_description": "Two lines at NZ boards. On whistle, each lead skater curves around center into OZ, give-and-go with coach at hashmarks, then shoot. Two goalies.",
        "expected_title": "Two-Line NZ Give-and-Go",
        "expected_players": "X1,X2,C1,C2,G1,G2",
        "expected_steps": "3",
        "expected_landmarks": "left_boards,right_boards,center_dot,left_hashmarks,right_hashmarks,low_slot,behind_net"
    }
    
    print("\n📊 Test Data:")
    print(f"  Test ID: {test_data['test_id']}")
    print(f"  Drill: {test_data['drill_description'][:50]}...")
    
    print("\n⚠️  Manual steps required:")
    print("1. Open n8n at http://localhost:5678")
    print("2. Import workflow: drill_evaluation_simplified.json")
    print("3. Open the workflow and click 'Execute Workflow'")
    print("4. The evaluation trigger will fetch data from Google Sheets")
    print("5. Results will be written back to the Results and Specs tabs")
    
    return True


def main():
    print("🔍 n8n Workflow API Tester")
    print("=" * 50)
    
    # Check if n8n is running
    tester = N8NWorkflowTester()
    
    print("\n🔌 Checking n8n connection...")
    if not tester.check_connection():
        print("\n⚠️  n8n is not running or not accessible")
        print("   Please start n8n with: npx n8n start")
        print("\n   Or use Docker:")
        print("   docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n")
        
        # Fallback to manual testing
        return test_manual_execution()
    
    print("✅ n8n is accessible")
    
    # Try to import and execute workflow
    workflow_path = "/Users/liammckendry/thunder_playbook_worktrees/issue-109/n8n/workflows/drill_evaluation_simplified.json"
    
    print(f"\n📤 Importing workflow...")
    workflow_id = tester.import_workflow(workflow_path)
    
    if workflow_id:
        print(f"\n🚀 Attempting to execute workflow {workflow_id}...")
        
        # Note: Execution via API might not work for evaluation trigger workflows
        # They typically need to be triggered through the UI
        result = tester.execute_workflow(workflow_id)
        
        if result:
            print("\n📊 Execution Result:")
            print(json.dumps(result, indent=2)[:500])  # Show first 500 chars
        else:
            print("\n⚠️  Could not execute via API (evaluation trigger workflows need UI)")
            print("   Please execute manually in n8n UI")
        
        # Clean up
        print("\n🧹 Cleaning up...")
        tester.delete_workflow(workflow_id)
    else:
        print("\n❌ Could not import workflow")
        return test_manual_execution()
    
    return True


if __name__ == "__main__":
    main()