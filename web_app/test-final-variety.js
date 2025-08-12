/**
 * Final test to verify question variety with better topic detection
 */

async function testFinalVariety() {
  const baseUrl = 'http://localhost:3000/api/hockey-iq/quiz'
  const category = 'rules'
  
  console.log('🧪 Final Variety Test - Hockey IQ Quiz')
  console.log('=====================================\n')
  
  // Clear cache
  console.log('🗑️  Clearing cache...')
  await fetch(baseUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'clear_cache', category: 'rules' })
  })
  
  // Test 10 questions for better sample size
  const questions = []
  const askedIds = []
  
  for (let i = 1; i <= 10; i++) {
    console.log(`\n📝 Question #${i}:`)
    
    const response = await fetch(baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'get_question',
        category: category,
        useDynamic: true,
        difficulty: 'rookie',
        askedQuestionIds: askedIds,
        includeThunderContext: false
      })
    })
    
    const data = await response.json()
    
    if (data.success && data.question) {
      const q = data.question
      questions.push(q)
      askedIds.push(q.id)
      
      console.log(`   Q: ${q.question}`)
      console.log(`   A: ${q.correctAnswer}`)
      console.log(`   Source: ${q.researchSource || 'unknown'}`)
      
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  }
  
  // Analyze topics based on actual question content
  console.log('\n=====================================')
  console.log('📊 Topic Analysis:')
  console.log('=====================================\n')
  
  const topics = questions.map(q => {
    const text = (q.question + ' ' + q.correctAnswer).toLowerCase()
    
    // More comprehensive topic detection
    if (text.includes('offside') || text.includes('off-side')) {
      if (text.includes('delayed')) return 'Offside - Delayed'
      if (text.includes('intentional')) return 'Offside - Intentional'
      return 'Offside - General'
    }
    if (text.includes('icing')) return 'Icing'
    if (text.includes('penalty shot')) return 'Penalty Shot'
    if (text.includes('tripping') || text.includes('slashing') || text.includes('hooking')) return 'Penalties - Minor'
    if (text.includes('fighting') || text.includes('misconduct')) return 'Penalties - Major'
    if (text.includes('power play') || text.includes('penalty kill')) return 'Special Teams'
    if (text.includes('face-off') || text.includes('faceoff')) return 'Face-offs'
    if (text.includes('overtime') || text.includes('shootout')) return 'Overtime/Shootout'
    if (text.includes('goalie') || text.includes('crease')) return 'Goalie Rules'
    if (text.includes('fair') || text.includes('bully') || text.includes('respect')) return 'Fair Play'
    if (text.includes('blue line') && !text.includes('offside')) return 'Zone Play'
    if (text.includes('whistle')) return 'Officials'
    
    return 'Other Rules'
  })
  
  // Count unique topics
  const topicCounts = {}
  topics.forEach(topic => {
    topicCounts[topic] = (topicCounts[topic] || 0) + 1
  })
  
  // Display results
  Object.entries(topicCounts).sort((a, b) => b[1] - a[1]).forEach(([topic, count]) => {
    const percentage = ((count / questions.length) * 100).toFixed(0)
    console.log(`   ${topic.padEnd(25)} ${count}/${questions.length} (${percentage}%)`)
  })
  
  const uniqueTopics = Object.keys(topicCounts).length
  const maxCount = Math.max(...Object.values(topicCounts))
  
  console.log('\n📋 Summary:')
  console.log(`   Total questions: ${questions.length}`)
  console.log(`   Unique topics: ${uniqueTopics}`)
  console.log(`   Most common topic appears: ${maxCount} times`)
  console.log(`   MCP server used: ${questions.filter(q => q.researchSource !== 'default').length}/${questions.length} times`)
  
  if (uniqueTopics >= 5) {
    console.log('\n✅ EXCELLENT: Great topic variety achieved!')
  } else if (uniqueTopics >= 3) {
    console.log('\n✅ GOOD: Reasonable topic variety.')
  } else {
    console.log('\n⚠️  LIMITED: Topic variety could be better.')
  }
  
  // Check for the original problem
  const offsideCount = Object.entries(topicCounts)
    .filter(([topic]) => topic.includes('Offside'))
    .reduce((sum, [_, count]) => sum + count, 0)
  
  if (offsideCount === questions.length) {
    console.log('\n🚨 PROBLEM PERSISTS: All questions still about offsides!')
  } else if (offsideCount > questions.length * 0.5) {
    console.log(`\n⚠️  PARTIAL FIX: ${(offsideCount/questions.length*100).toFixed(0)}% still about offsides.`)
  } else {
    console.log(`\n✅ PROBLEM FIXED: Only ${(offsideCount/questions.length*100).toFixed(0)}% about offsides.`)
  }
}

testFinalVariety().catch(console.error)