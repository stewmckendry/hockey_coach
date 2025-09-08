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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-red-50 p-12 relative overflow-hidden">
      {/* Ice rink pattern background (will be added as image) */}
      <div className="absolute inset-0 opacity-5 bg-repeat" style={{ backgroundImage: 'url(/ice-pattern.png)', backgroundSize: '400px' }}></div>
      
      <div className="max-w-xl w-full relative z-10">
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden border-2 border-gray-100 transform hover:scale-[1.02] transition-transform duration-300">
          {/* Header with Thunder Logo - More vibrant */}
          <div className="bg-gradient-to-b from-white to-gray-50 text-center py-12 px-8 relative">
            {/* Animated logo container */}
            <div className="w-32 h-32 mx-auto mb-8 relative animate-bounce-slow">
              <Image
                src="/thunder-logo.png"
                alt="Thunder Logo"
                width={128}
                height={128}
                className="object-contain drop-shadow-lg"
                priority
              />
              {/* Mascot overlay */}
              <Image 
                src="/mascot.png" 
                alt="Thunder Mascot"
                width={80}
                height={80}
                className="absolute -right-10 -bottom-6 animate-bounce-slow delay-200" 
              />
            </div>
            <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-thunder-red to-red-800 mb-4 animate-fade-in">
              Thunder Hockey Quiz
            </h1>
            <p className="text-xl text-gray-700 font-bold animate-slide-up">
              ⚡ Test your hockey knowledge! ⚡
            </p>
          </div>

          <div className="px-16 py-12 space-y-12">
            {/* Game Format Info - More playful */}
            <div className="bg-gradient-to-r from-blue-50 to-red-50 rounded-2xl p-8 border-2 border-blue-200">
              <h2 className="text-2xl font-black text-center mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-red-600">
                🎮 How to Play 🎮
              </h2>
              <div className="grid grid-cols-2 gap-6 text-base">
                <div className="flex items-center gap-3 transform hover:scale-110 transition-transform">
                  <span className="text-3xl animate-pulse">🏒</span>
                  <span className="text-gray-800 font-bold">15 questions total</span>
                </div>
                <div className="flex items-center gap-3 transform hover:scale-110 transition-transform">
                  <span className="text-3xl animate-pulse delay-100">⏱️</span>
                  <span className="text-gray-800 font-bold">60 seconds each</span>
                </div>
                <div className="flex items-center gap-3 transform hover:scale-110 transition-transform">
                  <span className="text-3xl animate-pulse delay-200">🚨</span>
                  <span className="text-gray-800 font-bold">Score goals!</span>
                </div>
                <div className="flex items-center gap-3 transform hover:scale-110 transition-transform">
                  <span className="text-3xl animate-pulse delay-300">🏆</span>
                  <span className="text-gray-800 font-bold">Beat the leaderboard</span>
                </div>
              </div>
            </div>

            {/* Top Scores Preview */}
            {topScores.length > 0 && (
              <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-2xl p-8 border-2 border-yellow-300">
                <h2 className="text-xl font-black text-center mb-6 text-transparent bg-clip-text bg-gradient-to-r from-yellow-600 to-orange-600">
                  🏆 Top Thunder Players 🏆
                </h2>
                <div className="space-y-3">
                  {topScores.map((player, index) => (
                    <div key={index} className="flex items-center justify-between px-4 py-3 bg-white rounded-xl border-2 border-yellow-200">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl font-black text-yellow-600">
                          {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                        </span>
                        <span className="font-bold text-gray-800">{player.nickname}</span>
                      </div>
                      <span className="font-black text-xl text-thunder-red">{player.score} pts</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Nickname Form - More playful */}
            <form onSubmit={handleSubmit} className="space-y-8">
              <div className="relative">
                <label htmlFor="nickname" className="block text-xl font-black text-gray-900 mb-4 text-center">
                  ⭐ Choose Your Nickname ⭐
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="nickname"
                    value={nickname}
                    onChange={(e) => {
                      setNickname(e.target.value);
                      setError('');
                    }}
                    className="w-full px-8 py-5 text-2xl font-bold border-4 border-blue-300 rounded-3xl focus:outline-none focus:border-thunder-red focus:ring-4 focus:ring-red-100 transition-all bg-gradient-to-r from-blue-50 to-white placeholder-gray-400"
                    placeholder="ThunderBolt99"
                    maxLength={15}
                    autoFocus
                  />
                  <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-3xl">
                    {nickname.length > 0 && '⚡'}
                  </div>
                </div>
                {error && (
                  <p className="mt-3 text-base text-red-600 font-bold text-center animate-shake">
                    ❌ {error}
                  </p>
                )}
                {!error && nickname.length > 0 && (
                  <p className="mt-3 text-base text-green-600 font-bold text-center animate-fade-in">
                    ✅ Great nickname!
                  </p>
                )}
                {!error && nickname.length === 0 && (
                  <p className="mt-3 text-sm text-gray-500 text-center">
                    3-15 characters, letters and numbers only
                  </p>
                )}
              </div>

              <button
                type="submit"
                className="w-full py-6 px-8 bg-gradient-to-r from-thunder-red to-red-700 hover:from-red-700 hover:to-red-800 text-white text-2xl font-black rounded-3xl transition-all duration-200 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 border-4 border-red-800"
              >
                <span className="flex items-center justify-center gap-3">
                  <span>Start Game</span>
                  <span className="text-3xl animate-bounce-slow">🏒</span>
                </span>
              </button>
            </form>

            {/* Footer - Match the style you like */}
            <div className="mt-10 pt-8 border-t border-gray-200 text-center">
              <p className="text-lg font-semibold text-gray-900">U10A Ted Reeve Thunder</p>
              <p className="text-base text-gray-600 mt-2 font-medium">Have fun, work hard, be a great teammate!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}