import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const maxDuration = 30;

interface FeedbackRequest {
  currentSpec: any;  // Diagram specification object
  feedback: string;  // Natural language feedback
}

interface FeedbackResponse {
  success: boolean;
  updatedSpec?: any;
  changes?: Array<{
    type: string;
    target: string;
    details: string;
  }>;
  explanation?: string;
  suggestions?: string[];
  error?: string;
  processingTime?: number;
}

export async function POST(request: NextRequest) {
  try {
    const body: FeedbackRequest = await request.json();
    const { currentSpec, feedback } = body;

    console.log('Feedback API received:', {
      hasCurrentSpec: !!currentSpec,
      currentSpecType: typeof currentSpec,
      currentSpecKeys: currentSpec ? Object.keys(currentSpec) : [],
      feedback: feedback
    });
    
    // Log the actual spec to debug
    console.log('Current spec:', JSON.stringify(currentSpec, null, 2));

    // Validate input
    if (!currentSpec || !feedback) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Missing required fields: currentSpec and feedback' 
        },
        { status: 400 }
      );
    }

    // Call MCP server to process feedback
    // Use direct hockey diagram MCP API on port 8001
    const mcp_url = 'http://localhost:8001/api/mcp';
    
    const requestBody = {
      tool: 'process_diagram_feedback',
      parameters: {
        current_spec: currentSpec,
        feedback: feedback
      }
    };
    
    console.log('Sending to MCP server:', JSON.stringify(requestBody, null, 2));
    console.log('MCP URL:', mcp_url);
    
    const response = await fetch(mcp_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    console.log('MCP response status:', response.status);
    const responseText = await response.text();
    console.log('MCP response body:', responseText);
    
    if (!response.ok) {
      throw new Error(`MCP server error: ${response.status} - ${responseText}`);
    }
    
    // Parse the response
    const mcp_result = JSON.parse(responseText);
    
    // Check for success
    if (!mcp_result.success) {
      throw new Error(mcp_result.error || 'MCP processing error');
    }

    // Extract the result data
    const result = mcp_result.data;

    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          error: result.error || 'Failed to process feedback',
          originalSpec: currentSpec
        },
        { status: 400 }
      );
    }

    // Return successful result
    return NextResponse.json({
      success: true,
      updatedSpec: result.updated_spec,
      changes: result.changes,
      explanation: result.explanation,
      suggestions: result.suggestions,
      processingTime: result.processing_time
    });

  } catch (error) {
    console.error('Feedback processing error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to process feedback'
      },
      { status: 500 }
    );
  }
}