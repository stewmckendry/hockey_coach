import { LeaderboardEntry } from './types';
import fs from 'fs';
import path from 'path';

const STORAGE_FILE = path.join(process.cwd(), '.leaderboard.json');

export class LocalLeaderboardStorage {
  private static instance: LocalLeaderboardStorage;
  private leaderboard: LeaderboardEntry[] = [];

  private constructor() {
    this.load();
  }

  static getInstance(): LocalLeaderboardStorage {
    if (!LocalLeaderboardStorage.instance) {
      LocalLeaderboardStorage.instance = new LocalLeaderboardStorage();
    }
    return LocalLeaderboardStorage.instance;
  }

  private load(): void {
    try {
      if (fs.existsSync(STORAGE_FILE)) {
        const data = fs.readFileSync(STORAGE_FILE, 'utf-8');
        this.leaderboard = JSON.parse(data);
      }
    } catch (error) {
      console.error('Error loading leaderboard from file:', error);
      this.leaderboard = [];
    }
  }

  private save(): void {
    try {
      fs.writeFileSync(STORAGE_FILE, JSON.stringify(this.leaderboard, null, 2));
    } catch (error) {
      console.error('Error saving leaderboard to file:', error);
    }
  }

  addEntry(entry: LeaderboardEntry): void {
    this.leaderboard.push(entry);
    this.sortAndTrim();
    this.save();
  }

  getTopScores(limit: number = 10): LeaderboardEntry[] {
    return this.leaderboard.slice(0, limit);
  }

  private sortAndTrim(): void {
    this.leaderboard.sort((a, b) => {
      const diffA = a.playerGoals - a.opponentGoals;
      const diffB = b.playerGoals - b.opponentGoals;
      if (diffB !== diffA) return diffB - diffA;
      if (b.playerGoals !== a.playerGoals) return b.playerGoals - a.playerGoals;
      return b.accuracy - a.accuracy;
    });

    // Keep only top 100
    if (this.leaderboard.length > 100) {
      this.leaderboard = this.leaderboard.slice(0, 100);
    }
  }

  getRank(entry: LeaderboardEntry): number {
    return this.leaderboard.findIndex(s => 
      s.id === entry.id
    ) + 1;
  }
}