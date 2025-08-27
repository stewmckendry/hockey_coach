# n8n Hockey Drill Evaluation API Documentation v8 - Google Sheets Integration

## Overview

The Hockey Drill Evaluation workflow v8 provides enhanced multi-source data capabilities, supporting both direct API data and Google Sheets as a test repository. This enables automated testing, CI/CD integration, centralized test management, and programmatic execution with flexible test selection.

## 🆕 What's New in v8

### Enhanced Data Source Support
- **Direct Test Data**: Backward compatible with v7 API formats
- **Google Sheets Integration**: Use Google Sheets as your test case repository
- **Advanced Filtering**: Filter tests by ID, status, or custom criteria
- **Batch Optimization**: Improved batch processing for large datasets

### Key Benefits
- ✅ **Single Source of Truth**: Manage all test cases in Google Sheets
- ✅ **Programmatic Execution**: API-driven testing with flexible selection
- ✅ **CI/CD Integration**: Automated testing workflows
- ✅ **Backward Compatibility**: Existing v7 integrations continue to work

## Webhook Endpoint

### Base URL
```
POST https://{your-n8n-instance}/webhook/drill-evaluation
```

### Authentication (Optional)
If configured, include the authentication token in the request header:
```
Authorization: Bearer {your-webhook-token}
```

Set the `WEBHOOK_AUTH_TOKEN` environment variable in your n8n instance to enable authentication.

## Request Formats

### Mode 1: Direct Test Data (v7 Compatibility)

#### Single Test Case
```json
{
  "test_case": {
    "test_id": "test_001",
    "drill_description": "Two players skate around center ice in opposite directions, then pass to coach and receive return pass",
    "expected_title": "Circle Passing Drill",
    "expected_players": "X1,X2,C1",
    "expected_steps": 3,
    "expected_landmarks": "center_dot,left_boards"
  },
  "config": {
    "modelName": "gpt-4o-mini",
    "temperature": 0.1,
    "returnFullSpecs": true,
    "includeDebugInfo": false
  }
}
```

#### Multiple Test Cases (Batch)
```json
{
  "test_cases": [
    {
      "test_id": "test_001",
      "drill_description": "Players skate figure-8 around center ice",
      "expected_title": "Figure-8 Drill"
    },
    {
      "test_id": "test_002", 
      "drill_description": "Three players pass in triangle formation",
      "expected_players": "X1,X2,X3"
    }
  ]
}
```

### Mode 2: 🆕 Google Sheets with Specific Test IDs
```json
{
  "source": "google_sheets",
  "test_ids": ["TC001", "TC002", "TC005"],
  "config": {
    "returnFullSpecs": true,
    "includeDebugInfo": false
  }
}
```

### Mode 3: 🆕 Google Sheets - Run All Tests
```json
{
  "source": "google_sheets",
  "run_all": true,
  "config": {
    "batchSize": 10,
    "returnFullSpecs": false
  }
}
```

### Mode 4: 🆕 Google Sheets with Custom Filters
```json
{
  "source": "google_sheets",
  "filter": {
    "status": "active",
    "priority": "high",
    "category": "passing"
  },
  "config": {
    "sheetsReadLimit": 50
  }
}
```

### Mode 5: 🆕 Google Sheets with Custom Sheet Name
```json
{
  "source": "google_sheets",
  "run_all": true,
  "sheet_name": "Advanced Test Cases",
  "config": {
    "testSheetName": "Custom Sheet Name"
  }
}
```

## Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | `application/json` |
| `Authorization` | Optional | `Bearer {token}` if authentication enabled |
| `X-Request-ID` | Optional | Unique identifier for tracking the request |

## Configuration Options

Configure the workflow behavior by including a `config` object:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `modelName` | string | `gpt-4o-mini` | OpenAI model to use |
| `temperature` | number | `0.1` | Model temperature (0-2) |
| `maxTokens` | number | `2000` | Maximum tokens per request |
| `batchSize` | number | `10` | Batch processing size (1-100) |
| `passingScore` | number | `70` | Minimum score to pass (0-100) |
| `returnFullSpecs` | boolean | `true` | Include generated specs in response |
| `includeDebugInfo` | boolean | `false` | Include debug information |
| `retryAttempts` | number | `3` | Number of retry attempts |
| `timeout` | number | `30000` | Request timeout in milliseconds |
| `sheetsReadLimit` | number | `1000` | 🆕 Maximum rows to read from Sheets |
| `sheetsFilterColumn` | string | `status` | 🆕 Default column for status filtering |

## Google Sheets Setup

### Required Sheets Structure

Your Google Sheets workbook should contain the following sheets:

#### 1. Test Cases Sheet (default name: "Test Cases")
| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `test_id` | Yes | Unique test identifier | `TC001` |
| `drill_description` | Yes | Hockey drill description | `Two players pass back and forth` |
| `expected_title` | No | Expected drill title | `Passing Drill` |
| `expected_players` | No | Expected player IDs | `X1,X2,C1` |
| `expected_steps` | No | Expected number of steps | `3` |
| `expected_landmarks` | No | Expected landmarks | `center_dot,left_boards` |
| `status` | No | Test status for filtering | `active`, `inactive`, `draft` |
| `priority` | No | Test priority | `high`, `medium`, `low` |
| `category` | No | Test category | `passing`, `shooting`, `skating` |

#### 2. Results Sheet (default name: "Results")
Automatically populated with test execution results.

#### 3. Specs Sheet (default name: "Specs")  
Automatically populated with generated drill specifications.

### Column Name Flexibility

The workflow supports multiple column naming conventions:
- `test_id`, `Test_ID`, `Test ID`, `TestID`, `ID`
- `drill_description`, `Drill_Description`, `Drill Description`, `Description`
- `expected_title`, `Expected_Title`, `Expected Title`, `Title`

## Response Format

### Success Response (200 OK) - Enhanced v8
```json
{
  "status": "success",
  "request_id": "req_1703123456789",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "workflow": {
    "id": "drill-evaluation-v8-sheets-integration",
    "version": "v8",
    "execution_mode": "api",
    "data_source": "google_sheets"
  },
  "summary": {
    "total_tests": 5,
    "passed_tests": 4,
    "failed_tests": 1,
    "average_score": "82.40",
    "pass_rate": "80.00%"
  },
  "source_info": {
    "data_source": "google_sheets",
    "direct_api_tests": 0,
    "google_sheets_tests": 5,
    "sheets_mode": {
      "run_all": false,
      "test_ids": ["TC001", "TC002"],
      "filter": null
    }
  },
  "results": [
    {
      "test_id": "TC001",
      "drill_description": "Two players skate around center ice",
      "score": 85,
      "passed": true,
      "explanation": "✅ PASSED (85%) [📊 Sheets]. Title captured correctly. All players correctly identified.",
      "source": "google_sheets",
      "processing_mode": "sheets_batch",
      "issues": [],
      "strengths": ["Title captured correctly", "All players correctly identified"],
      "sheets_filter_applied": {
        "run_all": false,
        "test_ids": ["TC001", "TC002"],
        "filter": null
      }
    }
  ],
  "performance": {
    "total_processing_time_ms": 3200,
    "average_processing_time_ms": "640.00",
    "processing_modes": {
      "sheets_batch": 5
    }
  },
  "v8_features": {
    "google_sheets_integration": true,
    "multi_source_support": true,
    "advanced_filtering": true,
    "backward_compatibility": true
  }
}
```

### Error Responses

#### Validation Error (400 Bad Request)
```json
{
  "status": "error",
  "error_code": "VALIDATION_FAILED_V8",
  "message": "Cannot use run_all with test_ids or filter options",
  "request_id": "req_1703123456789",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### Google Sheets Access Error (400 Bad Request)
```json
{
  "status": "error",
  "error_code": "SHEETS_ACCESS_ERROR",
  "message": "No test cases match the specified criteria",
  "request_id": "req_1703123456789",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Environment Variables

Configure your n8n instance with these environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_SHEETS_ID` | Yes | Google Sheets ID for storing results |
| `GOOGLE_SHEETS_CREDENTIAL_ID` | Yes | n8n credential ID for Google Sheets |
| `OPENAI_CREDENTIAL_ID` | Yes | n8n credential ID for OpenAI |
| `WEBHOOK_AUTH_TOKEN` | Optional | Authentication token for webhook |
| `TEST_SHEET_NAME` | No | Sheet name for test cases (default: "Test Cases") |
| `RESULTS_SHEET_NAME` | No | Sheet name for results (default: "Results") |
| `SPECS_SHEET_NAME` | No | Sheet name for specs (default: "Specs") |
| `SHEETS_READ_LIMIT` | No | 🆕 Maximum rows to read (default: 1000) |
| `SHEETS_FILTER_COLUMN` | No | 🆕 Default filter column (default: "status") |
| `DEBUG_MODE` | No | Enable debug logging (default: false) |

## Integration Examples

### Google Sheets Integration Examples

#### Run Specific Test Cases
```bash
curl -X POST "https://your-n8n-instance/webhook/drill-evaluation" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "source": "google_sheets",
    "test_ids": ["TC001", "TC003", "TC007"],
    "config": {
      "returnFullSpecs": false,
      "includeDebugInfo": true
    }
  }'
```

#### Run All Active Tests
```bash
curl -X POST "https://your-n8n-instance/webhook/drill-evaluation" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "google_sheets",
    "filter": {
      "status": "active"
    },
    "config": {
      "batchSize": 5
    }
  }'
```

#### Run All Tests from Custom Sheet
```bash
curl -X POST "https://your-n8n-instance/webhook/drill-evaluation" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "google_sheets",
    "run_all": true,
    "sheet_name": "Production Test Cases",
    "config": {
      "sheetsReadLimit": 100
    }
  }'
```

### Using Node.js/JavaScript - Google Sheets Mode
```javascript
const response = await fetch('https://your-n8n-instance/webhook/drill-evaluation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-token',
    'X-Request-ID': 'nodejs-sheets-' + Date.now()
  },
  body: JSON.stringify({
    source: 'google_sheets',
    filter: {
      priority: 'high',
      category: 'passing'
    },
    config: {
      batchSize: 10,
      returnFullSpecs: false
    }
  })
});

const result = await response.json();
console.log('Google Sheets Test Results:', result.source_info);
console.log('Total Tests from Sheets:', result.source_info.google_sheets_tests);
```

### Using Python - Google Sheets Integration
```python
import requests
import json

url = "https://your-n8n-instance/webhook/drill-evaluation"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-token"
}

# Test specific IDs from Google Sheets
payload = {
    "source": "google_sheets",
    "test_ids": ["TC001", "TC002", "TC005"],
    "config": {
        "temperature": 0.2,
        "batchSize": 5,
        "includeDebugInfo": True
    }
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
result = response.json()

print("Status:", result["status"])
print("Data Source:", result["source_info"]["data_source"])
print("Google Sheets Tests:", result["source_info"]["google_sheets_tests"])
print("Pass Rate:", result["summary"]["pass_rate"])

# Display Google Sheets specific info
for test_result in result["results"]:
    if test_result.get("sheets_filter_applied"):
        print(f"Test {test_result['test_id']} used filter:", 
              test_result["sheets_filter_applied"])
```

## CI/CD Integration Examples

### GitHub Actions with Google Sheets
```yaml
name: Hockey Drill Evaluation
on: [push, pull_request]

jobs:
  test-drills:
    runs-on: ubuntu-latest
    steps:
      - name: Run Active Drill Tests
        run: |
          curl -X POST "${{ secrets.N8N_WEBHOOK_URL }}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${{ secrets.N8N_TOKEN }}" \
            -d '{
              "source": "google_sheets",
              "filter": {"status": "active"},
              "config": {
                "batchSize": 20,
                "returnFullSpecs": false
              }
            }' | jq '.summary'

      - name: Run High Priority Tests
        if: github.event_name == 'pull_request'
        run: |
          curl -X POST "${{ secrets.N8N_WEBHOOK_URL }}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${{ secrets.N8N_TOKEN }}" \
            -d '{
              "source": "google_sheets",
              "filter": {"priority": "high"},
              "config": {"returnFullSpecs": false}
            }'
```

### Jenkins Pipeline with Google Sheets
```groovy
pipeline {
    agent any
    stages {
        stage('Test Hockey Drills') {
            steps {
                script {
                    def response = sh(
                        script: """
                            curl -X POST "${N8N_WEBHOOK_URL}" \
                              -H "Content-Type: application/json" \
                              -H "Authorization: Bearer ${N8N_TOKEN}" \
                              -d '{
                                "source": "google_sheets",
                                "run_all": true,
                                "config": {
                                  "batchSize": 15,
                                  "passingScore": 80
                                }
                              }'
                        """,
                        returnStdout: true
                    )
                    def result = readJSON text: response
                    
                    if (result.summary.pass_rate.replace('%', '').toFloat() < 90) {
                        error("Test pass rate below 90%: ${result.summary.pass_rate}")
                    }
                    
                    echo "Google Sheets tests: ${result.source_info.google_sheets_tests}"
                    echo "Pass rate: ${result.summary.pass_rate}"
                }
            }
        }
    }
}
```

## Rate Limiting and Best Practices

### Rate Limiting
- Maximum 100 test cases per request (increased from v7)
- Recommended batch size for Google Sheets: 10-20 test cases
- Google Sheets read limit: 1000 rows (configurable)
- Implement exponential backoff for retries

### Best Practices

#### Google Sheets Management
1. **Organize Test Cases**: Use categories, priorities, and status columns
2. **Regular Cleanup**: Remove inactive or obsolete test cases
3. **Column Naming**: Use consistent column names across sheets
4. **Access Control**: Ensure n8n has proper Google Sheets permissions
5. **Backup Strategy**: Keep backups of your test case sheets

#### API Usage
1. **Use Google Sheets Mode**: Centralize test management in Google Sheets
2. **Filter Efficiently**: Use specific test IDs or filters rather than run_all for faster execution
3. **Monitor Performance**: Track processing times for large test sets
4. **Error Handling**: Implement retry logic for network issues
5. **Request Tracking**: Use unique request IDs for debugging

#### Performance Optimization
- Use `run_all: false` with specific filters for faster responses
- Set `returnFullSpecs: false` when specs aren't needed
- Use appropriate batch sizes based on test complexity
- Consider `sheetsReadLimit` for very large test sheets
- Enable `includeDebugInfo: true` only when troubleshooting

## Migration from v7

The v8 workflow maintains complete backward compatibility with v7 API formats. Existing integrations will continue to work without modification.

### Upgrade Benefits
- **Enhanced Flexibility**: Multiple data source options
- **Centralized Management**: Google Sheets as single source of truth
- **Better Performance**: Optimized batch processing
- **Advanced Filtering**: Sophisticated test selection
- **Improved Monitoring**: Enhanced response tracking

### Migration Steps
1. **Keep Existing Code**: No changes needed for v7 API calls
2. **Add Google Sheets**: Set up Google Sheets with test cases
3. **Try New Features**: Experiment with Google Sheets modes
4. **Gradual Migration**: Slowly move test cases to Google Sheets
5. **Monitor Performance**: Compare response times and reliability

## Troubleshooting

### Common Issues

**Issue**: "No test cases match the specified criteria"
**Solution**: Check filter criteria, verify test case status in Google Sheets, ensure column names match

**Issue**: "Google Sheets access denied"
**Solution**: Verify Google Sheets credential configuration and sheet sharing permissions

**Issue**: "Sheets read limit exceeded"
**Solution**: Increase `sheetsReadLimit` or use more specific filters to reduce dataset size

**Issue**: "Test ID not found in sheets"
**Solution**: Verify test IDs exist in Google Sheets, check for typos, ensure correct sheet name

**Issue**: "Invalid sheets mode configuration"  
**Solution**: Don't combine `run_all: true` with `test_ids` or `filter` options

### Debug Mode

Enable enhanced debugging:
```json
{
  "source": "google_sheets",
  "filter": {"status": "active"},
  "config": {
    "includeDebugInfo": true,
    "debugMode": true
  }
}
```

This provides additional information about:
- Google Sheets reading process
- Filter application results
- Batch processing details
- Performance metrics by source

## Webhook URL Discovery

To find your webhook URL in n8n:
1. Open the v8 workflow in n8n editor
2. Click on the "Enhanced Webhook Trigger" node
3. Copy the "Production URL" from the webhook configuration

## Summary

Hockey Drill Evaluation v8 brings powerful Google Sheets integration while maintaining complete backward compatibility with v7. Whether you prefer direct API data submission or centralized test management through Google Sheets, v8 provides the flexibility and features needed for comprehensive hockey drill evaluation workflows.

Choose the approach that best fits your workflow:
- **Direct API**: For simple, immediate test execution
- **Google Sheets**: For centralized test management and team collaboration
- **Hybrid**: Use both approaches as needed for different scenarios