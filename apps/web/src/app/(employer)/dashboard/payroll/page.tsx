"use client";

import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatNaira, formatDate } from "@/lib/format";
import { useStore } from "@/lib/store";

export default function PayrollHistoryPage() {
  const { payslips, run, business } = useStore();

  const lifetime = payslips.reduce((sum, p) => sum + p.net, 0);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-ink-900">
          Payroll history
        </h1>
        <p className="mt-1 text-sm text-ink-500">
          Every salary {business.name ? `${business.name} has` : "you have"} paid,
          on record.
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="p-5">
          <p className="text-sm font-medium text-ink-500">Lifetime disbursed</p>
          <p className="mt-2 text-2xl font-semibold tabular-nums text-ink-900">
            {formatNaira(lifetime)}
          </p>
        </Card>
        <Card className="p-5">
          <p className="text-sm font-medium text-ink-500">Payslips issued</p>
          <p className="mt-2 text-2xl font-semibold tabular-nums text-ink-900">
            {payslips.length}
          </p>
        </Card>
        <Card className="p-5">
          <p className="text-sm font-medium text-ink-500">Latest run</p>
          <p className="mt-2 text-lg font-semibold text-ink-900">
            {run.period || "—"}
          </p>
          {run.state !== "idle" ? <StatusBadge status={run.state} /> : null}
        </Card>
      </div>

      <Card>
        <div className="border-b border-ink-200 px-5 py-4">
          <h2 className="text-sm font-semibold text-ink-900">Transaction receipts</h2>
        </div>
        {payslips.length === 0 ? (
          <p className="px-5 py-10 text-center text-sm text-ink-400">
            No payouts yet. Run payroll from the dashboard to generate receipts.
          </p>
        ) : (
          <ul className="divide-y divide-ink-100">
            {payslips.map((p) => (
              <li key={p.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <p className="text-sm font-medium text-ink-900">{p.employeeName}</p>
                  <p className="font-mono text-xs text-ink-400">{p.reference}</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm font-medium tabular-nums text-ink-900">
                      {formatNaira(p.net)}
                    </p>
                    <p className="text-xs text-ink-400">{formatDate(p.paidAt)}</p>
                  </div>
                  <StatusBadge status="paid" />
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
