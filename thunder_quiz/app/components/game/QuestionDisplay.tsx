'use client';

import React, { useState, useEffect } from 'react';
import { Question } from '@/lib/types';
import { useGame } from '@/lib/gameContext';

interface QuestionDisplayProps {
  question: Question;
  onAnswer: (answer: string | boolean, usedHint: boolean) => void;
  onTimeout: () => void;
}

export default function QuestionDisplay({ question, onAnswer, onTimeout }: QuestionDisplayProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<string | boolean | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [timeLeft, setTimeLeft] = useState(60);
  const [shortAnswer, setShortAnswer] = useState('');
  const [attemptedOnce, setAttemptedOnce] = useState(false);
  const [hintMessage, setHintMessage] = useState('');
  const { state } = useGame();

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onTimeout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [onTimeout]);

  const handleSubmit = async () => {
    if (!attemptedOnce && !showHint) {
      // First attempt - validate and show hint if wrong
      const answer = question.type === 'short-answer' ? shortAnswer : selectedAnswer;
      if (answer === null && question.type !== 'short-answer') return;
      
      // Check if answer is correct
      const response = await fetch('/api/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.question,
          answer,
          correctAnswer: question.correctAnswer,
          questionType: question.type,
          isSecondAttempt: false,
        }),
      });
      
      const validation = await response.json();
      
      if (validation.correct) {
        // Correct on first try - submit answer
        onAnswer(answer as string | boolean, false);
      } else {
        // Wrong - show hint and allow second attempt
        setAttemptedOnce(true);
        setShowHint(true);
        setHintMessage(validation.hint || question.hint || 'Think about it more carefully!');
        // Reset answer for second attempt
        setSelectedAnswer(null);
        setShortAnswer('');
      }
    } else {
      // Second attempt after hint
      if (question.type === 'short-answer') {
        onAnswer(shortAnswer, true);
      } else if (selectedAnswer !== null) {
        onAnswer(selectedAnswer, true);
      }
    }
  };

  const getTimeColor = () => {
    if (timeLeft > 30) return 'text-green-600 bg-green-50';
    if (timeLeft > 15) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const questionNumber = state.currentQuestion + 1;
  const isOvertime = state.isOvertime;

  const categoryConfig = {
    'rules-penalties': { color: 'from-red-500 to-red-600', icon: '⚖️', bg: 'bg-red-50' },
    'team-systems': { color: 'from-blue-500 to-blue-600', icon: '📋', bg: 'bg-blue-50' },
    'nhl-knowledge': { color: 'from-purple-500 to-purple-600', icon: '🏆', bg: 'bg-purple-50' },
    'equipment-safety': { color: 'from-green-500 to-green-600', icon: '🛡️', bg: 'bg-green-50' },
    'sportsmanship': { color: 'from-yellow-500 to-yellow-600', icon: '🤝', bg: 'bg-yellow-50' },
    'team-tactics': { color: 'from-orange-500 to-orange-600', icon: '♟️', bg: 'bg-orange-50' },
    'skills-fundamentals': { color: 'from-pink-500 to-pink-600', icon: '⭐', bg: 'bg-pink-50' },
    'practice-drills': { color: 'from-teal-500 to-teal-600', icon: '🎯', bg: 'bg-teal-50' },
    'fun-facts': { color: 'from-indigo-500 to-indigo-600', icon: '💡', bg: 'bg-indigo-50' },
  };

  const currentCategory = categoryConfig[question.category as keyof typeof categoryConfig] || 
                          { color: 'from-gray-500 to-gray-600', icon: '🏒', bg: 'bg-gray-50' };

  return (
    <div className="min-h-screen p-4 md:p-6">
      <div className="max-w-md mx-auto">
        {/* Top Header Bar - Mobile optimized */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          {/* Period Info */}
          <div className="modern-card-sm p-3 flex items-center justify-center">
            {isOvertime ? (
              <div className="text-center">
                <span className="text-thunder-red font-bold text-xs">OT</span>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-xs text-gray-500">Period</p>
                <p className="text-lg font-black text-gray-900">{state.currentPeriod}</p>
              </div>
            )}
          </div>

          {/* Question Progress */}
          <div className="modern-card-sm p-3 flex items-center justify-center">
            <div className="text-center">
              <p className="text-xs text-gray-500">Question</p>
              <p className="text-lg font-black text-gray-900">
                {(questionNumber - 1) % 5 + 1}/5
              </p>
            </div>
          </div>

          {/* Timer */}
          <div className={`modern-card-sm p-3 flex items-center justify-center ${getTimeColor()}`}>
            <div className="text-center">
              <p className="text-xs text-gray-600">Time</p>
              <p className="text-xl font-black">{timeLeft}s</p>
            </div>
          </div>
        </div>

        {/* Main Question Card */}
        <div className="modern-card">
          {/* Category Badge */}
          <div className="mb-4">
            <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold ${currentCategory.bg}`}>
              <span className="text-sm">{currentCategory.icon}</span>
              <span className="uppercase tracking-wide">{question.category.replace('-', ' ')}</span>
            </span>
          </div>

          {/* Question Text */}
          <h2 className="text-lg font-bold text-gray-900 mb-6 leading-relaxed">
            {question.question}
          </h2>

          {/* Answer Options */}
          <div className="space-y-3">
            {question.type === 'multiple-choice' && question.options && (
              <>
                {question.options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedAnswer(option)}
                    className={`w-full p-4 text-left rounded-xl border transition-all ${
                      selectedAnswer === option
                        ? 'border-thunder-red bg-red-50 shadow-md'
                        : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
                        selectedAnswer === option 
                          ? 'bg-thunder-red text-white' 
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {String.fromCharCode(65 + index)}
                      </span>
                      <span className="text-sm text-gray-800 font-medium flex-1">{option}</span>
                    </div>
                  </button>
                ))}
              </>
            )}

            {question.type === 'true-false' && (
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setSelectedAnswer(true)}
                  className={`p-5 rounded-xl border-2 transition-all ${
                    selectedAnswer === true
                      ? 'border-green-500 bg-green-50 shadow-md'
                      : 'border-gray-200 bg-white hover:border-green-300 hover:bg-green-50/50'
                  }`}
                >
                  <div className="text-center">
                    <span className="text-2xl mb-1 block">✅</span>
                    <span className="font-bold text-sm text-gray-800">TRUE</span>
                  </div>
                </button>
                <button
                  onClick={() => setSelectedAnswer(false)}
                  className={`p-5 rounded-xl border-2 transition-all ${
                    selectedAnswer === false
                      ? 'border-red-500 bg-red-50 shadow-md'
                      : 'border-gray-200 bg-white hover:border-red-300 hover:bg-red-50/50'
                  }`}
                >
                  <div className="text-center">
                    <span className="text-2xl mb-1 block">❌</span>
                    <span className="font-bold text-sm text-gray-800">FALSE</span>
                  </div>
                </button>
              </div>
            )}

            {question.type === 'short-answer' && (
              <div>
                <input
                  type="text"
                  value={shortAnswer}
                  onChange={(e) => setShortAnswer(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && shortAnswer.trim() !== '') {
                      handleSubmit();
                    }
                  }}
                  className="w-full px-4 py-3 text-base border border-gray-200 rounded-xl focus:outline-none focus:border-gray-400 bg-white transition-all"
                  placeholder="Type your answer here..."
                  autoFocus
                />
              </div>
            )}
          </div>

          {/* Hint Card */}
          {showHint && (
            <div className="mt-4 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl">
              <div className="flex items-start gap-2">
                <span className="text-lg">💡</span>
                <div className="flex-1">
                  <p className="font-semibold text-sm text-gray-900 mb-1">Hint</p>
                  <p className="text-xs text-gray-700">{hintMessage}</p>
                  <p className="text-xs text-gray-500 mt-1">Try again for half points!</p>
                </div>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="mt-6">
            <button
              onClick={handleSubmit}
              disabled={
                (question.type !== 'short-answer' && selectedAnswer === null) ||
                (question.type === 'short-answer' && shortAnswer.trim() === '')
              }
              className={`w-full py-4 px-6 font-bold rounded-xl transition-all shadow-lg ${
                ((question.type !== 'short-answer' && selectedAnswer !== null) ||
                (question.type === 'short-answer' && shortAnswer.trim() !== ''))
                  ? 'bg-gradient-to-r from-thunder-red to-red-600 hover:from-red-600 hover:to-red-700 text-white hover:shadow-xl'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed shadow-none'
              }`}
            >
              {attemptedOnce ? 'Try Again' : 'Submit Answer'}
            </button>
          </div>
        </div>

        {/* Score Preview */}
        <div className="mt-4 flex justify-center gap-3">
          <div className="bg-white rounded-xl px-4 py-2 flex items-center gap-2 shadow-sm">
            <span className="text-xs text-gray-500">Score:</span>
            <span className="font-bold text-thunder-red">{state.score}</span>
          </div>
          <div className="bg-white rounded-xl px-4 py-2 flex items-center gap-2 shadow-sm">
            <span className="text-xs text-gray-500">Streak:</span>
            <span className="font-bold text-thunder-red">{state.correctStreak}</span>
          </div>
        </div>
      </div>
    </div>
  );
}