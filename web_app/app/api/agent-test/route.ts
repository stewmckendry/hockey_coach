/**
 * API endpoint for testing OpenAI Agents SDK integration
 * 
 * This endpoint:
 * - Bridges web app to POC agent
 * - Handles async agent communication
 * - Provides proper error handling
 * - Returns structured responses for UI consumption
 */

import { NextRequest, NextResponse } from 'next/server';

interface AgentRequest {
  message: string;
  sessionId?: string;
}

interface AgentResponse {
  response: string;
  error?: string;
  timestamp: string;
  processingTime: number;
}

export async function POST(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    const body: AgentRequest = await request.json();
    
    if (!body.message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    console.log(`[Agent API] Processing message: "${body.message}"`);

    // Call POC agent via Python subprocess
    const agentResponse = await callPocAgent(body.message);
    
    const processingTime = Date.now() - startTime;
    
    const response: AgentResponse = {
      response: agentResponse,
      timestamp: new Date().toISOString(),
      processingTime
    };

    console.log(`[Agent API] Response generated in ${processingTime}ms`);

    return NextResponse.json(response);

  } catch (error) {
    console.error('[Agent API] Error:', error);
    
    const processingTime = Date.now() - startTime;
    
    return NextResponse.json(
      {
        error: 'Failed to process agent request',
        timestamp: new Date().toISOString(),
        processingTime
      },
      { status: 500 }
    );
  }
}

/**
 * Call the POC agent via HTTP server (avoids subprocess issues)
 */
async function callPocAgent(message: string): Promise<string> {
  const agentServerUrl = 'http://localhost:8002';
  
  console.log(`[Agent API] Using HTTP server approach: ${agentServerUrl}`);
  console.log(`[Agent API] With message: ${message}`);

  try {
    const response = await fetch(agentServerUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    console.log(`[Agent API] HTTP response received successfully`);
    return data.response;

  } catch (error) {
    console.error('[Agent API] HTTP request error:', error);
    throw new Error(`Failed to call agent HTTP server: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'Agent Test API is running',
    endpoint: '/api/agent-test',
    methods: ['POST'],
    timestamp: new Date().toISOString()
  });
}