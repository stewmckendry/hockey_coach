'use client'

import { Mode } from './HockeyIQInterface'

interface ModeSelectorProps {
  currentMode: Mode
  onModeChange: (mode: Mode) => void
}

/**
 * Mode selector component for switching between Q&A and Quiz modes
 * Designed with large, kid-friendly buttons for U10 players
 */
export function ModeSelector({ currentMode, onModeChange }: ModeSelectorProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 max-w-2xl mx-auto">
      <button
        onClick={() => onModeChange('qa')}
        className={`flex-1 p-6 rounded-xl transition-all transform hover:scale-105 ${
          currentMode === 'qa'
            ? 'bg-gradient-to-r from-green-400 to-green-500 text-white shadow-xl scale-105'
            : 'bg-white border-3 border-gray-200 text-gray-700 hover:border-green-300'
        }`}
      >
        <div className="flex flex-col items-center gap-2">
          <span className="text-4xl">💬</span>
          <div>
            <div className="text-lg font-bold">Ask Questions</div>
            <div className="text-xs opacity-80">
              I have hockey questions!
            </div>
          </div>
        </div>
      </button>

      <button
        onClick={() => onModeChange('quiz')}
        className={`flex-1 p-6 rounded-xl transition-all transform hover:scale-105 ${
          currentMode === 'quiz'
            ? 'bg-gradient-to-r from-purple-400 to-purple-500 text-white shadow-xl scale-105'
            : 'bg-white border-3 border-gray-200 text-gray-700 hover:border-purple-300'
        }`}
      >
        <div className="flex flex-col items-center gap-2">
          <span className="text-4xl">🎯</span>
          <div>
            <div className="text-lg font-bold">Quiz Me!</div>
            <div className="text-xs opacity-80">
              Test my hockey knowledge!
            </div>
          </div>
        </div>
      </button>
    </div>
  )
}