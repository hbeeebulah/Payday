"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  demoEmployees,
  demoPayrollRuns,
  demoReceipts,
} from "@/lib/demo-data";
import { formatNaira, formatDate, initials } from "@/lib/format";

export default function PayrollPage() {
  const [selectedRunId, setSelectedRunId] = useState(demoPayrollRuns[0].id);
  const selectedRun = demoPayrollRuns.find((r) => r.id === selectedRunId)!;

  const receiptsForRun = demoReceipts.filter(
    (r) => r.payroll_run_id === selectedRunId,
  );
  const employeeById = Object.fromEntries(
    demoEmployees.map((e) => [e.id, e]),
  );

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-ink-900">
            Payroll runs
          </h1>
          <p className="mt-1 text-sm text-ink-500">
            Fund once, pay everyone simultaneously via ALATPay.
          </p>
        </div>
        <button className="rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700">
          New payroll run
        </button>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_1.4fr]">
        <Card>
          <div className="border-b border-ink-200 px-5 py-4">
            <h2 className="text-sm font-semibold text-ink-900">History</h2>
          </div>
          <ul className="divide-y divide-ink-100">
            {demoPayrollRuns.map((run) => (
              <li key={run.id}>
                <button
                  onClick={() => setSelectedRunId(run.id)}
                  className={`flex w-full items-center justify-between px-5 py-4 text-left transition-colors ${
                    run.id === selectedRunId ? "bg-brand-50" : "hover:bg-ink-50"
                  }`}
                >
                  <div>
                    <p className="text-sm font-medium text-ink-900">
                      {run.period_label}
                    </p>
                    <p className="text-xs text-ink-400">
                      {formatNaira(run.total_funding_amount)} ·{" "}
                      {run.employee_count} staff
                    </p>
                  </div>
                  <StatusBadge status={run.status} />
                </button>
              </li>
            ))}
          </ul>
        </Card>

        <Card>
          <div className="flex items-center justify-between border-b border-ink-200 px-5 py-4">
            <div>
              <h2 className="text-sm font-semibold text-ink-900">
                {selectedRun.period_label}
              </h2>
              <p className="text-xs text-ink-400">
                Executed {formatDate(selectedRun.executed_at)}
              </p>
            </div>
            <span className="text-sm font-semibold text-ink-900">
              {formatNaira(selectedRun.total_funding_amount)}
            </span>
          </div>

          {receiptsForRun.length > 0 ? (
            <ul className="divide-y divide-ink-100">
              {receiptsForRun.map((rcpt) => {
                const emp = employeeById[rcpt.employee_id];
                return (
                  <li
                    key={rcpt.id}
                    className="flex items-center justify-between px-5 py-3"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-ink-100 text-xs font-semibold text-ink-600">
                        {emp ? initials(emp.first_name, emp.last_name) : "?"}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-ink-900">
                          {emp ? `${emp.first_name} ${emp.last_name}` : "—"}
                        </p>
                        <p className="font-mono text-xs text-ink-400">
                          {rcpt.alatpay_transaction_reference ?? "—"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-ink-900">
                        {formatNaira(rcpt.amount)}
                      </span>
                      <StatusBadge status={rcpt.distribution_state} />
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="px-5 py-8 text-center text-sm text-ink-400">
              No per-employee receipts recorded for this run yet.
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}
