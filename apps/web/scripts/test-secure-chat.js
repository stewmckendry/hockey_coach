#!/usr/bin/env node

/**
 * Simple test script for the secure chat API
 * Run with: node test-secure-chat.js
 */

const fetch = require('node-fetch')

async function testSecureChat() {
  console.log('🧪 Testing Secure Chat API...\n')

  const testMessage = "Plan a simple U10 practice"
  
  try {
    console.log(`📤 Sending message: "${testMessage}"`)
    
    const response = await fetch('http://localhost:3000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: testMessage,
        conversationHistory: []
      }),
    })

    console.log(`📡 Response status: ${response.status}`)

    if (!response.ok) {
      const errorData = await response.json()
      console.error('❌ Error response:', errorData)
      return
    }

    const data = await response.json()
    
    console.log('✅ Success! Response received:')
    console.log('📊 Metadata:', {
      intent: data.metadata?.intent?.intent,
      confidence: data.metadata?.intent?.confidence,
      toolsCalled: data.metadata?.toolsCalled,
      processingTime: `${data.metadata?.processingTimeMs}ms`
    })
    
    console.log('\n💬 Response preview:')
    console.log(data.response.substring(0, 200) + '...')

  } catch (error) {
    console.error('❌ Test failed:', error.message)
    console.log('\n💡 Make sure:')
    console.log('   1. Next.js dev server is running (npm run dev)')
    console.log('   2. OpenAI API key is set in .env.local')
    console.log('   3. FastMCP server is running')
  }
}

testSecureChat()
