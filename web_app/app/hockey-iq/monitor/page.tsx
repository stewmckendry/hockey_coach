'use client'

import { useState, useEffect } from 'react'
import { 
  SessionLog, 
  ChatInteraction, 
  QuizSession, 
  QuizTurn, 
  PerformanceMetrics,
  SessionListResponse,
  ChatHistoryResponse,
  QuizHistoryResponse,
  MonitorStatsResponse
} from '@/lib/types/monitoring'

/**
 * Hockey IQ Monitor Dashboard
 * 
 * Displays session tracking, chat history, quiz history, and performance metrics
 * for the Hockey IQ Chatbot monitoring system.
 */
export default function HockeyIQMonitorPage() {
  const [sessions, setSessions] = useState<SessionLog[]>([])
  const [selectedSession, setSelectedSession] = useState<SessionLog | null>(null)
  const [chatHistory, setChatHistory] = useState<ChatInteraction[]>([])
  const [quizHistory, setQuizHistory] = useState<{ session: QuizSession | null, turns: QuizTurn[] }>({ session: null, turns: [] })
  const [stats, setStats] = useState<PerformanceMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'sessions' | 'chat' | 'quiz' | 'stats'>('overview')
  const [error, setError] = useState<string | null>(null)

  // Load sessions on component mount
  useEffect(() => {
    loadSessions()
    loadStats()
    
    // Set up polling for real-time updates
    const interval = setInterval(() => {
      loadSessions()
      loadStats()
    }, 10000) // Update every 10 seconds
    
    return () => clearInterval(interval)
  }, [])

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/hockey-iq/monitor/sessions?limit=100')
      const data: SessionListResponse = await response.json()
      
      if (data.success) {
        setSessions(data.sessions)
      } else {
        setError('Failed to load sessions')
      }
    } catch (err) {
      console.error('Error loading sessions:', err)
      setError('Failed to load sessions')
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch('/api/hockey-iq/monitor/stats')
      const data: MonitorStatsResponse = await response.json()
      
      if (data.success) {
        setStats(data.metrics)
      } else {
        setError('Failed to load stats')
      }
      setLoading(false)
    } catch (err) {
      console.error('Error loading stats:', err)
      setError('Failed to load stats')
      setLoading(false)
    }
  }

  const loadSessionDetails = async (session: SessionLog) => {
    try {
      setSelectedSession(session)
      
      // Load chat history
      const chatResponse = await fetch(`/api/hockey-iq/monitor/chat/${session.sessionId}`)
      const chatData: ChatHistoryResponse = await chatResponse.json()
      
      if (chatData.success) {
        setChatHistory(chatData.interactions)
      }
      
      // Load quiz history  
      const quizResponse = await fetch(`/api/hockey-iq/monitor/quiz/${session.sessionId}`)
      const quizData: QuizHistoryResponse = await quizResponse.json()
      
      if (quizData.success) {
        setQuizHistory({ session: quizData.session, turns: quizData.turns })
      }
      
      setActiveTab('chat')
    } catch (err) {
      console.error('Error loading session details:', err)
      setError('Failed to load session details')
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const formatDuration = (startTime: string, endTime: string) => {
    const start = new Date(startTime).getTime()
    const end = new Date(endTime).getTime()
    const durationMs = end - start
    const minutes = Math.floor(durationMs / 60000)
    const seconds = Math.floor((durationMs % 60000) / 1000)
    return `${minutes}m ${seconds}s`
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading monitor data...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Hockey IQ Monitor Dashboard</h1>
          <p className="text-gray-600">Real-time monitoring and analytics for the Hockey IQ Chatbot</p>
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'sessions', name: 'Sessions' },
              { id: 'chat', name: 'Chat History' },
              { id: 'quiz', name: 'Quiz History' },
              { id: 'stats', name: 'Statistics' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow">
          {activeTab === 'overview' && (
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">System Overview</h2>
              
              {stats && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-blue-800">Total Sessions</h3>
                    <p className="text-2xl font-bold text-blue-900">{stats.sessionCount}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-green-800">Active Users</h3>
                    <p className="text-2xl font-bold text-green-900">{stats.activeUsers}</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-purple-800">Total Interactions</h3>
                    <p className="text-2xl font-bold text-purple-900">{stats.totalInteractions}</p>
                  </div>
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-orange-800">Avg Response Time</h3>
                    <p className="text-2xl font-bold text-orange-900">{stats.avgResponseTime.chat}ms</p>
                  </div>
                </div>
              )}

              <h3 className="text-lg font-medium mb-3">Recent Sessions</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Session</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mode</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Interactions</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Activity</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {sessions.slice(0, 10).map((session) => (
                      <tr key={session.sessionId} className="hover:bg-gray-50 cursor-pointer" onClick={() => loadSessionDetails(session)}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                          {session.sessionId.substring(0, 12)}...
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            session.mode === 'chat' ? 'bg-blue-100 text-blue-800' :
                            session.mode === 'quiz' ? 'bg-purple-100 text-purple-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {session.mode}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{session.totalInteractions}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatTimestamp(session.lastActivity)}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            session.isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {session.isActive ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'sessions' && (
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">All Sessions</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Session ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP Address</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mode</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Interactions</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {sessions.map((session) => (
                      <tr key={session.sessionId} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                          {session.sessionId}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{session.ipAddress}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            session.mode === 'chat' ? 'bg-blue-100 text-blue-800' :
                            session.mode === 'quiz' ? 'bg-purple-100 text-purple-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {session.mode}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{session.totalInteractions}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDuration(session.startTime, session.lastActivity)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            session.isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {session.isActive ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => loadSessionDetails(session)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'chat' && selectedSession && (
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">
                Chat History - {selectedSession.sessionId.substring(0, 12)}...
              </h2>
              <div className="space-y-4">
                {chatHistory.map((interaction) => (
                  <div key={interaction.messageId} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <span className="text-sm text-gray-500">{formatTimestamp(interaction.timestamp)}</span>
                        <span className="ml-2 text-sm text-gray-500">({interaction.processingTime}ms)</span>
                        {interaction.toolsUsed.length > 0 && (
                          <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                            Tools: {interaction.toolsUsed.join(', ')}
                          </span>
                        )}
                      </div>
                      <span className={`px-2 py-1 text-xs rounded ${
                        interaction.mode === 'qa' ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'
                      }`}>
                        {interaction.mode}
                      </span>
                    </div>
                    <div className="mb-2">
                      <p className="font-medium text-gray-900">Q: {interaction.question}</p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-gray-700">{interaction.response}</p>
                    </div>
                    {interaction.error && (
                      <div className="mt-2 p-2 bg-red-50 text-red-800 text-sm rounded">
                        Error: {interaction.error}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'quiz' && selectedSession && (
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">
                Quiz History - {selectedSession.sessionId.substring(0, 12)}...
              </h2>
              
              {quizHistory.session && (
                <div className="mb-6 bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-2">Quiz Session Summary</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <span className="text-sm text-gray-500">Score</span>
                      <p className="font-semibold">{quizHistory.session.userScore.correct}/{quizHistory.session.userScore.total}</p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-500">Accuracy</span>
                      <p className="font-semibold">
                        {quizHistory.session.userScore.total > 0 
                          ? Math.round((quizHistory.session.userScore.correct / quizHistory.session.userScore.total) * 100)
                          : 0}%
                      </p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-500">Difficulty</span>
                      <p className="font-semibold capitalize">{quizHistory.session.difficulty}</p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-500">Questions Bank</span>
                      <p className="font-semibold">{quizHistory.session.questionBank.length}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                {quizHistory.turns.map((turn, index) => (
                  <div key={turn.turnId} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <span className="text-sm text-gray-500">Turn #{quizHistory.turns.length - index}</span>
                        <span className="ml-2 text-sm text-gray-500">{formatTimestamp(turn.timestamp)}</span>
                        <span className="ml-2 text-sm text-gray-500">({turn.processingTime}ms)</span>
                      </div>
                      <div className="flex space-x-2">
                        <span className={`px-2 py-1 text-xs rounded ${
                          turn.isCorrect ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {turn.isCorrect ? 'Correct' : 'Incorrect'}
                        </span>
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                          {turn.category}
                        </span>
                        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                          {turn.questionType}
                        </span>
                      </div>
                    </div>
                    <div className="mb-2">
                      <p className="font-medium text-gray-900">Q: {turn.question}</p>
                    </div>
                    <div className="mb-2">
                      <p className="text-gray-700">Student Answer: "{turn.userAnswer}"</p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-gray-700">{turn.aiResponse}</p>
                    </div>
                    {turn.hintsUsed > 0 && (
                      <div className="mt-2 text-sm text-blue-600">
                        Hints used: {turn.hintsUsed}
                      </div>
                    )}
                    {turn.error && (
                      <div className="mt-2 p-2 bg-red-50 text-red-800 text-sm rounded">
                        Error: {turn.error}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'stats' && stats && (
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">Performance Statistics</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Response Times */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-3">Average Response Times</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Chat:</span>
                      <span className="font-mono">{stats.avgResponseTime.chat}ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Quiz:</span>
                      <span className="font-mono">{stats.avgResponseTime.quiz}ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Exa API:</span>
                      <span className="font-mono">{stats.avgResponseTime.exa}ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span>MCP:</span>
                      <span className="font-mono">{stats.avgResponseTime.mcp}ms</span>
                    </div>
                  </div>
                </div>

                {/* Success Rates */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-3">Success Rates</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Chat:</span>
                      <span className="font-mono">{(stats.successRates.chat * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Quiz:</span>
                      <span className="font-mono">{(stats.successRates.quiz * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Exa API:</span>
                      <span className="font-mono">{(stats.successRates.exa * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>MCP:</span>
                      <span className="font-mono">{(stats.successRates.mcp * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>

                {/* Quiz Statistics */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-3">Quiz Analytics</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Avg Correct Rate:</span>
                      <span className="font-mono">{(stats.quizStats.avgCorrectRate * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                  {Object.keys(stats.quizStats.popularCategories).length > 0 && (
                    <div className="mt-3">
                      <h4 className="text-sm font-medium mb-2">Popular Categories:</h4>
                      <div className="space-y-1">
                        {Object.entries(stats.quizStats.popularCategories)
                          .sort(([,a], [,b]) => b - a)
                          .slice(0, 5)
                          .map(([category, count]) => (
                            <div key={category} className="flex justify-between text-sm">
                              <span className="capitalize">{category}:</span>
                              <span>{count}</span>
                            </div>
                          ))
                        }
                      </div>
                    </div>
                  )}
                </div>

                {/* Cache Statistics */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium mb-3">Cache Performance</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Hit Rate:</span>
                      <span className="font-mono">{(stats.cacheStats.hitRate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Hits:</span>
                      <span className="font-mono">{stats.cacheStats.totalHits}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Misses:</span>
                      <span className="font-mono">{stats.cacheStats.totalMisses}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Avg Generation:</span>
                      <span className="font-mono">{stats.cacheStats.avgGenerationTime}ms</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Last updated: {stats?.timestamp ? formatTimestamp(stats.timestamp) : 'Loading...'}</p>
          <div className="mt-2 space-x-4">
            <a href="/api/hockey-iq/monitor/export" className="text-blue-600 hover:text-blue-800">Export Data</a>
            <button 
              onClick={() => window.location.reload()} 
              className="text-blue-600 hover:text-blue-800"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}