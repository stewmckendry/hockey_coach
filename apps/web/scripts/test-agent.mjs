/**
 * Standalone test for the Secure Hockey Agent
 * This tests the core logic without needing the full Next.js server
 */

import { SecureHockeyAgent } from './lib/server/hockeyAgent.js'

async function testSecureAgent() {
  console.log('🧪 Testing Secure Hockey Agent...\n')

  try {
    const agent = new SecureHockeyAgent()
    
    console.log('📤 Testing with message: "Plan a simple U10 practice"')
    
    const result = await agent.processMessage(
      "Plan a simple U10 practice",
      []
    )
    
    console.log('✅ Success! Agent processed the message')
    console.log('📊 Metadata:', {
      intent: result.metadata.intent.intent,
      confidence: Math.round(result.metadata.intent.confidence * 100) + '%',
      toolsCalled: result.metadata.toolsCalled,
      processingTime: result.metadata.processingTimeMs + 'ms'
    })
    
    console.log('\n💬 Response preview:')
    console.log(result.response.substring(0, 300) + '...')
    
  } catch (error) {
    console.error('❌ Test failed:', error.message)
    
    if (error.message.includes('API key')) {
      console.log('\n💡 Make sure your OpenAI API key is set in .env.local')
    } else if (error.message.includes('fetch')) {
      console.log('\n💡 This is likely due to the FastMCP server not running')
      console.log('   The agent should handle this gracefully with fallbacks')
    }
  }
}

testSecureAgent()
