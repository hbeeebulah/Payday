"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { BottomNav } from "@/components/staff/BottomNav";
import { useStore } from "@/lib/store";

export default function StaffLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { currentStaffId, hydrated } = useStore();

  const isLogin = pathname === "/portal/login";
  const needsAuth = !isLogin && !currentStaffId;

  useEffect(() => {
    if (hydrated && needsAuth) router.replace("/portal/login");
  }, [hydrated, needsAuth, router]);

  // Login screen: full mobile column, no bottom nav.
  if (isLogin) {
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
