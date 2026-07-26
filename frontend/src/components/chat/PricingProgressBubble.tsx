import { useEffect, useState } from 'react'
import ProgressBar from '@/components/ui/ProgressBar'
import { pollCostEstimateByJobId, type CostEstimateProgress, type CostEstimates } from '@/lib/api'

export default function PricingProgressBubble({
  jobId,
  destination,
  onResolved,
}: {
  jobId: string
  destination: string
  onResolved: (estimates: CostEstimates) => void
}) {
  const [progress, setProgress] = useState<CostEstimateProgress | null>(null)

  useEffect(() => {
    let cancelled = false
    pollCostEstimateByJobId(jobId, (p) => {
      if (!cancelled) setProgress(p)
    })
      .then((estimates) => {
        if (!cancelled) onResolved(estimates)
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId])

  if (!progress || progress.status === 'done') return null

  return (
    <div className="self-start max-w-[85%] bg-white border border-black/[0.08] rounded-[24px] px-5 py-4">
      <ProgressBar
        value={progress.status === 'searching' ? progress.resolved : 90}
        max={progress.status === 'searching' ? progress.total : 100}
      />
      <p className="mt-2.5 text-[13px] text-[#5c5c5c]">
        {progress.status === 'searching'
          ? `Finding real prices for ${destination} — ${progress.resolved} of ${progress.total} sources checked`
          : 'Compiling your personalized estimate…'}
      </p>
    </div>
  )
}
