"use client";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { formatNaira } from "@/lib/format";
import type { AppState } from "@/lib/models";
import { canRunPayroll, payrollTotal, startPayrollRun } from "@/lib/payroll-engine";

export function RunPayrollPanel({ state }: { state: AppState }) {
  const { workers, wallet, run } = state;
  const total = payrollTotal(workers);
  const paidCount = workers.filter((w) => w.status === "paid").length;
  const running = run.state === "running";
  const completed = run.state === "completed";
  const insufficient = wallet.balance < total;
  const disabled = running || !canRunPayroll();

  const progress = workers.length ? (paidCount / workers.length) * 100 : 0;

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-base font-semibold text-ink-900">One-Tap Payroll</h2>
          <p className="mt-1 text-sm text-ink-500">
            Pay all {workers.length} employees simultaneously via ALATPay.
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-ink-400">Total payout</p>
          <p className="text-xl font-semibold tabular-nums text-ink-900">
            {formatNaira(total)}
          </p>
        </div>
      </div>

      <Button
        onClick={startPayrollRun}
        disabled={disabled}
        size="lg"
        className="mt-5 w-full"
      >
        {running ? `Paying… ${paidCount}/${workers.length}` : "Run Payroll"}
      </Button>

      {running || completed ? (
        <div className="mt-4">
          <div className="h-2 w-full overflow-hidden rounded-full bg-ink-100">
            <div
              className="h-full rounded-full bg-brand-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="mt-2 text-center text-xs text-ink-500">
            {completed
              ? `Done — ${paidCount} of ${workers.length} workers paid`
              : `Disbursing to ${workers.length} workers in parallel…`}
          </p>
        </div>
      ) : insufficient ? (
        <p className="mt-3 text-center text-xs text-rose-600">
          Wallet balance is below the required {formatNaira(total)}. Top up to run payroll.
        </p>
      ) : (
        <p className="mt-3 text-center text-xs text-ink-400">
          Funds settle to staff instantly. Payslips are sent automatically.
        </p>
      )}
    </Card>
  );
}
