const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function parseErrorDetail(res: Response): Promise<string> {
  const messages: Record<number, string> = {
    401: 'Authentication failed. Please check your API key.',
    404: 'API endpoint not found. Verify the URL.',
  }
  const known = messages[res.status]
  if (known) return known
  try {
    const data = await res.json()
    return data?.detail || data?.error || `Request failed (${res.status})`
  } catch {
    return `Request failed (${res.status})`
  }
}

async function request<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new ApiError(res.status, await parseErrorDetail(res))
  return res.json() as Promise<T>
}

async function requestGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`)
  if (!res.ok) throw new ApiError(res.status, await parseErrorDetail(res))
  return res.json() as Promise<T>
}

export interface CostRange {
  cost: { min: number; max: number }
  unit: string
}

export interface CostEstimates {
  accommodation: Record<string, CostRange>
  dining: Record<string, CostRange>
  transportation: Record<string, CostRange>
}

export interface CostEstimateProgress {
  status: 'searching' | 'generating' | 'done' | 'error'
  resolved: number
  total: number
  generated_chars: number
  result: CostEstimates | null
  error: string | null
}

export interface CostEstimateParams {
  destination: string
  num_days: number
  travel_month: string
  total_budget: number
}

/**
 * Starts a cost-estimate job (13 parallel real-price searches + one LLM call
 * on the backend, often 20s-130s+) and polls its real progress until it
 * resolves. `onProgress` fires on every poll tick so the UI can show genuine
 * "N of 13 prices found" status — the wait is too long and too variable for a
 * simulated/fake progress bar to stay honest.
 */
export async function pollCostEstimate(
  params: CostEstimateParams,
  onProgress: (progress: CostEstimateProgress) => void,
  pollIntervalMs = 900,
): Promise<CostEstimates> {
  const { job_id } = await request<{ job_id: string }>('/api/cost-estimate/start', params)

  // eslint-disable-next-line no-constant-condition
  while (true) {
    const progress = await requestGet<CostEstimateProgress>(`/api/cost-estimate/status/${job_id}`)
    onProgress(progress)

    if (progress.status === 'done' && progress.result) {
      return progress.result
    }
    if (progress.status === 'error') {
      throw new ApiError(502, progress.error ?? 'Cost estimate failed.')
    }
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs))
  }
}

export interface ItineraryRequest {
  destination: string
  num_days: number
  total_budget: number
  travel_month: string
  companions: string
  child_ages: string | null
  interests_str: string
  accommodation: string
  transportation: string
  dining: string
  pace: string
  special_requests: string
  dietary_restrictions: string
  accessibility_needs: string
  nationality: string
}

export interface ItineraryProgress {
  status: 'generating' | 'done' | 'error'
  generated_chars: number
  result: { itinerary: string } | null
  error: string | null
}

/**
 * Starts an itinerary-generation job (a single, often 10s-100s+ LLM call whose
 * length scales with the number of days requested) and polls its real progress
 * until it resolves. `onProgress` fires on every poll tick with the real
 * character count streamed so far — the wait is too long and variable for a
 * simulated/fake progress bar to stay honest.
 */
export async function pollItinerary(
  params: ItineraryRequest,
  onProgress: (progress: ItineraryProgress) => void,
  pollIntervalMs = 900,
): Promise<{ itinerary: string }> {
  const { job_id } = await request<{ job_id: string }>('/api/itinerary/start', params)

  // eslint-disable-next-line no-constant-condition
  while (true) {
    const progress = await requestGet<ItineraryProgress>(`/api/itinerary/status/${job_id}`)
    onProgress(progress)

    if (progress.status === 'done' && progress.result) {
      return progress.result
    }
    if (progress.status === 'error') {
      throw new ApiError(502, progress.error ?? 'Itinerary generation failed.')
    }
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs))
  }
}

export async function fetchItineraryPdf(itinerary_markdown: string): Promise<Blob> {
  const res = await fetch(`${API_BASE_URL}/api/itinerary/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ itinerary_markdown }),
  })
  if (!res.ok) throw new ApiError(res.status, 'Failed to generate PDF.')
  return res.blob()
}
