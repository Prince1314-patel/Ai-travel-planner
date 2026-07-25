import { useId } from 'react'
import * as RadixSelect from '@radix-ui/react-select'
import { Check, ChevronDown } from 'lucide-react'
import { Label, fieldBase } from '@/components/ui/PillField'

export default function Select({
  label,
  value,
  onValueChange,
  options,
  id,
}: {
  label: string
  value: string
  onValueChange: (value: string) => void
  options: readonly string[]
  id?: string
}) {
  const generatedId = useId()
  const fieldId = id ?? generatedId

  return (
    <div>
      <Label htmlFor={fieldId}>{label}</Label>
      <RadixSelect.Root value={value} onValueChange={onValueChange}>
        <RadixSelect.Trigger
          id={fieldId}
          className={`${fieldBase} rounded-full px-5 py-3 flex items-center justify-between gap-2 data-[state=open]:ring-2 data-[state=open]:ring-wandor-dark data-[state=open]:ring-offset-2`}
        >
          <RadixSelect.Value className="truncate text-left" />
          <RadixSelect.Icon>
            <ChevronDown className="w-4 h-4 text-[#5c5c5c] shrink-0" />
          </RadixSelect.Icon>
        </RadixSelect.Trigger>

        <RadixSelect.Portal>
          <RadixSelect.Content
            position="popper"
            sideOffset={8}
            className="z-50 min-w-[var(--radix-select-trigger-width)] max-w-[320px] max-h-[300px] bg-white border border-black/10 rounded-2xl shadow-[0_0_4px_0_rgba(0,0,0,0.15)] overflow-hidden"
          >
            <RadixSelect.Viewport className="p-1.5">
              {options.map((option) => (
                <RadixSelect.Item
                  key={option}
                  value={option}
                  className="relative flex items-center justify-between gap-3 font-sans text-[15px] text-wandor-text rounded-xl px-3.5 py-2.5 cursor-pointer select-none outline-none data-[highlighted]:bg-black/[0.04] data-[state=checked]:text-wandor-prompt data-[state=checked]:font-medium"
                >
                  <RadixSelect.ItemText>{option}</RadixSelect.ItemText>
                  <RadixSelect.ItemIndicator>
                    <Check className="w-4 h-4 text-wandor-prompt shrink-0" />
                  </RadixSelect.ItemIndicator>
                </RadixSelect.Item>
              ))}
            </RadixSelect.Viewport>
          </RadixSelect.Content>
        </RadixSelect.Portal>
      </RadixSelect.Root>
    </div>
  )
}
