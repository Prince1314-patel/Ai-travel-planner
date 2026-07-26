export default function QuickReplyGroup({
  options,
  onSelect,
  disabled = false,
}: {
  options: string[]
  onSelect: (value: string) => void
  disabled?: boolean
}) {
  return (
    <div className="flex flex-wrap gap-2 self-start">
      {options.map((option) => (
        <button
          key={option}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(option)}
          className="font-sans text-[14px] font-medium px-4 py-2 rounded-full border border-black/10 bg-white text-wandor-text transition-all active:scale-95 hover:border-black/30 disabled:opacity-40 disabled:pointer-events-none"
        >
          {option}
        </button>
      ))}
    </div>
  )
}
