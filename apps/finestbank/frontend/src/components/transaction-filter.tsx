"use client"

import { useCallback } from "react"
import { usePathname, useRouter, useSearchParams } from "next/navigation"

interface TransactionFilterProps {
  currentType: string
  currentCategory: string
  currentDateFrom: string
  currentDateTo: string
}

export default function TransactionFilter({
  currentType,
  currentCategory,
  currentDateFrom,
  currentDateTo,
}: TransactionFilterProps) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const updateParam = useCallback(
    (key: string, value: string) => {
      const params = new URLSearchParams(Array.from(searchParams.entries()))
      if (value) {
        params.set(key, value)
      } else {
        params.delete(key)
      }
      params.set("page", "1")
      router.push(`${pathname}?${params.toString()}`)
    },
    [router, pathname, searchParams],
  )

  const inputClass =
    "rounded-md bg-surface-800 border border-surface-700 px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-primary-500"

  return (
    <div className="flex flex-wrap items-center gap-3">
      <select
        value={currentType}
        onChange={(e) => updateParam("type", e.target.value)}
        className={inputClass}
      >
        <option value="">All Types</option>
        <option value="credit">Credit</option>
        <option value="debit">Debit</option>
        <option value="transfer">Transfer</option>
        <option value="payment">Payment</option>
        <option value="wire">Wire</option>
      </select>

      <input
        type="text"
        placeholder="Category..."
        value={currentCategory}
        onChange={(e) => updateParam("category", e.target.value)}
        className={inputClass}
      />

      <input
        type="date"
        value={currentDateFrom}
        onChange={(e) => updateParam("date_from", e.target.value)}
        className={inputClass}
      />

      <input
        type="date"
        value={currentDateTo}
        onChange={(e) => updateParam("date_to", e.target.value)}
        className={inputClass}
      />
    </div>
  )
}
