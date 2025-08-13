'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'
import { DiagramGenerationLog, DiagramTestStats } from '@/lib/server/hockeyDiagramLogger'
import { TechnicalDetails } from '@/components/hockey-diagram/TechnicalDetails'

export default function HockeyDiagramMonitor() {
  const [logs, setLogs] = useState<DiagramGenerationLog[]>([])
  const [stats, setStats] = useState<DiagramTestStats | null>(null)
  const [selectedDate, setSelectedDate] = useState<string>('')
  const [availableDates, setAvailableDates] = useState<string[]>([])
  const [selectedLog, setSelectedLog] = useState<DiagramGenerationLog | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'gallery' | 'stats' | 'feedback'>('gallery')

  // Fetch data
  const fetchData = async () => {
    try {
      // Fetch recent logs
      const logsResponse = await fetch('/api/hockey-diagram/monitor?action=recent&limit=50')
      if (logsResponse.ok) {
        const logsData = await logsResponse.json()
        setLogs(logsData.logs)
      }

      // Fetch stats
      const statsResponse = await fetch('/api/hockey-diagram/monitor?action=stats')
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData.stats)
      }

      // Fetch available dates
      const datesResponse = await fetch('/api/hockey-diagram/monitor?action=dates')
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

  useEffect(() => {
    fetchData()
  }, [])

  // Load logs for specific date
  const loadDateLogs = async (date: string) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/hockey-diagram/monitor?action=date&date=${date}`)
      if (response.ok) {
        const data = await response.json()
        setLogs(data.logs)
      }
    } catch (error) {
      console.error('Failed to load date logs:', error)
    } finally {
      setLoading(false)
    }
  }

  // Format time
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
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
              <h1 className="text-2xl font-bold text-gray-900">🏒 Hockey Diagram Monitor</h1>
              <p className="text-sm text-gray-500">Review generated diagrams and feedback</p>
            </div>
            <div className="flex items-center gap-4">
              <select
                value={selectedDate}
                onChange={(e) => {
                  setSelectedDate(e.target.value)
                  if (e.target.value) {
                    loadDateLogs(e.target.value)
                  } else {
                    fetchData()
                  }
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="">Today</option>
                {availableDates.map(date => (
                  <option key={date} value={date}>{date}</option>
                ))}
              </select>
              <a
                href="/hockey-diagram-test"
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Test Console →
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('gallery')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'gallery'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Diagram Gallery
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
              onClick={() => setActiveTab('feedback')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'feedback'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Feedback Review
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        {/* Statistics Tab */}
        {activeTab === 'stats' && stats && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-2xl font-bold text-gray-900">{stats.totalGenerations}</div>
                <div className="text-sm text-gray-500">Total Generations</div>
                <div className="mt-2 text-xs text-gray-400">
                  Success rate: {((stats.successfulGenerations / stats.totalGenerations) * 100).toFixed(1)}%
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-2xl font-bold text-gray-900">{stats.averageProcessingTime}ms</div>
                <div className="text-sm text-gray-500">Avg Processing Time</div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-2xl font-bold text-gray-900">{stats.feedbackCount}</div>
                <div className="text-sm text-gray-500">Feedback Entries</div>
                <div className="mt-2 text-xs text-gray-400">
                  Avg rating: {stats.averageRating.toFixed(1)} ★
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-2xl font-bold text-gray-900">{stats.errorRate.toFixed(1)}%</div>
                <div className="text-sm text-gray-500">Error Rate</div>
              </div>
            </div>

            {/* Tool Usage */}
            {Object.keys(stats.toolUsageStats).length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Tool Usage</h3>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(stats.toolUsageStats).map(([tool, count]) => (
                    <div key={tool} className="flex justify-between">
                      <span className="text-sm text-gray-600">{tool}</span>
                      <span className="text-sm font-medium text-gray-900">{count} calls</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Common Prompts */}
            {Object.keys(stats.commonPrompts).length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Common Prompts</h3>
                <div className="space-y-2">
                  {Object.entries(stats.commonPrompts).map(([prompt, count]) => (
                    <div key={prompt} className="flex justify-between">
                      <span className="text-sm text-gray-600">{prompt}</span>
                      <span className="text-sm font-medium text-gray-900">{count} times</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Gallery Tab */}
        {activeTab === 'gallery' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {logs.filter(log => log.success).map((log) => (
              <div
                key={log.id}
                className="bg-white rounded-lg shadow overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => setSelectedLog(log)}
              >
                {log.imageBase64 ? (
                  <div className="aspect-[4/3] relative">
                    <img
                      src={`data:image/png;base64,${log.imageBase64}`}
                      alt={log.prompt}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ) : (
                  <div className="aspect-[4/3] bg-gray-100 flex items-center justify-center">
                    <span className="text-gray-400">No preview</span>
                  </div>
                )}
                <div className="p-4">
                  <p className="text-sm font-medium text-gray-900 line-clamp-2">{log.prompt}</p>
                  <div className="mt-2 flex justify-between items-center">
                    <span className="text-xs text-gray-500">{formatTime(log.timestamp)}</span>
                    {log.feedback && (
                      <span className="text-xs text-yellow-600">{log.feedback.rating}★</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Feedback Tab */}
        {activeTab === 'feedback' && (
          <div className="space-y-4">
            {logs.filter(log => log.feedback).map((log) => (
              <div key={log.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex gap-6">
                  {log.imageBase64 && (
                    <div className="w-32 h-24 flex-shrink-0">
                      <img
                        src={`data:image/png;base64,${log.imageBase64}`}
                        alt={log.prompt}
                        className="w-full h-full object-cover rounded"
                      />
                    </div>
                  )}
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-gray-900">{log.prompt}</p>
                        <p className="text-sm text-gray-500 mt-1">{formatTime(log.timestamp)}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-lg text-yellow-600">{log.feedback?.rating}★</div>
                        <div className="text-xs text-gray-500">{log.processingTimeMs}ms</div>
                      </div>
                    </div>
                    {log.feedback && (
                      <div className="mt-3">
                        {log.feedback.categories.length > 0 && (
                          <div className="flex gap-2 mb-2">
                            {log.feedback.categories.map(cat => (
                              <span key={cat} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                                {cat}
                              </span>
                            ))}
                          </div>
                        )}
                        {log.feedback.comment && (
                          <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                            {log.feedback.comment}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">Diagram Details</h3>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-gray-400 hover:text-gray-500"
              >
                ✕
              </button>
            </div>
            
            <div className="px-6 py-4 overflow-y-auto max-h-[calc(90vh-8rem)]">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Image */}
                <div>
                  {selectedLog.imageBase64 ? (
                    <img
                      src={`data:image/png;base64,${selectedLog.imageBase64}`}
                      alt={selectedLog.prompt}
                      className="w-full rounded-lg"
                    />
                  ) : (
                    <div className="aspect-[4/3] bg-gray-100 rounded-lg flex items-center justify-center">
                      <span className="text-gray-400">No image available</span>
                    </div>
                  )}
                </div>

                {/* Details */}
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Prompt</h4>
                    <p className="mt-1 text-sm text-gray-900">{selectedLog.prompt}</p>
                  </div>

                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Generation Info</h4>
                    <dl className="mt-1 text-sm text-gray-600 space-y-1">
                      <div className="flex justify-between">
                        <dt>ID:</dt>
                        <dd className="font-mono text-xs">{selectedLog.id}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt>Time:</dt>
                        <dd>{formatTime(selectedLog.timestamp)}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt>Processing:</dt>
                        <dd>{selectedLog.processingTimeMs}ms</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt>Tools:</dt>
                        <dd>{selectedLog.toolsUsed.join(', ')}</dd>
                      </div>
                    </dl>
                  </div>

                  {selectedLog.feedback && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700">Feedback</h4>
                      <div className="mt-1">
                        <div className="text-lg text-yellow-600 mb-2">{selectedLog.feedback.rating}★</div>
                        {selectedLog.feedback.categories.length > 0 && (
                          <div className="flex gap-2 mb-2">
                            {selectedLog.feedback.categories.map(cat => (
                              <span key={cat} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                                {cat}
                              </span>
                            ))}
                          </div>
                        )}
                        {selectedLog.feedback.comment && (
                          <p className="text-sm text-gray-700">{selectedLog.feedback.comment}</p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Technical Details - Parser Spec and Agent Traces */}
                  {(selectedLog.parserSpec || selectedLog.agentTraces) && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-3">Technical Details</h4>
                      <TechnicalDetails 
                        parserSpec={selectedLog.parserSpec}
                        agentTraces={(selectedLog.agentTraces || []) as any}
                      />
                    </div>
                  )}

                  {/* Original File Path (for debugging) */}
                  {selectedLog.imagePath && (
                    <div className="mt-4 p-3 bg-gray-50 rounded">
                      <p className="text-xs text-gray-600">
                        <span className="font-medium">Diagram File:</span> {selectedLog.imagePath}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}