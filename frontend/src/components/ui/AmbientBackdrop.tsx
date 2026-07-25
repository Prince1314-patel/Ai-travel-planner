export default function AmbientBackdrop() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-white">
      <div className="absolute -top-40 -left-40 w-[560px] h-[560px] rounded-full bg-black/[0.03] blur-3xl" />
      <div className="absolute top-1/3 -right-32 w-[480px] h-[480px] rounded-full bg-black/[0.025] blur-3xl" />
      <div className="absolute bottom-0 left-1/4 w-[420px] h-[420px] rounded-full bg-black/[0.02] blur-3xl" />
    </div>
  )
}
