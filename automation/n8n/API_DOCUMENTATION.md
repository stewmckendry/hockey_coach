# n8n Hockey Drill Evaluation API Documentation v7

## Overview

The Hockey Drill Evaluation workflow v7 provides both manual UI execution and programmatic API access through webhook endpoints. This enables automated testing, CI/CD integration, and external system integration.

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

### Single Test Case
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

### Multiple Test Cases (Batch)
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

### Direct Array Format
```json
[
  {
    "test_id": "test_001",
    "drill_description": "Simple passing drill between two players"
  },
  {
    "test_id": "test_002",
    "drill_description": "Shooting drill with goalie"
  }
]
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
| `batchSize` | number | `5` | Batch processing size (1-50) |
| `passingScore` | number | `70` | Minimum score to pass (0-100) |
| `returnFullSpecs` | boolean | `true` | Include generated specs in response |
| `includeDebugInfo` | boolean | `false` | Include debug information |
| `retryAttempts` | number | `3` | Number of retry attempts |
| `timeout` | number | `30000` | Request timeout in milliseconds |

## Response Format

### Success Response (200 OK)
```json
{
  "status": "success",
  "request_id": "req_1703123456789",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "workflow": {
    "id": "drill-evaluation-v7-programmable",
    "version": "v7",
    "execution_mode": "api"
  },
  "summary": {
    "total_tests": 2,
    "passed_tests": 1,
    "failed_tests": 1,
    "average_score": "75.50",
    "pass_rate": "50.00%"
  },
  "results": [
    {
      "test_id": "test_001",
      "drill_description": "Two players skate around center ice",
      "score": 85,
      "passed": true,
      "explanation": "✅ PASSED (85%). Title captured correctly. All players correctly identified.",
      "issues": [],
      "strengths": ["Title captured correctly", "All players correctly identified"],
      "generated_spec": {
        "schema_version": "0.1",
        "type": "drill",
        "title": "Center Ice Skating Drill",
        "players": [
          {
            "id": "X1",
            "role": "X",
            "location": {"landmark": "center_dot"}
          }
        ],
        "drill": {
          "sequence": [
            {
              "step": 1,
              "actions": [
                {
                  "actor": "X1",
                  "action": "skate",
                  "path": {
                    "type": "arc",
                    "around_landmark": "center_dot",
                    "direction": "cw"
                  }
                }
              ]
            }
          ]
        }
      }
    }
  ],
  "performance": {
    "total_processing_time_ms": 2500,
    "average_processing_time_ms": "1250.00"
  }
}
```

### Error Responses

#### Validation Error (400 Bad Request)
```json
{
  "status": "error",
  "error_code": "VALIDATION_FAILED",
  "message": "Missing required configuration: googleSheetsId",
  "request_id": "req_1703123456789",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### Authentication Error (401 Unauthorized)
```json
{
  "status": "error",
  "error_code": "TRIGGER_PROCESSING_ERROR", 
  "message": "Invalid authorization token",
  "request_id": "req_1703123456789",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### Processing Error (500 Internal Server Error)
```json
{
  "status": "error",
  "error_code": "PROCESSING_ERROR",
  "message": "OpenAI API timeout",
  "request_id": "req_1703123456789",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Test Case Fields

### Required Fields
- `test_id`: Unique identifier for the test case
- `drill_description`: Text description of the hockey drill

### Optional Expected Values (for evaluation)
- `expected_title`: Expected title of the generated drill
- `expected_players`: Comma-separated list of player IDs (e.g., "X1,X2,C1")
- `expected_steps`: Expected number of sequence steps
- `expected_landmarks`: Comma-separated list of landmarks to be used

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
| `DEBUG_MODE` | No | Enable debug logging (default: false) |

## Integration Examples

### Using curl
```bash
curl -X POST "https://your-n8n-instance/webhook/drill-evaluation" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "test_case": {
      "test_id": "curl_test_001",
      "drill_description": "Two players pass back and forth while skating",
      "expected_players": "X1,X2"
    },
    "config": {
      "returnFullSpecs": false,
      "includeDebugInfo": true
    }
  }'
```

### Using Node.js/JavaScript
```javascript
const response = await fetch('https://your-n8n-instance/webhook/drill-evaluation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-token',
    'X-Request-ID': 'nodejs-' + Date.now()
  },
  body: JSON.stringify({
    test_cases: [
      {
        test_id: 'js_test_001',
        drill_description: 'Players practice one-timers from the slot',
        expected_landmarks: 'low_slot,behind_net'
      }
    ]
  })
});

const result = await response.json();
console.log('Test Results:', result);
```

### Using Python
```python
import requests
import json

url = "https://your-n8n-instance/webhook/drill-evaluation"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-token"
}

payload = {
    "test_cases": [
        {
            "test_id": "python_test_001", 
            "drill_description": "Goalie practices rebound control drills",
            "expected_players": "G1,X1,X2"
        }
    ],
    "config": {
        "temperature": 0.2,
        "batchSize": 10
    }
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
result = response.json()

print("Status:", result["status"])
print("Summary:", result["summary"])
```

## Rate Limiting and Best Practices

### Rate Limiting
- Maximum 50 test cases per request
- Recommended batch size: 5-10 test cases
- Implement exponential backoff for retries

### Best Practices
1. **Use meaningful test IDs**: Include timestamps or unique identifiers
2. **Set request timeouts**: Default 30 seconds, adjust based on batch size
3. **Handle errors gracefully**: Check response status and error codes
4. **Monitor performance**: Track processing times and success rates
5. **Use batch processing**: Group multiple test cases for efficiency
6. **Include request IDs**: For tracing and debugging

### Performance Optimization
- Use smaller batch sizes (1-5) for faster response times
- Use larger batch sizes (10-50) for throughput optimization  
- Enable returnFullSpecs: false for faster responses when specs aren't needed
- Set appropriate model temperature (0.1 for consistency, higher for creativity)

## Troubleshooting

### Common Issues

**Issue**: "Invalid authorization token"
**Solution**: Check WEBHOOK_AUTH_TOKEN environment variable and Authorization header

**Issue**: "Google Sheets ID is required"
**Solution**: Set GOOGLE_SHEETS_ID environment variable or include in config

**Issue**: "OpenAI API timeout"
**Solution**: Increase timeout value or reduce batch size

**Issue**: "No test cases found"
**Solution**: Verify request payload format and required fields

### Debug Mode
Enable debug mode by setting `includeDebugInfo: true` in config or `DEBUG_MODE=true` environment variable to get additional diagnostic information.

## Webhook URL Discovery

To find your webhook URL in n8n:
1. Open the workflow in n8n editor
2. Click on the "Webhook Trigger" node
3. Copy the "Production URL" from the webhook configuration

## Migration from v6

The v7 workflow maintains backward compatibility with manual execution while adding API capabilities. Existing manual workflows will continue to work without modification.

### Key Differences
- Added webhook trigger alongside manual trigger
- Enhanced error handling for API responses
- Configurable response format options
- Request tracking and batch processing improvements
- Environment variable support for all configuration options