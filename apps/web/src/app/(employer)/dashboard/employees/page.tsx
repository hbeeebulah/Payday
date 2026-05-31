"use client";

import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatNaira, initials } from "@/lib/format";
import { useStore } from "@/lib/store";

export default function EmployeesPage() {
  const { workers } = useStore();

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-ink-900">
            Employees
          </h1>
          <p className="mt-1 text-sm text-ink-500">
            Manage staff, roles and salary levels.
          </p>
        </div>
        <Link href="/onboarding">
          <Button>Add employees</Button>
        </Link>
      </header>

      <Card>
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-ink-200 text-xs uppercase tracking-wide text-ink-400">
              <th className="px-5 py-3 font-medium">Employee</th>
              <th className="px-5 py-3 font-medium">Role</th>
              <th className="px-5 py-3 font-medium">Bank</th>
              <th className="px-5 py-3 text-right font-medium">Salary</th>
              <th className="px-5 py-3 text-right font-medium">Last payout</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-100">
            {workers.map((emp) => (
              <tr key={emp.id} className="hover:bg-ink-50">
                <td className="px-5 py-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                      {initials(emp.firstName, emp.lastName)}
                    </div>
                    <div>
                      <p className="font-medium text-ink-900">
                        {emp.firstName} {emp.lastName}
                      </p>
                      <p className="text-xs text-ink-400">{emp.email}</p>
                    </div>
                  </div>
                </td>
                <td className="px-5 py-3 text-ink-600">{emp.role}</td>
                <td className="px-5 py-3 text-ink-600">
                  <p>{emp.bankName}</p>
                  <p className="text-xs text-ink-400">
                    •••• {emp.accountNumber.slice(-4)}
                  </p>
                </td>
                <td className="px-5 py-3 text-right font-medium tabular-nums text-ink-900">
                  {formatNaira(emp.salary)}
                </td>
                <td className="px-5 py-3 text-right">
                  <StatusBadge status={emp.status} />
                </td>
              </tr>
            ))}
            {workers.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-5 py-10 text-center text-sm text-ink-400">
                  No employees yet.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
