import type { ButtonHTMLAttributes, ReactNode } from 'react'

interface PillButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost'
  children: ReactNode
}

export default function PillButton({
  variant = 'primary',
  className = '',
  children,
  ...props
}: PillButtonProps) {
  const base =
    'font-sans text-[15px] font-medium uppercase tracking-[0.04em] rounded-full transition-all active:scale-95 disabled:opacity-40 disabled:pointer-events-none cursor-pointer border-none'
  const variants = {
    primary: 'bg-wandor-dark text-[#fafafa] px-6 py-3.5 hover:bg-[#333]',
    ghost:
      'bg-transparent text-wandor-text px-6 py-3.5 border border-wandor-text/20 hover:opacity-55',
  }
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  )
}
