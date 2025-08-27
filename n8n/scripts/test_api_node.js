#!/usr/bin/env node

/**
 * Node.js API testing script for n8n Hockey Drill Evaluation v7
 * Comprehensive testing with error handling and reporting
 */

const https = require('https');
const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');

class HockeyDrillAPITesterNode {
    constructor(webhookUrl, authToken = null) {
        this.webhookUrl = webhookUrl;
        this.authToken = authToken;
        this.results = [];
    }

    /**
     * Make HTTP request with promise support
     */
    makeRequest(options, data = null) {
        return new Promise((resolve, reject) => {
            const parsedUrl = url.parse(this.webhookUrl);
            const isHttps = parsedUrl.protocol === 'https:';
            const lib = isHttps ? https : http;

            const requestOptions = {
                hostname: parsedUrl.hostname,
                port: parsedUrl.port || (isHttps ? 443 : 80),
                path: parsedUrl.path,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'User-Agent': 'HockeyDrillAPI-NodeTester/1.0',
                    ...options.headers
                }
            };

            if (this.authToken) {
                requestOptions.headers['Authorization'] = `Bearer ${this.authToken}`;
            }

            if (data) {
                const jsonData = JSON.stringify(data);
                requestOptions.headers['Content-Length'] = Buffer.byteLength(jsonData);
            }

            const req = lib.request(requestOptions, (res) => {
                let responseData = '';
                
                res.on('data', (chunk) => {
                    responseData += chunk;
                });
                
                res.on('end', () => {
                    try {
                        const result = {
                            statusCode: res.statusCode,
                            headers: res.headers,
                            data: responseData
                        };
                        
                        if (res.headers['content-type'] && res.headers['content-type'].includes('application/json')) {
                            result.json = JSON.parse(responseData);
                        }
                        
                        resolve(result);
                    } catch (error) {
                        reject(new Error(`Failed to parse response: ${error.message}`));
                    }
                });
            });

            req.on('error', (error) => {
                reject(error);
            });

            req.on('timeout', () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });

            if (data) {
                req.write(JSON.stringify(data));
            }

            req.end();
        });
    }

    /**
     * Test single drill case
     */
    async testSingle(testCase, config = {}) {
        const requestId = `node_single_${Date.now()}`;
        
        const payload = {
            test_case: testCase,
            config: {
                temperature: 0.1,
                returnFullSpecs: true,
                includeDebugInfo: false,
                ...config
            }
        };

        const options = {
            headers: {
                'X-Request-ID': requestId
            }
        };

        console.log(`🧪 Testing single case: ${testCase.test_id}`);
        console.log(`📋 Request ID: ${requestId}`);

        const startTime = Date.now();

        try {
            const response = await this.makeRequest(options, payload);
            const processingTime = Date.now() - startTime;

            console.log(`📡 Response: ${response.statusCode} (${processingTime}ms)`);

            return this.processResponse(response, processingTime, requestId);
        } catch (error) {
            return {
                success: false,
                error: error.message,
                requestId,
                processingTime: Date.now() - startTime
            };
        }
    }

    /**
     * Test multiple drill cases
     */
    async testBatch(testCases, config = {}) {
        const requestId = `node_batch_${Date.now()}`;
        
        const payload = {
            test_cases: testCases,
            config: {
                batchSize: 5,
                temperature: 0.1,
                returnFullSpecs: false,
                includeDebugInfo: false,
                ...config
            }
        };

        const options = {
            headers: {
                'X-Request-ID': requestId
            }
        };

        console.log(`🧪 Testing batch: ${testCases.length} cases`);
        console.log(`📋 Request ID: ${requestId}`);

        const startTime = Date.now();

        try {
            const response = await this.makeRequest(options, payload);
            const processingTime = Date.now() - startTime;

            console.log(`📡 Response: ${response.statusCode} (${processingTime}ms)`);

            return this.processResponse(response, processingTime, requestId);
        } catch (error) {
            return {
                success: false,
                error: error.message,
                requestId,
                processingTime: Date.now() - startTime
            };
        }
    }

    /**
     * Process API response
     */
    processResponse(response, processingTime, requestId) {
        const result = {
            success: false,
            requestId,
            processingTime,
            statusCode: response.statusCode
        };

        if (response.statusCode === 200 && response.json && response.json.status === 'success') {
            result.success = true;
            result.summary = response.json.summary;
            result.results = response.json.results;
            result.performance = response.json.performance;
            result.recommendations = response.json.recommendations;
        } else {
            result.error = response.json ? 
                (response.json.message || 'Unknown error') : 
                'Non-JSON response';
            result.errorCode = response.json ? response.json.error_code : null;
            result.responseData = response.data;
        }

        return result;
    }

    /**
     * Generate comprehensive report
     */
    generateReport(results) {
        const report = [];
        const timestamp = new Date().toISOString();
        
        report.push('='.repeat(80));
        report.push('HOCKEY DRILL NODE.JS API TEST REPORT');
        report.push('='.repeat(80));
        report.push(`Generated: ${timestamp}`);
        report.push(`Tests Executed: ${results.length}`);
        report.push('');

        let totalSuccess = 0;
        let totalProcessingTime = 0;

        results.forEach((result, index) => {
            report.push(`📋 TEST ${index + 1}: ${result.requestId}`);
            report.push(`   Status: ${result.success ? '✅ SUCCESS' : '❌ FAILED'}`);
            report.push(`   Processing Time: ${result.processingTime}ms`);
            report.push(`   HTTP Status: ${result.statusCode}`);

            if (result.success) {
                totalSuccess++;
                const summary = result.summary;
                
                report.push(`   Total Tests: ${summary.total_tests}`);
                report.push(`   Passed: ${summary.passed_tests}`);
                report.push(`   Failed: ${summary.failed_tests}`);
                report.push(`   Pass Rate: ${summary.pass_rate}`);
                report.push(`   Average Score: ${summary.average_score}`);

                // Individual results
                if (result.results && result.results.length > 0) {
                    report.push('   Individual Results:');
                    result.results.forEach((testResult, i) => {
                        const status = testResult.passed ? '✅' : '❌';
                        report.push(`     ${i + 1}. ${testResult.test_id} - ${status} (${testResult.score}/100)`);
                        if (testResult.issues && testResult.issues.length > 0) {
                            report.push(`        Issues: ${testResult.issues.join(', ')}`);
                        }
                    });
                }
            } else {
                report.push(`   Error: ${result.error}`);
                if (result.errorCode) {
                    report.push(`   Error Code: ${result.errorCode}`);
                }
            }

            totalProcessingTime += result.processingTime;
            report.push('');
        });

        // Summary
        report.push('📊 OVERALL SUMMARY:');
        report.push(`   Successful API Calls: ${totalSuccess}/${results.length}`);
        report.push(`   Success Rate: ${((totalSuccess / results.length) * 100).toFixed(1)}%`);
        report.push(`   Total Processing Time: ${totalProcessingTime}ms`);
        report.push(`   Average Processing Time: ${(totalProcessingTime / results.length).toFixed(1)}ms`);
        report.push('');
        report.push('='.repeat(80));

        return report.join('\n');
    }

    /**
     * Save report to file
     */
    saveReport(report, filename) {
        try {
            fs.writeFileSync(filename, report, 'utf8');
            console.log(`📄 Report saved to: ${filename}`);
        } catch (error) {
            console.error(`❌ Failed to save report: ${error.message}`);
        }
    }

    /**
     * Load test cases from JSON file
     */
    loadTestCasesFromFile(filename) {
        try {
            const data = fs.readFileSync(filename, 'utf8');
            return JSON.parse(data);
        } catch (error) {
            console.error(`❌ Failed to load test cases: ${error.message}`);
            return null;
        }
    }

    /**
     * Create default test cases
     */
    getDefaultTestCases() {
        return [
            {
                test_id: 'node_001',
                drill_description: 'Two players practice one-timer shots from the face-off circles',
                expected_title: 'One-Timer Practice',
                expected_players: 'X1,X2',
                expected_landmarks: 'left_hashmarks,right_hashmarks'
            },
            {
                test_id: 'node_002', 
                drill_description: 'Goalie and two forwards work on rebound control in the slot',
                expected_players: 'G1,X1,X2',
                expected_landmarks: 'low_slot'
            },
            {
                test_id: 'node_003',
                drill_description: 'Three players skate in a weaving pattern with puck control',
                expected_players: 'X1,X2,X3',
                expected_steps: 3
            }
        ];
    }
}

/**
 * Create sample test cases file
 */
function createSampleTestCases() {
    const sampleCases = {
        single_test: {
            test_id: 'sample_single',
            drill_description: 'Player skates around center ice with puck control',
            expected_title: 'Center Ice Control',
            expected_players: 'X1',
            expected_landmarks: 'center_dot'
        },
        batch_tests: [
            {
                test_id: 'sample_batch_001',
                drill_description: 'Two forwards practice give-and-go with coach',
                expected_players: 'X1,X2,C1'
            },
            {
                test_id: 'sample_batch_002',
                drill_description: 'Power play formation drill with five players',
                expected_players: 'X1,X2,X3,X4,X5'
            }
        ]
    };

    const filename = 'sample_test_cases.json';
    try {
        fs.writeFileSync(filename, JSON.stringify(sampleCases, null, 2));
        console.log(`📄 Sample test cases created: ${filename}`);
    } catch (error) {
        console.error(`❌ Failed to create sample file: ${error.message}`);
    }
}

/**
 * Main execution function
 */
async function main() {
    const args = process.argv.slice(2);
    
    // Parse command line arguments
    const config = {
        webhookUrl: process.env.N8N_WEBHOOK_URL || 'https://your-n8n-instance/webhook/drill-evaluation',
        authToken: process.env.N8N_WEBHOOK_TOKEN,
        testFile: null,
        outputFile: null,
        mode: 'default', // default, single, batch, sample
        batchSize: 5,
        temperature: 0.1
    };

    // Simple argument parsing
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--test-file':
                config.testFile = args[++i];
                break;
            case '--output':
                config.outputFile = args[++i];
                break;
            case '--mode':
                config.mode = args[++i];
                break;
            case '--batch-size':
                config.batchSize = parseInt(args[++i]);
                break;
            case '--temperature':
                config.temperature = parseFloat(args[++i]);
                break;
            case '--create-sample':
                createSampleTestCases();
                return;
            case '--help':
                console.log(`
Hockey Drill API Tester (Node.js)

Usage: node test_api_node.js [options]

Options:
  --test-file <file>    Load test cases from JSON file
  --output <file>       Save report to file
  --mode <mode>         Test mode: default, single, batch
  --batch-size <size>   Batch size for batch mode (default: 5)
  --temperature <temp>  Model temperature (default: 0.1)
  --create-sample       Create sample test cases file
  --help               Show this help message

Environment Variables:
  N8N_WEBHOOK_URL      Webhook URL (required)
  N8N_WEBHOOK_TOKEN    Authentication token (optional)

Examples:
  node test_api_node.js
  node test_api_node.js --mode batch --batch-size 10
  node test_api_node.js --test-file my_tests.json --output report.txt
                `);
                return;
        }
    }

    // Validate webhook URL
    if (config.webhookUrl === 'https://your-n8n-instance/webhook/drill-evaluation') {
        console.error('⚠️  Please set N8N_WEBHOOK_URL environment variable');
        console.error('   Example: export N8N_WEBHOOK_URL="https://your-instance/webhook/drill-evaluation"');
        process.exit(1);
    }

    // Initialize tester
    const tester = new HockeyDrillAPITesterNode(config.webhookUrl, config.authToken);

    console.log('🏒 Hockey Drill Node.js API Tester v1.0');
    console.log(`🔗 Webhook URL: ${config.webhookUrl}`);
    console.log(`🔐 Authentication: ${config.authToken ? 'Enabled' : 'Disabled'}`);
    console.log(`⚙️  Mode: ${config.mode}`);

    const results = [];

    try {
        switch (config.mode) {
            case 'single':
                console.log('\n🧪 Running single test...');
                const singleTest = {
                    test_id: 'node_single_test',
                    drill_description: 'Simple passing drill between two players at center ice',
                    expected_players: 'X1,X2',
                    expected_landmarks: 'center_dot'
                };
                const singleResult = await tester.testSingle(singleTest, {
                    temperature: config.temperature,
                    returnFullSpecs: true
                });
                results.push(singleResult);
                break;

            case 'batch':
                console.log('\n🧪 Running batch test...');
                const batchTests = config.testFile ? 
                    tester.loadTestCasesFromFile(config.testFile)?.batch_tests :
                    tester.getDefaultTestCases();
                
                if (!batchTests) {
                    console.error('❌ No test cases available');
                    process.exit(1);
                }

                const batchResult = await tester.testBatch(batchTests, {
                    batchSize: config.batchSize,
                    temperature: config.temperature,
                    returnFullSpecs: false
                });
                results.push(batchResult);
                break;

            default:
                console.log('\n🧪 Running default tests (single + batch)...');
                
                // Single test
                const defaultSingle = {
                    test_id: 'default_single',
                    drill_description: 'Player practices wrist shots from the slot',
                    expected_landmarks: 'low_slot'
                };
                const defaultSingleResult = await tester.testSingle(defaultSingle);
                results.push(defaultSingleResult);

                // Small batch test
                const defaultBatch = tester.getDefaultTestCases().slice(0, 2);
                const defaultBatchResult = await tester.testBatch(defaultBatch);
                results.push(defaultBatchResult);
                break;
        }

        // Generate and display report
        const report = tester.generateReport(results);
        console.log('\n' + report);

        // Save report if requested
        if (config.outputFile) {
            tester.saveReport(report, config.outputFile);
        }

        // Exit with success code if all tests passed
        const allSuccess = results.every(r => r.success);
        process.exit(allSuccess ? 0 : 1);

    } catch (error) {
        console.error(`💥 Unexpected error: ${error.message}`);
        process.exit(1);
    }
}

// Run if this is the main module
if (require.main === module) {
    main().catch(error => {
        console.error(`💥 Fatal error: ${error.message}`);
        process.exit(1);
    });
}

module.exports = HockeyDrillAPITesterNode;