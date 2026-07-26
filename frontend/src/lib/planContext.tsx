import { createContext, useContext, useState, type ReactNode } from 'react'
import type { CostEstimates } from '@/lib/api'

export type PlanStep = 'details' | 'preferences' | 'results'

export interface InterestRating {
  interest: string
  rating: number
}

export interface PlanState {
  step: PlanStep
  destination: string
  numDays: number
  travelMonth: string
  totalBudget: number
  costEstimates: CostEstimates | null
  interests: InterestRating[]
  companions: 'Solo' | 'Couple' | 'Family' | 'Group'
  childAges: string
  accommodation: string
  transportation: string
  dining: string
  pace: 'Relaxed' | 'Moderate' | 'Packed'
  specialRequests: string
  dietaryRestrictions: string
  accessibilityNeeds: string
  nationality: string
  itinerary: string
}

const defaultState: PlanState = {
  step: 'details',
  destination: '',
  numDays: 5,
  travelMonth: 'January',
  totalBudget: 50000,
  costEstimates: null,
  interests: [],
  companions: 'Solo',
  childAges: '',
  accommodation: '',
  transportation: '',
  dining: '',
  pace: 'Moderate',
  specialRequests: '',
  dietaryRestrictions: '',
  accessibilityNeeds: '',
  nationality: 'Indian',
  itinerary: '',
}

interface PlanContextValue {
  plan: PlanState
  update: (patch: Partial<PlanState>) => void
}

const PlanContext = createContext<PlanContextValue | null>(null)

export function PlanProvider({ children }: { children: ReactNode }) {
  const [plan, setPlan] = useState<PlanState>(defaultState)
  const update = (patch: Partial<PlanState>) =>
    setPlan((prev) => ({ ...prev, ...patch }))
  return (
    <PlanContext.Provider value={{ plan, update }}>
      {children}
    </PlanContext.Provider>
  )
}

export function usePlan() {
  const ctx = useContext(PlanContext)
  if (!ctx) throw new Error('usePlan must be used within a PlanProvider')
  return ctx
}

export const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

export const FALLBACK_ACCOMMODATION = ['Hotel', 'Hostel', 'Vacation rental', 'Boutique hotel', 'Eco-lodge']
export const FALLBACK_TRANSPORTATION = ['Taxi', 'Public transit', 'Car rental']
export const FALLBACK_DINING = ['Street food', 'Casual dining', 'Fine dining', 'Local cuisine', 'International cuisine']

export const PACE_OPTIONS = ['Relaxed', 'Moderate', 'Packed'] as const

export const PACE_DEFINITIONS: Record<(typeof PACE_OPTIONS)[number], string> = {
  Relaxed: 'a leisurely pace with ample downtime',
  Moderate: 'a balanced pace with a mix of activities and rest',
  Packed: 'a fast-paced schedule with many activities',
}
