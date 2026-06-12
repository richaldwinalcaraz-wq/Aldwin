export const Role = {
  CFO: "cfo",
  ANALYST: "analyst",
  VIEWER: "viewer",
} as const

export type RoleType = (typeof Role)[keyof typeof Role]

export const Division = {
  RETAIL: "retail",
  CORPORATE: "corporate",
  TREASURY: "treasury",
  WEALTH: "wealth",
} as const

export type DivisionType = (typeof Division)[keyof typeof Division]

export function getRedirectPath(role: string): string {
  if (role === Role.CFO) return "/dashboard/cfo"
  return "/dashboard/analyst"
}
