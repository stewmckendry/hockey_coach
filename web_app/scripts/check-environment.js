#!/usr/bin/env node

/**
 * Environment check script for the secure chat setup
 * Run with: node check-environment.js
 */

console.log('🔍 Checking Environment Setup...\n')

// Check if .env.local exists
const fs = require('fs')
const path = require('path')

const envPath = path.join(process.cwd(), '.env.local')
const envExists = fs.existsSync(envPath)

console.log(`📄 .env.local file: ${envExists ? '✅ Found' : '❌ Missing'}`)

if (envExists) {
  try {
    const envContent = fs.readFileSync(envPath, 'utf8')
    const hasOpenAIKey = envContent.includes('OPENAI_API_KEY=') && !envContent.includes('OPENAI_API_KEY=your_openai_api_key_here')
    const hasMCPUrl = envContent.includes('NEXT_PUBLIC_FASTMCP_URL=')
    
    console.log(`🔑 OpenAI API Key: ${hasOpenAIKey ? '✅ Configured' : '❌ Missing or placeholder'}`)
    console.log(`🌐 MCP Server URL: ${hasMCPUrl ? '✅ Configured' : '❌ Using default'}`)
    
    if (!hasOpenAIKey) {
      console.log('\n⚠️  To fix this:')
      console.log('   1. Copy .env.example to .env.local: cp .env.example .env.local')
      console.log('   2. Edit .env.local and add your actual OpenAI API key')
      console.log('   3. Get an API key from: https://platform.openai.com/api-keys')
    }
  } catch (error) {
    console.log('❌ Error reading .env.local:', error.message)
  }
} else {
  console.log('\n⚠️  To fix this:')
  console.log('   1. Copy the example: cp .env.example .env.local')
  console.log('   2. Edit .env.local and add your OpenAI API key')
}

// Check if FastMCP server is running
console.log('\n🌐 Checking FastMCP Server...')

const checkFastMCP = async () => {
  try {
    const response = await fetch('http://localhost:3001/health')
    if (response.ok) {
      console.log('✅ FastMCP Server is running on port 3001')
    } else {
      console.log('⚠️  FastMCP Server responded but not healthy')
    }
  } catch (error) {
    console.log('❌ FastMCP Server not reachable')
    console.log('   Make sure to run: python start_services.py')
  }
}

// Check if OpenAI package is installed
console.log('\n📦 Checking Dependencies...')
try {
  require('openai')
  console.log('✅ OpenAI package is installed')
} catch (error) {
  console.log('❌ OpenAI package missing - run: npm install openai')
}

// Run async checks
checkFastMCP().then(() => {
  console.log('\n🏒 Environment Check Complete!')
  console.log('If all items show ✅, your setup should work.')
})
