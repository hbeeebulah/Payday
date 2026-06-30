import { AuthPageShell } from "@/components/auth/AuthPageShell";
import { SignupForm } from "@/components/auth/SignupForm";

export default function SignupPage() {
  return (
    <AuthPageShell
      title="Create your account"
      subtitle="Sign up as staff or employer to access Payday."
    >
      <SignupForm defaultRole="employer" loginHref="/login" />
    </AuthPageShell>
  );
}
