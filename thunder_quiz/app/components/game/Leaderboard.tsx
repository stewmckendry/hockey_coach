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
      const response = await fetch('/api/leaderboard');
      const data = await response.json();
      setScores(data.scores || []);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      setScores([]);
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
    <div className="w-full max-w-3xl mx-auto p-4">
      <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-thunder-red to-red-700 p-8">
          <div className="flex justify-between items-center">
            <div className="text-center w-full">
              <h2 className="text-3xl font-bold text-white mb-2 flex items-center justify-center gap-3">
                <span className="text-4xl">🏆</span>
                <span>Leaderboard</span>
                <span className="text-4xl">🏆</span>
              </h2>
              <p className="text-white/90 text-lg">Top 10 Thunder Players</p>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="absolute top-4 right-4 text-white/80 hover:text-white transition-colors text-2xl"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Leaderboard Content */}
        <div className="p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-thunder-red"></div>
              <p className="mt-2 text-thunder-grey">Loading scores...</p>
            </div>
          ) : scores.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-thunder-grey">No scores yet. Be the first to play!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {scores.map((entry, index) => {
                const rank = index + 1;
                const isCurrentPlayer = entry.nickname === currentPlayer;
                const goalDiff = entry.playerGoals - entry.opponentGoals;
                
                return (
                  <div
                    key={entry.id}
                    className={`flex items-center justify-between p-4 rounded-xl transition-all ${
                      isCurrentPlayer
                        ? 'bg-gradient-to-r from-red-50 to-red-100 border-2 border-thunder-red shadow-md'
                        : rank <= 3
                        ? 'bg-gradient-to-r from-yellow-50 to-yellow-100 hover:shadow-md'
                        : 'bg-gray-50 hover:bg-gray-100 hover:shadow-sm'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {/* Rank */}
                      <div className="w-8 text-center">
                        {getMedalEmoji(rank) || (
                          <span className="text-thunder-grey font-semibold">
                            {rank}
                          </span>
                        )}
                      </div>
                      
                      {/* Player Info */}
                      <div>
                        <div className="font-semibold text-thunder-black">
                          {entry.nickname}
                          {isCurrentPlayer && (
                            <span className="ml-2 text-xs bg-thunder-red text-white px-2 py-0.5 rounded-full">
                              YOU
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-thunder-grey">
                          {formatDate(entry.date)} • Accuracy: {entry.accuracy}%
                        </div>
                      </div>
                    </div>

                    {/* Score */}
                    <div className="text-right">
                      <div className="font-bold text-thunder-black">
                        {entry.playerGoals} - {entry.opponentGoals}
                      </div>
                      <div className="text-xs text-thunder-grey">
                        {goalDiff > 0 ? (
                          <span className="text-green-600">+{goalDiff} WIN</span>
                        ) : goalDiff < 0 ? (
                          <span className="text-red-600">{goalDiff} LOSS</span>
                        ) : (
                          <span className="text-yellow-600">TIE</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Footer */}
          <div className="mt-6 pt-4 border-t border-thunder-lightGrey text-center">
            <p className="text-xs text-thunder-grey">
              Scores reset every 30 days • Keep practicing!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}