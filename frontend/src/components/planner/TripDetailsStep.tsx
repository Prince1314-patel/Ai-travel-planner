import { useState } from 'react'
import Card from '@/components/ui/Card'
import PillButton from '@/components/ui/PillButton'
import { PillInput } from '@/components/ui/PillField'
import Select from '@/components/ui/Select'
import ProgressBar from '@/components/ui/ProgressBar'
import { MONTHS, usePlan } from '@/lib/planContext'
import { pollCostEstimate, ApiError, type CostEstimateProgress, type CostEstimates } from '@/lib/api'

function formatCategory(estimates: CostEstimates[keyof CostEstimates]) {
  return Object.entries(estimates).map(([key, value]) => ({
    key,
    label: key.charAt(0).toUpperCase() + key.slice(1),
    range: `₹${value.cost.min}–₹${value.cost.max} ${value.unit}`,
  }))
}

function progressLabel(progress: CostEstimateProgress, destination: string) {
  if (progress.status === 'searching') {
    return `Finding real prices for ${destination} — ${progress.resolved} of ${progress.total} sources checked`
  }
  return progress.generated_chars > 0
    ? `Compiling your personalized estimate — ${progress.generated_chars} characters written`
    : 'Compiling your personalized estimate…'
}

// The LLM doesn't know its own final response length in advance, so this can't
// be a true 0-100%. Cap short of full so the bar never falsely claims "done"
// before the stream actually ends — it only reaches 100% on real completion.
const EXPECTED_RESPONSE_CHARS = 1200
function generationPercent(generatedChars: number) {
  return Math.min(96, Math.round((generatedChars / EXPECTED_RESPONSE_CHARS) * 100))
}

export default function TripDetailsStep() {
  const { plan, update } = usePlan()
  const [progress, setProgress] = useState<CostEstimateProgress | null>(null)
  const [error, setError] = useState<string | null>(null)

  const loading = progress !== null && progress.status !== 'done' && progress.status !== 'error'
  const canSubmit =
    plan.destination.trim().length > 0 && plan.numDays >= 1 && plan.totalBudget > 0

  const handleGetEstimate = async () => {
    setError(null)
    setProgress({
      status: 'searching',
      resolved: 0,
      total: 13,
      generated_chars: 0,
      result: null,
      error: null,
    })
    try {
      const estimates = await pollCostEstimate(
        {
          destination: plan.destination,
          num_days: plan.numDays,
          travel_month: plan.travelMonth,
          total_budget: plan.totalBudget,
        },
        setProgress,
      )
      update({ costEstimates: estimates })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.')
    } finally {
      setProgress(null)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <Card elevated={!plan.costEstimates} className="px-8 py-9 max-md:px-6">
        <h2 className="font-sans text-2xl font-semibold text-wandor-text mb-1">Trip details</h2>
        <p className="text-[15px] text-[#5c5c5c] mb-6">
          Tell us where and when — we'll estimate what it costs before you plan a thing.
        </p>

        <div className="grid grid-cols-2 gap-5 max-md:grid-cols-1">
          <div className="col-span-2 max-md:col-span-1">
            <PillInput
              label="Destination"
              placeholder="e.g., Paris, France"
              value={plan.destination}
              onChange={(e) => update({ destination: e.target.value })}
            />
          </div>
          <PillInput
            label="Number of days"
            type="number"
            min={1}
            value={plan.numDays}
            onChange={(e) => update({ numDays: Number(e.target.value) })}
          />
          <Select
            label="Travel month"
            value={plan.travelMonth}
            onValueChange={(travelMonth) => update({ travelMonth })}
            options={MONTHS}
          />
          <div className="col-span-2 max-md:col-span-1">
            <PillInput
              label="Total budget (INR)"
              type="number"
              min={0}
              step={500}
              value={plan.totalBudget}
              onChange={(e) => update({ totalBudget: Number(e.target.value) })}
              helperText="All costs are estimated in INR."
            />
          </div>
        </div>

        {loading && progress && (
          <div className="mt-6">
            <ProgressBar
              value={
                progress.status === 'generating'
                  ? generationPercent(progress.generated_chars)
                  : progress.resolved
              }
              max={progress.status === 'generating' ? 100 : progress.total}
            />
            <p className="mt-2.5 text-[13px] text-[#5c5c5c]">
              {progressLabel(progress, plan.destination)}
            </p>
          </div>
        )}

        {error && (
          <p className="mt-5 text-[14px] text-red-700 bg-red-50 border border-red-200 rounded-2xl px-4 py-3">
            {error}
          </p>
        )}

        <div className="mt-7 flex justify-end">
          <PillButton onClick={handleGetEstimate} disabled={!canSubmit || loading}>
            {loading ? 'Fetching real prices…' : 'Get cost estimate'}
          </PillButton>
        </div>
      </Card>

      {plan.costEstimates && (
        <Card elevated className="px-8 py-9 max-md:px-6">
          <h3 className="font-sans text-lg font-semibold text-wandor-text mb-4">
            Estimated costs for {plan.destination}
          </h3>
          <div className="grid grid-cols-3 gap-4 max-md:grid-cols-1">
            {(['accommodation', 'dining', 'transportation'] as const).map((category) => (
              <div key={category}>
                <p className="font-sans text-[13px] font-semibold uppercase tracking-[0.04em] text-[#5c5c5c] mb-2">
                  {category}
                </p>
                <ul className="flex flex-col gap-1.5">
                  {formatCategory(plan.costEstimates![category]).map((item) => (
                    <li key={item.key} className="text-[14px] text-wandor-text">
                      <span className="text-[#5c5c5c]">{item.label}: </span>
                      {item.range}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="mt-7 flex justify-end">
            <PillButton onClick={() => update({ step: 'preferences' })}>
              Continue to preferences
            </PillButton>
          </div>
        </Card>
      )}
    </div>
  )
}
