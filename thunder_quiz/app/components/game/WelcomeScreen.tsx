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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-thunder-white to-thunder-lightGrey p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Thunder Logo */}
          <div className="text-center mb-8">
            <div className="w-32 h-32 mx-auto mb-4 relative">
              <div className="absolute inset-0 thunder-gradient rounded-full flex items-center justify-center">
                <span className="text-4xl font-bold text-white">⚡</span>
              </div>
            </div>
            <h1 className="text-3xl font-bold thunder-text-gradient mb-2">
              Thunder Hockey Quiz
            </h1>
            <p className="text-thunder-grey">
              Test your hockey knowledge!
            </p>
          </div>

          {/* Game Format Info */}
          <div className="bg-thunder-lightGrey rounded-lg p-4 mb-6">
            <h2 className="font-semibold text-thunder-black mb-2">How to Play:</h2>
            <ul className="text-sm text-thunder-grey space-y-1">
              <li>🏒 3 periods, 5 questions each</li>
              <li>🚨 Score goals with correct answers</li>
              <li>💡 Get hints if you need help</li>
              <li>⏱️ 30 seconds per question</li>
              <li>🏆 Compete for the top leaderboard spot!</li>
            </ul>
          </div>

          {/* Nickname Form */}
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="nickname" className="block text-sm font-medium text-thunder-black mb-2">
                Enter Your Nickname
              </label>
              <input
                type="text"
                id="nickname"
                value={nickname}
                onChange={(e) => {
                  setNickname(e.target.value);
                  setError('');
                }}
                className="w-full px-4 py-2 border-2 border-thunder-grey rounded-lg focus:outline-none focus:border-thunder-red transition-colors"
                placeholder="ThunderBolt99"
                maxLength={15}
                autoFocus
              />
              {error && (
                <p className="mt-1 text-sm text-red-600">{error}</p>
              )}
              <p className="mt-1 text-xs text-thunder-grey">
                3-15 characters, letters and numbers only
              </p>
            </div>

            <button
              type="submit"
              className="w-full py-3 px-4 bg-thunder-red hover:bg-red-700 text-white font-bold rounded-lg transition-colors transform hover:scale-105 active:scale-95"
            >
              Start Game 🏒
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center text-xs text-thunder-grey">
            <p>U10A Ted Reeve Thunder</p>
            <p className="mt-1">Have fun, work hard, be respectful!</p>
          </div>
        </div>
      </div>
    </div>
  );
}