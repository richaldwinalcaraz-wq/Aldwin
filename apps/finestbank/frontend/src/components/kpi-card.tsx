import React from "react"

interface KpiCardProps {
  label: string
  value: number
  changePct: number
  prefix?: string
  colorScheme?: "blue" | "green" | "amber" | "purple"
}

function formatValue(value: number, prefix = ""): string {
  const abs = Math.abs(value)
  if (abs >= 1e9) return `${prefix}${(value / 1e9).toFixed(1)}B`
  if (abs >= 1e6) return `${prefix}${(value / 1e6).toFixed(1)}M`
  if (abs >= 1e3) return `${prefix}${(value / 1e3).toFixed(1)}K`
  return `${prefix}${value.toFixed(0)}`
}

const accentClasses: Record<NonNullable<KpiCardProps["colorScheme"]>, string> = {
  blue: "bg-blue-500",
  green: "bg-accent-500",
  amber: "bg-amber-500",
  purple: "bg-purple-500",
}

export default function KpiCard({
  label,
  value,
  changePct,
  prefix = "",
  colorScheme = "blue",
}: KpiCardProps) {
  const badgeClass =
    changePct > 0
      ? "bg-accent-500/20 text-accent-400"
      : changePct < 0
        ? "bg-red-500/20 text-red-400"
        : "bg-slate-500/20 text-slate-400"

  const badgeLabel =
    changePct > 0
      ? `↑ ${changePct.toFixed(1)}%`
      : changePct < 0
        ? `↓ ${Math.abs(changePct).toFixed(1)}%`
        : `— 0.0%`

  return (
    <div className="relative flex overflow-hidden rounded-xl border border-surface-700 bg-surface-900 p-5">
      <span
        className={`absolute inset-y-0 left-0 w-1 rounded-l-xl ${accentClasses[colorScheme]}`}
      />
      <div className="flex w-full flex-col gap-2 pl-3">
        <span className="text-sm text-slate-400">{label}</span>
        <div className="flex items-center gap-3">
          <span className="text-2xl font-bold text-slate-50">
            {formatValue(value, prefix)}
          </span>
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${badgeClass}`}>
            {badgeLabel}
          </span>
        </div>
      </div>
    </div>
  )
}

interface KpiGridProps {
  children: React.ReactNode
}

export function KpiGrid({ children }: KpiGridProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {children}
    </div>
  )
}
