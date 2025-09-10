'use client';

import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { GameState, Question, Answer } from './types';

interface GameContextType {
  state: GameState;
  dispatch: React.Dispatch<GameAction>;
}

type GameAction =
  | { type: 'SET_NICKNAME'; payload: string }
  | { type: 'START_GAME'; payload: Question[] }
  | { type: 'ANSWER_QUESTION'; payload: Answer }
  | { type: 'NEXT_QUESTION' }
  | { type: 'START_OVERTIME' }
  | { type: 'END_GAME' }
  | { type: 'RESET_GAME' }
  | { type: 'SET_CURRENT_TIME'; payload: number };

const initialState: GameState = {
  nickname: '',
  currentPeriod: 1,
  currentQuestion: 0,
  playerGoals: 0,
  opponentGoals: 0,
  questions: [],
  answers: [],
  isOvertime: false,
  gameStatus: 'not-started',
  correctStreak: 0,
  correctAnswers: 0,
  totalQuestions: 15,
};

function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'SET_NICKNAME':
      return { ...state, nickname: action.payload };

    case 'START_GAME':
      return {
        ...state,
        questions: action.payload,
        gameStatus: 'in-progress',
        startTime: new Date(),
        currentPeriod: 1,
        currentQuestion: 0,
        correctStreak: 0,
        correctAnswers: 0,
        totalQuestions: action.payload.length,
      };

    case 'ANSWER_QUESTION':
      const answer = action.payload;
      const updatedAnswers = [...state.answers, answer];
      const playerGoals = answer.isCorrect 
        ? state.playerGoals + (answer.usedHint ? 0.5 : 1)
        : state.playerGoals;
      const opponentGoals = !answer.isCorrect ? state.opponentGoals + 1 : state.opponentGoals;
      const correctStreak = answer.isCorrect ? state.correctStreak + 1 : 0;
      const correctAnswers = answer.isCorrect ? state.correctAnswers + 1 : state.correctAnswers;

      return {
        ...state,
        answers: updatedAnswers,
        playerGoals,
        opponentGoals,
        correctStreak,
        correctAnswers,
      };

    case 'NEXT_QUESTION':
      const nextQuestion = state.currentQuestion + 1;
      const questionsPerPeriod = 5;
      const nextPeriod = Math.floor(nextQuestion / questionsPerPeriod) + 1;

      // Check if game should end
      if (nextQuestion >= 15 && !state.isOvertime) {
        // Check for tie at end of regulation
        if (state.playerGoals === state.opponentGoals) {
          return { ...state, isOvertime: true, currentQuestion: nextQuestion };
        }
        return { ...state, gameStatus: 'finished', endTime: new Date() };
      }

      // Check if overtime should end
      if (state.isOvertime && state.playerGoals !== state.opponentGoals) {
        return { ...state, gameStatus: 'finished', endTime: new Date() };
      }

      return {
        ...state,
        currentQuestion: nextQuestion,
        currentPeriod: nextPeriod > 3 ? 3 : nextPeriod,
      };

    case 'START_OVERTIME':
      return { ...state, isOvertime: true };

    case 'END_GAME':
      return { ...state, gameStatus: 'finished', endTime: new Date() };

    case 'RESET_GAME':
      return initialState;

    default:
      return state;
  }
}

const GameContext = createContext<GameContextType | undefined>(undefined);

export function GameProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(gameReducer, initialState);

  return (
    <GameContext.Provider value={{ state, dispatch }}>
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
}