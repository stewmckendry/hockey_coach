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
    if (timeLeft > 30) return 'text-green-600';
    if (timeLeft > 15) return 'text-yellow-600';
    return 'text-red-600 animate-pulse';
  };

  const questionNumber = state.currentQuestion + 1;
  const isOvertime = state.isOvertime;

  return (
    <div className="max-w-3xl mx-auto p-4">
      {/* Period and Question Header */}
      <div className="bg-white rounded-xl shadow-md p-4 mb-4">
        <div className="flex justify-between items-center">
          <div className="text-lg font-bold text-thunder-black">
            {isOvertime ? (
              <span className="text-thunder-red animate-pulse">🚨 OVERTIME 🚨</span>
            ) : (
              <div className="flex items-center gap-2">
                <span className="text-gray-600">Period {state.currentPeriod}</span>
                <span className="text-gray-400">•</span>
                <span className="text-gray-600">Question {(questionNumber - 1) % 5 + 1}/5</span>
              </div>
            )}
          </div>
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 ${getTimeColor()}`}>
            <span className="text-2xl">⏱️</span>
            <span className="text-2xl font-bold">{timeLeft}s</span>
          </div>
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
          <span className="inline-block px-4 py-1 bg-thunder-red text-white text-xs font-bold rounded-full">
            {question.category.replace('-', ' ').toUpperCase()}
          </span>
        </div>
        <div className="p-6">
          <h2 className="text-2xl font-bold text-thunder-black mb-6">
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
                  className={`w-full p-4 text-left rounded-xl border-2 font-medium transition-all ${
                    selectedAnswer === option
                      ? 'border-thunder-red bg-red-50 shadow-md transform scale-[1.02]'
                      : 'border-gray-300 hover:border-thunder-red hover:bg-gray-50 hover:shadow-sm'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-sm font-bold">
                      {String.fromCharCode(65 + index)}
                    </span>
                    <span>{option}</span>
                  </div>
                </button>
              ))}
            </>
          )}

          {question.type === 'true-false' && (
            <div className="flex gap-4">
              <button
                onClick={() => setSelectedAnswer(true)}
                className={`flex-1 p-5 rounded-xl border-2 font-bold text-lg transition-all ${
                  selectedAnswer === true
                    ? 'border-green-600 bg-green-50 text-green-700 shadow-md transform scale-[1.02]'
                    : 'border-gray-300 hover:border-green-600 hover:bg-green-50'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <span className="text-2xl">✓</span>
                  <span>TRUE</span>
                </div>
              </button>
              <button
                onClick={() => setSelectedAnswer(false)}
                className={`flex-1 p-5 rounded-xl border-2 font-bold text-lg transition-all ${
                  selectedAnswer === false
                    ? 'border-red-600 bg-red-50 text-red-700 shadow-md transform scale-[1.02]'
                    : 'border-gray-300 hover:border-red-600 hover:bg-red-50'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <span className="text-2xl">✗</span>
                  <span>FALSE</span>
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
                className="w-full p-3 border-2 border-thunder-grey rounded-lg focus:outline-none focus:border-thunder-red"
                placeholder="Type your answer here..."
                autoFocus
              />
            </div>
          )}
        </div>

        {/* Hint Section */}
        {showHint && (
          <div className="mt-4 p-4 bg-yellow-50 border-2 border-yellow-300 rounded-lg">
            <p className="text-sm text-yellow-800">
              <span className="font-semibold">💡 Hint:</span> {hintMessage}
            </p>
            <p className="text-xs text-yellow-700 mt-2">
              Try again for half points!
            </p>
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={
            (question.type !== 'short-answer' && selectedAnswer === null) ||
            (question.type === 'short-answer' && shortAnswer.trim() === '')
          }
          className={`mt-8 w-full py-4 px-6 font-bold text-lg rounded-xl transition-all shadow-lg ${
            ((question.type !== 'short-answer' && selectedAnswer !== null) ||
            (question.type === 'short-answer' && shortAnswer.trim() !== ''))
              ? 'bg-gradient-to-r from-thunder-red to-red-700 hover:from-red-700 hover:to-red-800 text-white transform hover:scale-[1.02] active:scale-[0.98]'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {attemptedOnce ? 'Try Again 🏒' : 'Submit Answer 🏒'}
        </button>
        </div>
      </div>
    </div>
  );
}