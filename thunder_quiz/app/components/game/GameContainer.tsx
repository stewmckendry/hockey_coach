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
      // Get recently used questions from session storage
      const recentlyUsedJSON = sessionStorage.getItem('recentlyUsedQuestions');
      const recentlyUsed = recentlyUsedJSON ? JSON.parse(recentlyUsedJSON) : [];
      
      const response = await fetch('/api/questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          count: 15,
          recentlyUsedIds: recentlyUsed.slice(0, 60) // Keep last 60 questions in memory
        }),
      });
      const data = await response.json();
      
      // Update recently used questions in session storage
      const newQuestions = data.questions;
      const updatedRecentlyUsed = [
        ...newQuestions.map((q: Question) => q.id),
        ...recentlyUsed
      ].slice(0, 75); // Keep max 75 questions (5 games worth)
      
      sessionStorage.setItem('recentlyUsedQuestions', JSON.stringify(updatedRecentlyUsed));
      
      dispatch({ type: 'START_GAME', payload: newQuestions });
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
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-6">
        <div className="max-w-md mx-auto space-y-4">
          {/* Final Score - matching other cards width */}
          <div className="modern-card">
            <div className="text-center">
              <h1 className="text-2xl font-black text-gray-900 mb-4">Game Over!</h1>
              <div className="text-3xl font-bold text-gray-900 mb-3">
                {state.playerGoals} - {state.opponentGoals}
              </div>
              <div className="text-lg text-gray-600 font-semibold mb-2">
                {state.playerGoals > state.opponentGoals ? '🏆 You Win!' : 
                 state.playerGoals < state.opponentGoals ? '💪 Better luck next time!' : 
                 '🤝 It\'s a tie!'}
              </div>
              {state.nickname && (
                <div className="text-sm text-gray-500 font-medium">
                  Playing as: <span className="font-bold text-thunder-red">{state.nickname}</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Leaderboard component */}
          <Leaderboard key={Date.now()} currentPlayer={state.nickname} />
          
          {/* Play Again button */}
          <button
            onClick={playAgain}
            className="w-full py-4 bg-gradient-to-r from-thunder-red to-red-600 hover:from-red-600 hover:to-red-700 text-white font-bold rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            Play Again 🏒
          </button>
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
          <div className="w-full max-w-md mx-auto px-4">
            <div className={`modern-card-sm text-center ${
              feedback.correct 
                ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200' 
                : 'bg-gradient-to-br from-red-50 to-pink-50 border-red-200'
            }`}>
              <p className={`text-lg font-bold ${
                feedback.correct ? 'text-green-700' : 'text-red-700'
              }`}>
                {feedback.message}
              </p>
              {feedback.correct && (
                <div className="mt-3 flex justify-center gap-2">
                  <span className="text-xl">⭐</span>
                  <span className="text-xl">⭐</span>
                  <span className="text-xl">⭐</span>
                </div>
              )}
            </div>
          </div>
        ) : currentQuestion ? (
          <QuestionDisplay
            question={currentQuestion}
            onAnswer={handleAnswer}
            onTimeout={handleTimeout}
          />
        ) : (
          <div className="text-center py-16">
            <div className="inline-block rounded-full h-12 w-12 border-b-4 border-thunder-red"></div>
            <p className="mt-4 text-xl text-gray-600 font-medium">Loading question...</p>
          </div>
        )}
      </div>
    </div>
  );
}