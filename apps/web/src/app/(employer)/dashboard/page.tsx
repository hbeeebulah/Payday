"use client";

import Link from "next/link";
import { DemoControls } from "@/components/employer/DemoControls";
import { NotificationsFeed } from "@/components/employer/NotificationsFeed";
import { RunPayrollPanel } from "@/components/employer/RunPayrollPanel";
import { StaffRoster } from "@/components/employer/StaffRoster";
import { WalletCard } from "@/components/employer/WalletCard";
import { Button } from "@/components/ui/Button";
import { payrollTotal } from "@/lib/payroll-engine";
import { useStore } from "@/lib/store";

export default function DashboardPage() {
  const state = useStore();
  const total = payrollTotal(state.workers);

  if (state.workers.length === 0) {
    return (
      <div className="mx-auto max-w-lg py-16 text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-ink-900">
          Let&apos;s set up your payroll
        </h1>
        <p className="mt-2 text-sm text-ink-500">
          Add your business and team to start paying everyone in one tap.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Link href="/onboarding">
            <Button>Start setup</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-ink-900">
            {state.business.name}
          </h1>
          <p className="mt-1 text-sm text-ink-500">
            One-Tap Payroll Dashboard · {state.business.payCycle} on day{" "}
            {state.business.payDay}
          </p>
        </div>
        <DemoControls state={state} />
      </header>

      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <div className="space-y-6">
          <WalletCard wallet={state.wallet} required={total} />
          <RunPayrollPanel state={state} />
        </div>
        <div className="space-y-6">
          <StaffRoster workers={state.workers} />
          <NotificationsFeed notifications={state.notifications} />
        </div>
      </div>
    </div>
  );
}
