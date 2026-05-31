"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/Button";
import { initials } from "@/lib/format";
import { loginStaff, useStore } from "@/lib/store";

export default function StaffLoginPage() {
  const router = useRouter();
  const { workers } = useStore();
  const [selected, setSelected] = useState<string | null>(null);

  function signIn() {
    if (!selected) return;
    loginStaff(selected);
    router.replace("/portal");
  }

  return (
    <div className="flex min-h-screen flex-col px-6 py-10">
      <Logo />
      <div className="mt-10">
        <h1 className="text-2xl font-semibold tracking-tight text-ink-900">
          Staff sign in
        </h1>
        <p className="mt-1 text-sm text-ink-500">
          Securely access your payslips and earnings record.
        </p>
      </div>

      <div className="mt-8 space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-ink-400">
          Choose your profile
        </p>
        {workers.length === 0 ? (
          <p className="rounded-lg bg-ink-100 p-4 text-sm text-ink-500">
            No staff records found yet. Ask your employer to add you.
          </p>
        ) : (
          workers.map((w) => (
            <button
              key={w.id}
              onClick={() => setSelected(w.id)}
              className={`flex w-full items-center gap-3 rounded-xl border p-3 text-left transition-colors ${
                selected === w.id
                  ? "border-brand-500 bg-brand-50"
                  : "border-ink-200 bg-white hover:bg-ink-50"
              }`}
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700">
                {initials(w.firstName, w.lastName)}
              </span>
              <span>
                <span className="block text-sm font-medium text-ink-900">
                  {w.firstName} {w.lastName}
                </span>
                <span className="block text-xs text-ink-400">{w.role}</span>
              </span>
            </button>
          ))
        )}
      </div>

      <div className="mt-auto pt-8">
        <Button className="w-full" size="lg" onClick={signIn} disabled={!selected}>
          Continue
        </Button>
        <p className="mt-3 text-center text-xs text-ink-400">
          Protected by Payday · your data stays private
        </p>
      </div>
    </div>
  );
}
