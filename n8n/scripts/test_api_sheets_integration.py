#!/usr/bin/env python3
"""
Google Sheets Integration API testing script for n8n Hockey Drill Evaluation v8
Demonstrates all Google Sheets modes with comprehensive error handling and reporting
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class TestConfig:
    """Configuration for API testing"""
    webhook_url: str
    auth_token: Optional[str] = None
    timeout: int = 120
    max_retries: int = 3
    retry_delay: float = 1.0

class SheetsAPITester:
    """Google Sheets integration API tester for hockey drill evaluation workflow v8"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HockeyDrillAPI-SheetsIntegration-Tester/1.0'
        })
        
        if config.auth_token:
            self.session.headers['Authorization'] = f'Bearer {config.auth_token}'
    
    def test_sheets_specific_ids(self, test_ids: List[str], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test specific test IDs from Google Sheets (Mode 2)"""
        payload = {
            'source': 'google_sheets',
            'test_ids': test_ids
        }
        
        if config:
            payload['config'] = config
            
        request_id = f'sheets_ids_{int(time.time())}'
        headers = {'X-Request-ID': request_id}
        
        print(f"🔍 Testing specific test IDs from Google Sheets: {', '.join(test_ids)}")
        print(f"📋 Request ID: {request_id}")
        
        return self._make_request(payload, headers, f"specific IDs ({len(test_ids)} tests)")
    
    def test_sheets_run_all(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test running all tests from Google Sheets (Mode 3)"""
        payload = {
            'source': 'google_sheets',
            'run_all': True
        }
        
        if config:
            payload['config'] = config
            
        request_id = f'sheets_all_{int(time.time())}'
        headers = {'X-Request-ID': request_id}
        
        print(f"📊 Testing run all tests from Google Sheets")
        print(f"📋 Request ID: {request_id}")
        
        return self._make_request(payload, headers, "run all tests")
    
    def test_sheets_filtered(self, filter_criteria: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test filtered tests from Google Sheets (Mode 4)"""
        payload = {
            'source': 'google_sheets',
            'filter': filter_criteria
        }
        
        if config:
            payload['config'] = config
            
        request_id = f'sheets_filter_{int(time.time())}'
        headers = {'X-Request-ID': request_id}
        
        print(f"🎯 Testing filtered tests from Google Sheets")
        print(f"🔍 Filter: {json.dumps(filter_criteria, indent=2)}\")\n        print(f"📋 Request ID: {request_id}")
        
        return self._make_request(payload, headers, f"filtered tests ({len(filter_criteria)} criteria)")
    
    def test_sheets_custom_sheet(self, sheet_name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test using custom sheet name (Mode 5)"""
        payload = {
            'source': 'google_sheets',
            'run_all': True,
            'sheet_name': sheet_name
        }
        
        if config:
            payload['config'] = config
        
        # Also add sheet name to config for double coverage
        if 'config' not in payload:
            payload['config'] = {}
        payload['config']['testSheetName'] = sheet_name
            
        request_id = f'sheets_custom_{int(time.time())}'
        headers = {'X-Request-ID': request_id}
        
        print(f"📋 Testing custom sheet name: '{sheet_name}'")
        print(f"📋 Request ID: {request_id}")
        
        return self._make_request(payload, headers, f"custom sheet '{sheet_name}'")
    
    def test_direct_api_compatibility(self, test_case: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test direct API mode for v7 compatibility (Mode 1)"""
        payload = {
            'test_case': test_case
        }
        
        if config:
            payload['config'] = config
            
        request_id = f'direct_compat_{int(time.time())}'
        headers = {'X-Request-ID': request_id}
        
        print(f"🔌 Testing direct API compatibility (v7 mode)")
        print(f"🧪 Test ID: {test_case.get('test_id', 'unknown')}")
        print(f"📋 Request ID: {request_id}")
        
        return self._make_request(payload, headers, "direct API compatibility")
    
    def _make_request(self, payload: Dict[str, Any], headers: Dict[str, str], description: str) -> Dict[str, Any]:
        """Make HTTP request with retry logic and comprehensive error handling"""
        
        for attempt in range(1, self.config.max_retries + 1):
            try:
                print(f"🚀 Sending request (attempt {attempt}/{self.config.max_retries})...")
                
                response = self.session.post(
                    self.config.webhook_url, 
                    json=payload, 
                    headers=headers,
                    timeout=self.config.timeout
                )
                
                print(f"📡 Response Status: {response.status_code}")
                
                if response.headers.get('content-type', '').startswith('application/json'):
                    result = response.json()
                    return self._process_response(result, response.status_code, description)
                else:
                    return {
                        'success': False,
                        'error': 'Non-JSON response received',
                        'status_code': response.status_code,
                        'response_text': response.text[:500],
                        'description': description
                    }
                    
            except requests.exceptions.Timeout:
                error_msg = f'Request timeout (>{self.config.timeout}s) on attempt {attempt}'
                print(f"⏱️ {error_msg}")
                if attempt < self.config.max_retries:
                    print(f"⏳ Retrying in {self.config.retry_delay}s...")
                    time.sleep(self.config.retry_delay)
                    self.config.retry_delay *= 2  # Exponential backoff
                else:
                    return {'success': False, 'error': error_msg, 'description': description}
                    
            except requests.exceptions.ConnectionError:
                error_msg = f'Connection error on attempt {attempt} - check webhook URL'
                print(f"🔌 {error_msg}")
                if attempt < self.config.max_retries:
                    print(f"⏳ Retrying in {self.config.retry_delay}s...")
                    time.sleep(self.config.retry_delay)
                else:
                    return {'success': False, 'error': error_msg, 'description': description}
                    
            except requests.exceptions.RequestException as e:
                error_msg = f'Request error on attempt {attempt}: {str(e)}'
                print(f"❌ {error_msg}")
                if attempt < self.config.max_retries:
                    print(f"⏳ Retrying in {self.config.retry_delay}s...")
                    time.sleep(self.config.retry_delay)
                else:
                    return {'success': False, 'error': error_msg, 'description': description}
                    
            except json.JSONDecodeError:
                return {'success': False, 'error': 'Invalid JSON response', 'description': description}
        
        return {'success': False, 'error': 'All retry attempts failed', 'description': description}
    
    def _process_response(self, result: Dict[str, Any], status_code: int, description: str) -> Dict[str, Any]:
        """Process API response with v8 enhancements"""
        if status_code == 200 and result.get('status') == 'success':
            return {
                'success': True,
                'request_id': result.get('request_id'),
                'workflow_info': result.get('workflow', {}),
                'summary': result.get('summary', {}),
                'source_info': result.get('source_info', {}),
                'results': result.get('results', []),
                'performance': result.get('performance', {}),
                'v8_features': result.get('v8_features', {}),
                'description': description
            }
        else:
            return {
                'success': False,
                'error': result.get('message', 'Unknown error'),
                'error_code': result.get('error_code'),
                'status_code': status_code,
                'details': result,
                'description': description
            }
    
    def print_results(self, response: Dict[str, Any]):
        """Print formatted test results with v8 enhancements"""
        print("\n" + "="*80)
        print(f"TEST RESULTS - {response.get('description', 'Unknown Test').upper()}")
        print("="*80)
        
        if response['success']:
            # Workflow and source information
            workflow_info = response.get('workflow_info', {})
            source_info = response.get('source_info', {})
            
            print(f"✅ SUCCESS - Request ID: {response.get('request_id', 'N/A')}")
            print(f"🔧 Workflow: {workflow_info.get('id', 'N/A')} v{workflow_info.get('version', 'N/A')}")
            print(f"📊 Data Source: {workflow_info.get('data_source', source_info.get('data_source', 'N/A'))}")
            
            # Summary information
            summary = response.get('summary', {})
            print(f"📈 Summary:")
            print(f"   Total Tests: {summary.get('total_tests', 0)}")
            print(f"   Passed: {summary.get('passed_tests', 0)}")
            print(f"   Failed: {summary.get('failed_tests', 0)}")
            print(f"   Pass Rate: {summary.get('pass_rate', '0%')}")
            print(f"   Average Score: {summary.get('average_score', '0')}")
            
            # Source breakdown (v8 feature)
            if source_info:
                print(f"📊 Source Breakdown:")
                print(f"   Direct API Tests: {source_info.get('direct_api_tests', 0)}")
                print(f"   Google Sheets Tests: {source_info.get('google_sheets_tests', 0)}")
                
                # Show sheets mode if applicable
                sheets_mode = source_info.get('sheets_mode')
                if sheets_mode:
                    print(f"   Sheets Mode: {self._format_sheets_mode(sheets_mode)}")
            
            # Individual test results
            results = response.get('results', [])
            for i, result in enumerate(results, 1):
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                source_emoji = "📊" if result.get('source') == 'google_sheets' else "🔌"
                
                print(f"\n🧪 Test {i}: {result['test_id']} - {status} [{source_emoji}]")
                print(f"   Score: {result['score']}/100")
                print(f"   Processing Mode: {result.get('processing_mode', 'N/A')}")
                print(f"   Explanation: {result['explanation']}")
                
                if result.get('sheets_filter_applied'):
                    print(f"   Sheets Filter: {result['sheets_filter_applied']}")
                
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
                
                processing_modes = perf.get('processing_modes', {})
                if processing_modes:
                    print(f"   Processing Modes: {processing_modes}")
            
            # v8 Features confirmation
            v8_features = response.get('v8_features', {})
            if v8_features:
                print(f"\n🆕 v8 Features:")
                for feature, enabled in v8_features.items():
                    status = "✅" if enabled else "❌"
                    print(f"   {status} {feature.replace('_', ' ').title()}")
                    
        else:
            print(f"❌ FAILED - {response['error']}")
            if response.get('error_code'):
                print(f"   Error Code: {response['error_code']}")
            if response.get('status_code'):
                print(f"   HTTP Status: {response['status_code']}")
            
            # Show additional error details for debugging
            if response.get('details'):
                details = response['details']
                if isinstance(details, dict) and 'recommendations' in details:
                    print(f"   Recommendations:")
                    for rec in details['recommendations']:
                        print(f"     • {rec}")
        
        print("="*80)
    
    def _format_sheets_mode(self, sheets_mode: Dict[str, Any]) -> str:
        """Format sheets mode information for display"""
        if sheets_mode.get('run_all'):
            return "Run All"
        elif sheets_mode.get('test_ids'):
            ids = sheets_mode['test_ids']
            if len(ids) <= 3:
                return f"Specific IDs: {', '.join(ids)}"
            else:
                return f"Specific IDs: {', '.join(ids[:3])}, ... (+{len(ids)-3} more)"
        elif sheets_mode.get('filter'):
            filter_items = list(sheets_mode['filter'].items())
            if len(filter_items) <= 2:
                return f"Filter: {dict(filter_items)}"
            else:
                return f"Filter: {dict(filter_items[:2])}, ... (+{len(filter_items)-2} more)"
        else:
            return "Unknown"

def run_comprehensive_test_suite():
    """Run comprehensive test suite demonstrating all v8 features"""
    
    # Configuration
    webhook_url = os.getenv('N8N_WEBHOOK_URL', 'https://your-n8n-instance/webhook/drill-evaluation')
    auth_token = os.getenv('N8N_WEBHOOK_TOKEN')  # Optional
    
    if webhook_url == 'https://your-n8n-instance/webhook/drill-evaluation':
        print("⚠️  Please set N8N_WEBHOOK_URL environment variable")
        print("   Example: export N8N_WEBHOOK_URL='https://your-instance/webhook/drill-evaluation'")
        sys.exit(1)
    
    # Initialize tester
    config = TestConfig(webhook_url=webhook_url, auth_token=auth_token, timeout=180)
    tester = SheetsAPITester(config)
    
    print("🏒 Hockey Drill API v8 - Google Sheets Integration Tester")
    print(f"🔗 Webhook URL: {webhook_url}")
    print(f"🔐 Authentication: {'Enabled' if auth_token else 'Disabled'}")
    print(f"⏱️ Timeout: {config.timeout}s")
    
    # Test results storage
    test_results = []
    
    # Test 1: Direct API compatibility (Mode 1)
    print("\n" + "🔌 TEST 1: DIRECT API COMPATIBILITY (V7 MODE)" + "\n" + "-"*50)
    direct_test_case = {
        'test_id': 'compat_001',
        'drill_description': 'Two players pass the puck back and forth while skating in opposite directions around center ice',
        'expected_title': 'Center Ice Passing',
        'expected_players': 'X1,X2',
        'expected_steps': 2,
        'expected_landmarks': 'center_dot'
    }
    
    direct_config = {
        'temperature': 0.1,
        'returnFullSpecs': False,
        'includeDebugInfo': True
    }
    
    result = tester.test_direct_api_compatibility(direct_test_case, direct_config)
    tester.print_results(result)
    test_results.append(('Direct API Compatibility', result['success']))
    
    # Test 2: Google Sheets - Specific Test IDs (Mode 2)
    print("\n" + "📋 TEST 2: GOOGLE SHEETS - SPECIFIC TEST IDS" + "\n" + "-"*50)
    sheets_config = {
        'batchSize': 5,
        'returnFullSpecs': False,
        'includeDebugInfo': True
    }
    
    result = tester.test_sheets_specific_ids(['TC001', 'TC002'], sheets_config)
    tester.print_results(result)
    test_results.append(('Google Sheets - Specific IDs', result['success']))
    
    # Test 3: Google Sheets - Run All Tests (Mode 3) 
    print("\n" + "📊 TEST 3: GOOGLE SHEETS - RUN ALL TESTS" + "\n" + "-"*50)
    run_all_config = {
        'batchSize': 10,
        'sheetsReadLimit': 50,
        'returnFullSpecs': False
    }
    
    result = tester.test_sheets_run_all(run_all_config)
    tester.print_results(result)
    test_results.append(('Google Sheets - Run All', result['success']))
    
    # Test 4: Google Sheets - Filtered Tests (Mode 4)
    print("\n" + "🎯 TEST 4: GOOGLE SHEETS - FILTERED TESTS" + "\n" + "-"*50)
    filter_criteria = {
        'status': 'active',
        'priority': 'high'
    }
    
    filter_config = {
        'batchSize': 8,
        'returnFullSpecs': False,
        'includeDebugInfo': True
    }
    
    result = tester.test_sheets_filtered(filter_criteria, filter_config)
    tester.print_results(result)
    test_results.append(('Google Sheets - Filtered', result['success']))
    
    # Test 5: Google Sheets - Custom Sheet Name (Mode 5)
    print("\n" + "📋 TEST 5: GOOGLE SHEETS - CUSTOM SHEET NAME" + "\n" + "-"*50)
    custom_sheet_config = {
        'batchSize': 5,
        'returnFullSpecs': False
    }
    
    result = tester.test_sheets_custom_sheet('Test Cases', custom_sheet_config)  # Using default name for demo
    tester.print_results(result)
    test_results.append(('Google Sheets - Custom Sheet', result['success']))
    
    # Final Summary
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUITE SUMMARY")
    print("="*80)
    
    successful_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 Overall Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Successful: {successful_tests}")
    print(f"   Failed: {total_tests - successful_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 Individual Test Results:")
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🏒 Hockey Drill API v8 - Google Sheets Integration Testing Complete")
    
    # Exit with appropriate code
    sys.exit(0 if successful_tests == total_tests else 1)

def main():
    """Main execution function"""
    try:
        run_comprehensive_test_suite()
    except KeyboardInterrupt:
        print("\n\n🛑 Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()