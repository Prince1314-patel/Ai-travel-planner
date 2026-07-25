import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ChevronDown, Download } from 'lucide-react'
import Card from '@/components/ui/Card'
import PillButton from '@/components/ui/PillButton'
import { usePlan } from '@/lib/planContext'
import { fetchItineraryPdf, ApiError } from '@/lib/api'

interface DaySection {
  title: string
  body: string
}

function splitIntoDays(markdown: string): { intro: string; days: DaySection[] } {
  const dayHeaderRegex = /^###\s*Day\s+(\d+)\s*:?\s*(.*)$/gim
  const matches = [...markdown.matchAll(dayHeaderRegex)]
  if (matches.length === 0) {
    return { intro: markdown, days: [] }
  }
  const intro = markdown.slice(0, matches[0].index).trim()
  const days = matches.map((match, i) => {
    const start = match.index! + match[0].length
    const end = i + 1 < matches.length ? matches[i + 1].index! : markdown.length
    const label = match[2]?.trim()
    return {
      title: `Day ${match[1]}${label ? `: ${label}` : ''}`,
      body: markdown.slice(start, end).trim(),
    }
  })
  return { intro, days }
}

function DayCard({ day, defaultOpen }: { day: DaySection; defaultOpen: boolean }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <Card elevated={open} className="overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-7 py-5 text-left"
      >
        <span className="font-sans text-lg font-semibold text-wandor-text">{day.title}</span>
        <ChevronDown
          className={`w-5 h-5 text-[#5c5c5c] transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </button>
      {open && (
        <div className="px-7 pb-7 prose prose-wandor prose-sm max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{day.body}</ReactMarkdown>
        </div>
      )}
    </Card>
  )
}

export default function ResultsStep() {
  const { plan, update } = usePlan()
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { intro, days } = splitIntoDays(plan.itinerary)

  const handleDownload = async () => {
    setError(null)
    setDownloading(true)
    try {
      const blob = await fetchItineraryPdf(plan.itinerary)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'itinerary.pdf'
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not generate the PDF. Please try again.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between max-md:flex-col max-md:items-start max-md:gap-4">
        <div>
          <h2 className="font-sans text-2xl font-semibold text-wandor-text">
            Your itinerary for {plan.destination}
          </h2>
          <p className="text-[15px] text-[#5c5c5c]">
            {plan.numDays} days · {plan.travelMonth} · ₹{plan.totalBudget.toLocaleString('en-IN')} budget
          </p>
        </div>
        <PillButton onClick={handleDownload} disabled={downloading}>
          <span className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            {downloading ? 'Preparing PDF…' : 'Download PDF'}
          </span>
        </PillButton>
      </div>

      {error && (
        <p className="text-[14px] text-red-700 bg-red-50 border border-red-200 rounded-2xl px-4 py-3">
          {error}
        </p>
      )}

      {intro && (
        <Card className="px-7 py-6 prose prose-wandor prose-sm max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{intro}</ReactMarkdown>
        </Card>
      )}

      <div className="flex flex-col gap-4">
        {days.map((day, i) => (
          <DayCard key={day.title} day={day} defaultOpen={i === 0} />
        ))}
      </div>

      <p className="text-[13px] text-[#5c5c5c] bg-black/[0.03] border border-wandor-prompt/30 rounded-2xl px-5 py-4">
        The generated itinerary is based on AI suggestions and may not reflect
        real-time availability or accuracy. Please verify details before booking.
      </p>

      <button
        type="button"
        onClick={() => update({ step: 'details', itinerary: '' })}
        className="self-center font-sans text-[14px] text-[#5c5c5c] hover:opacity-70 transition-opacity mt-2"
      >
        Plan another trip
      </button>
    </div>
  )
}
