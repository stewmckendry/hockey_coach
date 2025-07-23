'use client'

import { useState, useEffect } from 'react'
import type { UseLocalStorageReturn } from '@/lib/types'
import { storage } from '@/lib/utils'

/**
 * Custom hook for managing localStorage with React state
 */
export function useLocalStorage<T>(key: string, defaultValue: T): UseLocalStorageReturn<T> {
  const [value, setValue] = useState<T>(() => {
    return storage.get(key, defaultValue)
  })

  const setStoredValue = (newValue: T | ((prev: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue
      setValue(valueToStore)
      storage.set(key, valueToStore)
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error)
    }
  }

  const removeValue = () => {
    try {
      setValue(defaultValue)
      storage.remove(key)
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error)
    }
  }

  // Sync with localStorage on mount and when key changes
  useEffect(() => {
    const storedValue = storage.get(key, defaultValue)
    if (JSON.stringify(storedValue) !== JSON.stringify(value)) {
      setValue(storedValue)
    }
  }, [key, defaultValue])

  // Listen for storage events (changes from other tabs)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        try {
          const newValue = JSON.parse(e.newValue)
          setValue(newValue)
        } catch (error) {
          console.warn(`Error parsing localStorage value for key "${key}":`, error)
        }
      }
    }

    if (typeof window !== 'undefined') {
      window.addEventListener('storage', handleStorageChange)
      return () => window.removeEventListener('storage', handleStorageChange)
    }
  }, [key])

  return {
    value,
    setValue: setStoredValue,
    removeValue
  }
}

/**
 * Hook for persisting chat messages in localStorage
 */
export function useChatPersistence() {
  const { value: messages, setValue: setMessages } = useLocalStorage('hockey-chat-messages', [])
  const { value: settings, setValue: setSettings } = useLocalStorage('hockey-chat-settings', {
    autoSave: true,
    maxMessages: 50
  })

  const addMessage = (message: any) => {
    setMessages((prev: any[]) => {
      const newMessages = [...prev, message]
      // Keep only the most recent messages based on settings
      return newMessages.slice(-settings.maxMessages)
    })
  }

  const clearMessages = () => {
    setMessages([])
  }

  const updateSettings = (newSettings: any) => {
    setSettings({ ...settings, ...newSettings })
  }

  return {
    messages,
    settings,
    addMessage,
    clearMessages,
    updateSettings,
    setMessages
  }
}
