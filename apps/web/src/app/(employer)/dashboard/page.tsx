import Link from "next/link";
import { Card, StatCard } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  demoBusiness,
  demoEmployees,
  demoPayrollRuns,
} from "@/lib/demo-data";
import { formatNaira, formatDate } from "@/lib/format";

export default function DashboardOverview() {
  const activeEmployees = demoEmployees.filter((e) => e.status === "active");
  const monthlyTotal = activeEmployees.reduce(
    (sum, e) => sum + Number(e.salary),
    0,
  );
  const lastRun = demoPayrollRuns[0];

  return (
    <div className="space-y-8">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-ink-900">
            Overview
          </h1>
          <p className="mt-1 text-sm text-ink-500">{demoBusiness.name}</p>
        </div>
        <Link
          href="/dashboard/payroll"
          className="rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700"
        >
          Run payroll
        </Link>
      </header>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Active employees"
          value={String(activeEmployees.length)}
          hint={`${demoEmployees.length} total on file`}
        />
        <StatCard
          label="Monthly payroll"
          value={formatNaira(monthlyTotal)}
          hint="Gross, active staff"
        />
        <StatCard
          label="Last run"
          value={lastRun.period_label}
          hint={`Paid ${formatDate(lastRun.completed_at)}`}
        />
      </div>

      <Card>
        <div className="flex items-center justify-between border-b border-ink-200 px-5 py-4">
          <h2 className="text-sm font-semibold text-ink-900">
            Recent payroll runs
          </h2>
          <Link
            href="/dashboard/payroll"
            className="text-sm font-medium text-brand-700 hover:text-brand-800"
          >
            View all
          </Link>
        </div>
        <ul className="divide-y divide-ink-100">
          {demoPayrollRuns.map((run) => (
            <li
              key={run.id}
              className="flex items-center justify-between px-5 py-4"
            >
              <div>
                <p className="text-sm font-medium text-ink-900">
                  {run.period_label}
                </p>
                <p className="text-xs text-ink-400">
                  {run.employee_count} employees · {formatDate(run.executed_at)}
                </p>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm font-semibold text-ink-900">
                  {formatNaira(run.total_funding_amount)}
                </span>
                <StatusBadge status={run.status} />
              </div>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
