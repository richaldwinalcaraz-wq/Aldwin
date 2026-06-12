import { auth } from "@clerk/nextjs/server"
import { redirect } from "next/navigation"
import Link from "next/link"
import KpiCard, { KpiGrid } from "@/components/kpi-card"
import TransactionFilter from "@/components/transaction-filter"
import PortfolioDonut from "@/components/portfolio-donut"
import { Role } from "@/lib/roles"
import LiveFeed from "@/components/live-feed"

interface AnalystSummary {
  division: { name: string; slug: string }
  transaction_count_30d: number
  transaction_volume_30d: number
  portfolio_market_value: number
  active_loan_count: number
}

interface TransactionItem {
  id: string
  type: string
  category: string
  amount: number
  currency: string
  description: string
  reference_id: string
  status: string
  created_at: string
}

interface TransactionPage {
  items: TransactionItem[]
  total: number
  page: number
  page_size: number
  pages: number
}

interface HoldingItem {
  id: string
  asset_name: string
  asset_type: string
  ticker: string | null
  quantity: number
  unit_cost: number
  current_price: number
  market_value: number
  unrealized_pnl: number
  weight_pct: number
}
interface AllocationSlice {
  asset_type: string
  market_value: number
  pct: number
}
interface PortfolioData {
  holdings: HoldingItem[]
  allocation: AllocationSlice[]
  total_market_value: number
}

const API_URL = process.env.API_URL ?? "http://localhost:8000"

export default async function AnalystPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const { sessionClaims, getToken } = auth()
  const role = (sessionClaims?.publicMetadata as { role?: string } | undefined)
    ?.role

  if (role === Role.VIEWER || !role) redirect("/")

  const token = (await getToken()) ?? ""
  const divisionId =
    (sessionClaims?.publicMetadata as { divisions?: string[] } | undefined)
      ?.divisions?.[0] ?? ""

  const res = await fetch(`${API_URL}/api/v1/analyst/summary`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  })
  const data: AnalystSummary | null = res.ok ? await res.json() : null

  const page = Number(searchParams.page ?? 1)
  const txnParams = new URLSearchParams()
  txnParams.set("page", String(page))
  txnParams.set("page_size", "20")
  if (searchParams.type) txnParams.set("type", String(searchParams.type))
  if (searchParams.category) txnParams.set("category", String(searchParams.category))
  if (searchParams.date_from) txnParams.set("date_from", String(searchParams.date_from))
  if (searchParams.date_to) txnParams.set("date_to", String(searchParams.date_to))

  const txnRes = await fetch(`${API_URL}/api/v1/analyst/transactions?${txnParams}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  })
  const txnData: TransactionPage | null = txnRes.ok ? await txnRes.json() : null

  const portRes = await fetch(`${API_URL}/api/v1/analyst/portfolio`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  })
  const portData: PortfolioData | null = portRes.ok ? await portRes.json() : null

  const divisionName = data?.division.name ?? "Your Division"

  const currentPage = txnData?.page ?? 1
  const totalPages = txnData?.pages ?? 1

  const buildPageUrl = (p: number) => {
    const params = new URLSearchParams()
    if (searchParams.type) params.set("type", String(searchParams.type))
    if (searchParams.category) params.set("category", String(searchParams.category))
    if (searchParams.date_from) params.set("date_from", String(searchParams.date_from))
    if (searchParams.date_to) params.set("date_to", String(searchParams.date_to))
    params.set("page", String(p))
    return `/dashboard/analyst?${params.toString()}`
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-slate-50">{divisionName}</h1>
          <span className="inline-flex items-center rounded-full bg-primary-500/20 px-2.5 py-0.5 text-xs font-medium text-primary-400 ring-1 ring-inset ring-primary-500/30">
            Role: Analyst
          </span>
        </div>
      </div>

      <KpiGrid>
        <KpiCard
          label="Transactions (30d)"
          value={data?.transaction_count_30d ?? 0}
          changePct={0}
          colorScheme="blue"
        />
        <KpiCard
          label="Transaction Volume"
          value={data?.transaction_volume_30d ?? 0}
          changePct={0}
          prefix="$"
          colorScheme="green"
        />
        <KpiCard
          label="Portfolio Value"
          value={data?.portfolio_market_value ?? 0}
          changePct={0}
          prefix="$"
          colorScheme="purple"
        />
        <KpiCard
          label="Active Loans"
          value={data?.active_loan_count ?? 0}
          changePct={0}
          colorScheme="amber"
        />
      </KpiGrid>

      {divisionId && (
        <div className="space-y-3">
          <LiveFeed divisionId={divisionId} token={token} />
        </div>
      )}

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-200">Transactions</h2>
          {txnData && (
            <span className="text-sm text-slate-500">
              {txnData.total.toLocaleString()} total
            </span>
          )}
        </div>

        <TransactionFilter
          currentType={String(searchParams.type ?? "")}
          currentCategory={String(searchParams.category ?? "")}
          currentDateFrom={String(searchParams.date_from ?? "")}
          currentDateTo={String(searchParams.date_to ?? "")}
        />

        <div className="overflow-x-auto rounded-lg border border-surface-700">
          <table className="w-full text-sm text-slate-300">
            <thead className="bg-surface-800 text-xs uppercase text-slate-500">
              <tr>
                {["Date", "Type", "Category", "Amount", "Currency", "Description", "Status"].map(
                  (h) => (
                    <th key={h} className="px-4 py-3 text-left">
                      {h}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-700">
              {(txnData?.items ?? []).map((txn) => (
                <tr key={txn.id} className="hover:bg-surface-800/50">
                  <td className="px-4 py-3 whitespace-nowrap">
                    {new Date(txn.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        txn.type === "credit"
                          ? "bg-green-500/20 text-green-400"
                          : "bg-red-500/20 text-red-400"
                      }`}
                    >
                      {txn.type}
                    </span>
                  </td>
                  <td className="px-4 py-3">{txn.category}</td>
                  <td className="px-4 py-3 font-mono">
                    {txn.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-3">{txn.currency}</td>
                  <td className="px-4 py-3 max-w-[200px] truncate">{txn.description}</td>
                  <td className="px-4 py-3">{txn.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {(txnData?.items ?? []).length === 0 && (
            <p className="py-8 text-center text-slate-500 text-sm">No transactions found.</p>
          )}
        </div>

        <div className="flex items-center justify-between text-sm text-slate-400">
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <div className="flex gap-2">
            {currentPage > 1 ? (
              <Link
                href={buildPageUrl(currentPage - 1)}
                className="rounded-md bg-surface-800 border border-surface-700 px-3 py-1.5 hover:bg-surface-700 transition-colors"
              >
                ← Prev
              </Link>
            ) : (
              <span className="rounded-md bg-surface-800 border border-surface-700 px-3 py-1.5 opacity-40 cursor-not-allowed">
                ← Prev
              </span>
            )}
            {currentPage < totalPages ? (
              <Link
                href={buildPageUrl(currentPage + 1)}
                className="rounded-md bg-surface-800 border border-surface-700 px-3 py-1.5 hover:bg-surface-700 transition-colors"
              >
                Next →
              </Link>
            ) : (
              <span className="rounded-md bg-surface-800 border border-surface-700 px-3 py-1.5 opacity-40 cursor-not-allowed">
                Next →
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-200">Portfolio Holdings</h2>
          {portData && (
            <span className="text-sm text-slate-500">
              {portData.holdings.length} positions &middot; Total{" "}
              {portData.total_market_value.toLocaleString("en-US", {
                style: "currency",
                currency: "USD",
                maximumFractionDigits: 0,
              })}
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 overflow-x-auto rounded-lg border border-surface-700">
            <table className="w-full text-sm text-slate-300">
              <thead className="bg-surface-800 text-xs uppercase text-slate-500">
                <tr>
                  {["Asset", "Type", "Ticker", "Qty", "Unit Cost", "Current Price", "Market Value", "P&L", "Weight%"].map(
                    (h) => (
                      <th key={h} className="px-4 py-3 text-left">
                        {h}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-700">
                {(portData?.holdings ?? []).map((h) => (
                  <tr key={h.id} className="hover:bg-surface-800/50">
                    <td className="px-4 py-3 font-medium">{h.asset_name}</td>
                    <td className="px-4 py-3 text-slate-400">{h.asset_type}</td>
                    <td className="px-4 py-3 font-mono text-xs">{h.ticker ?? "—"}</td>
                    <td className="px-4 py-3 font-mono">
                      {h.quantity.toLocaleString("en-US", { maximumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 font-mono">
                      {h.unit_cost.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 font-mono">
                      {h.current_price.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 font-mono">
                      {h.market_value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </td>
                    <td
                      className={`px-4 py-3 font-mono ${
                        h.unrealized_pnl >= 0 ? "text-green-400" : "text-red-400"
                      }`}
                    >
                      {h.unrealized_pnl >= 0 ? "+" : ""}
                      {h.unrealized_pnl.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 font-mono">{h.weight_pct.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(portData?.holdings ?? []).length === 0 && (
              <p className="py-8 text-center text-slate-500 text-sm">No holdings found.</p>
            )}
          </div>

          <div className="rounded-lg border border-surface-700 bg-surface-900 p-4">
            <h3 className="text-sm font-medium text-slate-400 mb-3">Allocation by Asset Type</h3>
            <PortfolioDonut data={portData?.allocation ?? []} />
          </div>
        </div>
      </div>
    </div>
  )
}
