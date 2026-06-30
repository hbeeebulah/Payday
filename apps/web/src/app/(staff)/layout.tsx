"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { BottomNav } from "@/components/staff/BottomNav";
import { isAuthHydrated, useAuth } from "@/lib/auth";

export default function StaffLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const auth = useAuth();

  const isAuthPage =
    pathname === "/portal/login" || pathname === "/portal/signup";
  const ready = isAuthHydrated();
  const authed = auth?.user.role === "staff";
  const needsAuth = !isAuthPage && ready && !authed;

  useEffect(() => {
    if (ready && needsAuth) router.replace("/portal/login");
  }, [ready, needsAuth, router]);

  if (isAuthPage) {
    return (
      <div className="min-h-screen bg-ink-100">
        <div className="mx-auto flex min-h-screen max-w-md flex-col bg-ink-50">
          {children}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-ink-100">
      <div className="mx-auto flex min-h-screen max-w-md flex-col bg-ink-50 shadow-card">
        <main className="flex-1 px-5 pb-6 pt-6">
          {needsAuth ? (
            <p className="py-20 text-center text-sm text-ink-400">Redirecting…</p>
          ) : (
            children
          )}
        </main>
        {needsAuth ? null : <BottomNav />}
      </div>
    </div>
  );
}
