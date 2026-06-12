import { UserButton } from "@clerk/nextjs"
import Link from "next/link"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen bg-surface-950">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 bg-surface-900 border-r border-surface-800">
        <div className="flex h-16 items-center px-6 border-b border-surface-800">
          <span className="text-lg font-bold text-slate-50">FinestBank</span>
        </div>
        <nav className="p-4 space-y-1">
          <Link
            href="/dashboard"
            className="flex items-center px-3 py-2 rounded-md text-sm text-slate-300 hover:bg-surface-800 hover:text-slate-50 transition-colors"
          >
            Overview
          </Link>
          <Link
            href="/dashboard/cfo"
            className="flex items-center px-3 py-2 rounded-md text-sm text-slate-300 hover:bg-surface-800 hover:text-slate-50 transition-colors"
          >
            CFO Overview
          </Link>
          <Link
            href="/dashboard/analyst"
            className="flex items-center px-3 py-2 rounded-md text-sm text-slate-300 hover:bg-surface-800 hover:text-slate-50 transition-colors"
          >
            Analyst View
          </Link>
        </nav>
      </aside>

      {/* Main content area */}
      <div className="flex flex-1 flex-col">
        {/* Top bar */}
        <header className="flex h-16 items-center justify-between px-6 bg-surface-900 border-b border-surface-800">
          <span className="text-sm text-slate-400">Financial Intelligence Dashboard</span>
          <UserButton afterSignOutUrl="/sign-in" />
        </header>

        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}
