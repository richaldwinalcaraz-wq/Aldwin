import { SignUp } from "@clerk/nextjs"

export default function SignUpPage() {
  return (
    <div className="flex justify-center">
      <SignUp appearance={{ baseTheme: undefined }} />
    </div>
  )
}
