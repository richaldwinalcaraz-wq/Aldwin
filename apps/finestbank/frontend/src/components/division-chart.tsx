"use client"

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

interface DivisionKpi {
  name: string
  slug: string
  total_revenue: number
  net_income: number
}

function formatCompact(v: number): string {
  if (v >= 1_000_000_000) return `$${(v / 1_000_000_000).toFixed(1)}B`
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `$${(v / 1_000).toFixed(1)}K`
  return `$${Math.round(v)}`
}

export default function DivisionChart({ data }: { data: DivisionKpi[] }) {
  if (!data.length) {
    return (
      <div className="flex h-[260px] items-center justify-center text-sm text-slate-500">
        No division data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#243055" vertical={false} />
        <XAxis
          dataKey="name"
          tick={{ fill: "#94A3B8", fontSize: 11 }}
          axisLine={{ stroke: "#243055" }}
          tickLine={false}
        />
        <YAxis
          tickFormatter={formatCompact}
          tick={{ fill: "#94A3B8", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={60}
        />
        <Tooltip
          formatter={(value: number, name: string) => [
            formatCompact(value),
            name === "total_revenue" ? "Revenue" : "Net Income",
          ]}
          contentStyle={{
            backgroundColor: "#0f1629",
            border: "1px solid #243055",
            borderRadius: "6px",
            color: "#F1F5F9",
            fontSize: 12,
          }}
          labelStyle={{ color: "#94A3B8" }}
        />
        <Bar
          dataKey="total_revenue"
          fill="#3B82F6"
          radius={[4, 4, 0, 0]}
          maxBarSize={40}
        />
        <Bar
          dataKey="net_income"
          fill="#10B981"
          radius={[4, 4, 0, 0]}
          maxBarSize={40}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}
