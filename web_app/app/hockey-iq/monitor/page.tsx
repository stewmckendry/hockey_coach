'use client'

import { useState, useEffect } from 'react'
import { HockeyIQLogEntry, HockeyIQStats } from '@/lib/server/hockeyIQLogger'

/**
 * Hockey IQ Monitoring Dashboard
 * Real-time monitoring of chatbot interactions, tool usage, and performance
 */
export default function HockeyIQMonitor() {
  const [logs, setLogs] = useState<HockeyIQLogEntry[]>([])
  const [stats, setStats] = useState<HockeyIQStats | null>(null)
  const [selectedDate, setSelectedDate] = useState<string>('')
  const [availableDates, setAvailableDates] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLog, setSelectedLog] = useState<HockeyIQLogEntry | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'live' | 'search' | 'stats'>('live')

  // Fetch recent logs and stats
  const fetchData = async () => {
    try {
      // Fetch recent logs
      const logsResponse = await fetch('/api/hockey-iq/monitor?action=recent&limit=30')
      if (logsResponse.ok) {
        const logsData = await logsResponse.json()
        setLogs(logsData.logs)
      }

      // Fetch stats
      const statsResponse = await fetch('/api/hockey-iq/monitor?action=stats')
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData.stats)
      }

      // Fetch available dates
      const datesResponse = await fetch('/api/hockey-iq/monitor?action=dates')
      if (datesResponse.ok) {
        const datesData = await datesResponse.json()
        setAvailableDates(datesData.dates)
      }
    } catch (error) {
      console.error('Failed to fetch monitoring data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Search logs
  const searchLogs = async () => {
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const url = selectedDate
        ? `/api/hockey-iq/monitor?action=search&query=${encodeURIComponent(searchQuery)}&date=${selectedDate}`
        : `/api/hockey-iq/monitor?action=search&query=${encodeURIComponent(searchQuery)}`
      
      const response = await fetch(url)
      if (response.ok) {
        const data = await response.json()
        setLogs(data.logs)
      }
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  // Auto-refresh effect
  useEffect(() => {
    fetchData()
    
    if (autoRefresh && activeTab === 'live') {
      const interval = setInterval(fetchData, 5000) // Refresh every 5 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh, activeTab])

  // Format timestamp
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  // Format date
  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading && logs.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading monitoring dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">🏒 Hockey IQ Monitor</h1>
              <p className="text-sm text-gray-500">Real-time chatbot analytics and monitoring</p>
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded text-blue-500"
                />
                <span className="text-sm text-gray-700">Auto-refresh</span>
              </label>
              <button
                onClick={fetchData}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Refresh Now
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('live')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'live'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Live Feed
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'stats'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Statistics
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'search'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Search Logs
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        {/* Statistics Tab */}
        {activeTab === 'stats' && stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-gray-900">{stats.totalInteractions}</div>
              <div className="text-sm text-gray-500">Total Interactions</div>
              <div className="mt-2 text-xs text-gray-400">
                Chat: {stats.chatInteractions} | Quiz: {stats.quizInteractions}
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-gray-900">{stats.averageResponseTime}ms</div>
              <div className="text-sm text-gray-500">Avg Response Time</div>
              <div className="mt-2">
                <div className="text-xs text-gray-400">Performance</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div 
                    className={`h-2 rounded-full ${
                      stats.averageResponseTime < 1000 ? 'bg-green-500' :
                      stats.averageResponseTime < 3000 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.min(100, (1000 / stats.averageResponseTime) * 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-gray-900">{stats.uniqueSessions}</div>
              <div className="text-sm text-gray-500">Unique Sessions</div>
              <div className="mt-2 text-xs text-gray-400">
                Error Rate: {stats.errorRate.toFixed(1)}%
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-gray-900">
                {Object.keys(stats.toolUsageStats).reduce((sum, key) => sum + stats.toolUsageStats[key], 0)}
              </div>
              <div className="text-sm text-gray-500">Tool Calls</div>
              <div className="mt-2 text-xs text-gray-400">
                {Object.keys(stats.toolUsageStats).length} different tools
              </div>
            </div>

            {/* Categories breakdown */}
            {Object.keys(stats.mostCommonCategories).length > 0 && (
              <div className="bg-white rounded-lg shadow p-6 col-span-2">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Popular Categories</h3>
                <div className="space-y-2">
                  {Object.entries(stats.mostCommonCategories)
                    .sort(([,a], [,b]) => b - a)
                    .slice(0, 5)
                    .map(([category, count]) => (
                      <div key={category} className="flex justify-between">
                        <span className="text-sm text-gray-600">{category}</span>
                        <span className="text-sm font-medium text-gray-900">{count}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Tool usage breakdown */}
            {Object.keys(stats.toolUsageStats).length > 0 && (
              <div className="bg-white rounded-lg shadow p-6 col-span-2">
                <h3 className="text-sm font-medium text-gray-900 mb-3">MCP Tool Usage</h3>
                <div className="space-y-2">
                  {Object.entries(stats.toolUsageStats)
                    .sort(([,a], [,b]) => b - a)
                    .map(([tool, count]) => (
                      <div key={tool} className="flex justify-between">
                        <span className="text-sm text-gray-600">{tool.replace('search_hockey_', '')}</span>
                        <span className="text-sm font-medium text-gray-900">{count} calls</span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && searchLogs()}
                placeholder="Search messages, responses, or tools..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <select
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="">All dates</option>
                {availableDates.map(date => (
                  <option key={date} value={date}>{date}</option>
                ))}
              </select>
              <button
                onClick={searchLogs}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Search
              </button>
            </div>
          </div>
        )}

        {/* Logs List */}
        {(activeTab === 'live' || activeTab === 'search') && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                {activeTab === 'live' ? 'Recent Interactions' : 'Search Results'}
              </h2>
              <p className="text-sm text-gray-500">{logs.length} entries</p>
            </div>
            
            <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className="px-6 py-4 hover:bg-gray-50 cursor-pointer"
                  onClick={() => setSelectedLog(log)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                          log.mode === 'chat' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'
                        }`}>
                          {log.mode}
                        </span>
                        {log.category && (
                          <span className="text-xs text-gray-500">{log.category}</span>
                        )}
                        {log.toolsCalled.length > 0 ? (
                          <span className="text-xs text-green-600">
                            🔧 {log.toolsCalled.length} tools
                          </span>
                        ) : (
                          <span className="text-xs text-gray-400">
                            No tools used
                          </span>
                        )}
                        {!log.success && (
                          <span className="text-xs text-red-600">⚠️ Error</span>
                        )}
                      </div>
                      <p className="mt-1 text-sm text-gray-900 font-medium">
                        {log.userMessage.substring(0, 100)}
                        {log.userMessage.length > 100 && '...'}
                      </p>
                      <p className="mt-1 text-sm text-gray-600">
                        {log.aiResponse.substring(0, 150)}
                        {log.aiResponse.length > 150 && '...'}
                      </p>
                    </div>
                    <div className="ml-4 text-right">
                      <p className="text-xs text-gray-500">{formatTime(log.timestamp)}</p>
                      <p className="text-xs text-gray-400 mt-1">{log.processingTimeMs}ms</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[80vh] overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">Interaction Details</h3>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-gray-400 hover:text-gray-500"
              >
                ✕
              </button>
            </div>
            
            <div className="px-6 py-4 overflow-y-auto max-h-[calc(80vh-8rem)]">
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-700">Metadata</h4>
                  <dl className="mt-2 text-sm text-gray-600 space-y-1">
                    <div className="flex justify-between">
                      <dt>ID:</dt>
                      <dd className="font-mono text-xs">{selectedLog.id}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt>Timestamp:</dt>
                      <dd>{formatDate(selectedLog.timestamp)}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt>Mode:</dt>
                      <dd>{selectedLog.mode}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt>Processing Time:</dt>
                      <dd>{selectedLog.processingTimeMs}ms</dd>
                    </div>
                    {selectedLog.responseId && (
                      <div className="flex justify-between">
                        <dt>Response ID:</dt>
                        <dd className="font-mono text-xs">{selectedLog.responseId}</dd>
                      </div>
                    )}
                  </dl>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-700">User Message</h4>
                  <p className="mt-2 text-sm text-gray-900 bg-gray-50 p-3 rounded">
                    {selectedLog.userMessage}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-700">AI Response</h4>
                  <p className="mt-2 text-sm text-gray-900 bg-blue-50 p-3 rounded whitespace-pre-wrap">
                    {selectedLog.aiResponse}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-700">Tools Called</h4>
                  {selectedLog.toolsCalled.length > 0 ? (
                    <ul className="mt-2 text-sm text-gray-600 bg-green-50 p-3 rounded">
                      {selectedLog.toolsCalled.map((tool, index) => (
                        <li key={index}>🔧 {tool}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-2 text-sm text-gray-500 bg-gray-50 p-3 rounded">
                      None - Response generated without external tools
                    </p>
                  )}
                </div>

                {selectedLog.error && (
                  <div>
                    <h4 className="text-sm font-medium text-red-700">Error</h4>
                    <p className="mt-2 text-sm text-red-900 bg-red-50 p-3 rounded">
                      {selectedLog.error}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}