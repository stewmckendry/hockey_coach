'use client';

import React from 'react';
import { useGame } from '@/lib/gameContext';

export default function ScoreDisplay() {
  const { state } = useGame();

  return (
    <div className="w-full max-w-3xl mx-auto mb-12">
      {/* Hockey Rink Visual Score Display */}
      <div className="relative bg-white rounded-3xl shadow-xl p-10 border border-gray-100 overflow-hidden">
        {/* Ice texture effect */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-x-0 top-1/2 h-0.5 bg-red-500 transform -translate-y-1/2"></div>
          <div className="absolute inset-y-0 left-1/2 w-0.5 bg-blue-500 transform -translate-x-1/2"></div>
        </div>
        
        {/* Score Container */}
        <div className="relative z-10 flex items-center justify-between">
          {/* Player Side */}
          <div className="flex-1 text-center">
            <div className="mb-2">
              <span className="text-sm font-semibold text-thunder-grey">YOU</span>
            </div>
            <div className="relative">
              <div className="text-5xl font-bold text-thunder-black">
                {state.playerGoals % 1 !== 0 ? (
                  <span>{Math.floor(state.playerGoals)}<sup className="text-2xl text-thunder-red">½</sup></span>
                ) : (
                  state.playerGoals
                )}
              </div>
            </div>
            <div className="mt-2">
              <span className="text-xs text-thunder-grey">{state.nickname}</span>
            </div>
          </div>

          {/* VS Divider */}
          <div className="px-4">
            <div className="w-16 h-16 rounded-full bg-thunder-red flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">VS</span>
            </div>
          </div>

          {/* Opponent Side */}
          <div className="flex-1 text-center">
            <div className="mb-2">
              <span className="text-sm font-semibold text-thunder-grey">OPPONENT</span>
            </div>
            <div className="text-5xl font-bold text-thunder-black">
              {state.opponentGoals}
            </div>
            <div className="mt-2">
              <span className="text-xs text-thunder-grey">Quiz Master</span>
            </div>
          </div>
        </div>

        {/* Period/Overtime Indicator */}
        <div className="mt-4 text-center">
          {state.isOvertime ? (
            <span className="inline-block px-4 py-1 bg-thunder-red text-white font-bold rounded-full">
              OVERTIME
            </span>
          ) : (
            <div className="flex justify-center gap-2">
              {[1, 2, 3].map((period) => (
                <div
                  key={period}
                  className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    period === state.currentPeriod
                      ? 'bg-thunder-red text-white'
                      : period < state.currentPeriod
                      ? 'bg-thunder-black text-white'
                      : 'bg-thunder-lightGrey text-thunder-grey'
                  }`}
                >
                  P{period}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Goal Celebration Animation Placeholder */}
        {state.answers.length > 0 && state.answers[state.answers.length - 1]?.isCorrect && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <span className="text-6xl">🚨</span>
            </div>
          </div>
        )}
      </div>

      {/* Stats Bar */}
      <div className="mt-4 flex justify-center gap-6 text-sm">
        <div className="text-thunder-grey">
          <span className="font-semibold">Questions:</span> {state.answers.length}/15
        </div>
        <div className="text-thunder-grey">
          <span className="font-semibold">Accuracy:</span>{' '}
          {state.answers.length > 0
            ? Math.round((state.answers.filter(a => a.isCorrect).length / state.answers.length) * 100)
            : 0}%
        </div>
      </div>
    </div>
  );
}