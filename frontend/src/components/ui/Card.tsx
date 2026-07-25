import type { ReactNode } from 'react'

export default function Card({
  children,
  elevated = false,
  className = '',
}: {
  children: ReactNode
  elevated?: boolean
  className?: string
}) {
  return (
    <div
      className={`bg-white border border-black/[0.08] rounded-[44px] transition-shadow ${
        elevated ? 'shadow-[0_0_4px_0_rgba(0,0,0,0.15)]' : ''
      } ${className}`}
    >
      {children}
    </div>
  )
}
