"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthField } from "@/components/auth/AuthField";
import { Button } from "@/components/ui/Button";
import { registerUser, type UserRole } from "@/lib/auth";
import { loginStaff, useStore } from "@/lib/store";

interface SignupFormProps {
  defaultRole?: UserRole;
  loginHref: string;
  afterSignupHref?: string;
}

export function SignupForm({
  defaultRole = "staff",
  loginHref,
  afterSignupHref,
}: SignupFormProps) {
  const router = useRouter();
  const { workers } = useStore();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [role, setRole] = useState<UserRole>(defaultRole);
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);
    try {
      const session = await registerUser({
        firstName,
        lastName,
        role,
        phone,
        email,
        password,
        confirmPassword,
      });

      if (session.user.role === "staff") {
        const match = workers.find(
          (w) => w.email?.toLowerCase() === session.user.email.toLowerCase(),
        );
        if (match) loginStaff(match.id);
      }

      const destination =
        afterSignupHref ??
        (session.user.role === "staff" ? "/portal" : "/dashboard");
      router.replace(destination);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <AuthField
        label="First name"
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
        autoComplete="given-name"
        required
      />
      <AuthField
        label="Last name"
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
        autoComplete="family-name"
        required
      />

      <div>
        <p className="text-sm font-medium text-ink-700">I am signing up as</p>
        <div className="mt-2 grid grid-cols-2 gap-2">
          {(["staff", "employer"] as const).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setRole(option)}
              className={`rounded-lg border px-3 py-2.5 text-sm font-medium capitalize transition-colors ${
                role === option
                  ? "border-brand-500 bg-brand-50 text-brand-700"
                  : "border-ink-200 bg-white text-ink-600 hover:bg-ink-50"
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      <AuthField
        label="Phone number"
        type="tel"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        autoComplete="tel"
        placeholder="+234 800 000 0000"
        required
      />
      <AuthField
        label="Email address"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        autoComplete="email"
        required
      />
      <AuthField
        label="Create password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        autoComplete="new-password"
        minLength={8}
        required
      />
      <AuthField
        label="Confirm password"
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        autoComplete="new-password"
        minLength={8}
        required
      />

      {error ? (
        <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>
      ) : null}

      <Button type="submit" className="w-full" size="lg" disabled={loading}>
        {loading ? "Creating account…" : "Sign up"}
      </Button>

      <p className="text-center text-sm text-ink-500">
        Already have an account?{" "}
        <Link href={loginHref} className="font-medium text-brand-600 hover:text-brand-700">
          Sign in
        </Link>
      </p>
    </form>
  );
}
