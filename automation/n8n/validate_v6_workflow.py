#!/usr/bin/env python3
"""
Validation script for n8n Drill Evaluation v6 Production Workflow
Tests workflow structure, node configurations, and connections.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

def load_workflow(file_path: str) -> Dict:
    """Load the workflow JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        sys.exit(1)

def validate_node_structure(workflow: Dict) -> List[str]:
    """Validate the basic node structure."""
    issues = []
    
    if 'nodes' not in workflow:
        issues.append("Missing 'nodes' key in workflow")
        return issues
    
    nodes = workflow['nodes']
    required_node_types = {
        'n8n-nodes-base.manualTrigger': 'Manual Trigger',
        'n8n-nodes-base.code': 'Code nodes for logic',
        'n8n-nodes-base.googleSheets': 'Google Sheets integration',
        '@n8n/n8n-nodes-langchain.lmChain': 'LangChain LLM Chain',
        '@n8n/n8n-nodes-langchain.lmChatOpenAi': 'OpenAI Chat Model',
        '@n8n/n8n-nodes-langchain.outputParserStructured': 'Structured Output Parser'
    }
    
    found_types = {node.get('type'): node.get('name', 'Unnamed') for node in nodes}
    
    for required_type, description in required_node_types.items():
        if required_type not in found_types:
            issues.append(f"Missing required node type: {required_type} ({description})")
    
    # Check for node IDs and names
    node_ids = []
    node_names = []
    
    for node in nodes:
        if 'id' not in node:
            issues.append(f"Node missing ID: {node.get('name', 'Unnamed')}")
        else:
            if node['id'] in node_ids:
                issues.append(f"Duplicate node ID: {node['id']}")
            node_ids.append(node['id'])
        
        if 'name' not in node:
            issues.append(f"Node missing name: {node.get('id', 'No ID')}")
        else:
            node_names.append(node['name'])
    
    return issues

def validate_model_configuration(workflow: Dict) -> List[str]:
    """Validate that the model configuration uses available models."""
    issues = []
    
    for node in workflow.get('nodes', []):
        if node.get('type') == '@n8n/n8n-nodes-langchain.lmChatOpenAi':
            params = node.get('parameters', {})
            model = params.get('model', params.get('modelId', {}).get('value', ''))
            
            # Check for the problematic gpt-5 model
            if model == 'gpt-5':
                issues.append(f"❌ CRITICAL: Node '{node.get('name')}' uses non-existent 'gpt-5' model")
            elif model in ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']:
                print(f"✅ Model configuration valid: {model}")
            elif '{{' in str(model) and '}}' in str(model):
                print(f"✅ Model configuration uses dynamic expression (runtime-configured): {model}")
            else:
                issues.append(f"⚠️  Unrecognized model: {model}")
    
    return issues

def validate_connections(workflow: Dict) -> List[str]:
    """Validate node connections."""
    issues = []
    
    if 'connections' not in workflow:
        issues.append("Missing 'connections' key in workflow")
        return issues
    
    connections = workflow['connections']
    node_names = {node['name'] for node in workflow.get('nodes', [])}
    
    # Validate connection structure
    for source_node, conn_data in connections.items():
        if source_node not in node_names:
            issues.append(f"Connection references non-existent source node: {source_node}")
        
        for connection_type, connections_list in conn_data.items():
            if connection_type not in ['main', 'ai_languageModel', 'ai_outputParser']:
                issues.append(f"Unknown connection type: {connection_type}")
            
            for conn_group in connections_list:
                for conn in conn_group:
                    target_node = conn.get('node')
                    if target_node and target_node not in node_names:
                        issues.append(f"Connection references non-existent target node: {target_node}")
    
    # Check for LangChain specific connections
    langchain_connections = {
        'ai_languageModel': [],
        'ai_outputParser': []
    }
    
    for source_node, conn_data in connections.items():
        for conn_type in langchain_connections.keys():
            if conn_type in conn_data:
                langchain_connections[conn_type].append(source_node)
    
    if not langchain_connections['ai_languageModel']:
        issues.append("Missing ai_languageModel connections for LangChain")
    
    if not langchain_connections['ai_outputParser']:
        issues.append("Missing ai_outputParser connections for LangChain")
    
    return issues

def validate_error_handling(workflow: Dict) -> List[str]:
    """Validate error handling implementations."""
    issues = []
    
    code_nodes = [node for node in workflow.get('nodes', []) 
                  if node.get('type') == 'n8n-nodes-base.code']
    
    error_handling_patterns = [
        'try {',
        'catch',
        'throw new Error',
        'error.message',
        'console.error'
    ]
    
    nodes_with_error_handling = []
    
    for node in code_nodes:
        js_code = node.get('parameters', {}).get('jsCode', '')
        has_error_handling = any(pattern in js_code for pattern in error_handling_patterns)
        
        if has_error_handling:
            nodes_with_error_handling.append(node.get('name', 'Unnamed'))
        else:
            issues.append(f"Code node '{node.get('name', 'Unnamed')}' lacks error handling")
    
    if len(nodes_with_error_handling) > 0:
        print(f"✅ Error handling found in {len(nodes_with_error_handling)} nodes: {', '.join(nodes_with_error_handling)}")
    
    return issues

def validate_configuration_management(workflow: Dict) -> List[str]:
    """Validate externalized configuration."""
    issues = []
    
    # Look for hardcoded values that should be externalized
    hardcoded_patterns = {
        '1xbgdJvP0TBeiInOS85ot0afIZRUp1t1jgbTy1NKhGLA': 'Google Sheets ID',
        '"1"': 'Credential ID',
        'gpt-4o-mini': 'Model name (should be configurable)'
    }
    
    workflow_str = json.dumps(workflow)
    externalized_configs = []
    
    for node in workflow.get('nodes', []):
        if node.get('type') == 'n8n-nodes-base.code':
            js_code = node.get('parameters', {}).get('jsCode', '')
            
            # Check for environment variable usage
            if '$env.' in js_code:
                externalized_configs.append(node.get('name', 'Unnamed'))
            
            # Check for hardcoded credential references
            if '"1"' in js_code and '$env.' not in js_code:
                issues.append(f"Node '{node.get('name', 'Unnamed')}' may have hardcoded credential ID")
    
    if externalized_configs:
        print(f"✅ Configuration externalization found in: {', '.join(externalized_configs)}")
    else:
        issues.append("No configuration externalization found")
    
    return issues

def validate_batch_processing(workflow: Dict) -> List[str]:
    """Validate batch processing implementation."""
    issues = []
    
    batch_indicators = [
        'batch',
        'batchSize',
        'batch_id',
        'parallel',
        'efficiency'
    ]
    
    nodes_with_batch_logic = []
    
    for node in workflow.get('nodes', []):
        if node.get('type') == 'n8n-nodes-base.code':
            js_code = node.get('parameters', {}).get('jsCode', '')
            
            if any(indicator in js_code for indicator in batch_indicators):
                nodes_with_batch_logic.append(node.get('name', 'Unnamed'))
    
    if nodes_with_batch_logic:
        print(f"✅ Batch processing logic found in: {', '.join(nodes_with_batch_logic)}")
    else:
        issues.append("No batch processing implementation found")
    
    return issues

def validate_performance_optimizations(workflow: Dict) -> List[str]:
    """Validate performance optimization features."""
    issues = []
    
    perf_indicators = [
        'timeout',
        'maxRetries',
        'performance_metrics',
        'retry',
        'optimization'
    ]
    
    optimized_nodes = []
    
    for node in workflow.get('nodes', []):
        # Check LangChain nodes for timeout and retry configurations
        if '@n8n/n8n-nodes-langchain' in node.get('type', ''):
            params = node.get('parameters', {})
            options = params.get('options', {})
            
            if 'timeout' in options or 'maxRetries' in options:
                optimized_nodes.append(node.get('name', 'Unnamed'))
        
        # Check code nodes for performance monitoring
        if node.get('type') == 'n8n-nodes-base.code':
            js_code = node.get('parameters', {}).get('jsCode', '')
            if any(indicator in js_code for indicator in perf_indicators):
                optimized_nodes.append(node.get('name', 'Unnamed'))
    
    if optimized_nodes:
        print(f"✅ Performance optimizations found in: {', '.join(set(optimized_nodes))}")
    else:
        issues.append("No performance optimization features found")
    
    return issues

def main():
    """Main validation function."""
    workflow_path = Path(__file__).parent / "workflows" / "drill_evaluation_v6_production.json"
    
    if not workflow_path.exists():
        print(f"❌ Workflow file not found: {workflow_path}")
        sys.exit(1)
    
    print("🔍 Validating n8n Drill Evaluation v6 Production Workflow...")
    print("=" * 70)
    
    workflow = load_workflow(workflow_path)
    
    # Run all validations
    validations = [
        ("Node Structure", validate_node_structure),
        ("Model Configuration", validate_model_configuration),
        ("Connections", validate_connections),
        ("Error Handling", validate_error_handling),
        ("Configuration Management", validate_configuration_management),
        ("Batch Processing", validate_batch_processing),
        ("Performance Optimizations", validate_performance_optimizations)
    ]
    
    total_issues = 0
    
    for validation_name, validation_func in validations:
        print(f"\n📋 {validation_name}:")
        print("-" * 40)
        
        issues = validation_func(workflow)
        
        if not issues:
            print(f"✅ {validation_name}: All checks passed")
        else:
            print(f"❌ {validation_name}: {len(issues)} issue(s) found:")
            for issue in issues:
                print(f"   • {issue}")
            total_issues += len(issues)
    
    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)
    
    if total_issues == 0:
        print("✅ ALL VALIDATIONS PASSED - Workflow is production ready!")
        print("\n🚀 Ready for import into n8n:")
        print(f"   File: {workflow_path}")
        print(f"   Workflow ID: {workflow.get('id', 'N/A')}")
        print(f"   Version: {workflow.get('versionId', 'N/A')}")
    else:
        print(f"❌ VALIDATION FAILED - {total_issues} issue(s) found")
        print("\n🔧 Next steps:")
        print("   1. Review and fix the issues listed above")
        print("   2. Re-run this validation script")
        print("   3. Import into n8n once all validations pass")
    
    print("\n📚 CONFIGURATION GUIDE:")
    print("-" * 40)
    print("Set these environment variables in n8n:")
    print("   • GOOGLE_SHEETS_ID=your_sheets_id")
    print("   • OPENAI_MODEL=gpt-4o-mini (or preferred model)")
    print("   • MODEL_TEMPERATURE=0.1")
    print("   • BATCH_SIZE=5")
    print("   • PASSING_SCORE=70")
    print("   • DEBUG_MODE=false")
    
    return total_issues == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)