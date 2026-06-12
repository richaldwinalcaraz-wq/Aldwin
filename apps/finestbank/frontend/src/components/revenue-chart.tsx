"use client"

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

interface TrendPoint {
  period: string
  total_revenue: number
  net_income: number
}

function formatCompact(v: number): string {
  if (v >= 1_000_000_000) return `$${(v / 1_000_000_000).toFixed(1)}B`
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `$${(v / 1_000).toFixed(1)}K`
  return `$${Math.round(v)}`
}

export default function RevenueChart({ data }: { data: TrendPoint[] }) {
  if (!data.length) {
    return (
      <div className="flex h-[260px] items-center justify-center text-sm text-slate-500">
        No trend data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 8 }}>
        <defs>
          <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="colorNetIncome" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10B981" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#243055" />
        <XAxis
          dataKey="period"
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
        <Area
          type="monotone"
          dataKey="total_revenue"
          stroke="#3B82F6"
          strokeWidth={2}
          fill="url(#colorRevenue)"
          dot={false}
        />
        <Area
          type="monotone"
          dataKey="net_income"
          stroke="#10B981"
          strokeWidth={2}
          fill="url(#colorNetIncome)"
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
