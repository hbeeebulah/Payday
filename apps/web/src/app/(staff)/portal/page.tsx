import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { demoEmployees, demoReceipts } from "@/lib/demo-data";
import { formatNaira, formatDate } from "@/lib/format";

export default function StaffHome() {
  // The signed-in staff member (demo: first employee).
  const me = demoEmployees[0];
  const myReceipts = demoReceipts.filter((r) => r.employee_id === me.id);
  const latest = myReceipts[0];

  return (
    <div className="space-y-5">
      <header>
        <p className="text-sm text-ink-500">Good morning,</p>
        <h1 className="text-xl font-semibold tracking-tight text-ink-900">
          {me.first_name} {me.last_name}
        </h1>
        <p className="text-sm text-ink-400">
          {me.role} · {me.department}
        </p>
      </header>

      <Card className="bg-brand-600 p-5 text-white">
        <p className="text-sm text-brand-100">Monthly net salary</p>
        <p className="mt-1 text-3xl font-semibold tracking-tight">
          {formatNaira(me.salary)}
        </p>
        <div className="mt-4 flex items-center justify-between text-sm text-brand-100">
          <span>Next payday</span>
          <span className="font-medium text-white">28 Jun 2026</span>
        </div>
      </Card>

      {latest ? (
        <Card className="p-5">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-ink-900">Latest payslip</p>
            <StatusBadge status={latest.distribution_state} />
          </div>
          <div className="mt-3 space-y-2 text-sm">
            <Row label="Amount" value={formatNaira(latest.amount)} />
            <Row label="Paid on" value={formatDate(latest.processed_at)} />
            <Row
              label="Reference"
              value={latest.alatpay_transaction_reference ?? "—"}
              mono
            />
          </div>
          <Link
            href="/portal/payslips"
            className="mt-4 block rounded-lg border border-ink-200 py-2.5 text-center text-sm font-medium text-ink-700 hover:bg-ink-100"
          >
            View all payslips
          </Link>
        </Card>
      ) : null}
    </div>
  );
}

function Row({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-ink-400">{label}</span>
      <span
        className={`font-medium text-ink-900 ${mono ? "font-mono text-xs" : ""}`}
      >
        {value}
      </span>
    </div>
  );
}
