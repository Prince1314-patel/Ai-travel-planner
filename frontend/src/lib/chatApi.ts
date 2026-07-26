import { ApiError } from '@/lib/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export interface Interest {
  interest: string
  rating: number
}

export interface TripState {
  destination: string
  num_days: number
  travel_month: string
  total_budget: number
  interests: Interest[]
  companions: string
  child_ages: string
  pace: string
  accommodation: string
  transportation: string
  dining: string
  special_requests: string
  dietary_restrictions: string
  accessibility_needs: string
  nationality: string
}

export type ChatWidget = 'text' | 'choice' | 'interest_picker' | 'optional_wrapup' | 'done'

export interface ChatTurnResponse {
  session_id: string
  message: string
  field: string | null
  widget: ChatWidget
  options: string[] | null
  pricing_job_id: string | null
  itinerary_job_id: string | null
  state: TripState
  phase: 'collecting' | 'optional_wrapup' | 'generating'
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new ApiError(res.status, await res.text())
  return res.json() as Promise<T>
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`)
  if (!res.ok) throw new ApiError(res.status, await res.text())
  return res.json() as Promise<T>
}

export function startChat(seedText?: string): Promise<ChatTurnResponse> {
  return post('/api/chat/start', { seed_text: seedText || null })
}

export function sendChatText(sessionId: string, text: string): Promise<ChatTurnResponse> {
  return post(`/api/chat/${sessionId}/message`, { text })
}

export function sendChatChoice(
  sessionId: string,
  field: string,
  value: unknown,
): Promise<ChatTurnResponse> {
  return post(`/api/chat/${sessionId}/message`, {
    structured_field: field,
    structured_value: value,
  })
}

export function getChatSession(sessionId: string): Promise<ChatTurnResponse> {
  return get(`/api/chat/${sessionId}`)
}
