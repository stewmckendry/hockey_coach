'use client';

import React, { useState } from 'react';
import { useGame } from '@/lib/gameContext';
import Image from 'next/image';

export default function WelcomeScreen({ onStart }: { onStart: () => void }) {
  const [nickname, setNickname] = useState('');
  const [error, setError] = useState('');
  const { dispatch } = useGame();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate nickname
    const trimmedNickname = nickname.trim();
    if (trimmedNickname.length < 3) {
      setError('Nickname must be at least 3 characters');
      return;
    }
    if (trimmedNickname.length > 15) {
      setError('Nickname must be 15 characters or less');
      return;
    }
    if (!/^[a-zA-Z0-9]+$/.test(trimmedNickname)) {
      setError('Nickname can only contain letters and numbers');
      return;
    }

    dispatch({ type: 'SET_NICKNAME', payload: trimmedNickname });
    onStart();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white p-6">
      <div className="max-w-lg w-full">
        <div className="notion-card">
          {/* Header with Thunder Logo */}
          <div className="bg-gradient-to-r from-thunder-red to-red-700 p-8 text-center">
            <div className="w-40 h-40 mx-auto mb-4 relative">
              <Image
                src="/thunder-logo.png"
                alt="Thunder Logo"
                width={160}
                height={160}
                className="object-contain filter drop-shadow-lg"
                priority
              />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-lg">
              Thunder Hockey Quiz
            </h1>
            <p className="text-white/90 text-lg">
              Test your hockey knowledge!
            </p>
          </div>

          <div className="p-10 space-y-8">
            {/* Game Format Info - Simplified */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-5 mb-8 border border-gray-200">
              <h2 className="font-bold text-thunder-black mb-3 text-lg">How to Play</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-xl">🏒</span>
                  <span className="text-gray-700">15 questions total</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xl">⏱️</span>
                  <span className="text-gray-700">60 seconds each</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xl">🚨</span>
                  <span className="text-gray-700">Score goals!</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xl">🏆</span>
                  <span className="text-gray-700">Beat the leaderboard</span>
                </div>
              </div>
            </div>

            {/* Nickname Form - Cleaner */}
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="nickname" className="block text-base font-bold text-thunder-black mb-3">
                  Choose Your Nickname
                </label>
                <input
                  type="text"
                  id="nickname"
                  value={nickname}
                  onChange={(e) => {
                    setNickname(e.target.value);
                    setError('');
                  }}
                  className="w-full px-5 py-3 text-lg border-2 border-gray-300 rounded-xl focus:outline-none focus:border-thunder-red focus:ring-2 focus:ring-red-200 transition-all"
                  placeholder="ThunderBolt99"
                  maxLength={15}
                  autoFocus
                />
                {error && (
                  <p className="mt-2 text-sm text-red-600 font-medium">{error}</p>
                )}
                {!error && (
                  <p className="mt-2 text-xs text-gray-500">
                    3-15 characters, letters and numbers only
                  </p>
                )}
              </div>

              <button
                type="submit"
                className="w-full py-4 px-6 bg-gradient-to-r from-thunder-red to-red-700 hover:from-red-700 hover:to-red-800 text-white text-lg font-bold rounded-xl transition-all transform hover:scale-[1.02] active:scale-[0.98] shadow-lg"
              >
                Start Game 🏒
              </button>
            </form>

            {/* Footer - Cleaner */}
            <div className="mt-8 pt-6 border-t border-gray-200 text-center">
              <p className="text-sm font-semibold text-gray-700">U10A Ted Reeve Thunder</p>
              <p className="text-xs text-gray-500 mt-1">Have fun, work hard, be respectful!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}