import type { PlanStep } from '@/lib/planContext'

const STEPS: { key: PlanStep; label: string }[] = [
  { key: 'details', label: 'Details' },
  { key: 'preferences', label: 'Preferences' },
  { key: 'results', label: 'Itinerary' },
]

export default function StepIndicator({ current }: { current: PlanStep }) {
  const currentIndex = STEPS.findIndex((s) => s.key === current)
  return (
    <div className="flex items-center justify-center gap-3 mb-10">
      {STEPS.map((step, index) => {
        const done = index < currentIndex
        const active = index === currentIndex
        return (
          <div key={step.key} className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full transition-colors ${
                  active || done ? 'bg-wandor-dark' : 'bg-black/15'
                }`}
              />
              <span
                className={`font-sans text-[13px] font-medium uppercase tracking-[0.04em] ${
                  active ? 'text-wandor-text' : 'text-[#5c5c5c]'
                }`}
              >
                {step.label}
              </span>
            </div>
            {index < STEPS.length - 1 && (
              <span className="w-8 h-px bg-black/10" />
            )}
          </div>
        )
      })}
    </div>
  )
}
