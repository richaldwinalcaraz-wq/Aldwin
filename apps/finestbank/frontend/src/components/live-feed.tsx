"use client"

import { useEffect, useState } from "react"

interface LiveFeedProps {
  divisionId: string
  token: string
}

interface LiveEvent {
  id: string
  type: string
  category: string
  amount: number
  currency: string
  description: string
  created_at: string
}

export default function LiveFeed({ divisionId, token }: LiveFeedProps) {
  const [events, setEvents] = useState<LiveEvent[]>([])
  const [status, setStatus] = useState<"connecting" | "open" | "closed">("connecting")

  useEffect(() => {
    const wsBase = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000"
    const url = `${wsBase}/ws/live/${divisionId}?token=${token}`
    const ws = new WebSocket(url)

    ws.onopen = () => setStatus("open")
    ws.onmessage = (e) => {
      try {
        const parsed: LiveEvent = JSON.parse(e.data)
        setEvents((prev) => [parsed, ...prev].slice(0, 50))
      } catch {
        // ignore malformed messages
      }
    }
    ws.onclose = () => setStatus("closed")
    ws.onerror = () => setStatus("closed")

    return () => ws.close()
  }, [divisionId, token])

  return (
    <div className="rounded-lg border border-surface-700 bg-surface-900 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-200">Live Transactions</h2>
        {status === "connecting" && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-700/50 px-2.5 py-0.5 text-xs font-medium text-slate-400 ring-1 ring-inset ring-slate-600">
            Connecting…
          </span>
        )}
        {status === "open" && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-green-500/20 px-2.5 py-0.5 text-xs font-medium text-green-400 ring-1 ring-inset ring-green-500/30">
            <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" />
            Live
          </span>
        )}
        {status === "closed" && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-red-500/20 px-2.5 py-0.5 text-xs font-medium text-red-400 ring-1 ring-inset ring-red-500/30">
            Disconnected
          </span>
        )}
      </div>

      <div className="max-h-48 overflow-y-auto space-y-1">
        {events.length === 0 && status === "open" && (
          <p className="py-4 text-center text-sm text-slate-500">Waiting for events…</p>
        )}
        {events.length === 0 && status !== "open" && (
          <p className="py-4 text-center text-sm text-slate-600">No events.</p>
        )}
        {events.map((ev) => (
          <div
            key={ev.id}
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-surface-800/50"
          >
            <span className="w-32 shrink-0 font-mono text-xs text-slate-500">
              {new Date(ev.created_at).toLocaleTimeString()}
            </span>
            <span
              className={`inline-flex shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
                ev.type === "credit"
                  ? "bg-green-500/20 text-green-400"
                  : "bg-red-500/20 text-red-400"
              }`}
            >
              {ev.type}
            </span>
            <span className="font-mono text-slate-300">
              {ev.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })} {ev.currency}
            </span>
            <span className="truncate text-slate-400">{ev.description}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
