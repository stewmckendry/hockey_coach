'use client';

import React, { useState, useEffect } from 'react';
import { useGame } from '@/lib/gameContext';
import WelcomeScreen from './WelcomeScreen';
import QuestionDisplay from './QuestionDisplay';
import ScoreDisplay from './ScoreDisplay';
import Leaderboard from './Leaderboard';
import { Question, Answer } from '@/lib/types';

export default function GameContainer() {
  const { state, dispatch } = useGame();
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [feedback, setFeedback] = useState<{
    show: boolean;
    correct: boolean;
    message: string;
  }>({ show: false, correct: false, message: '' });

  useEffect(() => {
    if (state.gameStatus === 'finished' && !showLeaderboard) {
      // Submit score then show leaderboard with a small delay to ensure data is saved
      submitScore().then(() => {
        setTimeout(() => {
          setShowLeaderboard(true);
        }, 500);
      });
    }
  }, [state.gameStatus]);

  const startGame = async () => {
    try {
      const response = await fetch('/api/questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: 15 }),
      });
      const data = await response.json();
      dispatch({ type: 'START_GAME', payload: data.questions });
    } catch (error) {
      console.error('Error starting game:', error);
      alert('Failed to load questions. Please try again.');
    }
  };

  const handleAnswer = async (answer: string | boolean, usedHint: boolean) => {
    if (isValidating) return;
    setIsValidating(true);

    const currentQuestion = state.questions[state.currentQuestion];
    
    try {
      // Validate answer with API
      const response = await fetch('/api/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: currentQuestion.question,
          answer,
          correctAnswer: currentQuestion.correctAnswer,
          isSecondAttempt: usedHint,
        }),
      });
      
      const validation = await response.json();
      
      // Record answer
      const answerRecord: Answer = {
        questionId: currentQuestion.id,
        userAnswer: answer,
        isCorrect: validation.correct,
        usedHint,
        timeSpent: 60 - 0, // TODO: Track actual time spent
      };
      
      dispatch({ type: 'ANSWER_QUESTION', payload: answerRecord });
      
      // Show feedback
      setFeedback({
        show: true,
        correct: validation.correct,
        message: validation.correct 
          ? ['🚨 GOAL!', '🎯 Nice shot!', '⭐ Excellent!', '🏒 Great play!'][Math.floor(Math.random() * 4)]
          : validation.hint || validation.explanation || "Not quite, but keep trying!",
      });
      
      // Auto-advance after feedback
      setTimeout(() => {
        setFeedback({ show: false, correct: false, message: '' });
        dispatch({ type: 'NEXT_QUESTION' });
        setIsValidating(false);
      }, 2500);
      
    } catch (error) {
      console.error('Error validating answer:', error);
      // Fallback validation
      const isCorrect = String(answer).toLowerCase() === String(currentQuestion.correctAnswer).toLowerCase();
      
      const answerRecord: Answer = {
        questionId: currentQuestion.id,
        userAnswer: answer,
        isCorrect,
        usedHint,
        timeSpent: 60,
      };
      
      dispatch({ type: 'ANSWER_QUESTION', payload: answerRecord });
      dispatch({ type: 'NEXT_QUESTION' });
      setIsValidating(false);
    }
  };

  const handleTimeout = () => {
    const currentQuestion = state.questions[state.currentQuestion];
    
    const answerRecord: Answer = {
      questionId: currentQuestion.id,
      userAnswer: '',
      isCorrect: false,
      usedHint: false,
      timeSpent: 30,
    };
    
    dispatch({ type: 'ANSWER_QUESTION', payload: answerRecord });
    
    setFeedback({
      show: true,
      correct: false,
      message: "⏱️ Time's up! The opponent scores!",
    });
    
    setTimeout(() => {
      setFeedback({ show: false, correct: false, message: '' });
      dispatch({ type: 'NEXT_QUESTION' });
    }, 2000);
  };

  const submitScore = async () => {
    if (!state.nickname || state.answers.length === 0) return;
    
    const accuracy = Math.round(
      (state.answers.filter(a => a.isCorrect).length / state.answers.length) * 100
    );
    
    const scoreData = {
      nickname: state.nickname,
      playerGoals: state.playerGoals,
      opponentGoals: state.opponentGoals,
      totalQuestions: state.answers.length,
      accuracy,
    };
    
    try {
      // Try Notion API first
      const notionResponse = await fetch('/api/notion-leaderboard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scoreData),
      });
      
      if (!notionResponse.ok) {
        // Fallback to regular leaderboard
        await fetch('/api/leaderboard', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(scoreData),
        });
      }
    } catch (error) {
      console.error('Error submitting score:', error);
      // Try fallback
      try {
        await fetch('/api/leaderboard', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(scoreData),
        });
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
      }
    }
  };

  const playAgain = () => {
    dispatch({ type: 'RESET_GAME' });
    setShowLeaderboard(false);
  };

    // Render based on game state
  if (state.gameStatus === 'not-started') {
    return <WelcomeScreen onStart={startGame} />;
  }

  if (state.gameStatus === 'finished' || showLeaderboard) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-12">
        <div className="max-w-2xl mx-auto space-y-8">
          {/* Final Score - matching leaderboard width */}
          <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
            <div className="text-center py-10 px-8">
              <h1 className="text-5xl font-bold text-gray-900 mb-6 tracking-tight">Game Over!</h1>
              <div className="text-3xl font-bold text-gray-900 mb-4">
                Final Score: {state.playerGoals} - {state.opponentGoals}
              </div>
              <div className="text-xl text-gray-600 font-medium mb-3">
                {state.playerGoals > state.opponentGoals ? '🏆 You Win!' : 
                 state.playerGoals < state.opponentGoals ? '💪 Better luck next time!' : 
                 '🤝 It\'s a tie!'}
              </div>
              {state.nickname && (
                <div className="text-lg text-gray-500 font-medium">
                  Playing as: <span className="font-bold text-thunder-red">{state.nickname}</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Leaderboard component */}
          <Leaderboard key={Date.now()} currentPlayer={state.nickname} />
          
          {/* Play Again button with better styling */}
          <div className="text-center">
            <button
              onClick={playAgain}
              className="w-full max-w-md mx-auto px-12 py-5 bg-gradient-to-r from-thunder-red to-red-700 hover:from-red-700 hover:to-red-800 text-white text-2xl font-bold rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Play Again 🏒
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = state.questions[state.currentQuestion];
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-16">
      <div className="max-w-4xl mx-auto">
        <ScoreDisplay />
        
        {feedback.show ? (
          <div className={`text-center py-16 animate-fade-in`}>
            <div className={`text-6xl mb-6 ${feedback.correct ? 'animate-goal-celebration' : ''}`}>
              {feedback.correct ? '🚨' : '❌'}
            </div>
            <p className={`text-3xl font-bold ${feedback.correct ? 'text-green-600' : 'text-red-600'}`}>
              {feedback.message}
            </p>
          </div>
        ) : currentQuestion ? (
          <QuestionDisplay
            question={currentQuestion}
            onAnswer={handleAnswer}
            onTimeout={handleTimeout}
          />
        ) : (
          <div className="text-center py-16">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-4 border-thunder-red"></div>
            <p className="mt-4 text-xl text-gray-600 font-medium">Loading question...</p>
          </div>
        )}
      </div>
    </div>
  );
}