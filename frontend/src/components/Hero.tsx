/**
 * THESIS: A single glass card over ambient video replaces the category's static
 * "search bar hero" — the product's mechanism (describe your trip, get a plan) is
 * shown, not a form waiting to be filled in.
 * OWN-WORLD: near-black Geist type over white-into-video, one terracotta (#905831)
 * accent reserved for the example prompt text, black pill CTAs, Special Elite
 * confined to the "wandor" wordmark.
 * STORY: visitor sees a real, moving travel scene, reads "Where will you go next?",
 * sees exactly what kind of thing to type, and presses one pill to start planning.
 * FIRST VIEWPORT: full-bleed looping video, white-to-transparent top fade for nav/
 * headline legibility, centered headline + subtitle, one glass prompt card with the
 * CTA bottom-right.
 * FORM: user-pinned brief, executed literally (no concept-seed roll) — this hero is
 * the given landing world; the rest of the product extends it per DESIGN.md.
 */
import { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload } from 'lucide-react'

function NavButton({ children }: { children: React.ReactNode }) {
  return (
    <button
      type="button"
      className="bg-transparent border-none cursor-pointer font-sans text-[15px] font-medium uppercase text-wandor-text tracking-[0.04em] transition-opacity hover:opacity-55"
    >
      {children}
    </button>
  )
}

export default function Hero() {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const goToPlan = () => navigate('/plan')

  return (
    <section className="relative min-h-svh w-full overflow-hidden">
      <video
        className="absolute inset-0 w-full h-full object-cover z-0"
        src="https://pollen-batch-41236914.figma.site/_components/v2/f0ee2dae7671c170c34f12e31c4cb41418976c98/769c564298c132f7919405cd9f17c1b1231f341d.769c5642.mp4"
        autoPlay
        muted
        loop
        playsInline
      />

      <div
        className="absolute inset-x-0 top-0 h-[687px] pointer-events-none z-[1]"
        style={{
          background:
            'linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(255,255,255,0) 100%)',
        }}
      />

      <div className="relative z-[2] max-w-[1360px] mx-auto">
        <nav className="flex items-center justify-between px-20 pt-6 pb-4 max-md:px-6 max-md:pt-5">
          <span className="font-display text-[40px] max-md:text-[32px] text-black leading-none select-none">
            wandor
          </span>

          <div className="absolute left-1/2 -translate-x-1/2 flex gap-8 max-md:hidden">
            <NavButton>Discover</NavButton>
            <NavButton>Pricing</NavButton>
            <NavButton>FAQs</NavButton>
          </div>

          <div className="flex items-center gap-8">
            <button
              type="button"
              className="max-md:hidden bg-transparent border-none cursor-pointer font-sans text-[15px] font-semibold uppercase text-[#292929] tracking-[0.04em] transition-opacity hover:opacity-55"
            >
              Login
            </button>
            <button
              type="button"
              onClick={goToPlan}
              className="bg-wandor-dark text-[#fafafa] border-none cursor-pointer font-sans text-[15px] font-medium uppercase tracking-[0.04em] px-5 py-3.5 rounded-full transition-all hover:bg-[#333] active:scale-95"
            >
              Plan My Trip
            </button>
          </div>
        </nav>

        <div className="flex flex-col items-center px-6 pt-16 pb-24 text-center">
          <h1 className="font-sans text-[clamp(40px,6vw,68px)] font-medium text-wandor-text leading-[1.05] tracking-[-0.04em] max-w-[820px] mb-5">
            Where will you go next?
          </h1>
          <p className="font-sans text-xl font-medium text-wandor-muted leading-relaxed max-w-[500px] mb-10">
            Tell our AI where you're going and what you love. We'll create a
            personalized itinerary for you.
          </p>

          <div className="relative w-[701px] max-md:w-[calc(100vw-48px)] min-h-[208px] bg-white/[0.06] border-[3px] border-white rounded-[44px] shadow-[0_0_4px_0_rgba(0,0,0,0.15)] overflow-hidden backdrop-blur-[20px]">
            <p className="absolute left-[29px] top-[57px] -translate-y-1/2 w-[609px] max-md:w-[calc(100%-58px)] font-sans text-xl max-md:text-[17px] font-medium text-wandor-prompt leading-relaxed break-words">
              I'm planning a 7-day trip to Japan in October. I love food,
              hidden cafés, scenic hikes, and want to avoid crowds....
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,.pdf"
              className="hidden"
            />
            <button
              type="button"
              aria-label="Upload inspiration"
              onClick={() => fileInputRef.current?.click()}
              className="absolute left-[21px] top-[137px] w-11 h-11 bg-transparent border border-white/70 rounded-full cursor-pointer flex items-center justify-center backdrop-blur-[14px] transition-transform hover:scale-105 focus-visible:outline-2 focus-visible:outline-white focus-visible:outline-offset-2"
            >
              <Upload className="w-[18px] h-[18px] text-wandor-text flex-shrink-0" />
            </button>

            <button
              type="button"
              onClick={goToPlan}
              className="absolute bottom-[21px] right-[21px] w-[156px] h-14 bg-black border-none rounded-[44px] shadow-[0_0_2px_0_rgba(0,0,0,0.05)] cursor-pointer flex items-center justify-center font-sans text-base font-medium text-[#fafafa] uppercase tracking-[0.02em] transition-all hover:bg-[#333] active:scale-95"
            >
              Plan My Trip
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
