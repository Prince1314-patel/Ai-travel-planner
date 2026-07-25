export default function PillRadioGroup<T extends string>({
  label,
  options,
  value,
  onChange,
}: {
  label: string
  options: readonly T[]
  value: T
  onChange: (value: T) => void
}) {
  return (
    <div>
      <span className="block font-sans text-[13px] font-semibold uppercase tracking-[0.04em] text-wandor-text mb-2">
        {label}
      </span>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const active = option === value
          return (
            <button
              key={option}
              type="button"
              onClick={() => onChange(option)}
              className={`font-sans text-[14px] font-medium px-4 py-2 rounded-full border transition-all active:scale-95 ${
                active
                  ? 'bg-wandor-dark text-[#fafafa] border-wandor-dark'
                  : 'bg-white text-wandor-text border-black/10 hover:border-black/30'
              }`}
            >
              {option}
            </button>
          )
        })}
      </div>
    </div>
  )
}
