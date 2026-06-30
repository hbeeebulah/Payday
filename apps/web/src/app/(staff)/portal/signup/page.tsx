import { AuthPageShell } from "@/components/auth/AuthPageShell";
import { SignupForm } from "@/components/auth/SignupForm";

export default function StaffSignupPage() {
  return (
    <AuthPageShell
      title="Create your account"
      subtitle="Register to access your payslips and earnings record."
      compact
    >
      <SignupForm defaultRole="staff" loginHref="/portal/login" />
    </AuthPageShell>
  );
}
