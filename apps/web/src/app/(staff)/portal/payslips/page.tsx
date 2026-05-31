"use client";

import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatNaira, formatDate } from "@/lib/format";
import { useStore } from "@/lib/store";

export default function PayslipsPage() {
  const { workers, payslips, currentStaffId } = useStore();
  const me = workers.find((w) => w.id === currentStaffId);
  if (!me) return null;

  const myPayslips = payslips.filter((p) => p.employeeId === me.id);

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-semibold tracking-tight text-ink-900">
          Payslips
        </h1>
        <p className="text-sm text-ink-400">Every salary paid to you, on record.</p>
      </header>

      {myPayslips.length === 0 ? (
        <Card className="p-6 text-center text-sm text-ink-400">
          No payslips yet.
        </Card>
      ) : (
        <div className="space-y-3">
          {myPayslips.map((p) => (
            <Link key={p.id} href={`/portal/payslips/${p.id}`}>
              <Card className="p-4 transition-colors hover:bg-ink-50">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-ink-900">
                      {formatNaira(p.net)}
                    </p>
                    <p className="text-xs text-ink-400">
                      {p.period} · {formatDate(p.paidAt)}
                    </p>
                  </div>
                  <StatusBadge status="paid" />
                </div>
                <p className="mt-2 font-mono text-xs text-ink-400">{p.reference}</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
