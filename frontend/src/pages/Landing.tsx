import { useState } from 'react'
import Hero from '@/components/Hero'
import ChatThread from '@/components/chat/ChatThread'
import ChatBubble from '@/components/chat/ChatBubble'
import QuickReplyGroup from '@/components/chat/QuickReplyGroup'
import InterestPickerMessage from '@/components/chat/InterestPickerMessage'
import PricingProgressBubble from '@/components/chat/PricingProgressBubble'
import OptionalWrapupBubble from '@/components/chat/OptionalWrapupBubble'
import ItineraryBubble from '@/components/chat/ItineraryBubble'
import type { CostEstimates } from '@/lib/api'
import { useChatConversation } from '@/lib/useChatConversation'

export default function Landing() {
  const { sessionId, entries, latest, sending, error, begin, send, choose, reset } = useChatConversation()
  const [draft, setDraft] = useState('')
  const [costEstimates, setCostEstimates] = useState<CostEstimates | null>(null)
  const started = sessionId !== null

  const handleSend = () => {
    if (!draft.trim()) return
    send(draft.trim())
    setDraft('')
  }

  if (!started) {
    return <Hero onSubmit={begin} disabled={sending} />
  }

  return (
    <div className="relative min-h-svh w-full bg-white">
      <header className="max-w-[720px] mx-auto px-6 pt-6">
        <span className="font-display text-[32px] text-black leading-none select-none">wandor</span>
      </header>

      <ChatThread>
        {entries.map((entry, i) => (
          <ChatBubble key={i} role={entry.role}>
            {entry.text}
          </ChatBubble>
        ))}
        {latest?.widget === 'choice' && latest.options && (
          <QuickReplyGroup
            options={latest.options}
            disabled={sending}
            onSelect={(value) => choose(latest.field!, value, value)}
          />
        )}
        {latest?.widget === 'interest_picker' && (
          <InterestPickerMessage
            disabled={sending}
            onSubmit={(interests) => choose('interests', interests, `${interests.length} interests selected`)}
          />
        )}
        {latest?.pricing_job_id && (
          <PricingProgressBubble
            jobId={latest.pricing_job_id}
            destination={latest.state.destination}
            onResolved={setCostEstimates}
          />
        )}
        {latest?.widget === 'optional_wrapup' && (
          <OptionalWrapupBubble
            costEstimates={costEstimates}
            disabled={sending}
            onSubmit={(values) => choose('wrapup_submit', values, 'Generate my itinerary')}
          />
        )}
        {latest?.widget === 'done' && latest.itinerary_job_id && (
          <ItineraryBubble
            jobId={latest.itinerary_job_id}
            destination={latest.state.destination}
            numDays={latest.state.num_days}
            travelMonth={latest.state.travel_month}
            totalBudget={latest.state.total_budget}
            onReset={reset}
          />
        )}
        {error && <p className="text-[14px] text-red-700">{error}</p>}
      </ChatThread>

      {latest?.widget !== 'done' && (
        <div className="fixed bottom-0 inset-x-0 bg-white/90 backdrop-blur-sm border-t border-black/[0.08] px-6 py-4">
          <div className="max-w-[720px] mx-auto flex gap-3">
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type your answer..."
              disabled={sending}
              className="flex-1 font-sans text-[15px] text-wandor-text bg-white border border-black/10 rounded-full px-5 py-3 focus:outline-none focus:ring-2 focus:ring-wandor-dark focus:ring-offset-2"
            />
            <button
              type="button"
              onClick={handleSend}
              disabled={sending || !draft.trim()}
              className="bg-wandor-dark text-[#fafafa] rounded-full px-6 py-3 font-sans text-[15px] font-medium uppercase tracking-[0.04em] transition-all hover:bg-[#333] active:scale-95 disabled:opacity-40"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
