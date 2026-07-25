import { useId, type InputHTMLAttributes, type ReactNode, type TextareaHTMLAttributes } from 'react'

export const fieldBase =
  'w-full font-sans text-[15px] text-wandor-text bg-white border border-black/10 focus:outline-none focus:ring-2 focus:ring-wandor-dark focus:ring-offset-2 transition-shadow placeholder:text-[#767676]'

export function Label({ htmlFor, children }: { htmlFor: string; children: ReactNode }) {
  return (
    <label
      htmlFor={htmlFor}
      className="block font-sans text-[13px] font-semibold uppercase tracking-[0.04em] text-wandor-text mb-2"
    >
      {children}
    </label>
  )
}

export function PillInput({
  label,
  helperText,
  id,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { label: string; helperText?: string }) {
  const generatedId = useId()
  const fieldId = id ?? generatedId
  return (
    <div>
      <Label htmlFor={fieldId}>{label}</Label>
      <input id={fieldId} className={`${fieldBase} rounded-full px-5 py-3`} {...props} />
      {helperText && <p className="mt-1.5 text-[13px] text-[#5c5c5c]">{helperText}</p>}
    </div>
  )
}

export function PillTextarea({
  label,
  helperText,
  id,
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string; helperText?: string }) {
  const generatedId = useId()
  const fieldId = id ?? generatedId
  return (
    <div>
      <Label htmlFor={fieldId}>{label}</Label>
      <textarea id={fieldId} className={`${fieldBase} rounded-[24px] px-5 py-3 min-h-[88px] resize-none`} {...props} />
      {helperText && <p className="mt-1.5 text-[13px] text-[#5c5c5c]">{helperText}</p>}
    </div>
  )
}
