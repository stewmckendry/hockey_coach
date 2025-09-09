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
    <div className="w-full">
      <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
        {/* Header */}
        <div className="bg-white text-center py-10 px-8">
          <div className="flex justify-between items-center">
            <div className="text-center w-full">
              <h2 className="text-4xl font-bold text-gray-900 mb-4 flex items-center justify-center gap-4 tracking-tight">
                <span className="text-5xl">🏆</span>
                <span>Leaderboard</span>
                <span className="text-5xl">🏆</span>
              </h2>
              <p className="text-xl text-gray-600 font-medium">Top 10 Thunder Players</p>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="absolute top-6 right-6 text-gray-600 hover:text-gray-900 transition-colors text-3xl"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Leaderboard Content */}
        <div className="px-10 py-8">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block rounded-full h-12 w-12 border-b-4 border-thunder-red"></div>
              <p className="mt-4 text-xl text-gray-600 font-medium">Loading scores...</p>
            </div>
          ) : scores.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-xl text-gray-600 font-medium">No scores yet. Be the first to play!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {scores.map((entry, index) => {
                const rank = index + 1;
                const isCurrentPlayer = entry.nickname === currentPlayer;
                const goalDiff = entry.playerGoals - entry.opponentGoals;
                
                return (
                  <div
                    key={entry.id}
                    className={`flex items-center justify-between p-6 rounded-2xl transition-all ${
                      isCurrentPlayer
                        ? 'bg-gradient-to-r from-red-50 to-red-100 border-2 border-thunder-red shadow-lg'
                        : rank <= 3
                        ? 'bg-gradient-to-r from-yellow-50 to-yellow-100 hover:shadow-lg'
                        : 'bg-gray-50 hover:bg-gray-100 hover:shadow-md'
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      {/* Rank */}
                      <div className="w-10 text-center">
                        {getMedalEmoji(rank) || (
                          <span className="text-gray-600 font-bold text-lg">
                            {rank}
                          </span>
                        )}
                      </div>
                      
                      {/* Player Info */}
                      <div>
                        <div className="font-bold text-gray-900 text-lg">
                          {entry.nickname}
                          {isCurrentPlayer && (
                            <span className="ml-3 text-sm bg-thunder-red text-white px-3 py-1 rounded-full">
                              YOU
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-600 mt-1 font-medium">
                          {formatDate(entry.date)} • Accuracy: {entry.accuracy}%
                        </div>
                      </div>
                    </div>

                    {/* Score */}
                    <div className="text-right">
                      <div className="font-bold text-gray-900 text-lg">
                        {entry.playerGoals} - {entry.opponentGoals}
                      </div>
                      <div className="text-sm text-gray-600 font-medium">
                        {goalDiff > 0 ? (
                          <span className="text-green-600 font-bold">+{goalDiff} WIN</span>
                        ) : goalDiff < 0 ? (
                          <span className="text-red-600 font-bold">{goalDiff} LOSS</span>
                        ) : (
                          <span className="text-yellow-600 font-bold">TIE</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-600 font-medium">
              Scores reset every 30 days • Keep practicing!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}