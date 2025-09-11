#!/bin/bash

# n8n Hockey Drill Evaluation API - Curl Testing Script v7
# Tests webhook endpoint with various scenarios using curl

set -e  # Exit on error

# Configuration
WEBHOOK_URL="${N8N_WEBHOOK_URL:-https://your-n8n-instance/webhook/drill-evaluation}"
AUTH_TOKEN="${N8N_WEBHOOK_TOKEN:-}"
OUTPUT_DIR="./curl_test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check dependencies
check_dependencies() {
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log_warning "jq not found - JSON responses will not be formatted"
        HAS_JQ=false
    else
        HAS_JQ=true
    fi
}

# Setup output directory
setup_output_dir() {
    mkdir -p "$OUTPUT_DIR"
    log_info "Output directory: $OUTPUT_DIR"
}

# Build curl headers
build_headers() {
    local headers=()
    headers+=("-H" "Content-Type: application/json")
    headers+=("-H" "User-Agent: HockeyDrillAPI-CurlTester/1.0")
    
    if [[ -n "$AUTH_TOKEN" ]]; then
        headers+=("-H" "Authorization: Bearer $AUTH_TOKEN")
        log_info "Authentication enabled"
    else
        log_warning "No authentication token provided"
    fi
    
    echo "${headers[@]}"
}

# Format JSON response
format_response() {
    local response="$1"
    local output_file="$2"
    
    if [[ "$HAS_JQ" == true ]]; then
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        echo "$response"
    fi > "$output_file"
}

# Execute API test
execute_test() {
    local test_name="$1"
    local payload="$2"
    local expected_status="${3:-200}"
    
    log_info "Running test: $test_name"
    
    local request_id="curl_${test_name}_${TIMESTAMP}_$$"
    local output_file="${OUTPUT_DIR}/${test_name}_${TIMESTAMP}.json"
    local headers_file="${OUTPUT_DIR}/${test_name}_${TIMESTAMP}_headers.txt"
    
    # Build headers array
    local headers_array
    IFS=' ' read -ra headers_array <<< "$(build_headers)"
    
    # Add request ID
    headers_array+=("-H" "X-Request-ID: $request_id")
    
    log_info "Request ID: $request_id"
    log_info "Payload: $(echo "$payload" | tr -d '\n' | cut -c1-100)..."
    
    # Execute request
    local start_time=$(date +%s%3N)
    
    local response
    local http_status
    
    response=$(curl -s -w "\n%{http_code}" \
        "${headers_array[@]}" \
        -X POST \
        -d "$payload" \
        --max-time 300 \
        --dump-header "$headers_file" \
        "$WEBHOOK_URL")
    
    local end_time=$(date +%s%3N)
    local duration=$((end_time - start_time))
    
    # Extract HTTP status code (last line)
    http_status=$(echo "$response" | tail -n 1)
    response_body=$(echo "$response" | sed '$d')
    
    log_info "Response time: ${duration}ms"
    log_info "HTTP Status: $http_status"
    
    # Save response
    format_response "$response_body" "$output_file"
    
    # Analyze response
    if [[ "$http_status" == "$expected_status" ]]; then
        log_success "Test $test_name: HTTP status correct ($http_status)"
        
        # Check if it's a successful API response
        if [[ "$http_status" == "200" && "$HAS_JQ" == true ]]; then
            local api_status=$(echo "$response_body" | jq -r '.status // "unknown"' 2>/dev/null)
            if [[ "$api_status" == "success" ]]; then
                local summary=$(echo "$response_body" | jq -r '.summary // empty' 2>/dev/null)
                if [[ -n "$summary" ]]; then
                    local total_tests=$(echo "$summary" | jq -r '.total_tests // 0' 2>/dev/null)
                    local passed_tests=$(echo "$summary" | jq -r '.passed_tests // 0' 2>/dev/null)
                    local pass_rate=$(echo "$summary" | jq -r '.pass_rate // "0%"' 2>/dev/null)
                    log_success "API Success: $passed_tests/$total_tests tests passed ($pass_rate)"
                fi
            else
                local error_msg=$(echo "$response_body" | jq -r '.message // "Unknown error"' 2>/dev/null)
                log_error "API Error: $error_msg"
            fi
        fi
        
        echo "✅ PASS" > "${OUTPUT_DIR}/${test_name}_${TIMESTAMP}_result.txt"
        return 0
    else
        log_error "Test $test_name: Expected $expected_status, got $http_status"
        
        if [[ "$HAS_JQ" == true ]]; then
            local error_msg=$(echo "$response_body" | jq -r '.message // .error // "No error message"' 2>/dev/null)
            log_error "Error message: $error_msg"
        fi
        
        echo "❌ FAIL" > "${OUTPUT_DIR}/${test_name}_${TIMESTAMP}_result.txt"
        return 1
    fi
}

# Test 1: Single test case
test_single_case() {
    local payload='{
        "test_case": {
            "test_id": "curl_single_001",
            "drill_description": "Two players skate in a figure-8 pattern around center ice while passing the puck",
            "expected_title": "Figure-8 Passing Drill", 
            "expected_players": "X1,X2",
            "expected_steps": 3,
            "expected_landmarks": "center_dot"
        },
        "config": {
            "temperature": 0.1,
            "returnFullSpecs": true,
            "includeDebugInfo": false
        }
    }'
    
    execute_test "single_case" "$payload" 200
}

# Test 2: Batch test cases
test_batch_cases() {
    local payload='{
        "test_cases": [
            {
                "test_id": "curl_batch_001",
                "drill_description": "Three forwards practice triangle passing with quick release shots",
                "expected_players": "X1,X2,X3"
            },
            {
                "test_id": "curl_batch_002",
                "drill_description": "Goalie and two defenders work on breakout passes from behind the net",
                "expected_players": "G1,X1,X2",
                "expected_landmarks": "behind_net"
            },
            {
                "test_id": "curl_batch_003",
                "drill_description": "Power play unit practices one-timer shots from the hash marks",
                "expected_landmarks": "left_hashmarks,right_hashmarks"
            }
        ],
        "config": {
            "batchSize": 3,
            "temperature": 0.2,
            "returnFullSpecs": false,
            "includeDebugInfo": false
        }
    }'
    
    execute_test "batch_cases" "$payload" 200
}

# Test 3: Direct array format
test_direct_array() {
    local payload='[
        {
            "test_id": "curl_array_001",
            "drill_description": "Simple skating drill around the perimeter of the rink"
        },
        {
            "test_id": "curl_array_002", 
            "drill_description": "Basic passing drill between center and wing positions"
        }
    ]'
    
    execute_test "direct_array" "$payload" 200
}

# Test 4: Minimal test case
test_minimal_case() {
    local payload='{
        "test_case": {
            "drill_description": "Player practices wrist shots from the slot"
        }
    }'
    
    execute_test "minimal_case" "$payload" 200
}

# Test 5: Invalid payload (should fail)
test_invalid_payload() {
    local payload='{
        "invalid_field": "this should cause an error",
        "test_case": {}
    }'
    
    execute_test "invalid_payload" "$payload" 400
}

# Test 6: Empty payload (should fail)
test_empty_payload() {
    local payload='{}'
    
    execute_test "empty_payload" "$payload" 400
}

# Test 7: Large batch test
test_large_batch() {
    local payload='{
        "test_cases": [
            {"test_id": "large_001", "drill_description": "Basic skating drill number 1"},
            {"test_id": "large_002", "drill_description": "Basic skating drill number 2"},
            {"test_id": "large_003", "drill_description": "Basic skating drill number 3"},
            {"test_id": "large_004", "drill_description": "Basic skating drill number 4"},
            {"test_id": "large_005", "drill_description": "Basic skating drill number 5"},
            {"test_id": "large_006", "drill_description": "Basic skating drill number 6"},
            {"test_id": "large_007", "drill_description": "Basic skating drill number 7"},
            {"test_id": "large_008", "drill_description": "Basic skating drill number 8"}
        ],
        "config": {
            "batchSize": 4,
            "returnFullSpecs": false
        }
    }'
    
    execute_test "large_batch" "$payload" 200
}

# Test 8: Authentication test (if token is set)
test_authentication() {
    if [[ -z "$AUTH_TOKEN" ]]; then
        log_warning "Skipping authentication test - no token provided"
        return 0
    fi
    
    # Test with wrong token
    local old_token="$AUTH_TOKEN"
    AUTH_TOKEN="invalid_token_12345"
    
    local payload='{
        "test_case": {
            "test_id": "auth_test",
            "drill_description": "This should fail with invalid token"
        }
    }'
    
    log_info "Testing invalid authentication token"
    execute_test "invalid_auth" "$payload" 400
    
    # Restore original token
    AUTH_TOKEN="$old_token"
}

# Generate summary report
generate_summary() {
    log_info "Generating test summary..."
    
    local summary_file="${OUTPUT_DIR}/test_summary_${TIMESTAMP}.txt"
    local total_tests=0
    local passed_tests=0
    
    echo "===============================================" > "$summary_file"
    echo "Hockey Drill API Curl Test Summary" >> "$summary_file"
    echo "===============================================" >> "$summary_file"
    echo "Timestamp: $(date)" >> "$summary_file"
    echo "Webhook URL: $WEBHOOK_URL" >> "$summary_file"
    echo "Authentication: ${AUTH_TOKEN:+Enabled}" >> "$summary_file"
    echo "" >> "$summary_file"
    
    # Count results
    for result_file in "${OUTPUT_DIR}"/*_${TIMESTAMP}_result.txt; do
        if [[ -f "$result_file" ]]; then
            total_tests=$((total_tests + 1))
            if grep -q "✅ PASS" "$result_file"; then
                passed_tests=$((passed_tests + 1))
            fi
        fi
    done
    
    local pass_rate=0
    if [[ $total_tests -gt 0 ]]; then
        pass_rate=$(( (passed_tests * 100) / total_tests ))
    fi
    
    echo "Test Results:" >> "$summary_file"
    echo "  Total Tests: $total_tests" >> "$summary_file"
    echo "  Passed: $passed_tests" >> "$summary_file"
    echo "  Failed: $((total_tests - passed_tests))" >> "$summary_file"
    echo "  Pass Rate: ${pass_rate}%" >> "$summary_file"
    echo "" >> "$summary_file"
    
    # Individual test results
    echo "Individual Test Results:" >> "$summary_file"
    for result_file in "${OUTPUT_DIR}"/*_${TIMESTAMP}_result.txt; do
        if [[ -f "$result_file" ]]; then
            local test_name=$(basename "$result_file" "_${TIMESTAMP}_result.txt")
            local result=$(cat "$result_file")
            echo "  $test_name: $result" >> "$summary_file"
        fi
    done
    
    echo "" >> "$summary_file"
    echo "Output files saved in: $OUTPUT_DIR" >> "$summary_file"
    
    # Display summary
    log_info "Test Summary:"
    log_info "  Total Tests: $total_tests"
    log_info "  Passed: $passed_tests"
    log_info "  Failed: $((total_tests - passed_tests))"
    log_info "  Pass Rate: ${pass_rate}%"
    log_info "Summary saved to: $summary_file"
    
    # Return exit code based on results
    if [[ $passed_tests -eq $total_tests && $total_tests -gt 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Help function
show_help() {
    echo "Hockey Drill API Curl Tester v7"
    echo ""
    echo "Usage: $0 [options] [test_name]"
    echo ""
    echo "Options:"
    echo "  --help                Show this help message"
    echo "  --webhook-url URL     Set webhook URL (overrides N8N_WEBHOOK_URL)"
    echo "  --auth-token TOKEN    Set authentication token (overrides N8N_WEBHOOK_TOKEN)"
    echo "  --output-dir DIR      Set output directory (default: ./curl_test_results)"
    echo "  --list-tests          List available test cases"
    echo ""
    echo "Available Tests:"
    echo "  single_case          Test single test case"
    echo "  batch_cases          Test multiple test cases"
    echo "  direct_array         Test direct array format"
    echo "  minimal_case         Test minimal payload"
    echo "  invalid_payload      Test invalid payload (should fail)"
    echo "  empty_payload        Test empty payload (should fail)"
    echo "  large_batch          Test large batch processing"
    echo "  authentication       Test authentication (if token provided)"
    echo "  all                  Run all tests (default)"
    echo ""
    echo "Environment Variables:"
    echo "  N8N_WEBHOOK_URL      Webhook URL (required)"
    echo "  N8N_WEBHOOK_TOKEN    Authentication token (optional)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all tests"
    echo "  $0 single_case                       # Run only single case test"
    echo "  $0 --webhook-url https://... all     # Run all with custom URL"
}

# List available tests
list_tests() {
    echo "Available test cases:"
    echo "  single_case"
    echo "  batch_cases"
    echo "  direct_array"
    echo "  minimal_case"
    echo "  invalid_payload"
    echo "  empty_payload"
    echo "  large_batch"
    echo "  authentication"
    echo "  all"
}

# Main execution
main() {
    local run_tests=("all")
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                exit 0
                ;;
            --webhook-url)
                WEBHOOK_URL="$2"
                shift 2
                ;;
            --auth-token)
                AUTH_TOKEN="$2"
                shift 2
                ;;
            --output-dir)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --list-tests)
                list_tests
                exit 0
                ;;
            single_case|batch_cases|direct_array|minimal_case|invalid_payload|empty_payload|large_batch|authentication|all)
                run_tests=("$1")
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Validate configuration
    if [[ "$WEBHOOK_URL" == "https://your-n8n-instance/webhook/drill-evaluation" ]]; then
        log_error "Please set N8N_WEBHOOK_URL environment variable or use --webhook-url"
        echo "Example: export N8N_WEBHOOK_URL='https://your-instance/webhook/drill-evaluation'"
        exit 1
    fi
    
    # Initialize
    check_dependencies
    setup_output_dir
    
    log_success "Hockey Drill API Curl Tester v7"
    log_info "Webhook URL: $WEBHOOK_URL"
    log_info "Output Directory: $OUTPUT_DIR"
    log_info "Timestamp: $TIMESTAMP"
    
    # Run tests
    local overall_success=true
    
    for test_name in "${run_tests[@]}"; do
        case $test_name in
            all)
                log_info "Running all tests..."
                test_single_case || overall_success=false
                test_batch_cases || overall_success=false
                test_direct_array || overall_success=false
                test_minimal_case || overall_success=false
                test_invalid_payload || true  # Expected to fail
                test_empty_payload || true    # Expected to fail
                test_large_batch || overall_success=false
                test_authentication || true  # May be skipped
                ;;
            single_case)
                test_single_case || overall_success=false
                ;;
            batch_cases)
                test_batch_cases || overall_success=false
                ;;
            direct_array)
                test_direct_array || overall_success=false
                ;;
            minimal_case)
                test_minimal_case || overall_success=false
                ;;
            invalid_payload)
                test_invalid_payload || true  # Expected to fail
                ;;
            empty_payload)
                test_empty_payload || true    # Expected to fail
                ;;
            large_batch)
                test_large_batch || overall_success=false
                ;;
            authentication)
                test_authentication || true  # May be skipped
                ;;
        esac
    done
    
    # Generate summary
    generate_summary
    local summary_success=$?
    
    # Final result
    if [[ "$overall_success" == true && $summary_success -eq 0 ]]; then
        log_success "All tests completed successfully!"
        exit 0
    else
        log_error "Some tests failed. Check the results in $OUTPUT_DIR"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"