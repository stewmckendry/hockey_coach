#!/usr/bin/env python3
"""
Test n8n workflow with API authentication
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, Optional

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MzRiMTgxNy1mZTU3LTRiZjItYjE4NS00MmY5NzI5Y2M3NWQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU2MjI4NDIxLCJleHAiOjE3NTg3NzI4MDB9.1poGdQ35aOEglSKFGC8hDi75iK1HNg9O_dlQUcY42lY"

class N8NWorkflowTester:
    def __init__(self, base_url: str = "http://localhost:5678", api_key: str = API_KEY):
        """Initialize n8n API client with authentication"""
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-N8N-API-KEY": api_key
        }
    
    def check_connection(self) -> bool:
        """Check if n8n instance is accessible"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/workflows", 
                headers=self.headers, 
                timeout=5
            )
            print(f"Connection check status: {response.status_code}")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to n8n at {self.base_url}: {e}")
            return False
    
    def list_workflows(self) -> Optional[list]:
        """List all workflows"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                workflows = response.json()['data']
                print(f"✅ Found {len(workflows)} workflows")
                for wf in workflows[:5]:  # Show first 5
                    print(f"   - {wf.get('name', 'Unnamed')} (ID: {wf.get('id')})")
                return workflows
            else:
                print(f"❌ Failed to list workflows: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error listing workflows: {e}")
            return None
    
    def import_workflow(self, workflow_path: str) -> Optional[str]:
        """Import workflow into n8n"""
        try:
            with open(workflow_path, 'r') as f:
                workflow_data = json.load(f)
            
            # Set a unique name
            workflow_name = f"Drill Evaluation Test - {int(time.time())}"
            
            # Extract only the fields n8n API expects
            api_workflow = {
                "name": workflow_name,
                "nodes": workflow_data.get("nodes", []),
                "connections": workflow_data.get("connections", {}),
                "settings": workflow_data.get("settings", {"executionOrder": "v1"}),
                "staticData": workflow_data.get("staticData")
            }
            
            # Remove None values
            api_workflow = {k: v for k, v in api_workflow.items() if v is not None}
            
            # Create workflow via API
            response = requests.post(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                json=api_workflow,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                # Handle different response formats
                if 'data' in result:
                    workflow = result['data']
                else:
                    workflow = result  # Direct response
                
                print(f"✅ Workflow imported successfully!")
                print(f"   Name: {workflow.get('name')}")
                print(f"   ID: {workflow.get('id')}")
                return workflow.get('id')
            else:
                print(f"❌ Failed to import workflow: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"❌ Error importing workflow: {e}")
            return None
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow"""
        try:
            response = requests.patch(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json={"active": True},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Workflow {workflow_id} activated")
                return True
            else:
                print(f"❌ Failed to activate workflow: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error activating workflow: {e}")
            return False
    
    def execute_workflow(self, workflow_id: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Execute a workflow via API"""
        try:
            # For manual trigger workflows
            payload = {}
            if data:
                payload = {"body": data}
            
            response = requests.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Workflow execution started")
                
                # If we get an execution ID, check its status
                if 'data' in result and 'executionId' in result['data']:
                    exec_id = result['data']['executionId']
                    print(f"   Execution ID: {exec_id}")
                    
                    # Wait a bit and check status
                    time.sleep(3)
                    exec_result = self.get_execution(exec_id)
                    if exec_result:
                        print(f"   Status: {exec_result.get('status', 'unknown')}")
                
                return result
            else:
                print(f"❌ Failed to execute workflow: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"❌ Error executing workflow: {e}")
            return None
    
    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get execution details"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/executions/{execution_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                return None
                
        except Exception as e:
            print(f"Error getting execution: {e}")
            return None
    
    def test_webhook_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Test workflow with webhook/form trigger"""
        try:
            # Get workflow details to find webhook URL
            response = requests.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                workflow = response.json()['data']
                print(f"✅ Retrieved workflow details")
                
                # Look for webhook nodes
                for node in workflow.get('nodes', []):
                    if 'webhook' in node.get('type', '').lower():
                        webhook_id = node.get('webhookId') or node.get('parameters', {}).get('path')
                        if webhook_id:
                            webhook_url = f"{self.base_url}/webhook/{webhook_id}"
                            print(f"   Found webhook: {webhook_url}")
                            
                            # Test the webhook
                            test_data = {
                                "test_id": "TC001",
                                "drill_description": "Test drill description"
                            }
                            
                            webhook_response = requests.post(
                                webhook_url,
                                json=test_data,
                                timeout=30
                            )
                            
                            if webhook_response.status_code == 200:
                                print(f"✅ Webhook triggered successfully")
                                return webhook_response.json()
                            else:
                                print(f"❌ Webhook failed: {webhook_response.status_code}")
                
                print("⚠️  No webhook found in workflow")
                return None
            else:
                print(f"❌ Failed to get workflow details: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error testing webhook: {e}")
            return None
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
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


def main():
    print("🔍 n8n Workflow API Tester (with Authentication)")
    print("=" * 50)
    
    tester = N8NWorkflowTester()
    
    print("\n🔌 Checking n8n connection...")
    if not tester.check_connection():
        print("\n❌ Cannot connect to n8n")
        print("   Please ensure n8n is running at http://localhost:5678")
        return False
    
    print("✅ Connected to n8n successfully!")
    
    # List existing workflows
    print("\n📋 Listing existing workflows...")
    tester.list_workflows()
    
    # Import the cleaned workflow
    workflow_path = "/Users/liammckendry/thunder_playbook_worktrees/issue-109/n8n/workflows/drill_evaluation_clean.json"
    
    print(f"\n📤 Importing workflow from: {Path(workflow_path).name}")
    workflow_id = tester.import_workflow(workflow_path)
    
    if not workflow_id:
        print("\n❌ Failed to import workflow")
        return False
    
    # Try to activate it
    print(f"\n🚀 Activating workflow...")
    if tester.activate_workflow(workflow_id):
        print("✅ Workflow is active")
    
    # Try different execution methods
    print("\n🎯 Testing workflow execution...")
    
    # Method 1: Direct execution (for manual trigger workflows)
    print("\n1️⃣ Attempting direct execution...")
    result = tester.execute_workflow(workflow_id)
    
    if not result:
        # Method 2: Webhook execution
        print("\n2️⃣ Attempting webhook execution...")
        result = tester.test_webhook_workflow(workflow_id)
    
    if not result:
        print("\n⚠️  Note: Evaluation trigger workflows cannot be executed via API")
        print("   They must be triggered through the n8n UI")
        print("\n📋 Next Steps:")
        print(f"   1. Open n8n at http://localhost:5678")
        print(f"   2. Find workflow: 'Drill Evaluation Test - {workflow_id}'")
        print(f"   3. Open the workflow")
        print(f"   4. Click 'Execute Workflow' button")
        print(f"   5. The evaluation will fetch data from Google Sheets")
    
    # Optional: Clean up
    print("\n🧹 Keeping workflow for manual testing...")
    print(f"   Workflow ID: {workflow_id}")
    print("   To delete later, use the n8n UI or API")
    
    return True


if __name__ == "__main__":
    success = main()