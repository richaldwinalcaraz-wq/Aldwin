"use client"

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts"

interface AllocationSlice {
  asset_type: string
  market_value: number
  pct: number
}

const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444", "#06B6D4", "#F97316"]

function formatCompact(v: number): string {
  if (v >= 1_000_000_000) return `$${(v / 1_000_000_000).toFixed(1)}B`
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `$${(v / 1_000).toFixed(1)}K`
  return `$${Math.round(v)}`
}

export default function PortfolioDonut({ data }: { data: AllocationSlice[] }) {
  if (!data.length) {
    return (
      <div className="flex h-[260px] items-center justify-center text-sm text-slate-500">
        No portfolio data
      </div>
    )
  }

  return (
    <>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={data}
            dataKey="market_value"
            nameKey="asset_type"
            cx="50%"
            cy="50%"
            innerRadius={70}
            outerRadius={110}
            paddingAngle={2}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number, name: string) => [formatCompact(value), name]}
            contentStyle={{
              backgroundColor: "#0f1629",
              border: "1px solid #243055",
              borderRadius: "6px",
              color: "#F1F5F9",
              fontSize: 12,
            }}
            labelStyle={{ color: "#94A3B8" }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap justify-center gap-3 mt-2">
        {data.map((d, i) => (
          <div key={d.asset_type} className="flex items-center gap-1.5 text-xs text-slate-400">
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: COLORS[i % COLORS.length] }}
            />
            {d.asset_type} ({d.pct}%)
          </div>
        ))}
      </div>
    </>
  )
}
