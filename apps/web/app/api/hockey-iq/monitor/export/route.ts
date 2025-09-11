/**
 * Hockey IQ Monitor - Data Export API
 * 
 * GET /api/hockey-iq/monitor/export - Export monitoring data for analysis
 */

import { NextRequest, NextResponse } from 'next/server'
import { monitorStorage } from '@/lib/server/monitorStorage'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    
    // Parse date range for export
    const dateRange = searchParams.get('startDate') && searchParams.get('endDate') ? {
      start: searchParams.get('startDate')!,
      end: searchParams.get('endDate')!
    } : undefined
    
    const format = searchParams.get('format') || 'json'
    
    // Export data using MonitorStorage
    const exportData = monitorStorage.exportData(dateRange)
    
    if (!exportData) {
      return NextResponse.json({
        success: false,
        error: 'Failed to export data'
      }, { status: 500 })
    }
    
    console.log(`[Monitor][API] Export: ${exportData.stats.sessions} sessions, ${exportData.stats.chatInteractions} chat interactions, ${exportData.stats.quizTurns} quiz turns`)
    
    // Return JSON format
    if (format === 'json') {
      const response = NextResponse.json({
        success: true,
        export: exportData
      })
      
      // Set download headers
      response.headers.set('Content-Disposition', `attachment; filename="hockey-iq-monitor-export-${new Date().toISOString().split('T')[0]}.json"`)
      
      return response
    }
    
    // TODO: Add CSV format support if needed
    if (format === 'csv') {
      return NextResponse.json({
        success: false,
        error: 'CSV format not yet implemented'
      }, { status: 400 })
    }
    
    return NextResponse.json({
      success: false,
      error: 'Unsupported export format'
    }, { status: 400 })
    
  } catch (error) {
    console.error('[Monitor][API] Export error:', error)
    
    return NextResponse.json({
      success: false,
      error: 'Failed to export data',
      details: error instanceof Error ? error.message : 'Unknown error'
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