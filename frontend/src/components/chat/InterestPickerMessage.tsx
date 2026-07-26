import { useState } from 'react'
import InterestPicker from '@/components/ui/InterestPicker'
import PillButton from '@/components/ui/PillButton'
import type { Interest } from '@/lib/chatApi'

export default function InterestPickerMessage({
  disabled,
  onSubmit,
}: {
  disabled?: boolean
  onSubmit: (interests: Interest[]) => void
}) {
  const [interests, setInterests] = useState<Interest[]>([])

  return (
    <div className="self-start max-w-[85%] bg-white border border-black/[0.08] rounded-[24px] px-5 py-4 flex flex-col gap-4">
      <InterestPicker value={interests} onChange={setInterests} />
      <PillButton
        onClick={() => onSubmit(interests)}
        disabled={disabled || interests.length === 0}
        className="self-end"
      >
        Continue
      </PillButton>
    </div>
  )
}
