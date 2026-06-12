"use client"

import { useCallback } from "react"
import { usePathname, useRouter, useSearchParams } from "next/navigation"

interface DivisionOption {
  name: string
  slug: string
}

interface FilterBarProps {
  divisions: DivisionOption[]
  periods: string[]
  currentDivision: string
  currentFrom: string
  currentTo: string
}

export default function FilterBar({
  divisions,
  periods,
  currentDivision,
  currentFrom,
  currentTo,
}: FilterBarProps) {
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
      router.push(`${pathname}?${params.toString()}`)
    },
    [router, pathname, searchParams],
  )

  const selectClass =
    "rounded-md bg-surface-800 border border-surface-700 px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-primary-500"

  return (
    <div className="flex flex-wrap items-center gap-3">
      <select
        value={currentDivision}
        onChange={(e) => updateParam("division_slug", e.target.value)}
        className={selectClass}
      >
        <option value="">All Divisions</option>
        {divisions.map((d) => (
          <option key={d.slug} value={d.slug}>
            {d.name}
          </option>
        ))}
      </select>

      <select
        value={currentFrom}
        onChange={(e) => updateParam("from_period", e.target.value)}
        className={selectClass}
      >
        <option value="">From: All</option>
        {periods.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>

      <select
        value={currentTo}
        onChange={(e) => updateParam("to_period", e.target.value)}
        className={selectClass}
      >
        <option value="">To: All</option>
        {periods.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
    </div>
  )
}
