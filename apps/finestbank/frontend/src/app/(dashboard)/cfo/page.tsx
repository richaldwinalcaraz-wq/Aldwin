import { auth } from "@clerk/nextjs/server"
import FilterBar from "@/components/filter-bar"
import KpiCard, { KpiGrid } from "@/components/kpi-card"
import RevenueChart from "@/components/revenue-chart"
import DivisionChart from "@/components/division-chart"

interface KpiValue {
  value: number
  change_pct: number
}

interface KpiResponse {
  period: string
  kpis: {
    total_revenue: KpiValue
    net_income: KpiValue
    total_assets: KpiValue
    loan_portfolio: KpiValue
  }
}

interface TrendPoint {
  period: string
  total_revenue: number
  net_income: number
}

interface TrendsResponse {
  data: TrendPoint[]
}

interface DivisionKpi {
  name: string
  slug: string
  total_revenue: number
  net_income: number
}

interface DivisionsResponse {
  period: string
  divisions: DivisionKpi[]
}

const API_URL = process.env.API_URL ?? "http://localhost:8000"

function buildQuery(params: Record<string, string | undefined>): string {
  const q = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v) q.set(k, v)
  }
  const s = q.toString()
  return s ? `?${s}` : ""
}

export default async function CFOPage({
  searchParams,
}: {
  searchParams: { division_slug?: string; from_period?: string; to_period?: string }
}) {
  const { getToken } = auth()
  const token = (await getToken()) ?? ""
  const headers = { Authorization: `Bearer ${token}` }
  const opts = { headers, cache: "no-store" as const }

  const filterParams = {
    division_slug: searchParams.division_slug,
    from_period: searchParams.from_period,
    to_period: searchParams.to_period,
  }
  const qs = buildQuery(filterParams)
  const periodQs = buildQuery({
    from_period: searchParams.from_period,
    to_period: searchParams.to_period,
  })

  const [kpisResult, trendsResult, divisionsResult] = await Promise.allSettled([
    fetch(`${API_URL}/api/v1/rollup/kpis${qs}`, opts).then((r) =>
      r.ok ? (r.json() as Promise<KpiResponse>) : null
    ),
    fetch(`${API_URL}/api/v1/rollup/trends${qs}`, opts).then((r) =>
      r.ok ? (r.json() as Promise<TrendsResponse>) : null
    ),
    fetch(`${API_URL}/api/v1/rollup/divisions${periodQs}`, opts).then((r) =>
      r.ok ? (r.json() as Promise<DivisionsResponse>) : null
    ),
  ])

  const kpisData = kpisResult.status === "fulfilled" ? kpisResult.value : null
  const trendsData = trendsResult.status === "fulfilled" ? trendsResult.value : null
  const divisionsData = divisionsResult.status === "fulfilled" ? divisionsResult.value : null

  const kpis = kpisData?.kpis
  const period = kpisData?.period ?? "—"
  const trendPoints = trendsData?.data ?? []
  const divisionList = divisionsData?.divisions ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-slate-50">CFO Overview</h1>
          <span className="inline-flex items-center rounded-full bg-accent-500/20 px-2.5 py-0.5 text-xs font-medium text-accent-400 ring-1 ring-inset ring-accent-500/30">
            Role: CFO
          </span>
        </div>
        <span className="text-sm text-slate-500">Period: {period}</span>
      </div>

      <FilterBar
        divisions={divisionList.map((d) => ({ name: d.name, slug: d.slug }))}
        periods={trendPoints.map((t) => t.period)}
        currentDivision={searchParams.division_slug ?? ""}
        currentFrom={searchParams.from_period ?? ""}
        currentTo={searchParams.to_period ?? ""}
      />

      <KpiGrid>
        <KpiCard
          label="Total Revenue"
          value={kpis?.total_revenue.value ?? 0}
          changePct={kpis?.total_revenue.change_pct ?? 0}
          prefix="$"
          colorScheme="green"
        />
        <KpiCard
          label="Net Income"
          value={kpis?.net_income.value ?? 0}
          changePct={kpis?.net_income.change_pct ?? 0}
          prefix="$"
          colorScheme="blue"
        />
        <KpiCard
          label="Total Assets"
          value={kpis?.total_assets.value ?? 0}
          changePct={kpis?.total_assets.change_pct ?? 0}
          prefix="$"
          colorScheme="purple"
        />
        <KpiCard
          label="Loan Portfolio"
          value={kpis?.loan_portfolio.value ?? 0}
          changePct={kpis?.loan_portfolio.change_pct ?? 0}
          prefix="$"
          colorScheme="amber"
        />
      </KpiGrid>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl bg-surface-900 p-5 ring-1 ring-surface-700">
          <h2 className="mb-4 text-sm font-semibold text-slate-300">
            Revenue &amp; Net Income Trend
          </h2>
          <RevenueChart data={trendPoints} />
        </div>
        <div className="rounded-xl bg-surface-900 p-5 ring-1 ring-surface-700">
          <h2 className="mb-4 text-sm font-semibold text-slate-300">
            Division Comparison — {period}
          </h2>
          <DivisionChart data={divisionList} />
        </div>
      </div>
    </div>
  )
}
