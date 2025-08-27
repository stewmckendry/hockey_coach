#!/usr/bin/env python3
"""
Basic API testing script for n8n Hockey Drill Evaluation v7
Tests single test case execution via webhook API
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any, Optional

class HockeyDrillAPITester:
    """Basic API tester for hockey drill evaluation workflow"""
    
    def __init__(self, webhook_url: str, auth_token: Optional[str] = None):
        self.webhook_url = webhook_url
        self.auth_token = auth_token
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HockeyDrillAPI-Tester/1.0'
        })
        
        if auth_token:
            self.session.headers['Authorization'] = f'Bearer {auth_token}'
    
    def test_single_drill(self, test_case: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test a single drill case"""
        payload = {
            'test_case': test_case
        }
        
        if config:
            payload['config'] = config
            
        request_id = f'basic_test_{int(time.time())}'
        headers = {'X-Request-ID': request_id}
        
        print(f"Testing single drill: {test_case.get('test_id', 'unknown')}")
        print(f"Request ID: {request_id}")
        
        try:
            response = self.session.post(
                self.webhook_url, 
                json=payload, 
                headers=headers,
                timeout=60
            )
            
            print(f"Response Status: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                return self._process_response(result, response.status_code)
            else:
                return {
                    'success': False,
                    'error': 'Non-JSON response received',
                    'status_code': response.status_code,
                    'response_text': response.text[:500]
                }
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection error - check webhook URL'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Request error: {str(e)}'}
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Invalid JSON response'}
    
    def _process_response(self, result: Dict[str, Any], status_code: int) -> Dict[str, Any]:
        """Process API response"""
        if status_code == 200 and result.get('status') == 'success':
            return {
                'success': True,
                'request_id': result.get('request_id'),
                'summary': result.get('summary', {}),
                'results': result.get('results', []),
                'performance': result.get('performance', {})
            }
        else:
            return {
                'success': False,
                'error': result.get('message', 'Unknown error'),
                'error_code': result.get('error_code'),
                'status_code': status_code,
                'details': result
            }
    
    def print_results(self, response: Dict[str, Any]):
        """Print formatted test results"""
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        
        if response['success']:
            summary = response['summary']
            print(f"✅ SUCCESS - Request ID: {response.get('request_id', 'N/A')}")
            print(f"📊 Summary:")
            print(f"   Total Tests: {summary.get('total_tests', 0)}")
            print(f"   Passed: {summary.get('passed_tests', 0)}")
            print(f"   Failed: {summary.get('failed_tests', 0)}")
            print(f"   Pass Rate: {summary.get('pass_rate', '0%')}")
            print(f"   Average Score: {summary.get('average_score', '0')}")
            
            # Show individual results
            for i, result in enumerate(response['results'], 1):
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                print(f"\n🧪 Test {i}: {result['test_id']} - {status}")
                print(f"   Score: {result['score']}/100")
                print(f"   Explanation: {result['explanation']}")
                
                if result['issues']:
                    print(f"   Issues: {', '.join(result['issues'])}")
                if result['strengths']:
                    print(f"   Strengths: {', '.join(result['strengths'])}")
            
            # Performance metrics
            perf = response.get('performance', {})
            if perf:
                print(f"\n⚡ Performance:")
                print(f"   Total Time: {perf.get('total_processing_time_ms', 0)}ms")
                print(f"   Average Time: {perf.get('average_processing_time_ms', 0)}ms")
        else:
            print(f"❌ FAILED - {response['error']}")
            if response.get('error_code'):
                print(f"   Error Code: {response['error_code']}")
            if response.get('status_code'):
                print(f"   HTTP Status: {response['status_code']}")
        
        print("="*60)

def main():
    """Main test execution"""
    # Configuration
    webhook_url = os.getenv('N8N_WEBHOOK_URL', 'https://your-n8n-instance/webhook/drill-evaluation')
    auth_token = os.getenv('N8N_WEBHOOK_TOKEN')  # Optional
    
    if webhook_url == 'https://your-n8n-instance/webhook/drill-evaluation':
        print("⚠️  Please set N8N_WEBHOOK_URL environment variable")
        print("   Example: export N8N_WEBHOOK_URL='https://your-instance/webhook/drill-evaluation'")
        sys.exit(1)
    
    # Initialize tester
    tester = HockeyDrillAPITester(webhook_url, auth_token)
    
    # Test case 1: Simple passing drill
    test_case_1 = {
        'test_id': 'basic_001',
        'drill_description': 'Two players pass the puck back and forth while skating in a straight line',
        'expected_title': 'Passing Drill',
        'expected_players': 'X1,X2',
        'expected_steps': 2,
        'expected_landmarks': 'center_dot'
    }
    
    # Test configuration
    config = {
        'temperature': 0.1,
        'returnFullSpecs': True,
        'includeDebugInfo': False
    }
    
    print("🏒 Hockey Drill API Tester v1.0")
    print(f"🔗 Webhook URL: {webhook_url}")
    print(f"🔐 Authentication: {'Enabled' if auth_token else 'Disabled'}")
    
    # Run test
    response = tester.test_single_drill(test_case_1, config)
    tester.print_results(response)
    
    # Exit with appropriate code
    sys.exit(0 if response['success'] else 1)

if __name__ == '__main__':
    main()