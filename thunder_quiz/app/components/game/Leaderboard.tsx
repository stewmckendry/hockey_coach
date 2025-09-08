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
    <div className="w-full max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-xl">
        {/* Header */}
        <div className="bg-thunder-gradient p-6 rounded-t-lg">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-white">🏆 Leaderboard</h2>
              <p className="text-white/80 text-sm mt-1">Top 10 Thunder Players</p>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="text-white/80 hover:text-white transition-colors"
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
                    className={`flex items-center justify-between p-3 rounded-lg transition-all ${
                      isCurrentPlayer
                        ? 'bg-thunder-red/10 border-2 border-thunder-red'
                        : 'bg-thunder-lightGrey hover:bg-gray-100'
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