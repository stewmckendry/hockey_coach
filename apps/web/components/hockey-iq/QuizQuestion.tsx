'use client'

import { useState, useEffect } from 'react'
import { Question } from './HockeyIQInterface'

interface QuizQuestionProps {
  question: Question
  onAnswer: (correct: boolean) => void
  questionsAnswered: number
}

/**
 * Quiz question component with Socratic hints and encouragement
 * Designed for U10 players with large buttons and visual feedback
 */
export function QuizQuestion({ question, onAnswer, questionsAnswered }: QuizQuestionProps) {
  const [userAnswer, setUserAnswer] = useState('')
  const [showHint, setShowHint] = useState(false)
  const [hintIndex, setHintIndex] = useState(0)
  const [attempts, setAttempts] = useState(0)
  const [showFollowUp, setShowFollowUp] = useState(false)
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null)

  // Reset state when new question loads
  useEffect(() => {
    setUserAnswer('')
    setShowHint(false)
    setHintIndex(0)
    setAttempts(0)
    setShowFollowUp(false)
    setIsCorrect(null)
    
    // Log question source for debugging
    if (question.id.startsWith('dynamic_')) {
      console.log('📚 Dynamic question loaded:', question.id, 'Research:', (question as any).researchSource)
    } else {
      console.log('📝 Static question loaded:', question.id)
    }
  }, [question.id])

  const handleSubmit = async () => {
    // Use LLM to check answer instead of simple string matching
    try {
      const response = await fetch('/api/hockey-iq/quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'evaluate_answer',
          questionId: question.id,
          userAnswer: userAnswer,
          // Include question data for dynamic questions
          questionText: question.question,
          correctAnswer: question.correctAnswer,
          funFact: question.funFact,
          followUpQuestions: question.followUpQuestions
        })
      })

      const result = await response.json()
      
      // Use LLM evaluation result
      const correct = result.correct || false
      
      setIsCorrect(correct)
      setAttempts(attempts + 1)

      if (correct) {
        setShowFollowUp(true)
        setTimeout(() => {
          onAnswer(true)
        }, 3000)
      } else if (attempts < 2) {
        // Show hint after wrong answer
        setShowHint(true)
        if (hintIndex < question.hints.length - 1) {
          setHintIndex(hintIndex + 1)
        }
      } else {
        // After 3 attempts, show the answer and move on
        setTimeout(() => {
          onAnswer(false)
        }, 3000)
      }
    } catch (error) {
      console.error('Error checking answer:', error)
      // Fallback to simple string matching if API fails
      const correct = userAnswer.toLowerCase().includes(question.correctAnswer.toLowerCase()) ||
                     question.correctAnswer.toLowerCase().includes(userAnswer.toLowerCase())
      
      setIsCorrect(correct)
      setAttempts(attempts + 1)

      if (correct) {
        setShowFollowUp(true)
        setTimeout(() => {
          onAnswer(true)
        }, 3000)
      } else if (attempts < 2) {
        setShowHint(true)
        if (hintIndex < question.hints.length - 1) {
          setHintIndex(hintIndex + 1)
        }
      } else {
        setTimeout(() => {
          onAnswer(false)
        }, 3000)
      }
    }
  }

  const getLevelBadge = () => {
    const colors: Record<string, string> = {
      rookie: 'bg-green-200 text-green-800',
      player: 'bg-blue-200 text-blue-800',
      'all-star': 'bg-purple-200 text-purple-800'
    }
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-bold ${colors[question.level]}`}>
        {question.level.charAt(0).toUpperCase() + question.level.slice(1)}
      </span>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Question Header */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-4">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              {getLevelBadge()}
              <span className="text-sm text-gray-500">Question #{questionsAnswered + 1}</span>
              {/* Research Source Indicator */}
              {question.researchSource && question.researchSource !== 'static' && question.researchSource !== 'default' && (
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700 flex items-center gap-1">
                  <span>🔍</span>
                  <span>
                    AI Generated from {
                      question.researchSource === 'exa_web_search' 
                        ? 'Web Search' 
                        : question.researchSource.replace('search_hockey_', '').replace('_', ' ')
                    }
                  </span>
                </span>
              )}
              {question.thunderContext && (
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700 flex items-center gap-1">
                  <span>⚡</span>
                  <span>Thunder Team</span>
                </span>
              )}
            </div>
            <h2 className="text-2xl font-bold text-gray-800 leading-relaxed">
              {question.question}
            </h2>
          </div>
          <span className="text-4xl ml-4">🤔</span>
        </div>

        {/* Hint Display */}
        {showHint && (
          <div className="mt-4 p-4 bg-yellow-50 border-2 border-yellow-200 rounded-lg">
            <div className="flex items-start gap-2">
              <span className="text-2xl">💡</span>
              <div>
                <p className="font-medium text-yellow-800">Hint:</p>
                <p className="text-gray-700">{question.hints[hintIndex]}</p>
              </div>
            </div>
          </div>
        )}

        {/* Answer Input */}
        <div className="mt-6">
          <textarea
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            placeholder="Type your answer here... or just the key words!"
            className="w-full p-4 text-lg border-2 border-gray-200 rounded-lg focus:border-blue-400 focus:outline-none resize-none"
            rows={3}
            disabled={isCorrect !== null}
          />
        </div>

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={!userAnswer.trim() || isCorrect !== null}
          className={`mt-4 w-full py-4 rounded-lg font-bold text-lg transition-all transform hover:scale-105 ${
            isCorrect === true
              ? 'bg-green-500 text-white'
              : isCorrect === false
              ? 'bg-orange-400 text-white'
              : userAnswer.trim()
              ? 'bg-blue-500 text-white hover:bg-blue-600 shadow-lg'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          {isCorrect === true
            ? '🎉 Correct! Great job!'
            : isCorrect === false
            ? `💪 Good try! The answer is: ${question.correctAnswer}`
            : 'Check My Answer!'}
        </button>

        {/* Feedback Message */}
        {isCorrect !== null && (
          <div className={`mt-4 p-4 rounded-lg ${
            isCorrect ? 'bg-green-50 border-2 border-green-200' : 'bg-orange-50 border-2 border-orange-200'
          }`}>
            <p className={`font-medium ${isCorrect ? 'text-green-800' : 'text-orange-800'}`}>
              {isCorrect 
                ? question.encouragementMessages.correct
                : question.encouragementMessages.incorrect}
            </p>
          </div>
        )}

        {/* Follow-up Question */}
        {showFollowUp && question.followUpQuestions.length > 0 && (
          <div className="mt-4 p-4 bg-blue-50 border-2 border-blue-200 rounded-lg">
            <div className="flex items-start gap-2">
              <span className="text-2xl">🎯</span>
              <div>
                <p className="font-medium text-blue-800">Think about this:</p>
                <p className="text-gray-700">
                  {question.followUpQuestions[0]}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Fun Fact */}
        {isCorrect && question.funFact && (
          <div className="mt-4 p-4 bg-purple-50 border-2 border-purple-200 rounded-lg">
            <div className="flex items-start gap-2">
              <span className="text-2xl">⭐</span>
              <div>
                <p className="font-medium text-purple-800">Fun Fact:</p>
                <p className="text-gray-700">{question.funFact}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Encouragement Footer */}
      {attempts > 0 && !isCorrect && (
        <div className="text-center">
          <p className="text-gray-600 font-medium">
            {attempts === 1 
              ? "Keep thinking! You're doing great! 🌟"
              : "Learning is fun! Every question makes you smarter! 🧠"}
          </p>
        </div>
      )}
    </div>
  )
}