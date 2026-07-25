import { Link } from 'react-router-dom'
import AmbientBackdrop from '@/components/ui/AmbientBackdrop'
import StepIndicator from '@/components/ui/StepIndicator'
import TripDetailsStep from '@/components/planner/TripDetailsStep'
import PreferencesStep from '@/components/planner/PreferencesStep'
import ResultsStep from '@/components/planner/ResultsStep'
import { PlanProvider, usePlan } from '@/lib/planContext'

function PlanContent() {
  const { plan } = usePlan()

  return (
    <div className="relative min-h-svh w-full">
      <AmbientBackdrop />

      <header className="max-w-[1360px] mx-auto px-20 max-md:px-6 pt-6 pb-4">
        <Link
          to="/"
          className="font-display text-[32px] text-black leading-none select-none"
        >
          wandor
        </Link>
      </header>

      <main className="max-w-[720px] mx-auto px-6 pb-24">
        <StepIndicator current={plan.step} />
        {plan.step === 'details' && <TripDetailsStep />}
        {plan.step === 'preferences' && <PreferencesStep />}
        {plan.step === 'results' && <ResultsStep />}
      </main>
    </div>
  )
}

export default function Plan() {
  return (
    <PlanProvider>
      <PlanContent />
    </PlanProvider>
  )
}
