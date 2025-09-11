'use client';

import React from 'react';
import { useGame } from '@/lib/gameContext';

export default function ScoreDisplay() {
  const { state } = useGame();

  return (
    <div className="w-full max-w-md mx-auto mb-8 px-4">
      {/* Hockey Rink Visual Score Display */}
      <div className="relative bg-white rounded-3xl shadow-xl p-6 border border-gray-100 overflow-hidden">
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
              <div className="text-4xl font-bold text-thunder-black">
                {state.playerGoals % 1 !== 0 ? (
                  <span>{Math.floor(state.playerGoals)}<sup className="text-xl text-thunder-red">½</sup></span>
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
          <div className="px-3">
            <div className="w-12 h-12 rounded-full bg-thunder-red flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-sm">VS</span>
            </div>
          </div>

          {/* Opponent Side */}
          <div className="flex-1 text-center">
            <div className="mb-2">
              <span className="text-sm font-semibold text-thunder-grey">OPPONENT</span>
            </div>
            <div className="text-4xl font-bold text-thunder-black">
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
                  className={`w-2 h-2 rounded-full ${
                    period <= state.currentPeriod
                      ? 'bg-thunder-red'
                      : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}