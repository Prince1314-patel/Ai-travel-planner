import { useEffect, useState } from 'react'
import {
  getChatSession,
  sendChatChoice,
  sendChatText,
  startChat,
  type ChatTurnResponse,
} from '@/lib/chatApi'

export interface ChatEntry {
  role: 'user' | 'assistant'
  text: string
  response?: ChatTurnResponse
}

const SESSION_STORAGE_KEY = 'wandor_chat_session_id'

export function useChatConversation() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [entries, setEntries] = useState<ChatEntry[]>([])
  const [latest, setLatest] = useState<ChatTurnResponse | null>(null)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const stored = sessionStorage.getItem(SESSION_STORAGE_KEY)
    if (!stored) return
    getChatSession(stored)
      .then((response) => {
        setSessionId(stored)
        setLatest(response)
        setEntries([{ role: 'assistant', text: response.message, response }])
      })
      .catch(() => sessionStorage.removeItem(SESSION_STORAGE_KEY))
  }, [])

  const begin = async (seedText: string) => {
    if (sending) return
    setSending(true)
    setError(null)
    if (seedText.trim()) {
      setEntries([{ role: 'user', text: seedText.trim() }])
    }
    try {
      const response = await startChat(seedText.trim() || undefined)
      sessionStorage.setItem(SESSION_STORAGE_KEY, response.session_id)
      setSessionId(response.session_id)
      setLatest(response)
      setEntries((prev) => [...prev, { role: 'assistant', text: response.message, response }])
    } catch {
      setError('Something went wrong starting the chat. Please try again.')
    } finally {
      setSending(false)
    }
  }

  const send = async (text: string) => {
    if (!sessionId) return
    setSending(true)
    setError(null)
    setEntries((prev) => [...prev, { role: 'user', text }])
    try {
      const response = await sendChatText(sessionId, text)
      setLatest(response)
      setEntries((prev) => [...prev, { role: 'assistant', text: response.message, response }])
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setSending(false)
    }
  }

  const choose = async (field: string, value: unknown, label: string) => {
    if (!sessionId) return
    setSending(true)
    setError(null)
    setEntries((prev) => [...prev, { role: 'user', text: label }])
    try {
      const response = await sendChatChoice(sessionId, field, value)
      setLatest(response)
      setEntries((prev) => [...prev, { role: 'assistant', text: response.message, response }])
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setSending(false)
    }
  }

  const reset = () => {
    sessionStorage.removeItem(SESSION_STORAGE_KEY)
    setSessionId(null)
    setEntries([])
    setLatest(null)
  }

  return { sessionId, entries, latest, sending, error, begin, send, choose, reset }
}
