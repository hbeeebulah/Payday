"use client";

import { AuthPageShell } from "@/components/auth/AuthPageShell";
import { LoginForm } from "@/components/auth/LoginForm";

export default function StaffLoginPage() {
  return (
    <AuthPageShell
      title="Staff sign in"
      subtitle="Securely access your payslips and earnings record."
      compact
    >
      <LoginForm
        expectedRole="staff"
        signupHref="/portal/signup"
        afterLoginHref="/portal"
      />
    </AuthPageShell>
  );
}
