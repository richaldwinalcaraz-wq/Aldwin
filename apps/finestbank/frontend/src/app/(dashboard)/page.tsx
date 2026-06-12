import { auth } from "@clerk/nextjs/server"
import { redirect } from "next/navigation"
import { getRedirectPath, Role } from "@/lib/roles"

export default async function DashboardPage() {
  const { sessionClaims } = auth()
  const role = (sessionClaims?.publicMetadata as { role?: string } | undefined)
    ?.role
  redirect(getRedirectPath(role ?? Role.ANALYST))
}
