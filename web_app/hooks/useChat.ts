'use client'

import { useState, useCallback, useRef } from 'react'
import { ChatMessage, ConversationThread, UseChatReturn } from '@/lib/types'
import { useLocalStorage } from '@/hooks/useLocalStorage'

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  
  // Persistent conversation storage with date handling
  const { 
    value: rawConversations, 
    setValue: setConversations 
  } = useLocalStorage<ConversationThread[]>('chat-conversations', [])
  
  // Ensure conversations have proper Date objects (handle localStorage deserialization)
  const conversations = rawConversations.map(conv => ({
    ...conv,
    createdAt: conv.createdAt instanceof Date ? conv.createdAt : new Date(conv.createdAt),
    updatedAt: conv.updatedAt instanceof Date ? conv.updatedAt : new Date(conv.updatedAt),
    messages: conv.messages?.map(msg => ({
      ...msg,
      timestamp: msg.timestamp instanceof Date ? msg.timestamp : new Date(msg.timestamp)
    })) || []
  }))
  
  const abortControllerRef = useRef<AbortController | null>(null)

  const getCurrentConversation = useCallback(() => {
    return conversations.find(c => c.id === activeConversationId) || null
  }, [conversations, activeConversationId])

  const updateConversation = useCallback((conversationId: string, updates: Partial<ConversationThread>) => {
    setConversations(prev => 
      prev.map(c => 
        c.id === conversationId 
          ? { ...c, ...updates, updatedAt: new Date() }
          : c
      )
    )
  }, [setConversations])

  const createNewConversation = useCallback(() => {
    const newThread: ConversationThread = {
      id: Date.now().toString(),
      title: 'New Conversation',
      responseId: '',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    }
    
    setConversations(prev => [newThread, ...prev])
    setActiveConversationId(newThread.id)
    setMessages([])
    setError(null)
  }, [setConversations])

  const selectConversation = useCallback((conversationId: string) => {
    const conversation = conversations.find(c => c.id === conversationId)
    if (conversation) {
      setActiveConversationId(conversationId)
      setMessages(conversation.messages)
      setError(null)
    }
  }, [conversations])

  const sendMessage = useCallback(async (content: string) => {
    let conversationToUse = getCurrentConversation()
    
    if (!activeConversationId || !conversationToUse) {
      // Create new conversation synchronously and get reference
      const newThread: ConversationThread = {
        id: Date.now().toString(),
        title: content.length > 50 ? content.substring(0, 50) + '...' : content,
        responseId: '',
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date()
      }
      
      setConversations(prev => [newThread, ...prev])
      setActiveConversationId(newThread.id)
      setMessages([])
      setError(null)
      
      conversationToUse = newThread
    }

    if (!conversationToUse) return

    setIsLoading(true)
    setError(null)

    // Cancel any existing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    abortControllerRef.current = new AbortController()

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    }

    // Add user message immediately
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    
    // Update thread title if this is the first message (only if not already set during creation)
    if (newMessages.length === 1 && conversationToUse.title === 'New Conversation') {
      const title = content.length > 50 ? content.substring(0, 50) + '...' : content
      updateConversation(conversationToUse.id, { title })
    }

    try {
      // Get the most current responseId from the conversation
      const currentConversation = getCurrentConversation() || conversationToUse
      const previousResponseId = currentConversation.responseId || null
      
      console.log('🔗 Sending message with context:', {
        conversationId: currentConversation.id,
        previousResponseId,
        messageLength: content.length
      })
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          previousResponseId
        }),
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        metadata: data.metadata
      }

      const finalMessages = [...newMessages, assistantMessage]
      setMessages(finalMessages)
      
      console.log('💾 Updating conversation with responseId:', data.responseId)
      
      // Update thread with new messages and response metadata
      updateConversation(conversationToUse.id, {
        messages: finalMessages,
        responseId: data.responseId || ''
      })

    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Request was aborted')
        return
      }
      
      console.error('Chat error:', error)
      setError(error.message || 'An error occurred while sending your message.')
    } finally {
      setIsLoading(false)
      abortControllerRef.current = null
    }
  }, [messages, activeConversationId, getCurrentConversation, updateConversation, setConversations])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  const retry = useCallback(async () => {
    if (messages.length > 0) {
      const lastUserMessage = [...messages].reverse().find(m => m.role === 'user')
      if (lastUserMessage) {
        // Remove last assistant message if it exists
        const filteredMessages = messages.filter(m => 
          m.timestamp <= lastUserMessage.timestamp
        )
        setMessages(filteredMessages)
        await sendMessage(lastUserMessage.content)
      }
    }
  }, [messages, sendMessage])

  return {
    messages,
    conversations,
    activeConversationId,
    createNewConversation,
    selectConversation,
    sendMessage,
    isLoading,
    error,
    clearMessages,
    retry
  }
}
