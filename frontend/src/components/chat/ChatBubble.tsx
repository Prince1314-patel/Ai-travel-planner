import type { ReactNode } from 'react'

export default function ChatBubble({
  role,
  children,
}: {
  role: 'user' | 'assistant'
  children: ReactNode
}) {
  const alignment = role === 'user' ? 'self-end text-wandor-prompt' : 'self-start text-wandor-text'
  return (
    <div
      className={`max-w-[80%] font-sans text-[16px] font-medium bg-white border border-black/[0.08] rounded-[24px] px-5 py-3 ${alignment}`}
    >
      {children}
    </div>
  )
}
