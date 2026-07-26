import { useEffect, useRef, type ReactNode } from 'react'

export default function ChatThread({ children }: { children: ReactNode }) {
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  })

  return (
    <div className="flex flex-col gap-4 max-w-[720px] mx-auto px-6 pb-40 pt-6">
      {children}
      <div ref={endRef} />
    </div>
  )
}
