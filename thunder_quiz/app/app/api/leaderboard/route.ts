import { NextResponse } from 'next/server';
import { kv } from '@vercel/kv';
import { LeaderboardEntry } from '@/lib/types';

// In-memory fallback for local development
let localLeaderboard: LeaderboardEntry[] = [];

export async function GET() {
  try {
    // Try to use Vercel KV if available
    if (process.env.KV_REST_API_URL) {
      const scores = await kv.zrange('leaderboard', 0, 9, {
        rev: true,
        withScores: false,
      }) as LeaderboardEntry[];
      return NextResponse.json({ scores });
    }
    
    // Fallback to local storage for development
    const topScores = localLeaderboard
      .sort((a, b) => {
        // Sort by goal differential (player goals - opponent goals)
        const diffA = a.playerGoals - a.opponentGoals;
        const diffB = b.playerGoals - b.opponentGoals;
        if (diffB !== diffA) return diffB - diffA;
        // Then by player goals
        if (b.playerGoals !== a.playerGoals) return b.playerGoals - a.playerGoals;
        // Then by accuracy
        return b.accuracy - a.accuracy;
      })
      .slice(0, 10);
    
    return NextResponse.json({ scores: topScores });
  } catch (error) {
    console.error('Error fetching leaderboard:', error);
    // Return empty leaderboard on error
    return NextResponse.json({ scores: [] });
  }
}

export async function POST(request: Request) {
  try {
    const entry: LeaderboardEntry = await request.json();
    
    // Add timestamp and ID
    const newEntry: LeaderboardEntry = {
      ...entry,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      date: new Date(),
    };
    
    // Calculate score for ranking (goal differential * 100 + player goals)
    const score = (newEntry.playerGoals - newEntry.opponentGoals) * 100 + newEntry.playerGoals;
    
    // Try to use Vercel KV if available
    if (process.env.KV_REST_API_URL) {
      // Add to sorted set with score
      await kv.zadd('leaderboard', {
        score,
        member: JSON.stringify(newEntry),
      });
      
      // Keep only top 100 entries
      const count = await kv.zcard('leaderboard');
      if (count > 100) {
        await kv.zpopmin('leaderboard', count - 100);
      }
      
      // Set 30-day expiry for the whole leaderboard
      await kv.expire('leaderboard', 30 * 24 * 60 * 60);
    } else {
      // Fallback to local storage for development
      localLeaderboard.push(newEntry);
      // Keep only top 100 in memory
      if (localLeaderboard.length > 100) {
        localLeaderboard = localLeaderboard
          .sort((a, b) => {
            const diffA = a.playerGoals - a.opponentGoals;
            const diffB = b.playerGoals - b.opponentGoals;
            if (diffB !== diffA) return diffB - diffA;
            if (b.playerGoals !== a.playerGoals) return b.playerGoals - a.playerGoals;
            return b.accuracy - a.accuracy;
          })
          .slice(0, 100);
      }
    }
    
    return NextResponse.json({ 
      success: true, 
      entry: newEntry,
      rank: await getPlayerRank(newEntry)
    });
  } catch (error) {
    console.error('Error saving to leaderboard:', error);
    return NextResponse.json(
      { error: 'Failed to save score' },
      { status: 500 }
    );
  }
}

async function getPlayerRank(entry: LeaderboardEntry): Promise<number> {
  try {
    if (process.env.KV_REST_API_URL) {
      const scores = await kv.zrange('leaderboard', 0, -1, {
        rev: true,
        withScores: false,
      }) as LeaderboardEntry[];
      
      return scores.findIndex(s => 
        s.nickname === entry.nickname && 
        s.playerGoals === entry.playerGoals &&
        s.opponentGoals === entry.opponentGoals
      ) + 1;
    }
    
    // Local fallback
    const sorted = localLeaderboard
      .sort((a, b) => {
        const diffA = a.playerGoals - a.opponentGoals;
        const diffB = b.playerGoals - b.opponentGoals;
        if (diffB !== diffA) return diffB - diffA;
        if (b.playerGoals !== a.playerGoals) return b.playerGoals - a.playerGoals;
        return b.accuracy - a.accuracy;
      });
    
    return sorted.findIndex(s => 
      s.nickname === entry.nickname && 
      s.playerGoals === entry.playerGoals &&
      s.opponentGoals === entry.opponentGoals
    ) + 1;
  } catch {
    return 0;
  }
}