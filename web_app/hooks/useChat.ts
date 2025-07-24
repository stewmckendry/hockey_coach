'use client'

import { useState, useCallback } from 'react'
import type { ChatMessage, ChatState, UseChatReturn } from '@/lib/types'
import { apiClient } from '@/lib/api'
import { generateId } from '@/lib/utils'

/**
 * Custom hook for managing chat state and interactions
 */
export function useChat(): UseChatReturn {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
    isTyping: false
  })

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: ChatMessage = {
      id: generateId(),
      content,
      role: 'user',
      timestamp: new Date()
    }

    // Add user message immediately
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null,
      isTyping: true
    }))

    try {
      // ✅ SECURE: Call server-side API endpoint
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          conversationHistory: state.messages.slice(-6) // Send last 6 messages for context
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to get coaching response')
      }

      const data = await response.json()

      // Create assistant message
      const assistantMessage: ChatMessage = {
        id: generateId(),
        content: data.response,
        role: 'assistant',
        timestamp: new Date(),
        metadata: {
          intent: data.metadata?.intent,
          toolsCalled: data.metadata?.toolsCalled,
          processingTime: data.metadata?.processingTimeMs
        }
      }

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
        isTyping: false
      }))

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred'
      
      const assistantMessage: ChatMessage = {
        id: generateId(),
        content: `I'm having trouble right now. Could you try again? ${errorMessage}`,
        role: 'assistant',
        timestamp: new Date(),
        metadata: {
          error: errorMessage
        }
      }

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
        error: errorMessage,
        isTyping: false
      }))
    }
  }, [state.messages])

  const clearMessages = useCallback(() => {
    setState({
      messages: [],
      isLoading: false,
      error: null,
      isTyping: false
    })
  }, [])

  const retry = useCallback(async () => {
    const lastUserMessage = [...state.messages]
      .reverse()
      .find(msg => msg.role === 'user')

    if (lastUserMessage) {
      // Remove the last assistant message if it was an error
      const filteredMessages = state.messages.filter(msg => 
        msg.id !== state.messages[state.messages.length - 1]?.id
      )
      
      setState(prev => ({
        ...prev,
        messages: filteredMessages,
        error: null
      }))

      await sendMessage(lastUserMessage.content)
    }
  }, [state.messages, sendMessage])

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    isTyping: state.isTyping,
    sendMessage,
    clearMessages,
    retry
  }
}

/**
 * Format API response for display in chat
 */
function formatResponse(response: any): string {
  if (typeof response === 'string') {
    return response
  }

  // Handle practice plan response
  if (response.title && response.main_activities) {
    return formatPracticePlan(response)
  }

  // Handle player development plan
  if (response.player_name && response.recommended_drills) {
    return formatDevelopmentPlan(response)
  }

  // Handle search results
  if (Array.isArray(response)) {
    return formatSearchResults(response)
  }

  // Handle coaching recommendations
  if (response.recommendation) {
    return formatCoachingRecommendation(response)
  }

  // Fallback to JSON representation
  return JSON.stringify(response, null, 2)
}

function formatPracticePlan(plan: any): string {
  let formatted = `# 🏒 ${plan.title}\n\n`
  formatted += `**Duration:** ${plan.duration_minutes} minutes | **Age Group:** ${plan.age_group}\n\n`
  
  if (plan.focus_areas?.length > 0) {
    formatted += `**Focus Areas:** ${plan.focus_areas.join(', ')}\n\n`
  }

  if (plan.warmup?.length > 0) {
    formatted += `## 🔥 Warm-up\n`
    plan.warmup.forEach((activity: any) => {
      formatted += `- **${activity.activity}** (${activity.duration}): ${activity.description}\n`
    })
    formatted += '\n'
  }

  if (plan.main_activities?.length > 0) {
    formatted += `## 🎯 Main Activities\n`
    plan.main_activities.forEach((activity: any, index: number) => {
      formatted += `### ${index + 1}. ${activity.activity} (${activity.duration})\n`
      formatted += `${activity.description}\n`
      if (activity.teaching_points) {
        formatted += `**Teaching Points:** ${activity.teaching_points}\n`
      }
      if (activity.setup) {
        formatted += `**Setup:** ${activity.setup}\n`
      }
      formatted += '\n'
    })
  }

  if (plan.cooldown?.length > 0) {
    formatted += `## 🧊 Cool-down\n`
    plan.cooldown.forEach((activity: any) => {
      formatted += `- **${activity.activity}** (${activity.duration}): ${activity.description}\n`
    })
    formatted += '\n'
  }

  if (plan.equipment_needed?.length > 0) {
    formatted += `## 🥅 Equipment Needed\n`
    formatted += plan.equipment_needed.map((item: string) => `- ${item}`).join('\n')
    formatted += '\n\n'
  }

  if (plan.coaching_notes) {
    formatted += `## 📝 Coaching Notes\n${plan.coaching_notes}\n`
  }

  return formatted
}

function formatDevelopmentPlan(plan: any): string {
  let formatted = `# 🚀 Player Development Plan\n\n`
  formatted += `**Player:** ${plan.player_name} | **Position:** ${plan.position}\n`
  formatted += `**Current Level:** ${plan.current_level} | **Timeline:** ${plan.timeline_weeks} weeks\n\n`

  if (plan.target_skills?.length > 0) {
    formatted += `## 🎯 Target Skills\n`
    formatted += plan.target_skills.map((skill: string) => `- ${skill}`).join('\n')
    formatted += '\n\n'
  }

  if (plan.recommended_drills?.length > 0) {
    formatted += `## 🏒 Recommended Drills\n`
    formatted += plan.recommended_drills.map((drill: string) => `- ${drill}`).join('\n')
    formatted += '\n\n'
  }

  if (plan.dryland_exercises?.length > 0) {
    formatted += `## 💪 Off-Ice Training\n`
    formatted += plan.dryland_exercises.map((exercise: string) => `- ${exercise}`).join('\n')
    formatted += '\n\n'
  }

  if (plan.progress_markers?.length > 0) {
    formatted += `## 📈 Progress Markers\n`
    formatted += plan.progress_markers.map((marker: string) => `- ${marker}`).join('\n')
    formatted += '\n'
  }

  return formatted
}

function formatSearchResults(results: any[]): string {
  if (results.length === 0) {
    return "I didn't find any specific results for your query. Try rephrasing or asking about a different topic."
  }

  let formatted = `# 🔍 Hockey Knowledge Results\n\nI found ${results.length} relevant results:\n\n`

  results.slice(0, 5).forEach((result, index) => {
    formatted += `## ${index + 1}. ${result.title}\n`
    formatted += `**Type:** ${result.content_type} | **Complexity:** ${result.complexity}\n`
    formatted += `${result.summary}\n`
    
    if (result.teaching_points) {
      formatted += `**Teaching Points:** ${result.teaching_points}\n`
    }
    
    if (result.equipment) {
      formatted += `**Equipment:** ${result.equipment}\n`
    }
    
    formatted += '\n'
  })

  if (results.length > 5) {
    formatted += `\n*Showing top 5 of ${results.length} results*`
  }

  return formatted
}

function formatCoachingRecommendation(recommendation: any): string {
  let formatted = `# 💡 Coaching Recommendation\n\n`
  formatted += `${recommendation.recommendation}\n\n`
  
  if (recommendation.rationale) {
    formatted += `## 🤔 Rationale\n${recommendation.rationale}\n\n`
  }

  if (recommendation.supporting_evidence?.length > 0) {
    formatted += `## 📚 Supporting Evidence\n`
    recommendation.supporting_evidence.forEach((evidence: any, index: number) => {
      formatted += `${index + 1}. **${evidence.title}** (${evidence.content_type})\n`
      formatted += `   ${evidence.summary}\n\n`
    })
  }

  return formatted
}
