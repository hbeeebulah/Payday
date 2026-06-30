import { AuthPageShell } from "@/components/auth/AuthPageShell";
import { LoginForm } from "@/components/auth/LoginForm";

export default function EmployerLoginPage() {
  return (
    <AuthPageShell
      title="Employer sign in"
      subtitle="Access your payroll dashboard and pay your team in one tap."
    >
      <LoginForm
        expectedRole="employer"
        signupHref="/signup"
        afterLoginHref="/dashboard"
      />
    </AuthPageShell>
  );
}
