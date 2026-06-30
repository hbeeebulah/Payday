"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthField } from "@/components/auth/AuthField";
import { Button } from "@/components/ui/Button";
import { loginUser, logoutUser, type UserRole } from "@/lib/auth";
import { loginStaff, useStore } from "@/lib/store";

interface LoginFormProps {
  expectedRole: UserRole;
  signupHref: string;
  afterLoginHref: string;
}

export function LoginForm({ expectedRole, signupHref, afterLoginHref }: LoginFormProps) {
  const router = useRouter();
  const { workers } = useStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const session = await loginUser({ email, password });

      if (session.user.role !== expectedRole) {
        logoutUser();
        setError(
          expectedRole === "staff"
            ? "This account is registered as an employer. Use the employer login instead."
            : "This account is registered as staff. Use the staff portal login instead.",
        );
        return;
      }

      if (expectedRole === "staff") {
        const match = workers.find(
          (w) => w.email?.toLowerCase() === session.user.email.toLowerCase(),
        );
        if (match) loginStaff(match.id);
      }

      router.replace(afterLoginHref);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <AuthField
        label="Email address"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        autoComplete="email"
        required
      />
      <AuthField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        autoComplete="current-password"
        required
      />

      {error ? (
        <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>
      ) : null}

      <Button type="submit" className="w-full" size="lg" disabled={loading}>
        {loading ? "Signing in…" : "Sign in"}
      </Button>

      <p className="text-center text-sm text-ink-500">
        Don&apos;t have an account?{" "}
        <Link href={signupHref} className="font-medium text-brand-600 hover:text-brand-700">
          Sign up
        </Link>
      </p>
    </form>
  );
}
