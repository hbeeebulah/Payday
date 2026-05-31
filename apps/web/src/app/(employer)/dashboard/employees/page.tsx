import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { demoEmployees } from "@/lib/demo-data";
import { formatNaira, initials } from "@/lib/format";

export default function EmployeesPage() {
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
        <button className="rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700">
          Add employee
        </button>
      </header>

      <Card>
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-ink-200 text-xs uppercase tracking-wide text-ink-400">
              <th className="px-5 py-3 font-medium">Employee</th>
              <th className="px-5 py-3 font-medium">Role</th>
              <th className="px-5 py-3 font-medium">Bank</th>
              <th className="px-5 py-3 text-right font-medium">Salary</th>
              <th className="px-5 py-3 text-right font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-100">
            {demoEmployees.map((emp) => (
              <tr key={emp.id} className="hover:bg-ink-50">
                <td className="px-5 py-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                      {initials(emp.first_name, emp.last_name)}
                    </div>
                    <div>
                      <p className="font-medium text-ink-900">
                        {emp.first_name} {emp.last_name}
                      </p>
                      <p className="text-xs text-ink-400">{emp.email}</p>
                    </div>
                  </div>
                </td>
                <td className="px-5 py-3 text-ink-600">{emp.role}</td>
                <td className="px-5 py-3 text-ink-600">
                  <p>{emp.bank_name}</p>
                  <p className="text-xs text-ink-400">
                    •••• {emp.bank_account_number.slice(-4)}
                  </p>
                </td>
                <td className="px-5 py-3 text-right font-medium text-ink-900">
                  {formatNaira(emp.salary)}
                </td>
                <td className="px-5 py-3 text-right">
                  <StatusBadge status={emp.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
