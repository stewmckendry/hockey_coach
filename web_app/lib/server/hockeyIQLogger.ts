/**
 * Hockey IQ Chatbot Monitoring Logger
 * Tracks all interactions for analytics and monitoring
 */

import fs from 'fs/promises';
import path from 'path';

export interface HockeyIQLogEntry {
  id: string;
  timestamp: string;
  mode: 'chat' | 'quiz';
  
  // User interaction
  userMessage: string;
  category?: string;
  ageGroup: string;
  
  // AI Response
  aiResponse: string;
  responseId?: string;
  previousResponseId?: string;
  
  // Tool usage
  toolsCalled: string[];
  toolResults?: any;
  
  // Performance metrics
  processingTimeMs: number;
  tokenCount?: number;
  
  // Session info
  sessionId?: string;
  ipAddress?: string;
  
  // Error tracking
  error?: string;
  success: boolean;
}

export interface HockeyIQStats {
  totalInteractions: number;
  chatInteractions: number;
  quizInteractions: number;
  averageResponseTime: number;
  mostCommonCategories: Record<string, number>;
  toolUsageStats: Record<string, number>;
  errorRate: number;
  uniqueSessions: number;
  timeRange: {
    start: string;
    end: string;
  };
}

class HockeyIQLogger {
  private logDir: string;
  private currentLogFile: string;
  private inMemoryCache: HockeyIQLogEntry[] = [];
  private maxCacheSize = 100; // Keep last 100 entries in memory for quick access

  constructor() {
    // Store logs in a dedicated directory
    this.logDir = path.join(process.cwd(), 'logs', 'hockey-iq');
    this.currentLogFile = path.join(this.logDir, `hockey-iq-${this.getDateString()}.json`);
    this.initializeLogger();
  }

  private async initializeLogger() {
    try {
      // Create logs directory if it doesn't exist
      await fs.mkdir(this.logDir, { recursive: true });
      
      // Load today's logs into memory cache if file exists
      try {
        const content = await fs.readFile(this.currentLogFile, 'utf-8');
        const lines = content.trim().split('\n').filter(line => line);
        this.inMemoryCache = lines.slice(-this.maxCacheSize).map(line => JSON.parse(line));
      } catch (error) {
        // File doesn't exist yet, that's fine
        console.log('📝 Starting new Hockey IQ log file for today');
      }
    } catch (error) {
      console.error('Failed to initialize Hockey IQ logger:', error);
    }
  }

  private getDateString(): string {
    return new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  }

  private generateId(): string {
    return `hiq_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Log a chat interaction
   */
  async logChatInteraction(
    userMessage: string,
    aiResponse: string,
    metadata: {
      responseId?: string;
      previousResponseId?: string;
      category?: string;
      toolsCalled?: string[];
      processingTimeMs: number;
      sessionId?: string;
      ipAddress?: string;
      error?: string;
    }
  ): Promise<void> {
    const entry: HockeyIQLogEntry = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      mode: 'chat',
      userMessage,
      aiResponse,
      ageGroup: 'U10',
      responseId: metadata.responseId,
      previousResponseId: metadata.previousResponseId,
      category: metadata.category,
      toolsCalled: metadata.toolsCalled || [],
      processingTimeMs: metadata.processingTimeMs,
      sessionId: metadata.sessionId,
      ipAddress: metadata.ipAddress,
      error: metadata.error,
      success: !metadata.error
    };

    await this.writeLog(entry);
  }

  /**
   * Log a quiz interaction
   */
  async logQuizInteraction(
    action: string,
    data: any,
    metadata: {
      processingTimeMs: number;
      sessionId?: string;
      ipAddress?: string;
      error?: string;
    }
  ): Promise<void> {
    const entry: HockeyIQLogEntry = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      mode: 'quiz',
      userMessage: `Quiz Action: ${action}`,
      aiResponse: JSON.stringify(data),
      ageGroup: 'U10',
      toolsCalled: [],
      processingTimeMs: metadata.processingTimeMs,
      sessionId: metadata.sessionId,
      ipAddress: metadata.ipAddress,
      error: metadata.error,
      success: !metadata.error
    };

    await this.writeLog(entry);
  }

  /**
   * Write log entry to file and update cache
   */
  private async writeLog(entry: HockeyIQLogEntry): Promise<void> {
    try {
      // Check if we need to rotate to a new file (new day)
      const currentDate = this.getDateString();
      if (!this.currentLogFile.includes(currentDate)) {
        this.currentLogFile = path.join(this.logDir, `hockey-iq-${currentDate}.json`);
        this.inMemoryCache = []; // Clear cache for new day
      }

      // Append to file (one JSON object per line for easy streaming)
      await fs.appendFile(this.currentLogFile, JSON.stringify(entry) + '\n');

      // Update in-memory cache
      this.inMemoryCache.push(entry);
      if (this.inMemoryCache.length > this.maxCacheSize) {
        this.inMemoryCache.shift(); // Remove oldest entry
      }

      // Log to console in development
      if (process.env.NODE_ENV === 'development') {
        console.log(`🏒 [Hockey IQ ${entry.mode}] ${entry.userMessage.substring(0, 50)}...`);
        if (entry.toolsCalled.length > 0) {
          console.log(`   🔧 Tools: ${entry.toolsCalled.join(', ')}`);
        }
        console.log(`   ⏱️ Response time: ${entry.processingTimeMs}ms`);
      }
    } catch (error) {
      console.error('Failed to write Hockey IQ log:', error);
    }
  }

  /**
   * Get recent logs from memory cache
   */
  getRecentLogs(limit: number = 50): HockeyIQLogEntry[] {
    return this.inMemoryCache.slice(-limit).reverse();
  }

  /**
   * Get all logs for a specific date
   */
  async getLogsForDate(date: string): Promise<HockeyIQLogEntry[]> {
    try {
      const logFile = path.join(this.logDir, `hockey-iq-${date}.json`);
      const content = await fs.readFile(logFile, 'utf-8');
      const lines = content.trim().split('\n').filter(line => line);
      return lines.map(line => JSON.parse(line));
    } catch (error) {
      console.error(`Failed to read logs for date ${date}:`, error);
      return [];
    }
  }

  /**
   * Get available log dates
   */
  async getAvailableDates(): Promise<string[]> {
    try {
      const files = await fs.readdir(this.logDir);
      return files
        .filter(file => file.startsWith('hockey-iq-') && file.endsWith('.json'))
        .map(file => file.replace('hockey-iq-', '').replace('.json', ''))
        .sort()
        .reverse();
    } catch (error) {
      console.error('Failed to get available log dates:', error);
      return [];
    }
  }

  /**
   * Calculate statistics from logs
   */
  async getStatistics(date?: string): Promise<HockeyIQStats> {
    let logs: HockeyIQLogEntry[] = [];
    
    if (date) {
      logs = await this.getLogsForDate(date);
    } else {
      // Use today's logs from cache
      logs = this.inMemoryCache;
    }

    if (logs.length === 0) {
      return {
        totalInteractions: 0,
        chatInteractions: 0,
        quizInteractions: 0,
        averageResponseTime: 0,
        mostCommonCategories: {},
        toolUsageStats: {},
        errorRate: 0,
        uniqueSessions: 0,
        timeRange: {
          start: new Date().toISOString(),
          end: new Date().toISOString()
        }
      };
    }

    // Calculate statistics
    const chatLogs = logs.filter(log => log.mode === 'chat');
    const quizLogs = logs.filter(log => log.mode === 'quiz');
    const errorLogs = logs.filter(log => !log.success);
    
    // Category frequency
    const categoryCount: Record<string, number> = {};
    logs.forEach(log => {
      if (log.category) {
        categoryCount[log.category] = (categoryCount[log.category] || 0) + 1;
      }
    });

    // Tool usage frequency
    const toolCount: Record<string, number> = {};
    logs.forEach(log => {
      log.toolsCalled.forEach(tool => {
        toolCount[tool] = (toolCount[tool] || 0) + 1;
      });
    });

    // Unique sessions
    const uniqueSessions = new Set(logs.map(log => log.sessionId).filter(Boolean)).size;

    // Average response time
    const totalTime = logs.reduce((sum, log) => sum + log.processingTimeMs, 0);
    const avgTime = logs.length > 0 ? Math.round(totalTime / logs.length) : 0;

    return {
      totalInteractions: logs.length,
      chatInteractions: chatLogs.length,
      quizInteractions: quizLogs.length,
      averageResponseTime: avgTime,
      mostCommonCategories: categoryCount,
      toolUsageStats: toolCount,
      errorRate: logs.length > 0 ? (errorLogs.length / logs.length) * 100 : 0,
      uniqueSessions,
      timeRange: {
        start: logs[0]?.timestamp || new Date().toISOString(),
        end: logs[logs.length - 1]?.timestamp || new Date().toISOString()
      }
    };
  }

  /**
   * Search logs by query
   */
  async searchLogs(query: string, date?: string): Promise<HockeyIQLogEntry[]> {
    const logs = date ? await this.getLogsForDate(date) : this.inMemoryCache;
    const lowerQuery = query.toLowerCase();
    
    return logs.filter(log => 
      log.userMessage.toLowerCase().includes(lowerQuery) ||
      log.aiResponse.toLowerCase().includes(lowerQuery) ||
      log.category?.toLowerCase().includes(lowerQuery) ||
      log.toolsCalled.some(tool => tool.toLowerCase().includes(lowerQuery))
    );
  }
}

// Singleton instance
export const hockeyIQLogger = new HockeyIQLogger();