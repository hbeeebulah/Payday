"use client";

import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatNaira, initials } from "@/lib/format";
import type { Worker } from "@/lib/models";

export function StaffRoster({ workers }: { workers: Worker[] }) {
  return (
    <Card>
      <div className="flex items-center justify-between border-b border-ink-200 px-5 py-4">
        <h2 className="text-sm font-semibold text-ink-900">Active staff roster</h2>
        <span className="text-xs text-ink-400">{workers.length} employees</span>
      </div>
      <ul className="divide-y divide-ink-100">
        {workers.map((w) => (
          <li key={w.id} className="flex items-center justify-between px-5 py-3">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                {initials(w.firstName, w.lastName)}
              </div>
              <div>
                <p className="text-sm font-medium text-ink-900">
                  {w.firstName} {w.lastName}
                </p>
                <p className="text-xs text-ink-400">
                  {w.role} · {w.bankName}
                  {w.bankCode === "035" ? " (direct debit)" : ""}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium tabular-nums text-ink-900">
                  {formatNaira(w.salary)}
                </p>
                {w.reference ? (
                  <p className="font-mono text-[11px] text-ink-400">{w.reference}</p>
                ) : null}
              </div>
              <div className="w-20 text-right">
                <StatusBadge status={w.status} />
              </div>
            </div>
          </li>
        ))}
        {workers.length === 0 ? (
          <li className="px-5 py-10 text-center text-sm text-ink-400">
            No employees yet. Add your team to start running payroll.
          </li>
        ) : null}
      </ul>
    </Card>
  );
}
