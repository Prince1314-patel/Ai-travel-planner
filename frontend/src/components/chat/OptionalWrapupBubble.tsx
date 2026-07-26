import { useState } from 'react'
import PillRadioGroup from '@/components/ui/PillRadioGroup'
import { PillTextarea } from '@/components/ui/PillField'
import PillButton from '@/components/ui/PillButton'
import type { CostEstimates } from '@/lib/api'

const FALLBACK_ACCOMMODATION = ['Hotel', 'Hostel', 'Vacation rental', 'Boutique hotel', 'Eco-lodge']
const FALLBACK_TRANSPORTATION = ['Taxi', 'Public transit', 'Car rental']
const FALLBACK_DINING = ['Street food', 'Casual dining', 'Fine dining', 'Local cuisine', 'International cuisine']

function optionsFor(
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

export default function OptionalWrapupBubble({
  costEstimates,
  disabled,
  onSubmit,
}: {
  costEstimates: CostEstimates | null
  disabled?: boolean
  onSubmit: (values: Record<string, string>) => void
}) {
  const accommodationOptions = optionsFor(costEstimates, 'accommodation', FALLBACK_ACCOMMODATION)
  const transportationOptions = optionsFor(costEstimates, 'transportation', FALLBACK_TRANSPORTATION)
  const diningOptions = optionsFor(costEstimates, 'dining', FALLBACK_DINING)

  const [accommodation, setAccommodation] = useState(accommodationOptions[0])
  const [transportation, setTransportation] = useState(transportationOptions[0])
  const [dining, setDining] = useState(diningOptions[0])
  const [notes, setNotes] = useState('')

  const normalize = (value: string) => value.split(' -')[0]

  return (
    <div className="self-start max-w-[90%] bg-white border border-black/[0.08] rounded-[24px] px-5 py-5 flex flex-col gap-5">
      <PillRadioGroup label="Accommodation" options={accommodationOptions} value={accommodation} onChange={setAccommodation} />
      <PillRadioGroup label="Transportation" options={transportationOptions} value={transportation} onChange={setTransportation} />
      <PillRadioGroup label="Dining" options={diningOptions} value={dining} onChange={setDining} />
      <PillTextarea
        label="Anything else? (dietary, accessibility, special requests, nationality)"
        placeholder="e.g., vegetarian, wheelchair access, Indian passport"
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
      />
      <PillButton
        disabled={disabled}
        onClick={() =>
          onSubmit({
            accommodation: normalize(accommodation),
            transportation: normalize(transportation),
            dining: normalize(dining),
            special_requests: notes,
          })
        }
        className="self-end"
      >
        Generate my itinerary
      </PillButton>
    </div>
  )
}
