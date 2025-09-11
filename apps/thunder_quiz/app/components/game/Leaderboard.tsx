'use client';

import React, { useEffect, useState } from 'react';
import { LeaderboardEntry } from '@/lib/types';

interface LeaderboardProps {
  currentPlayer?: string;
  onClose?: () => void;
}

export default function Leaderboard({ currentPlayer, onClose }: LeaderboardProps) {
  const [scores, setScores] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchLeaderboard = async () => {
    try {
      // Try Notion API first, fallback to regular leaderboard
      const notionResponse = await fetch('/api/notion-leaderboard');
      if (notionResponse.ok) {
        const data = await notionResponse.json();
        setScores(data.scores || []);
      } else {
        // Fallback to regular leaderboard
        const response = await fetch('/api/leaderboard');
        const data = await response.json();
        setScores(data.scores || []);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      // Try fallback
      try {
        const response = await fetch('/api/leaderboard');
        const data = await response.json();
        setScores(data.scores || []);
      } catch {
        setScores([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (date: string | Date) => {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getMedalEmoji = (rank: number) => {
    switch (rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return '';
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-4">
      <div className="modern-card relative">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-3xl">🏆</span>
            </div>
            <div>
              <h2 className="text-2xl font-black text-gray-900">Top Players</h2>
              <p className="text-sm text-gray-500">Thunder Hockey Quiz Champions</p>
            </div>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="w-10 h-10 rounded-xl bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
              aria-label="Close"
            >
              <span className="text-gray-600 text-lg">✕</span>
            </button>
          )}
        </div>

        {/* Leaderboard Content */}
        {loading ? (
          <div className="text-center py-16">
            <div className="w-16 h-16 bg-gray-100 rounded-2xl mx-auto mb-4 flex items-center justify-center">
              <div className="w-8 h-8 border-3 border-thunder-red border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p className="text-sm text-gray-500">Loading scores...</p>
          </div>
        ) : scores.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-gray-100 rounded-2xl mx-auto mb-4 flex items-center justify-center">
              <span className="text-3xl">📊</span>
            </div>
            <p className="text-gray-600 font-semibold mb-2">No scores yet</p>
            <p className="text-sm text-gray-500">Be the first to play!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {scores.map((entry, index) => {
              const rank = index + 1;
              const isCurrentPlayer = entry.nickname === currentPlayer;
              const goalDiff = entry.playerGoals - entry.opponentGoals;
              
              return (
                <div
                  key={entry.id}
                  className={`p-4 rounded-2xl transition-all ${
                    isCurrentPlayer
                      ? 'bg-gradient-to-r from-thunder-red/10 to-red-50 border-2 border-thunder-red shadow-md'
                      : rank === 1
                      ? 'bg-gradient-to-r from-yellow-50 to-yellow-100 border border-yellow-200'
                      : rank <= 3
                      ? 'bg-gradient-to-r from-gray-50 to-gray-100'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {/* Rank Badge */}
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm ${
                        rank === 1 ? 'bg-yellow-200 text-yellow-700' :
                        rank === 2 ? 'bg-gray-200 text-gray-700' :
                        rank === 3 ? 'bg-orange-200 text-orange-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {getMedalEmoji(rank) || rank}
                      </div>
                      
                      {/* Player Info */}
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-gray-900 text-sm">
                            {entry.nickname}
                          </span>
                          {isCurrentPlayer && (
                            <span className="px-2 py-0.5 bg-thunder-red text-white text-xs font-semibold rounded-full">
                              YOU
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 mt-1">
                          <span className="text-xs text-gray-500">{formatDate(entry.date)}</span>
                          <span className="text-xs text-gray-400">•</span>
                          <span className="text-xs text-gray-500">Accuracy {entry.accuracy}%</span>
                        </div>
                      </div>
                    </div>

                    {/* Score Card */}
                    <div className="text-right">
                      <div className="font-black text-lg text-gray-900">
                        {entry.playerGoals} - {entry.opponentGoals}
                      </div>
                      <div className="text-xs font-semibold mt-1">
                        {goalDiff > 0 ? (
                          <span className="text-green-600">WIN +{goalDiff}</span>
                        ) : goalDiff < 0 ? (
                          <span className="text-red-600">LOSS {goalDiff}</span>
                        ) : (
                          <span className="text-yellow-600">TIE</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Footer Stats */}
        {scores.length > 0 && (
          <div className="mt-8 pt-6 border-t border-gray-100">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs text-gray-500">Games Played</p>
                <p className="font-bold text-gray-900">{scores.length}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Avg Score</p>
                <p className="font-bold text-gray-900">
                  {Math.round(scores.reduce((acc, s) => acc + s.playerGoals, 0) / scores.length)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Top Score</p>
                <p className="font-bold text-thunder-red">
                  {Math.max(...scores.map(s => s.playerGoals))}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}