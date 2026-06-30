"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { isAuthHydrated, useAuth } from "@/lib/auth";

export function EmployerAuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const auth = useAuth();
  const ready = isAuthHydrated();
  const authed = auth?.user.role === "employer";

  useEffect(() => {
    if (ready && !authed) {
      router.replace("/login");
    }
  }, [ready, authed, router]);

  if (!ready || !authed) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-ink-50 text-sm text-ink-400">
        Redirecting…
      </div>
    );
  }

  return <>{children}</>;
}
