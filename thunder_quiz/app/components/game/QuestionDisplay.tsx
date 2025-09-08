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
    if (timeLeft > 30) return 'text-green-600';
    if (timeLeft > 15) return 'text-yellow-600';
    return 'text-red-600 animate-pulse';
  };

  const questionNumber = state.currentQuestion + 1;
  const isOvertime = state.isOvertime;

  return (
    <div className="max-w-3xl mx-auto">
      {/* Period and Question Header */}
      <div className="bg-white rounded-3xl shadow-xl mb-10 p-10">
        <div className="flex justify-between items-center">
          <div className="text-xl font-bold text-gray-900">
            {isOvertime ? (
              <span className="text-thunder-red animate-pulse text-2xl">🚨 OVERTIME 🚨</span>
            ) : (
              <div className="flex items-center gap-3">
                <span className="text-gray-700 font-semibold">Period {state.currentPeriod}</span>
                <span className="text-gray-400">•</span>
                <span className="text-gray-700 font-semibold">Question {(questionNumber - 1) % 5 + 1}/5</span>
              </div>
            )}
          </div>
          <div className={`flex items-center gap-3 px-6 py-3 rounded-2xl bg-gray-100 ${getTimeColor()}`}>
            <span className="text-3xl">⏱️</span>
            <span className="text-3xl font-bold">{timeLeft}s</span>
          </div>
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-3xl shadow-xl overflow-hidden">
        <div className="bg-gradient-to-r from-blue-50 to-red-50 px-10 py-6 border-b-4 border-blue-200">
          <span className={`inline-flex items-center gap-2 px-8 py-4 text-white text-base font-black rounded-full tracking-wide shadow-lg transform hover:scale-105 transition-transform ${
            question.category === 'rules-penalties' ? 'bg-gradient-to-r from-red-500 to-red-600' :
            question.category === 'team-systems' ? 'bg-gradient-to-r from-blue-500 to-blue-600' :
            question.category === 'nhl-knowledge' ? 'bg-gradient-to-r from-purple-500 to-purple-600' :
            question.category === 'equipment-safety' ? 'bg-gradient-to-r from-green-500 to-green-600' :
            question.category === 'sportsmanship' ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
            question.category === 'team-tactics' ? 'bg-gradient-to-r from-orange-500 to-orange-600' :
            question.category === 'skills-fundamentals' ? 'bg-gradient-to-r from-pink-500 to-pink-600' :
            question.category === 'practice-drills' ? 'bg-gradient-to-r from-teal-500 to-teal-600' :
            question.category === 'fun-facts' ? 'bg-gradient-to-r from-indigo-500 to-indigo-600' :
            'bg-gradient-to-r from-gray-500 to-gray-600'
          }`}>
            <span className="text-2xl">
              {question.category === 'rules-penalties' ? '⚖️' :
               question.category === 'team-systems' ? '📋' :
               question.category === 'nhl-knowledge' ? '🏆' :
               question.category === 'equipment-safety' ? '🛡️' :
               question.category === 'sportsmanship' ? '🤝' :
               question.category === 'team-tactics' ? '♟️' :
               question.category === 'skills-fundamentals' ? '⭐' :
               question.category === 'practice-drills' ? '🎯' :
               question.category === 'fun-facts' ? '💡' : '🏒'}
            </span>
            <span>{question.category.replace('-', ' ').toUpperCase()}</span>
          </span>
        </div>
        <div className="p-14 space-y-10">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 leading-relaxed">
            {question.question}
          </h2>

        {/* Answer Options */}
        <div className="space-y-6">
          {question.type === 'multiple-choice' && question.options && (
            <>
              {question.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedAnswer(option)}
                  className={`w-full p-6 text-left rounded-2xl border-2 font-medium transition-all text-lg ${
                    selectedAnswer === option
                      ? 'border-thunder-red bg-red-50 shadow-lg'
                      : 'border-gray-200 hover:border-thunder-red hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <span className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-base font-bold">
                      {String.fromCharCode(65 + index)}
                    </span>
                    <span>{option}</span>
                  </div>
                </button>
              ))}
            </>
          )}

          {question.type === 'true-false' && (
            <div className="flex gap-6">
              <button
                onClick={() => setSelectedAnswer(true)}
                className={`flex-1 p-8 rounded-3xl border-4 font-black text-2xl transition-all transform hover:scale-105 ${
                  selectedAnswer === true
                    ? 'border-green-500 bg-gradient-to-r from-green-400 to-green-500 text-white shadow-2xl animate-pulse-glow scale-105'
                    : 'border-green-300 bg-gradient-to-r from-green-50 to-white hover:border-green-400 hover:from-green-100'
                }`}
              >
                <div className="flex flex-col items-center gap-2">
                  <span className="text-5xl">✅</span>
                  <span className="tracking-wide">TRUE</span>
                </div>
              </button>
              <button
                onClick={() => setSelectedAnswer(false)}
                className={`flex-1 p-8 rounded-3xl border-4 font-black text-2xl transition-all transform hover:scale-105 ${
                  selectedAnswer === false
                    ? 'border-red-500 bg-gradient-to-r from-red-400 to-red-500 text-white shadow-2xl animate-pulse-glow scale-105'
                    : 'border-red-300 bg-gradient-to-r from-red-50 to-white hover:border-red-400 hover:from-red-100'
                }`}
              >
                <div className="flex flex-col items-center gap-2">
                  <span className="text-5xl">❌</span>
                  <span className="tracking-wide">FALSE</span>
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
                className="w-full px-8 py-6 text-lg border-2 border-gray-300 rounded-2xl focus:outline-none focus:border-thunder-red focus:ring-4 focus:ring-red-100 bg-gray-50 transition-all"
                placeholder="Type your answer here..."
                autoFocus
              />
            </div>
          )}
        </div>

        {/* Hint Section */}
        {showHint && (
          <div className="mt-8 px-8 py-7 bg-yellow-50 border-2 border-yellow-300 rounded-2xl">
            <p className="text-base text-yellow-800">
              <span className="font-bold text-lg">💡 Hint:</span> {hintMessage}
            </p>
            <p className="text-sm text-yellow-700 mt-3 font-medium">
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
          className={`mt-12 w-full py-7 px-10 font-bold text-xl rounded-2xl transition-colors duration-200 shadow-lg ${
            ((question.type !== 'short-answer' && selectedAnswer !== null) ||
            (question.type === 'short-answer' && shortAnswer.trim() !== ''))
              ? 'bg-gradient-to-r from-thunder-red to-red-700 hover:from-red-700 hover:to-red-800 text-white hover:shadow-xl'
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