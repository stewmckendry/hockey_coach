'use client'

import { useState, useEffect } from 'react'
import { ModeSelector } from './ModeSelector'
import { QuizQuestion } from './QuizQuestion'
import { KidFriendlyChat } from './KidFriendlyChat'
import questionsData from '@/data/hockey-iq-questions.json'

export type Mode = 'qa' | 'quiz'
export type Question = typeof questionsData.questions[0] & {
  // Dynamic generation fields
  researchSource?: string
  thunderContext?: string
}
export type Category = keyof typeof questionsData.categories
export type Achievement = keyof typeof questionsData.achievements

interface HockeyIQInterfaceProps {
  embedded?: boolean
  className?: string
}

/**
 * Main Hockey IQ Chatbot interface for U10 players (8-9 years old)
 * Features two modes: Q&A (ask questions) and Quiz (answer questions)
 */
export function HockeyIQInterface({ embedded = false, className = '' }: HockeyIQInterfaceProps) {
  const [mode, setMode] = useState<Mode>('qa')
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [score, setScore] = useState(0)
  const [questionsAnswered, setQuestionsAnswered] = useState(0)
  const [streak, setStreak] = useState(0)
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null)
  const [showCelebration, setShowCelebration] = useState(false)
  const [celebrationMessage, setCelebrationMessage] = useState('')

  // Check for achievements
  useEffect(() => {
    if (score === 1 && !achievements.includes('first_correct')) {
      unlockAchievement('first_correct')
    }
    if (streak === 5 && !achievements.includes('five_in_row')) {
      unlockAchievement('five_in_row')
    }
  }, [score, streak, achievements])

  const unlockAchievement = (achievement: Achievement) => {
    const achievementData = questionsData.achievements[achievement]
    setAchievements([...achievements, achievement])
    setCelebrationMessage(`${achievementData.emoji} ${achievementData.message}`)
    setShowCelebration(true)
    setTimeout(() => setShowCelebration(false), 3000)
  }

  const getRandomQuestion = (category?: Category): Question => {
    const questions = category 
      ? questionsData.questions.filter(q => q.category === category)
      : questionsData.questions
    return questions[Math.floor(Math.random() * questions.length)]
  }

  const handleModeSwitch = (newMode: Mode) => {
    setMode(newMode)
    if (newMode === 'quiz') {
      // Start with a random question when entering quiz mode
      setCurrentQuestion(getRandomQuestion(selectedCategory || undefined))
    }
  }

  const handleQuizAnswer = (correct: boolean) => {
    if (correct) {
      setScore(score + 1)
      setStreak(streak + 1)
      setCelebrationMessage('🌟 Great job! You got it right!')
    } else {
      setStreak(0)
      setCelebrationMessage('💪 Keep trying! You\'re learning!')
    }
    setQuestionsAnswered(questionsAnswered + 1)
    setShowCelebration(true)
    setTimeout(() => {
      setShowCelebration(false)
      // Load next question after celebration
      setCurrentQuestion(getRandomQuestion(selectedCategory || undefined))
    }, 2000)
  }

  const handleCategorySelect = (category: Category) => {
    setSelectedCategory(category)
    // Categories are now only used in quiz mode
    if (mode === 'quiz') {
      setCurrentQuestion(getRandomQuestion(category))
    }
  }

  return (
    <div className={`flex flex-col h-full bg-gradient-to-b from-blue-50 to-white ${className} ${embedded ? 'max-w-full' : 'max-w-4xl mx-auto'}`}>
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🏒</span>
            <div>
              <h1 className="text-xl font-bold">Hockey IQ Coach</h1>
              <p className="text-xs opacity-90">Learn hockey the fun way!</p>
            </div>
          </div>
          {mode === 'quiz' && (
            <div className="text-right">
              <div className="text-lg font-bold">Score: {score} ⭐</div>
              <div className="text-xs">Streak: {streak} 🔥</div>
            </div>
          )}
        </div>
      </div>

      {/* Mode Selector */}
      <div className="p-4 bg-white border-b">
        <ModeSelector 
          currentMode={mode} 
          onModeChange={handleModeSwitch}
        />
      </div>

      {/* Category Selector - Only show in Quiz mode */}
      {mode === 'quiz' && (
        <div className="p-4 bg-gray-50 border-b">
          <div className="flex flex-wrap gap-2 justify-center">
            {Object.entries(questionsData.categories).map(([key, category]) => (
              <button
                key={key}
                onClick={() => handleCategorySelect(key as Category)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all transform hover:scale-105 ${
                  selectedCategory === key
                    ? 'bg-blue-500 text-white shadow-lg'
                    : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-blue-300'
                }`}
              >
                <span className="mr-1">{category.emoji}</span>
                {category.name}
              </button>
            ))}
          </div>
          {selectedCategory && (
            <p className="text-center text-xs text-gray-600 mt-2">
              {questionsData.categories[selectedCategory].description}
            </p>
          )}
        </div>
      )}

      {/* Celebration Message */}
      {showCelebration && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50">
          <div className="bg-yellow-400 text-gray-900 px-8 py-4 rounded-full shadow-2xl animate-bounce">
            <div className="text-2xl font-bold text-center">{celebrationMessage}</div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-4">
        {mode === 'qa' ? (
          <KidFriendlyChat 
            selectedCategory={selectedCategory}
            embedded={embedded}
          />
        ) : (
          currentQuestion && (
            <QuizQuestion
              question={currentQuestion}
              onAnswer={handleQuizAnswer}
              questionsAnswered={questionsAnswered}
            />
          )
        )}
      </div>

      {/* Achievements Bar */}
      {achievements.length > 0 && (
        <div className="p-3 bg-yellow-50 border-t">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Achievements:</span>
            <div className="flex gap-2">
              {achievements.map(achievement => (
                <div
                  key={achievement}
                  className="bg-yellow-200 px-3 py-1 rounded-full text-sm"
                  title={questionsData.achievements[achievement].name}
                >
                  {questionsData.achievements[achievement].emoji} {questionsData.achievements[achievement].name}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="p-3 bg-gray-100 border-t text-center">
        <p className="text-xs text-gray-600">
          Made for U10 hockey players • Keep learning and having fun! 🏒
        </p>
      </div>
    </div>
  )
}