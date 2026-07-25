import { useEffect, useState } from 'react'
import Card from '@/components/ui/Card'
import PillButton from '@/components/ui/PillButton'
import { PillInput, PillTextarea } from '@/components/ui/PillField'
import Select from '@/components/ui/Select'
import PillRadioGroup from '@/components/ui/PillRadioGroup'
import InterestPicker from '@/components/ui/InterestPicker'
import ProgressBar from '@/components/ui/ProgressBar'
import {
  usePlan,
  FALLBACK_ACCOMMODATION,
  FALLBACK_TRANSPORTATION,
  FALLBACK_DINING,
  PACE_OPTIONS,
} from '@/lib/planContext'
import { pollItinerary, ApiError, type CostEstimates, type ItineraryProgress } from '@/lib/api'

const COMPANION_OPTIONS = ['Solo', 'Couple', 'Family', 'Group'] as const

// Output length scales with the number of days requested (each day gets its
// own morning/afternoon/evening breakdown), so the expected total scales too.
// The LLM doesn't know its own final length in advance, so this can't be a
// true 0-100% — capped short of full so the bar never claims "done" before
// the stream actually ends.
const CHARS_PER_DAY = 900
const BASE_OVERHEAD_CHARS = 600
function generationPercent(generatedChars: number, numDays: number) {
  const expected = numDays * CHARS_PER_DAY + BASE_OVERHEAD_CHARS
  return Math.min(96, Math.round((generatedChars / expected) * 100))
}

function dynamicOptions(
  estimates: CostEstimates | null,
  category: 'accommodation' | 'dining' | 'transportation',
  fallback: string[],
) {
  const source = estimates?.[category]
  if (!source) return fallback
  return Object.entries(source).map(([key, value]) => {
    const label = key.charAt(0).toUpperCase() + key.slice(1)
    return `${label} - ₹${value.cost.min} to ₹${value.cost.max} ${value.unit}`
  })
}

export default function PreferencesStep() {
  const { plan, update } = usePlan()
  const [progress, setProgress] = useState<ItineraryProgress | null>(null)
  const [error, setError] = useState<string | null>(null)
  const loading = progress !== null && progress.status !== 'done' && progress.status !== 'error'

  const accommodationOptions = dynamicOptions(plan.costEstimates, 'accommodation', FALLBACK_ACCOMMODATION)
  const transportationOptions = dynamicOptions(plan.costEstimates, 'transportation', FALLBACK_TRANSPORTATION)
  const diningOptions = dynamicOptions(plan.costEstimates, 'dining', FALLBACK_DINING)

  useEffect(() => {
    if (!plan.accommodation && accommodationOptions.length) {
      update({ accommodation: accommodationOptions[0] })
    }
    if (!plan.transportation && transportationOptions.length) {
      update({ transportation: transportationOptions[0] })
    }
    if (!plan.dining && diningOptions.length) {
      update({ dining: diningOptions[0] })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const canSubmit = plan.interests.length > 0

  const handleGenerate = async () => {
    setError(null)
    setProgress({ status: 'generating', generated_chars: 0, result: null, error: null })
    try {
      const interestsStr = plan.interests
        .map((i) => `${i.interest} (rated ${i.rating}/5)`)
        .join(', ')
      const normalize = (value: string) => value.split(' -')[0]

      const { itinerary } = await pollItinerary(
        {
          destination: plan.destination,
          num_days: plan.numDays,
          total_budget: plan.totalBudget,
          travel_month: plan.travelMonth,
          companions: plan.companions,
          child_ages: plan.companions === 'Family' && plan.childAges ? plan.childAges : null,
          interests_str: interestsStr,
          accommodation: normalize(plan.accommodation),
          transportation: normalize(plan.transportation),
          dining: normalize(plan.dining),
          pace: plan.pace,
          special_requests: plan.specialRequests,
          dietary_restrictions: plan.dietaryRestrictions,
          accessibility_needs: plan.accessibilityNeeds,
          nationality: plan.nationality,
        },
        setProgress,
      )
      update({ itinerary, step: 'results' })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.')
    } finally {
      setProgress(null)
    }
  }

  return (
    <Card elevated className="px-8 py-9 max-md:px-6">
      <h2 className="font-sans text-2xl font-semibold text-wandor-text mb-1">Preferences</h2>
      <p className="text-[15px] text-[#5c5c5c] mb-7">
        The more you tell us, the less this itinerary reads like a template.
      </p>

      <div className="flex flex-col gap-7">
        <InterestPicker value={plan.interests} onChange={(interests) => update({ interests })} />

        <div>
          <PillRadioGroup
            label="Travel companions"
            options={COMPANION_OPTIONS}
            value={plan.companions}
            onChange={(companions) => update({ companions })}
          />
          {plan.companions === 'Family' && (
            <div className="mt-3">
              <PillInput
                label="Children's ages"
                placeholder="e.g., 5, 8, 12"
                value={plan.childAges}
                onChange={(e) => update({ childAges: e.target.value })}
              />
            </div>
          )}
        </div>

        <div className="grid grid-cols-3 gap-5 max-md:grid-cols-1">
          <Select
            label="Accommodation"
            value={plan.accommodation}
            onValueChange={(accommodation) => update({ accommodation })}
            options={accommodationOptions}
          />
          <Select
            label="Transportation"
            value={plan.transportation}
            onValueChange={(transportation) => update({ transportation })}
            options={transportationOptions}
          />
          <Select
            label="Dining"
            value={plan.dining}
            onValueChange={(dining) => update({ dining })}
            options={diningOptions}
          />
        </div>

        <PillRadioGroup
          label="Pace of travel"
          options={PACE_OPTIONS}
          value={plan.pace}
          onChange={(pace) => update({ pace })}
        />

        <PillTextarea
          label="Special requests or notes"
          placeholder="e.g., 'I prefer vegetarian options' or 'Need quiet areas'"
          value={plan.specialRequests}
          onChange={(e) => update({ specialRequests: e.target.value })}
        />

        <div className="grid grid-cols-3 gap-5 max-md:grid-cols-1">
          <PillInput
            label="Dietary restrictions"
            placeholder="e.g., vegetarian"
            value={plan.dietaryRestrictions}
            onChange={(e) => update({ dietaryRestrictions: e.target.value })}
          />
          <PillInput
            label="Accessibility needs"
            placeholder="e.g., wheelchair access"
            value={plan.accessibilityNeeds}
            onChange={(e) => update({ accessibilityNeeds: e.target.value })}
          />
          <PillInput
            label="Nationality"
            helperText="For visa considerations"
            value={plan.nationality}
            onChange={(e) => update({ nationality: e.target.value })}
          />
        </div>
      </div>

      {!canSubmit && (
        <p className="mt-6 text-[13px] text-[#5c5c5c]">Select at least one interest to continue.</p>
      )}
      {loading && progress && (
        <div className="mt-6">
          <ProgressBar value={generationPercent(progress.generated_chars, plan.numDays)} max={100} />
          <p className="mt-2.5 text-[13px] text-[#5c5c5c]">
            {progress.generated_chars > 0
              ? `Writing your ${plan.numDays}-day itinerary — ${progress.generated_chars.toLocaleString()} characters written`
              : 'Writing your itinerary…'}
          </p>
        </div>
      )}
      {error && (
        <p className="mt-5 text-[14px] text-red-700 bg-red-50 border border-red-200 rounded-2xl px-4 py-3">
          {error}
        </p>
      )}

      <div className="mt-8 flex justify-between items-center">
        <button
          type="button"
          onClick={() => update({ step: 'details' })}
          className="font-sans text-[14px] text-[#5c5c5c] hover:opacity-70 transition-opacity"
        >
          ← Back to trip details
        </button>
        <PillButton onClick={handleGenerate} disabled={!canSubmit || loading}>
          {loading ? 'Generating itinerary…' : 'Generate itinerary'}
        </PillButton>
      </div>
    </Card>
  )
}
