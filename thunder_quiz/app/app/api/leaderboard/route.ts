import { NextResponse } from 'next/server';
import { kv } from '@vercel/kv';
import { LeaderboardEntry } from '@/lib/types';
import { LocalLeaderboardStorage } from '@/lib/localStorage';

// File-based storage for local development
const localStorage = LocalLeaderboardStorage.getInstance();

export async function GET() {
  try {
    // Try to use Vercel KV if available
    if (process.env.KV_REST_API_URL) {
      const ids = await kv.zrange('leaderboard:scores', 0, 9, {
        rev: true,
        withScores: false,
      }) as string[];
      
      const scores: LeaderboardEntry[] = [];
      for (const id of ids) {
        const entry = await kv.hgetall(`leaderboard:${id}`) as LeaderboardEntry | null;
        if (entry) scores.push(entry);
      }
      
      return NextResponse.json({ scores });
    }
    
    // Fallback to local storage for development
    const topScores = localStorage.getTopScores(10);
    
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
      // Store entry in hash
      await kv.hset(`leaderboard:${newEntry.id}`, newEntry);
      
      // Add to sorted set with score
      await kv.zadd('leaderboard:scores', {
        score,
        member: newEntry.id,
      });
      
      // Keep only top 100 entries
      const count = await kv.zcard('leaderboard:scores');
      if (count > 100) {
        const toRemove = await kv.zpopmin('leaderboard:scores', count - 100) as Array<{member: string, score: number}>;
        // Clean up hash entries
        for (const item of toRemove) {
          await kv.del(`leaderboard:${item.member}`);
        }
      }
      
      // Set 30-day expiry for this entry
      await kv.expire(`leaderboard:${newEntry.id}`, 30 * 24 * 60 * 60);
    } else {
      // Fallback to local storage for development
      localStorage.addEntry(newEntry);
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
      const ids = await kv.zrange('leaderboard:scores', 0, -1, {
        rev: true,
        withScores: false,
      }) as string[];
      
      // Find the entry's position
      return ids.findIndex(id => id === entry.id) + 1;
    }
    
    // Local fallback
    return localStorage.getRank(entry);
  } catch {
    return 0;
  }
}