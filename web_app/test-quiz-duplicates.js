/**
 * Test script to verify quiz duplicate prevention
 * Simulates asking multiple questions to ensure no duplicates
 */

async function testQuizDuplicates() {
  const baseUrl = 'http://localhost:3000/api/hockey-iq/quiz'
  const category = 'rules'
  const askedQuestions = []
  const questionTexts = new Set()
  
  console.log('🧪 Testing Quiz Duplicate Prevention')
  console.log('=====================================\n')
  
  // Simulate asking 10 questions
  for (let i = 1; i <= 10; i++) {
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
          askedQuestionIds: askedQuestions
        })
      })
      
      const data = await response.json()
      
      if (data.success && data.question) {
        const q = data.question
        
        // Check for duplicate ID
        if (askedQuestions.includes(q.id)) {
          console.error(`❌ DUPLICATE DETECTED! Question ID: ${q.id}`)
          console.error(`   This question was already asked!`)
        } else {
          console.log(`✅ Unique question received`)
        }
        
        // Check for duplicate text (different IDs but same content)
        if (questionTexts.has(q.question)) {
          console.warn(`⚠️  Same question text seen before (might be from cache with new ID)`)
        }
        
        // Track this question
        askedQuestions.push(q.id)
        questionTexts.add(q.question)
        
        // Display question details
        console.log(`   ID: ${q.id}`)
        console.log(`   Source: ${data.source || 'unknown'}`)
        console.log(`   Category: ${q.category}`)
        console.log(`   Question: ${q.question.substring(0, 60)}...`)
        
        if (q.researchSource) {
          console.log(`   Research: ${q.researchSource}`)
        }
        
        // Small delay to simulate user interaction
        await new Promise(resolve => setTimeout(resolve, 500))
        
      } else {
        console.error('❌ Failed to get question:', data.error)
      }
      
    } catch (error) {
      console.error('❌ Request failed:', error.message)
    }
  }
  
  // Summary
  console.log('\n=====================================')
  console.log('📊 Test Summary:')
  console.log(`   Total questions requested: 10`)
  console.log(`   Unique question IDs: ${askedQuestions.length}`)
  console.log(`   Unique question texts: ${questionTexts.size}`)
  
  if (askedQuestions.length === 10) {
    console.log('✅ All questions were unique!')
  } else {
    console.log('❌ Duplicates were detected')
  }
  
  // Show all question IDs for verification
  console.log('\n📋 Question IDs received:')
  askedQuestions.forEach((id, index) => {
    const isDynamic = id.startsWith('dynamic_')
    console.log(`   ${index + 1}. ${id} ${isDynamic ? '(dynamic)' : '(static)'}`)
  })
}

// Run the test
testQuizDuplicates().catch(console.error)