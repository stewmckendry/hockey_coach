#!/usr/bin/env python3
"""
Batch API testing script for n8n Hockey Drill Evaluation v7
Tests multiple test cases in batch mode with comprehensive reporting
"""

import requests
import json
import time
import sys
import os
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
import argparse

class HockeyDrillBatchTester:
    """Batch API tester for hockey drill evaluation workflow"""
    
    def __init__(self, webhook_url: str, auth_token: Optional[str] = None):
        self.webhook_url = webhook_url
        self.auth_token = auth_token
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HockeyDrillAPI-BatchTester/1.0'
        })
        
        if auth_token:
            self.session.headers['Authorization'] = f'Bearer {auth_token}'
    
    def load_test_cases_from_csv(self, csv_file: str) -> List[Dict[str, Any]]:
        """Load test cases from CSV file"""
        test_cases = []
        
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert CSV row to test case format
                    test_case = {
                        'test_id': row.get('test_id', f'csv_{len(test_cases) + 1}'),
                        'drill_description': row['drill_description']
                    }
                    
                    # Add optional expected values
                    if row.get('expected_title'):
                        test_case['expected_title'] = row['expected_title']
                    if row.get('expected_players'):
                        test_case['expected_players'] = row['expected_players']
                    if row.get('expected_steps'):
                        try:
                            test_case['expected_steps'] = int(row['expected_steps'])
                        except ValueError:
                            pass
                    if row.get('expected_landmarks'):
                        test_case['expected_landmarks'] = row['expected_landmarks']
                    
                    test_cases.append(test_case)
                    
        except FileNotFoundError:
            print(f"❌ Test cases file not found: {csv_file}")
            return []
        except Exception as e:
            print(f"❌ Error reading test cases: {e}")
            return []
            
        return test_cases
    
    def create_default_test_cases(self) -> List[Dict[str, Any]]:
        """Create default test cases for demonstration"""
        return [
            {
                'test_id': 'batch_001',
                'drill_description': 'Three players form a triangle and pass the puck clockwise',
                'expected_title': 'Triangle Passing',
                'expected_players': 'X1,X2,X3',
                'expected_steps': 3,
                'expected_landmarks': 'center_dot'
            },
            {
                'test_id': 'batch_002',
                'drill_description': 'Two goalies practice passing to each other behind the net',
                'expected_players': 'G1,G2',
                'expected_landmarks': 'behind_net'
            },
            {
                'test_id': 'batch_003',
                'drill_description': 'One player skates figure-8 around center ice while coach watches',
                'expected_players': 'X1,C1',
                'expected_landmarks': 'center_dot'
            },
            {
                'test_id': 'batch_004',
                'drill_description': 'Power play setup drill with four players and one goalie in low slot',
                'expected_players': 'X1,X2,X3,X4,G1',
                'expected_landmarks': 'low_slot'
            },
            {
                'test_id': 'batch_005',
                'drill_description': 'Simple shooting drill from the hash marks',
                'expected_landmarks': 'left_hashmarks,right_hashmarks'
            }
        ]
    
    def test_batch(self, test_cases: List[Dict[str, Any]], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test multiple drill cases in batch"""
        payload = {
            'test_cases': test_cases
        }
        
        if config:
            payload['config'] = config
            
        request_id = f'batch_test_{int(time.time())}'
        headers = {'X-Request-ID': request_id}
        
        print(f"Testing batch of {len(test_cases)} drill cases")
        print(f"Request ID: {request_id}")
        
        start_time = time.time()
        
        try:
            response = self.session.post(
                self.webhook_url, 
                json=payload, 
                headers=headers,
                timeout=300  # 5 minute timeout for batch processing
            )
            
            processing_time = (time.time() - start_time) * 1000
            print(f"Response Status: {response.status_code}")
            print(f"Total Request Time: {processing_time:.2f}ms")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                result['client_processing_time_ms'] = processing_time
                return self._process_batch_response(result, response.status_code)
            else:
                return {
                    'success': False,
                    'error': 'Non-JSON response received',
                    'status_code': response.status_code,
                    'response_text': response.text[:1000]
                }
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout (5 minutes exceeded)'}\n        except requests.exceptions.ConnectionError:\n            return {'success': False, 'error': 'Connection error - check webhook URL'}\n        except requests.exceptions.RequestException as e:\n            return {'success': False, 'error': f'Request error: {str(e)}'}\n        except json.JSONDecodeError:\n            return {'success': False, 'error': 'Invalid JSON response'}\n    \n    def _process_batch_response(self, result: Dict[str, Any], status_code: int) -> Dict[str, Any]:\n        \"\"\"Process batch API response\"\"\"\n        if status_code == 200 and result.get('status') == 'success':\n            return {\n                'success': True,\n                'request_id': result.get('request_id'),\n                'summary': result.get('summary', {}),\n                'results': result.get('results', []),\n                'performance': result.get('performance', {}),\n                'client_processing_time_ms': result.get('client_processing_time_ms', 0),\n                'recommendations': result.get('recommendations', [])\n            }\n        else:\n            return {\n                'success': False,\n                'error': result.get('message', 'Unknown error'),\n                'error_code': result.get('error_code'),\n                'status_code': status_code,\n                'details': result\n            }\n    \n    def generate_report(self, response: Dict[str, Any], output_file: Optional[str] = None):\n        \"\"\"Generate comprehensive test report\"\"\"\n        report_lines = []\n        \n        report_lines.append(\"=\"*80)\n        report_lines.append(\"HOCKEY DRILL BATCH TEST REPORT\")\n        report_lines.append(\"=\"*80)\n        report_lines.append(f\"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\")\n        report_lines.append(f\"Request ID: {response.get('request_id', 'N/A')}\")\n        report_lines.append(\"\")\n        \n        if response['success']:\n            summary = response['summary']\n            report_lines.extend([\n                \"📊 OVERALL RESULTS:\",\n                f\"   Status: ✅ SUCCESS\",\n                f\"   Total Tests: {summary.get('total_tests', 0)}\",\n                f\"   Passed: {summary.get('passed_tests', 0)}\",\n                f\"   Failed: {summary.get('failed_tests', 0)}\",\n                f\"   Pass Rate: {summary.get('pass_rate', '0%')}\",\n                f\"   Average Score: {summary.get('average_score', '0')}\",\n                \"\"\n            ])\n            \n            # Performance metrics\n            perf = response.get('performance', {})\n            report_lines.extend([\n                \"⚡ PERFORMANCE METRICS:\",\n                f\"   Server Processing Time: {perf.get('total_processing_time_ms', 0)}ms\",\n                f\"   Average Per Test: {perf.get('average_processing_time_ms', 0)}ms\",\n                f\"   Client Request Time: {response.get('client_processing_time_ms', 0):.2f}ms\",\n                \"\"\n            ])\n            \n            # Individual test results\n            report_lines.append(\"🧪 INDIVIDUAL TEST RESULTS:\")\n            report_lines.append(\"-\" * 60)\n            \n            for i, result in enumerate(response['results'], 1):\n                status = \"✅ PASS\" if result['passed'] else \"❌ FAIL\"\n                report_lines.extend([\n                    f\"Test {i}: {result['test_id']} - {status} ({result['score']}/100)\",\n                    f\"   Description: {result['drill_description'][:80]}...\",\n                    f\"   Explanation: {result['explanation']}\"\n                ])\n                \n                if result['issues']:\n                    report_lines.append(f\"   Issues: {', '.join(result['issues'])}\")\n                if result['strengths']:\n                    report_lines.append(f\"   Strengths: {', '.join(result['strengths'])}\")\n                    \n                report_lines.append(\"\")\n            \n            # Recommendations\n            recommendations = response.get('recommendations', [])\n            if recommendations:\n                report_lines.extend([\n                    \"💡 RECOMMENDATIONS:\",\n                    *[f\"   • {rec}\" for rec in recommendations],\n                    \"\"\n                ])\n        else:\n            report_lines.extend([\n                \"❌ BATCH TEST FAILED\",\n                f\"   Error: {response['error']}\",\n                f\"   Error Code: {response.get('error_code', 'N/A')}\",\n                f\"   HTTP Status: {response.get('status_code', 'N/A')}\",\n                \"\"\n            ])\n        \n        report_lines.append(\"=\"*80)\n        \n        # Print report\n        report_text = \"\\n\".join(report_lines)\n        print(report_text)\n        \n        # Save to file if requested\n        if output_file:\n            try:\n                with open(output_file, 'w', encoding='utf-8') as f:\n                    f.write(report_text)\n                print(f\"\\n📄 Report saved to: {output_file}\")\n            except Exception as e:\n                print(f\"\\n⚠️  Failed to save report: {e}\")\n    \n    def save_results_csv(self, response: Dict[str, Any], csv_file: str):\n        \"\"\"Save detailed results to CSV file\"\"\"\n        if not response['success']:\n            print(\"❌ Cannot save CSV - test failed\")\n            return\n        \n        try:\n            with open(csv_file, 'w', newline='', encoding='utf-8') as f:\n                fieldnames = [\n                    'test_id', 'drill_description', 'score', 'passed', \n                    'explanation', 'issues', 'strengths', 'timestamp'\n                ]\n                writer = csv.DictWriter(f, fieldnames=fieldnames)\n                writer.writeheader()\n                \n                for result in response['results']:\n                    writer.writerow({\n                        'test_id': result['test_id'],\n                        'drill_description': result['drill_description'],\n                        'score': result['score'],\n                        'passed': result['passed'],\n                        'explanation': result['explanation'],\n                        'issues': '; '.join(result['issues']) if result['issues'] else '',\n                        'strengths': '; '.join(result['strengths']) if result['strengths'] else '',\n                        'timestamp': datetime.now().isoformat()\n                    })\n            \n            print(f\"📊 Results saved to CSV: {csv_file}\")\n            \n        except Exception as e:\n            print(f\"⚠️  Failed to save CSV: {e}\")\n\ndef create_sample_csv():\n    \"\"\"Create a sample CSV file with test cases\"\"\"\n    sample_file = 'sample_test_cases.csv'\n    \n    sample_data = [\n        {\n            'test_id': 'csv_001',\n            'drill_description': 'Two players skate around center ice in opposite directions',\n            'expected_title': 'Center Ice Skating',\n            'expected_players': 'X1,X2',\n            'expected_steps': '2',\n            'expected_landmarks': 'center_dot'\n        },\n        {\n            'test_id': 'csv_002',\n            'drill_description': 'Three players form triangle passing pattern with coach',\n            'expected_title': 'Triangle Passing Drill',\n            'expected_players': 'X1,X2,X3,C1',\n            'expected_steps': '4',\n            'expected_landmarks': 'center_dot'\n        },\n        {\n            'test_id': 'csv_003',\n            'drill_description': 'Goalie practices rebound control with two forwards',\n            'expected_players': 'G1,X1,X2',\n            'expected_landmarks': 'low_slot,behind_net'\n        }\n    ]\n    \n    try:\n        with open(sample_file, 'w', newline='', encoding='utf-8') as f:\n            fieldnames = ['test_id', 'drill_description', 'expected_title', \n                         'expected_players', 'expected_steps', 'expected_landmarks']\n            writer = csv.DictWriter(f, fieldnames=fieldnames)\n            writer.writeheader()\n            writer.writerows(sample_data)\n        \n        print(f\"📄 Sample CSV created: {sample_file}\")\n        return sample_file\n        \n    except Exception as e:\n        print(f\"⚠️  Failed to create sample CSV: {e}\")\n        return None\n\ndef main():\n    \"\"\"Main batch test execution\"\"\"\n    parser = argparse.ArgumentParser(description='Batch test hockey drill evaluation API')\n    parser.add_argument('--csv', help='CSV file with test cases')\n    parser.add_argument('--output', help='Output report file')\n    parser.add_argument('--results-csv', help='Save results to CSV file')\n    parser.add_argument('--create-sample', action='store_true', help='Create sample CSV file')\n    parser.add_argument('--batch-size', type=int, default=5, help='Batch size (default: 5)')\n    parser.add_argument('--temperature', type=float, default=0.1, help='Model temperature (default: 0.1)')\n    parser.add_argument('--full-specs', action='store_true', help='Return full generated specs')\n    parser.add_argument('--debug', action='store_true', help='Include debug information')\n    \n    args = parser.parse_args()\n    \n    # Create sample CSV if requested\n    if args.create_sample:\n        create_sample_csv()\n        return\n    \n    # Configuration\n    webhook_url = os.getenv('N8N_WEBHOOK_URL', 'https://your-n8n-instance/webhook/drill-evaluation')\n    auth_token = os.getenv('N8N_WEBHOOK_TOKEN')  # Optional\n    \n    if webhook_url == 'https://your-n8n-instance/webhook/drill-evaluation':\n        print(\"⚠️  Please set N8N_WEBHOOK_URL environment variable\")\n        print(\"   Example: export N8N_WEBHOOK_URL='https://your-instance/webhook/drill-evaluation'\")\n        sys.exit(1)\n    \n    # Initialize tester\n    tester = HockeyDrillBatchTester(webhook_url, auth_token)\n    \n    # Load test cases\n    if args.csv:\n        test_cases = tester.load_test_cases_from_csv(args.csv)\n        if not test_cases:\n            sys.exit(1)\n    else:\n        test_cases = tester.create_default_test_cases()\n    \n    # Test configuration\n    config = {\n        'batchSize': args.batch_size,\n        'temperature': args.temperature,\n        'returnFullSpecs': args.full_specs,\n        'includeDebugInfo': args.debug\n    }\n    \n    print(\"🏒 Hockey Drill Batch API Tester v1.0\")\n    print(f\"🔗 Webhook URL: {webhook_url}\")\n    print(f\"🔐 Authentication: {'Enabled' if auth_token else 'Disabled'}\")\n    print(f\"📁 Test Cases: {len(test_cases)} {'(from CSV)' if args.csv else '(default)'}\")\n    print(f\"⚙️  Batch Size: {args.batch_size}\")\n    print(f\"🌡️  Temperature: {args.temperature}\")\n    \n    # Run batch test\n    response = tester.test_batch(test_cases, config)\n    \n    # Generate report\n    tester.generate_report(response, args.output)\n    \n    # Save CSV if requested\n    if args.results_csv:\n        tester.save_results_csv(response, args.results_csv)\n    \n    # Exit with appropriate code\n    sys.exit(0 if response['success'] else 1)\n\nif __name__ == '__main__':\n    main()