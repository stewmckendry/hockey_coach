/**
 * Hockey Diagram Testing Logger
 * Tracks all diagram generation requests and feedback for analysis
 */

import fs from 'fs/promises';
import path from 'path';

export interface DiagramGenerationLog {
  id: string;
  timestamp: string;
  
  // Request
  prompt: string;
  sessionId?: string;
  ipAddress?: string;
  
  // Processing
  processingTimeMs: number;
  toolsUsed: string[];
  parserType?: string;
  agentTraces?: {
    stage: string;
    detail: string;
    timestamp: string;
  }[];
  
  // Results
  success: boolean;
  imagePath?: string;
  imageBase64?: string;
  parserSpec?: any;
  error?: string;
  
  // Feedback
  feedback?: {
    id: string;
    rating: number;
    categories: string[];
    comment: string;
    timestamp: string;
  };
}

export interface DiagramTestStats {
  totalGenerations: number;
  successfulGenerations: number;
  averageProcessingTime: number;
  toolUsageStats: Record<string, number>;
  parserTypeStats: Record<string, number>;
  commonPrompts: Record<string, number>;
  feedbackCount: number;
  averageRating: number;
  errorRate: number;
  timeRange: {
    start: string;
    end: string;
  };
}

class HockeyDiagramLogger {
  private logDir: string;
  private currentLogFile: string;
  private feedbackFile: string;
  private inMemoryCache: DiagramGenerationLog[] = [];
  private maxCacheSize = 50; // Keep last 50 entries in memory

  constructor() {
    this.logDir = path.join(process.cwd(), 'logs', 'hockey-diagram-test');
    this.currentLogFile = path.join(this.logDir, `diagram-test-${this.getDateString()}.json`);
    this.feedbackFile = path.join(this.logDir, `diagram-feedback-${this.getDateString()}.json`);
    this.initializeLogger();
  }

  private async initializeLogger() {
    try {
      await fs.mkdir(this.logDir, { recursive: true });
      
      // Load today's logs into memory cache if file exists
      try {
        const content = await fs.readFile(this.currentLogFile, 'utf-8');
        const lines = content.trim().split('\n').filter(line => line);
        this.inMemoryCache = lines.slice(-this.maxCacheSize).map(line => JSON.parse(line));
        
        // Load feedback into corresponding logs
        await this.loadFeedback();
      } catch (error) {
        console.log('📝 Starting new Hockey Diagram test log for today');
      }
    } catch (error) {
      console.error('Failed to initialize Hockey Diagram logger:', error);
    }
  }

  private getDateString(): string {
    return new Date().toISOString().split('T')[0];
  }

  private generateId(): string {
    return `hdt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Load feedback from feedback file and merge with logs
   */
  private async loadFeedback() {
    try {
      // Load feedback from current date file
      const content = await fs.readFile(this.feedbackFile, 'utf-8');
      const lines = content.trim().split('\n').filter(line => line);
      const feedbackEntries = lines.map(line => JSON.parse(line));
      
      // Merge feedback with logs
      feedbackEntries.forEach(feedback => {
        const log = this.inMemoryCache.find(l => l.id === feedback.logId);
        if (log) {
          log.feedback = feedback;
        }
      });
    } catch (error) {
      // No feedback file yet
    }

    // Also load cross-date feedback
    try {
      const feedbackFiles = await this.getAvailableFeedbackFiles();
      for (const file of feedbackFiles) {
        if (file === path.basename(this.feedbackFile)) continue; // Skip current file
        
        try {
          const content = await fs.readFile(path.join(this.logDir, file), 'utf-8');
          const lines = content.trim().split('\n').filter(line => line);
          const feedbackEntries = lines.map(line => JSON.parse(line));
          
          feedbackEntries.forEach(feedback => {
            const log = this.inMemoryCache.find(l => l.id === feedback.logId);
            if (log && !log.feedback) { // Only add if no feedback already
              log.feedback = feedback;
            }
          });
        } catch (error) {
          // Skip this feedback file
        }
      }
    } catch (error) {
      // Failed to scan for feedback files
    }
  }

  /**
   * Log a diagram generation request
   */
  async logGeneration(
    prompt: string,
    result: {
      success: boolean;
      processingTimeMs: number;
      toolsUsed: string[];
      parserType?: string;
      imagePath?: string;
      imageBase64?: string;
      parserSpec?: any;
      agentTraces?: any[];
      error?: string;
    },
    metadata?: {
      sessionId?: string;
      ipAddress?: string;
    }
  ): Promise<string> {
    const entry: DiagramGenerationLog = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      prompt,
      processingTimeMs: result.processingTimeMs,
      toolsUsed: result.toolsUsed,
      parserType: result.parserType,
      success: result.success,
      imagePath: result.imagePath,
      imageBase64: result.imageBase64,
      parserSpec: result.parserSpec,
      agentTraces: result.agentTraces,
      error: result.error,
      sessionId: metadata?.sessionId,
      ipAddress: metadata?.ipAddress
    };

    await this.writeLog(entry);
    return entry.id;
  }

  /**
   * Add feedback to a generation log
   */
  async addFeedback(
    logId: string,
    feedback: {
      rating: number;
      categories: string[];
      comment: string;
    }
  ): Promise<void> {
    const feedbackEntry = {
      id: this.generateId(),
      logId,
      rating: feedback.rating,
      categories: feedback.categories,
      comment: feedback.comment,
      timestamp: new Date().toISOString()
    };

    // Write to feedback file
    await fs.appendFile(this.feedbackFile, JSON.stringify(feedbackEntry) + '\n');

    // Update in-memory cache
    const log = this.inMemoryCache.find(l => l.id === logId);
    if (log) {
      log.feedback = feedbackEntry;
    }

    console.log(`💬 Feedback added for ${logId}: ${feedback.rating}★`);
  }

  /**
   * Write log entry to file and update cache
   */
  private async writeLog(entry: DiagramGenerationLog): Promise<void> {
    try {
      // Check if we need to rotate to a new file
      const currentDate = this.getDateString();
      if (!this.currentLogFile.includes(currentDate)) {
        this.currentLogFile = path.join(this.logDir, `diagram-test-${currentDate}.json`);
        this.feedbackFile = path.join(this.logDir, `diagram-feedback-${currentDate}.json`);
        this.inMemoryCache = [];
      }

      // Don't store base64 in logs to save space
      const logEntry = { ...entry };
      delete logEntry.imageBase64;

      await fs.appendFile(this.currentLogFile, JSON.stringify(logEntry) + '\n');

      // Update in-memory cache
      this.inMemoryCache.push(entry);
      if (this.inMemoryCache.length > this.maxCacheSize) {
        this.inMemoryCache.shift();
      }

      if (process.env.NODE_ENV === 'development') {
        console.log(`🎨 [Diagram Test] "${entry.prompt}"`);
        console.log(`   🛠️ Tools: ${entry.toolsUsed.join(' → ')}`);
        console.log(`   ⏱️ Time: ${entry.processingTimeMs}ms`);
        console.log(`   ${entry.success ? '✅ Success' : '❌ Failed'}`);
      }
    } catch (error) {
      console.error('Failed to write diagram test log:', error);
    }
  }

  /**
   * Get recent logs
   */
  getRecentLogs(limit: number = 20, includeFeedback: boolean = true): DiagramGenerationLog[] {
    const logs = this.inMemoryCache.slice(-limit).reverse();
    return includeFeedback ? logs : logs.map(log => {
      const { feedback, ...rest } = log;
      return rest;
    });
  }

  /**
   * Get logs for a specific date
   */
  async getLogsForDate(date: string): Promise<DiagramGenerationLog[]> {
    try {
      const logFile = path.join(this.logDir, `diagram-test-${date}.json`);
      const content = await fs.readFile(logFile, 'utf-8');
      const lines = content.trim().split('\n').filter(line => line);
      const logs = lines.map(line => JSON.parse(line));

      // Load feedback from the same date file
      const feedbackFile = path.join(this.logDir, `diagram-feedback-${date}.json`);
      try {
        const feedbackContent = await fs.readFile(feedbackFile, 'utf-8');
        const feedbackLines = feedbackContent.trim().split('\n').filter(line => line);
        const feedbackEntries = feedbackLines.map(line => JSON.parse(line));
        
        feedbackEntries.forEach(feedback => {
          const log = logs.find(l => l.id === feedback.logId);
          if (log) {
            log.feedback = feedback;
          }
        });
      } catch (error) {
        // No feedback file for same date
      }

      // Also check for feedback in all feedback files (cross-date feedback)
      const feedbackFiles = await this.getAvailableFeedbackFiles();
      for (const file of feedbackFiles) {
        if (file.includes(date)) continue; // Skip the same date file we already checked
        
        try {
          const feedbackContent = await fs.readFile(path.join(this.logDir, file), 'utf-8');
          const feedbackLines = feedbackContent.trim().split('\n').filter(line => line);
          const feedbackEntries = feedbackLines.map(line => JSON.parse(line));
          
          feedbackEntries.forEach(feedback => {
            const log = logs.find(l => l.id === feedback.logId);
            if (log && !log.feedback) { // Only add if no feedback already
              log.feedback = feedback;
            }
          });
        } catch (error) {
          // Skip this feedback file
        }
      }

      return logs;
    } catch (error) {
      console.error(`Failed to read logs for date ${date}:`, error);
      return [];
    }
  }

  /**
   * Get available feedback files
   */
  private async getAvailableFeedbackFiles(): Promise<string[]> {
    try {
      const files = await fs.readdir(this.logDir);
      return files.filter(file => file.startsWith('diagram-feedback-') && file.endsWith('.json'));
    } catch (error) {
      return [];
    }
  }

  /**
   * Get statistics
   */
  async getStatistics(date?: string): Promise<DiagramTestStats> {
    let logs: DiagramGenerationLog[] = [];
    
    if (date) {
      logs = await this.getLogsForDate(date);
    } else {
      logs = this.inMemoryCache;
    }

    if (logs.length === 0) {
      return {
        totalGenerations: 0,
        successfulGenerations: 0,
        averageProcessingTime: 0,
        toolUsageStats: {},
        parserTypeStats: {},
        commonPrompts: {},
        feedbackCount: 0,
        averageRating: 0,
        errorRate: 0,
        timeRange: {
          start: new Date().toISOString(),
          end: new Date().toISOString()
        }
      };
    }

    const successfulLogs = logs.filter(log => log.success);
    const logsWithFeedback = logs.filter(log => log.feedback);
    
    // Tool usage stats
    const toolCount: Record<string, number> = {};
    logs.forEach(log => {
      log.toolsUsed.forEach(tool => {
        toolCount[tool] = (toolCount[tool] || 0) + 1;
      });
    });

    // Parser type stats
    const parserCount: Record<string, number> = {};
    logs.forEach(log => {
      if (log.parserType) {
        parserCount[log.parserType] = (parserCount[log.parserType] || 0) + 1;
      }
    });

    // Common prompts
    const promptCount: Record<string, number> = {};
    logs.forEach(log => {
      const normalizedPrompt = log.prompt.toLowerCase().trim();
      promptCount[normalizedPrompt] = (promptCount[normalizedPrompt] || 0) + 1;
    });

    // Get top 5 prompts
    const commonPrompts = Object.entries(promptCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .reduce((acc, [prompt, count]) => ({ ...acc, [prompt]: count }), {});

    // Average processing time
    const totalTime = logs.reduce((sum, log) => sum + log.processingTimeMs, 0);
    const avgTime = logs.length > 0 ? Math.round(totalTime / logs.length) : 0;

    // Average rating
    const totalRating = logsWithFeedback.reduce((sum, log) => sum + (log.feedback?.rating || 0), 0);
    const avgRating = logsWithFeedback.length > 0 ? totalRating / logsWithFeedback.length : 0;

    return {
      totalGenerations: logs.length,
      successfulGenerations: successfulLogs.length,
      averageProcessingTime: avgTime,
      toolUsageStats: toolCount,
      parserTypeStats: parserCount,
      commonPrompts,
      feedbackCount: logsWithFeedback.length,
      averageRating: Math.round(avgRating * 10) / 10,
      errorRate: logs.length > 0 ? ((logs.length - successfulLogs.length) / logs.length) * 100 : 0,
      timeRange: {
        start: logs[0]?.timestamp || new Date().toISOString(),
        end: logs[logs.length - 1]?.timestamp || new Date().toISOString()
      }
    };
  }

  /**
   * Search logs
   */
  async searchLogs(query: string, date?: string): Promise<DiagramGenerationLog[]> {
    const logs = date ? await this.getLogsForDate(date) : this.inMemoryCache;
    const lowerQuery = query.toLowerCase();
    
    return logs.filter(log => 
      log.prompt.toLowerCase().includes(lowerQuery) ||
      log.error?.toLowerCase().includes(lowerQuery) ||
      log.toolsUsed.some(tool => tool.toLowerCase().includes(lowerQuery)) ||
      log.feedback?.comment.toLowerCase().includes(lowerQuery)
    );
  }

  /**
   * Get a specific log by ID
   */
  async getLogById(id: string): Promise<DiagramGenerationLog | null> {
    // Check cache first
    const cached = this.inMemoryCache.find(log => log.id === id);
    if (cached) return cached;

    // Search in files
    const dates = await this.getAvailableDates();
    for (const date of dates) {
      const logs = await this.getLogsForDate(date);
      const found = logs.find(log => log.id === id);
      if (found) return found;
    }

    return null;
  }

  /**
   * Get available dates
   */
  async getAvailableDates(): Promise<string[]> {
    try {
      const files = await fs.readdir(this.logDir);
      return files
        .filter(file => file.startsWith('diagram-test-') && file.endsWith('.json'))
        .map(file => file.replace('diagram-test-', '').replace('.json', ''))
        .sort()
        .reverse();
    } catch (error) {
      console.error('Failed to get available dates:', error);
      return [];
    }
  }
}

// Singleton instance
export const hockeyDiagramLogger = new HockeyDiagramLogger();