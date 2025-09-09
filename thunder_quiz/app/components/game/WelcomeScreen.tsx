'use client';

import React, { useState, useEffect } from 'react';
import { useGame } from '@/lib/gameContext';
import Image from 'next/image';

export default function WelcomeScreen({ onStart }: { onStart: () => void }) {
  const [nickname, setNickname] = useState('');
  const [error, setError] = useState('');
  const [topScores, setTopScores] = useState<Array<{nickname: string, score: number}>>([]);
  const { dispatch } = useGame();

  useEffect(() => {
    // Fetch top scores
    fetch('/api/leaderboard')
      .then(res => res.json())
      .then(data => {
        if (data.entries) {
          setTopScores(data.entries.slice(0, 5));
        }
      })
      .catch(err => console.error('Failed to fetch leaderboard:', err));
  }, []);

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
    <div className="min-h-screen p-4 md:p-6">
      {/* Mobile-first single column layout */}
      <div className="max-w-md mx-auto space-y-4">
        
        {/* Main Game Card */}
        <div className="modern-card">
          {/* Thunder Logo and Title */}
          <div className="text-center mb-6">
            <div className="w-20 h-20 mx-auto mb-4 relative">
              <div className="absolute inset-0 bg-gradient-to-br from-thunder-red/20 to-red-600/20 rounded-2xl blur-xl"></div>
              <Image
                src="/thunder-logo.png"
                alt="Thunder Logo"
                width={80}
                height={80}
                className="relative object-contain drop-shadow-lg"
                priority
              />
            </div>
            <span className="inline-block px-3 py-1 bg-thunder-red/10 text-thunder-red text-xs font-bold rounded-full mb-3">
              HOCKEY QUIZ
            </span>
            <h1 className="text-2xl font-black text-gray-900 mb-1">
              Thunder Challenge
            </h1>
            <p className="text-sm text-gray-500">Test your hockey knowledge</p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-3 mb-6">
            <div className="bg-gray-50 rounded-xl p-3 text-center">
              <p className="text-xl font-bold text-thunder-red">15</p>
              <p className="text-xs text-gray-500">Questions</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-3 text-center">
              <p className="text-xl font-bold text-thunder-red">60s</p>
              <p className="text-xs text-gray-500">Per Question</p>
            </div>
          </div>

          {/* Nickname Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="nickname" className="block text-sm font-semibold text-gray-700 mb-2">
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
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:border-gray-400 focus:bg-white transition-all text-sm font-medium"
                placeholder="ThunderBolt99"
                maxLength={15}
                autoFocus
              />
              {error && (
                <p className="mt-2 text-xs text-red-600 font-medium">{error}</p>
              )}
              {!error && nickname.length > 0 && (
                <p className="mt-2 text-xs text-gray-500">
                  {15 - nickname.length} characters remaining
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={nickname.length === 0}
              className="w-full py-4 bg-gradient-to-r from-thunder-red to-red-600 hover:from-red-600 hover:to-red-700 disabled:from-gray-300 disabled:to-gray-400 text-white font-bold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:shadow-none"
            >
              Start Playing
            </button>
          </form>
        </div>

        {/* Game Format Card */}
        <div className="modern-card-sm">
          <h3 className="font-bold text-gray-900 mb-3">How to Play</h3>
          <div className="space-y-2">
            <div className="flex items-center gap-3 p-2.5 bg-gray-50 rounded-lg">
              <span className="text-lg">⚡</span>
              <span className="text-xs text-gray-700">Answer quickly to earn more points</span>
            </div>
            <div className="flex items-center gap-3 p-2.5 bg-gray-50 rounded-lg">
              <span className="text-lg">💡</span>
              <span className="text-xs text-gray-700">Use hints if stuck (half points)</span>
            </div>
            <div className="flex items-center gap-3 p-2.5 bg-gray-50 rounded-lg">
              <span className="text-lg">🎯</span>
              <span className="text-xs text-gray-700">Build streaks for bonus points</span>
            </div>
          </div>
        </div>

        {/* Leaderboard Preview */}
        {topScores.length > 0 && (
          <div className="modern-card-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-900">Top Players</h3>
              <span className="text-xl">🏆</span>
            </div>
            <div className="space-y-2">
              {topScores.map((player, index) => (
                <div
                  key={index}
                  className={`p-2.5 rounded-lg flex items-center justify-between ${
                    index === 0 
                      ? 'bg-gradient-to-r from-yellow-50 to-yellow-100' 
                      : 'bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold">
                      {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                    </span>
                    <span className="text-sm font-medium text-gray-800">{player.nickname}</span>
                  </div>
                  <span className="text-sm font-bold text-thunder-red">{player.score}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center pt-2">
          <p className="text-xs text-gray-500">
            Ted Reeve Thunder U10A
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Have fun, work hard, be a great teammate!
          </p>
        </div>
      </div>
    </div>
  );
}