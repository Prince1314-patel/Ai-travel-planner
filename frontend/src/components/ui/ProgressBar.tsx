export default function ProgressBar({
  value,
  max,
  indeterminate = false,
}: {
  value: number
  max: number
  indeterminate?: boolean
}) {
  const percent = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0

  return (
    <div
      role="progressbar"
      aria-valuenow={indeterminate ? undefined : value}
      aria-valuemin={0}
      aria-valuemax={max}
      className="w-full h-2 rounded-full bg-black/[0.06] overflow-hidden"
    >
      <div
        className={`h-full rounded-full bg-wandor-dark transition-[width] duration-500 ease-out ${
          indeterminate ? 'animate-pulse' : ''
        }`}
        style={{ width: `${indeterminate ? 100 : percent}%` }}
      />
    </div>
  )
}
