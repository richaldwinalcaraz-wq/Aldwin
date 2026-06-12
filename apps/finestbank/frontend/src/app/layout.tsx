import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { ClerkProvider } from "@clerk/nextjs"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "FinestBank — Financial Intelligence Dashboard",
  description:
    "Real-time financial intelligence for CFOs and fintech analysts. Multi-division visibility across transactions, portfolio, loans, and financial statements.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <ClerkProvider>
      <html lang="en" className="dark">
        <body className={`${inter.className} bg-surface-950 text-slate-50 antialiased`}>
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}
