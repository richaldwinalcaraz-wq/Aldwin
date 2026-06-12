export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-surface-950">
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-primary-500 flex items-center justify-center">
            <span className="text-white font-bold text-lg">F</span>
          </div>
          <h1 className="text-4xl font-bold text-slate-50 tracking-tight">
            FinestBank
          </h1>
        </div>
        <p className="text-slate-400 text-lg max-w-md">
          Financial Intelligence Dashboard — loading experience...
        </p>
        <div className="flex items-center justify-center gap-2 mt-8">
          <div className="w-2 h-2 rounded-full bg-accent-500 animate-pulse" />
          <span className="text-slate-500 text-sm">Phase 1 scaffold complete</span>
        </div>
      </div>
    </main>
  )
}
