/**
 * Test script to verify dynamic query generation produces varied questions
 * This tests that the queries are now dynamic and produce different topics
 */

async function testDynamicQueries() {
  const baseUrl = 'http://localhost:3000/api/hockey-iq/quiz'
  const category = 'rules' // Same category that was producing only offsides questions
  const questions = []
  
  console.log('🧪 Testing Dynamic Query Generation')
  console.log('=====================================\n')
  console.log('Testing category: rules')
  console.log('Expected: Varied topics (penalties, icing, face-offs, etc.)')
  console.log('Previous issue: All questions were about offsides\n')
  
  // Clear the cache first to force new generation
  console.log('🗑️  Clearing cache for rules category...')
  const clearResponse = await fetch(baseUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'clear_cache',
      category: 'rules'
    })
  })
  
  const clearResult = await clearResponse.json()
  console.log(`   ${clearResult.message}\n`)
  
  // Track asked question IDs to force new generation
  const askedQuestionIds = []
  
  // Request 5 questions to see variety
  for (let i = 1; i <= 5; i++) {
    console.log(`\n📝 Requesting Question #${i}...`)
    
    try {
      const response = await fetch(baseUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'get_question',
          category: category,
          useDynamic: true,
          difficulty: 'rookie',
          askedQuestionIds: askedQuestionIds, // Pass previously asked questions to force new generation
          includeThunderContext: false // Disable Thunder context for cleaner testing
        })
      })
      
      const data = await response.json()
      
      if (data.success && data.question) {
        const q = data.question
        questions.push(q)
        askedQuestionIds.push(q.id) // Track this question as asked
        
        // Display question details
        console.log(`✅ Question received`)
        console.log(`   ID: ${q.id}`)
        console.log(`   Source: ${data.source || 'unknown'}`)
        console.log(`   Research: ${q.researchSource || 'none'}`)
        console.log(`   Question: ${q.question}`)
        console.log(`   Answer: ${q.correctAnswer}`)
        
        // Extract topic from question
        const topicIndicators = {
          'offside': 'Offsides',
          'icing': 'Icing',
          'penalty': 'Penalties',
          'face-off': 'Face-offs',
          'face off': 'Face-offs',
          'goalie': 'Goalie rules',
          'crease': 'Crease rules',
          'overtime': 'Overtime',
          'shootout': 'Shootout',
          'too many men': 'Too many men',
          'line change': 'Line changes',
          'tripping': 'Penalties',
          'slashing': 'Penalties',
          'hooking': 'Penalties',
          'fighting': 'Penalties',
          'checking': 'Penalties',
          'power play': 'Power play',
          'penalty kill': 'Penalty kill',
          'two-line pass': 'Two-line pass',
          'coach challenge': 'Video review',
          'video review': 'Video review'
        }
        
        let detectedTopic = 'Other'
        const questionLower = q.question.toLowerCase()
        for (const [keyword, topic] of Object.entries(topicIndicators)) {
          if (questionLower.includes(keyword)) {
            detectedTopic = topic
            break
          }
        }
        
        console.log(`   📌 Topic: ${detectedTopic}`)
        
        // Small delay to simulate user interaction
        await new Promise(resolve => setTimeout(resolve, 1000))
        
      } else {
        console.error('❌ Failed to get question:', data.error)
      }
      
    } catch (error) {
      console.error('❌ Request failed:', error.message)
    }
  }
  
  // Analyze topic diversity
  console.log('\n=====================================')
  console.log('📊 Topic Diversity Analysis:')
  console.log('=====================================\n')
  
  const topicCounts = {}
  questions.forEach((q, index) => {
    const questionLower = q.question.toLowerCase()
    
    // Detect topics
    const topicIndicators = {
      'offside': 'Offsides',
      'icing': 'Icing',
      'penalty': 'Penalties',
      'face-off': 'Face-offs',
      'face off': 'Face-offs',
      'goalie': 'Goalie rules',
      'crease': 'Crease rules',
      'overtime': 'Overtime',
      'shootout': 'Shootout',
      'too many men': 'Too many men',
      'line change': 'Line changes',
      'tripping': 'Penalties',
      'slashing': 'Penalties',
      'hooking': 'Penalties',
      'fighting': 'Penalties',
      'checking': 'Penalties',
      'power play': 'Power play',
      'penalty kill': 'Penalty kill',
      'two-line pass': 'Two-line pass',
      'coach challenge': 'Video review',
      'video review': 'Video review'
    }
    
    let detectedTopic = 'Other'
    for (const [keyword, topic] of Object.entries(topicIndicators)) {
      if (questionLower.includes(keyword)) {
        detectedTopic = topic
        break
      }
    }
    
    topicCounts[detectedTopic] = (topicCounts[detectedTopic] || 0) + 1
    console.log(`Question ${index + 1}: ${detectedTopic}`)
  })
  
  console.log('\n📈 Topic Distribution:')
  Object.entries(topicCounts).forEach(([topic, count]) => {
    const percentage = ((count / questions.length) * 100).toFixed(0)
    const bar = '█'.repeat(Math.ceil(count * 10 / questions.length))
    console.log(`   ${topic.padEnd(15)} ${bar} ${count}/${questions.length} (${percentage}%)`)
  })
  
  // Determine if variety improved
  const uniqueTopics = Object.keys(topicCounts).length
  const maxTopicCount = Math.max(...Object.values(topicCounts))
  const dominanceRatio = maxTopicCount / questions.length
  
  console.log('\n📋 Results:')
  console.log(`   Total questions: ${questions.length}`)
  console.log(`   Unique topics: ${uniqueTopics}`)
  console.log(`   Topic dominance: ${(dominanceRatio * 100).toFixed(0)}% (lower is better)`)
  
  if (uniqueTopics >= 3 && dominanceRatio < 0.6) {
    console.log('\n✅ SUCCESS: Questions show good topic variety!')
    console.log('   The dynamic query generation is working correctly.')
  } else if (uniqueTopics >= 2 && dominanceRatio < 0.8) {
    console.log('\n⚠️  PARTIAL SUCCESS: Some variety, but could be better.')
    console.log('   Consider checking if MCP server is responding properly.')
  } else {
    console.log('\n❌ ISSUE PERSISTS: Questions still lack variety.')
    console.log('   Check if MCP server is running and responding to varied queries.')
  }
  
  // Check if all questions were about offsides (the original problem)
  if (topicCounts['Offsides'] === questions.length) {
    console.log('\n🚨 CRITICAL: All questions are still about offsides!')
    console.log('   The fix may not be working. Check server logs.')
  }
}

// Run the test
testDynamicQueries().catch(console.error)