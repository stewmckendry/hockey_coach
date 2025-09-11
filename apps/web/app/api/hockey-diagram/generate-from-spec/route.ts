import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const maxDuration = 30;

interface GenerateFromSpecRequest {
  spec: any;  // Parsed diagram specification
}

interface GenerateFromSpecResponse {
  success: boolean;
  imageBase64?: string;
  error?: string;
  processingTime?: number;
}

export async function POST(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    const body: GenerateFromSpecRequest = await request.json();
    const { spec } = body;

    // Validate input
    if (!spec) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Missing required field: spec' 
        },
        { status: 400 }
      );
    }

    // Call the direct API endpoint for spec generation
    const api_url = 'http://localhost:8001/generate-from-spec';
    
    const response = await fetch(api_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        spec: spec
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('MCP server error:', response.status, errorText);
      throw new Error(`MCP server error: ${response.status}`);
    }

    const result = await response.json();
    
    // Check for success
    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          error: result.error || 'Failed to generate diagram from spec'
        },
        { status: 400 }
      );
    }

    // Return successful result with base64 image
    return NextResponse.json({
      success: true,
      imageBase64: result.base64_data || result.image_base64 || result.imageBase64,
      processingTime: Date.now() - startTime
    });

  } catch (error) {
    console.error('Generate from spec error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to generate diagram from spec',
        processingTime: Date.now() - startTime
      },
      { status: 500 }
    );
  }
}