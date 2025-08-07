/**
 * Hockey IQ Monitor - Performance Statistics API
 * 
 * GET /api/hockey-iq/monitor/stats - Get performance metrics and statistics
 */

import { NextRequest, NextResponse } from 'next/server'
import { SessionManager } from '@/lib/server/sessionManager'
import { monitorStorage } from '@/lib/server/monitorStorage'
import { MonitorStatsResponse, MonitoringConfig } from '@/lib/types/monitoring'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    
    // Optional time range for stats
    const timeRange = searchParams.get('startDate') && searchParams.get('endDate') ? {
      start: searchParams.get('startDate')!,
      end: searchParams.get('endDate')!
    } : undefined
    
    // Get current performance metrics
    const metrics = SessionManager.getPerformanceMetrics()
    
    // Get storage stats
    const storageStats = monitorStorage.getStorageStats()
    
    // Get session statistics
    const sessionStats = SessionManager.getSessionStats()
    
    // Configuration settings for monitoring
    const config: MonitoringConfig = {
      enableSessionTracking: true,
      enablePerformanceMetrics: true,
      logRetentionDays: parseInt(process.env.MONITOR_RETENTION_DAYS || '7'),
      maxSessionsToStore: parseInt(process.env.MONITOR_MAX_SESSIONS || '1000'),
      performanceMetricsInterval: parseInt(process.env.MONITOR_METRICS_INTERVAL || '30'),
      enableRealTimeUpdates: process.env.MONITOR_REALTIME === 'true'
    }
    
    // Add additional statistics
    const enhancedMetrics = {
      ...metrics,
      // Add storage information
      storage: storageStats,
      
      // Add session breakdown
      sessionBreakdown: {
        ...sessionStats,
        avgSessionDuration: 0, // TODO: Calculate based on session data
        avgInteractionsPerSession: sessionStats.total > 0 ? Math.round(sessionStats.totalInteractions / sessionStats.total) : 0
      },
      
      // Add system health indicators
      systemHealth: {
        memoryUsage: process.memoryUsage(),
        uptime: process.uptime(),
        nodeVersion: process.version,
        environment: process.env.NODE_ENV || 'development'
      },
      
      // Add time range if provided
      timeRange: timeRange
    }
    
    const response: MonitorStatsResponse = {
      success: true,
      metrics: enhancedMetrics,
      config,
      timestamp: new Date().toISOString()
    }
    
    console.log(`[Monitor][API] Stats endpoint: ${sessionStats.total} total sessions, ${sessionStats.active} active, ${sessionStats.totalInteractions} total interactions`)
    
    return NextResponse.json(response)
    
  } catch (error) {
    console.error('[Monitor][API] Stats endpoint error:', error)
    
    // Return basic error response with minimal stats
    const fallbackConfig: MonitoringConfig = {
      enableSessionTracking: true,
      enablePerformanceMetrics: true,
      logRetentionDays: 7,
      maxSessionsToStore: 1000,
      performanceMetricsInterval: 30,
      enableRealTimeUpdates: false
    }
    
    const fallbackMetrics = {
      timestamp: new Date().toISOString(),
      sessionCount: 0,
      activeUsers: 0,
      totalInteractions: 0,
      avgResponseTime: { chat: 0, quiz: 0, exa: 0, mcp: 0 },
      successRates: { chat: 1, quiz: 1, exa: 1, mcp: 1 },
      toolUsage: {},
      cacheStats: { hitRate: 0, totalHits: 0, totalMisses: 0, avgGenerationTime: 0 },
      quizStats: { avgCorrectRate: 0, popularCategories: {}, difficultyDistribution: {} },
      error: error instanceof Error ? error.message : 'Unknown error'
    }
    
    return NextResponse.json({
      success: false,
      metrics: fallbackMetrics,
      config: fallbackConfig,
      timestamp: new Date().toISOString(),
      error: 'Failed to retrieve statistics'
    }, { status: 500 })
  }
}

// Export OPTIONS for CORS if needed
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}