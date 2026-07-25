import { INTEREST_OPTIONS, type InterestRating } from '@/lib/planContext'

function DotRating({
  value,
  onChange,
}: {
  value: number
  onChange: (value: number) => void
}) {
  return (
    <div className="flex items-center gap-1.5">
      {[1, 2, 3, 4, 5].map((level) => (
        <button
          key={level}
          type="button"
          aria-label={`Importance ${level} of 5`}
          onClick={() => onChange(level)}
          className={`w-3 h-3 rounded-full border-[1.5px] bg-white transition-all active:scale-90 ${
            level <= value
              ? 'border-wandor-prompt'
              : 'border-black/15 hover:border-black/30'
          }`}
        />
      ))}
    </div>
  )
}

export default function InterestPicker({
  value,
  onChange,
}: {
  value: InterestRating[]
  onChange: (value: InterestRating[]) => void
}) {
  const isSelected = (interest: string) => value.some((v) => v.interest === interest)
  const ratingFor = (interest: string) =>
    value.find((v) => v.interest === interest)?.rating ?? 3

  const toggle = (interest: string) => {
    if (isSelected(interest)) {
      onChange(value.filter((v) => v.interest !== interest))
    } else {
      onChange([...value, { interest, rating: 3 }])
    }
  }

  const setRating = (interest: string, rating: number) => {
    onChange(value.map((v) => (v.interest === interest ? { ...v, rating } : v)))
  }

  return (
    <div>
      <span className="block font-sans text-[13px] font-semibold uppercase tracking-[0.04em] text-wandor-text mb-2">
        Interests
      </span>
      <div className="flex flex-wrap gap-2 mb-3">
        {INTEREST_OPTIONS.map((interest) => {
          const active = isSelected(interest)
          return (
            <button
              key={interest}
              type="button"
              onClick={() => toggle(interest)}
              className={`font-sans text-[14px] font-medium px-4 py-2 rounded-full border transition-all active:scale-95 ${
                active
                  ? 'bg-white text-wandor-prompt border-wandor-prompt'
                  : 'bg-white text-wandor-text border-black/10 hover:border-black/30'
              }`}
            >
              {interest}
            </button>
          )
        })}
      </div>

      {value.length === 0 ? (
        <p className="text-[13px] text-[#5c5c5c]">Pick at least one interest.</p>
      ) : (
        <div className="flex flex-col gap-2.5 pt-1">
          {value.map(({ interest }) => (
            <div key={interest} className="flex items-center justify-between gap-4">
              <span className="text-[14px] text-wandor-text">{interest}</span>
              <DotRating value={ratingFor(interest)} onChange={(r) => setRating(interest, r)} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
