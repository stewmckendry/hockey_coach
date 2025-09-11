# Hockey Drill Evaluation API Test Scripts

This directory contains comprehensive testing scripts for the n8n Hockey Drill Evaluation API v7 with webhook support.

## Overview

The v7 workflow provides both manual UI execution and programmatic API access through webhook endpoints. These scripts enable automated testing, CI/CD integration, and external system integration.

## Test Scripts

### 1. `test_api_basic.py` - Basic Python Testing
**Purpose**: Simple single test case execution with detailed error handling
**Best for**: Quick API validation, development testing, learning the API

**Usage**:
```bash
# Set environment variables
export N8N_WEBHOOK_URL="https://your-n8n-instance/webhook/drill-evaluation"
export N8N_WEBHOOK_TOKEN="your-optional-token"

# Run basic test
python test_api_basic.py
```

**Features**:
- Single test case execution
- Clear success/failure reporting
- Performance metrics
- Error analysis
- Configurable test parameters

### 2. `test_api_batch.py` - Comprehensive Batch Testing
**Purpose**: Advanced batch testing with CSV support and comprehensive reporting
**Best for**: Performance testing, bulk validation, CI/CD pipelines

**Usage**:
```bash
# Run with default test cases
python test_api_batch.py

# Run with custom CSV file
python test_api_batch.py --csv my_test_cases.csv --output report.txt

# Create sample CSV file
python test_api_batch.py --create-sample

# Advanced configuration
python test_api_batch.py \
  --csv test_cases.csv \
  --batch-size 10 \
  --temperature 0.2 \
  --full-specs \
  --debug \
  --output detailed_report.txt \
  --results-csv results.csv
```

**Features**:
- Batch test case processing
- CSV input/output support
- Comprehensive reporting
- Performance analysis
- Configuration flexibility
- Command-line interface

**Command Line Options**:
- `--csv FILE`: Load test cases from CSV file
- `--output FILE`: Save report to file
- `--results-csv FILE`: Save results to CSV
- `--create-sample`: Create sample CSV file
- `--batch-size N`: Set batch processing size
- `--temperature N`: Set model temperature
- `--full-specs`: Return complete generated specs
- `--debug`: Include debug information

### 3. `test_api_node.js` - Node.js Testing
**Purpose**: JavaScript/Node.js environment testing with modular design
**Best for**: JavaScript projects, web applications, microservices

**Usage**:
```bash
# Install Node.js if not already installed
# Run basic test
node test_api_node.js

# Run specific modes
node test_api_node.js --mode single
node test_api_node.js --mode batch --batch-size 10

# Create sample test file
node test_api_node.js --create-sample

# Advanced usage
node test_api_node.js \
  --test-file test_cases.json \
  --output report.txt \
  --mode batch \
  --temperature 0.1
```

**Features**:
- Promise-based HTTP requests
- Multiple test modes (single, batch, default)
- JSON file support
- Modular class design
- Error handling
- Performance tracking

**Command Line Options**:
- `--test-file FILE`: Load test cases from JSON
- `--output FILE`: Save report to file
- `--mode MODE`: Test mode (single, batch, default)
- `--batch-size N`: Batch processing size
- `--temperature N`: Model temperature
- `--create-sample`: Create sample test file
- `--help`: Show help message

### 4. `test_api_curl.sh` - Shell Script Testing
**Purpose**: Shell-based testing using curl, ideal for CI/CD and system administration
**Best for**: CI/CD pipelines, system testing, quick validation

**Usage**:
```bash
# Run all tests
./test_api_curl.sh

# Run specific test
./test_api_curl.sh single_case

# Custom configuration
./test_api_curl.sh \
  --webhook-url "https://your-instance/webhook/drill-evaluation" \
  --auth-token "your-token" \
  --output-dir ./results \
  batch_cases
```

**Features**:
- Multiple test scenarios
- Authentication testing
- Error case validation
- Comprehensive reporting
- JSON formatting (with jq)
- File-based result storage

**Available Tests**:
- `single_case`: Single test case
- `batch_cases`: Multiple test cases
- `direct_array`: Array format input
- `minimal_case`: Minimal required fields
- `invalid_payload`: Error testing
- `empty_payload`: Empty request testing
- `large_batch`: Performance testing
- `authentication`: Auth validation
- `all`: Run all tests (default)

## Environment Variables

All scripts use these environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `N8N_WEBHOOK_URL` | Yes | Full webhook URL for the API |
| `N8N_WEBHOOK_TOKEN` | No | Authentication token if enabled |

**Example Setup**:
```bash
export N8N_WEBHOOK_URL="https://your-n8n-instance/webhook/drill-evaluation"
export N8N_WEBHOOK_TOKEN="your-secret-token"
```

## Test Case Formats

### CSV Format (for Python batch tester)
```csv
test_id,drill_description,expected_title,expected_players,expected_steps,expected_landmarks
test_001,"Two players pass back and forth","Passing Drill","X1,X2","2","center_dot"
test_002,"Goalie practices saves","Goalie Drill","G1,X1","","low_slot"
```

### JSON Format (for Node.js tester)
```json
{
  "single_test": {
    "test_id": "json_single",
    "drill_description": "Player practices skating with puck",
    "expected_players": "X1"
  },
  "batch_tests": [
    {
      "test_id": "json_batch_001",
      "drill_description": "Two players practice passing"
    }
  ]
}
```

## Integration Examples

### CI/CD Pipeline (GitHub Actions)
```yaml
name: Hockey Drill API Tests
on: [push, pull_request]
jobs:
  test-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test API
        env:
          N8N_WEBHOOK_URL: ${{ secrets.N8N_WEBHOOK_URL }}
          N8N_WEBHOOK_TOKEN: ${{ secrets.N8N_WEBHOOK_TOKEN }}
        run: |
          python scripts/test_api_batch.py --output ci_report.txt
```

### Docker Testing
```dockerfile
FROM python:3.9-slim
COPY scripts/ /scripts/
WORKDIR /scripts
RUN chmod +x *.py
ENV N8N_WEBHOOK_URL=""
CMD ["python", "test_api_batch.py"]
```

### Monitoring Script
```bash
#!/bin/bash
# Monitor API health
while true; do
    if python test_api_basic.py > /dev/null 2>&1; then
        echo "$(date): API healthy"
    else
        echo "$(date): API failed" | mail -s "API Alert" admin@example.com
    fi
    sleep 300  # Check every 5 minutes
done
```

## Performance Testing

### Load Testing with Batch Script
```bash
# Test with increasing batch sizes
for size in 1 5 10 20; do
    echo "Testing batch size: $size"
    python test_api_batch.py \
      --batch-size $size \
      --output "performance_test_${size}.txt" \
      --results-csv "results_${size}.csv"
done
```

### Concurrent Testing
```bash
# Run multiple tests in parallel
for i in {1..5}; do
    python test_api_basic.py &
done
wait
echo "All concurrent tests completed"
```

## Troubleshooting

### Common Issues

**Issue**: "Connection refused"
**Solutions**:
- Verify webhook URL is correct
- Check n8n instance is running
- Ensure webhook trigger is active

**Issue**: "Invalid authorization token"
**Solutions**:
- Check `N8N_WEBHOOK_TOKEN` environment variable
- Verify token matches n8n configuration
- Ensure token is properly set in webhook trigger

**Issue**: "Request timeout"
**Solutions**:
- Increase timeout values in scripts
- Reduce batch sizes for large requests
- Check n8n server performance

**Issue**: "Invalid JSON response"
**Solutions**:
- Check n8n workflow for errors
- Verify webhook response configuration
- Review n8n logs for execution errors

### Debug Mode

Enable debug output in each script:
- Python: Use `--debug` flag
- Node.js: Set `includeDebugInfo: true` in config
- Curl: Check generated output files

### Log Analysis

Check n8n execution logs:
1. Open n8n interface
2. Go to Executions tab
3. Find your test execution
4. Review node execution details

## Best Practices

1. **Start Simple**: Begin with `test_api_basic.py` to validate basic connectivity
2. **Use Appropriate Batch Sizes**: 1-5 for development, 5-20 for production testing
3. **Set Timeouts**: Allow sufficient time for batch processing
4. **Monitor Performance**: Track response times and success rates
5. **Handle Errors Gracefully**: Implement retry logic for transient failures
6. **Version Control**: Store test cases in version control
7. **Automate Testing**: Integrate into CI/CD pipelines
8. **Document Results**: Save test reports for analysis

## Support

For issues with the scripts or API:
1. Check the API documentation
2. Review n8n workflow logs
3. Validate environment variables
4. Test with minimal payloads first
5. Check network connectivity and permissions