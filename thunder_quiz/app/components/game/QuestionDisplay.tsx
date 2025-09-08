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
  const [timeLeft, setTimeLeft] = useState(30);
  const [shortAnswer, setShortAnswer] = useState('');
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

  const handleSubmit = () => {
    if (question.type === 'short-answer') {
      onAnswer(shortAnswer, showHint);
    } else if (selectedAnswer !== null) {
      onAnswer(selectedAnswer, showHint);
    }
  };

  const getTimeColor = () => {
    if (timeLeft > 20) return 'text-green-600';
    if (timeLeft > 10) return 'text-yellow-600';
    return 'text-red-600 animate-pulse';
  };

  const questionNumber = state.currentQuestion + 1;
  const isOvertime = state.isOvertime;

  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* Period and Question Header */}
      <div className="flex justify-between items-center mb-6">
        <div className="text-lg font-semibold text-thunder-black">
          {isOvertime ? (
            <span className="text-thunder-red">OVERTIME</span>
          ) : (
            <>Period {state.currentPeriod} - Question {(questionNumber - 1) % 5 + 1}</>
          )}
        </div>
        <div className={`text-2xl font-bold ${getTimeColor()}`}>
          {timeLeft}s
        </div>
      </div>

      {/* Question */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-4">
        <div className="mb-4">
          <span className="inline-block px-3 py-1 bg-thunder-lightGrey text-thunder-grey text-xs font-semibold rounded-full mb-2">
            {question.category.replace('-', ' ').toUpperCase()}
          </span>
          <h2 className="text-xl font-bold text-thunder-black">
            {question.question}
          </h2>
        </div>

        {/* Answer Options */}
        <div className="space-y-3">
          {question.type === 'multiple-choice' && question.options && (
            <>
              {question.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedAnswer(option)}
                  className={`w-full p-3 text-left rounded-lg border-2 transition-all ${
                    selectedAnswer === option
                      ? 'border-thunder-red bg-red-50'
                      : 'border-thunder-grey hover:border-thunder-red hover:bg-thunder-lightGrey'
                  }`}
                >
                  {option}
                </button>
              ))}
            </>
          )}

          {question.type === 'true-false' && (
            <div className="flex gap-4">
              <button
                onClick={() => setSelectedAnswer(true)}
                className={`flex-1 p-4 rounded-lg border-2 font-semibold transition-all ${
                  selectedAnswer === true
                    ? 'border-green-600 bg-green-50 text-green-700'
                    : 'border-thunder-grey hover:border-green-600'
                }`}
              >
                TRUE
              </button>
              <button
                onClick={() => setSelectedAnswer(false)}
                className={`flex-1 p-4 rounded-lg border-2 font-semibold transition-all ${
                  selectedAnswer === false
                    ? 'border-red-600 bg-red-50 text-red-700'
                    : 'border-thunder-grey hover:border-red-600'
                }`}
              >
                FALSE
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
        {!showHint && question.hint && (
          <button
            onClick={() => setShowHint(true)}
            className="mt-4 text-sm text-thunder-red hover:text-red-700 underline"
          >
            Need a hint? (Half points if correct)
          </button>
        )}
        
        {showHint && question.hint && (
          <div className="mt-4 p-3 bg-yellow-50 border-2 border-yellow-300 rounded-lg">
            <p className="text-sm text-yellow-800">
              <span className="font-semibold">💡 Hint:</span> {question.hint}
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
          className={`mt-6 w-full py-3 px-4 font-bold rounded-lg transition-all ${
            ((question.type !== 'short-answer' && selectedAnswer !== null) ||
            (question.type === 'short-answer' && shortAnswer.trim() !== ''))
              ? 'bg-thunder-red hover:bg-red-700 text-white transform hover:scale-105 active:scale-95'
              : 'bg-thunder-grey text-gray-400 cursor-not-allowed'
          }`}
        >
          Submit Answer
        </button>
      </div>
    </div>
  );
}