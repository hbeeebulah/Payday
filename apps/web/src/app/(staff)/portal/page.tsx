"use client";

import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useAuth } from "@/lib/auth";
import { formatNaira, formatDate } from "@/lib/format";
import { useStore } from "@/lib/store";

export default function StaffHome() {
  const auth = useAuth();
  const { workers, payslips, currentStaffId, business } = useStore();
  const me = workers.find((w) => w.id === currentStaffId);
  const authUser = auth?.user.role === "staff" ? auth.user : null;

  if (!me && !authUser) return null;

  const displayName = me
    ? `${me.firstName} ${me.lastName}`
    : `${authUser!.firstName} ${authUser!.lastName}`;
  const displayRole = me?.role ?? "Staff member";
  const employeeId = me?.id ?? authUser!.id;

  const myPayslips = payslips.filter((p) => p.employeeId === employeeId);
  const latest = myPayslips[0];

  return (
    <div className="space-y-5">
      <header>
        <p className="text-sm text-ink-500">Welcome back,</p>
        <h1 className="text-xl font-semibold tracking-tight text-ink-900">
          {displayName}
        </h1>
        <p className="text-sm text-ink-400">
          {displayRole} · {business.name}
        </p>
      </header>

      {me ? (
        <Card className="bg-brand-600 p-5 text-white">
          <p className="text-sm text-brand-100">Monthly salary</p>
          <p className="mt-1 text-3xl font-semibold tabular-nums tracking-tight">
            {formatNaira(me.salary)}
          </p>
          <div className="mt-4 flex items-center justify-between text-sm text-brand-100">
            <span>Paid to</span>
            <span className="font-medium text-white">
              {me.bankName} ••••{me.accountNumber.slice(-4)}
            </span>
          </div>
        </Card>
      ) : null}

      {latest ? (
        <Card className="p-5">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-ink-900">Latest payslip</p>
            <StatusBadge status="paid" />
          </div>
          <div className="mt-3 space-y-2 text-sm">
            <Row label="Period" value={latest.period} />
            <Row label="Amount" value={formatNaira(latest.net)} />
            <Row label="Paid on" value={formatDate(latest.paidAt)} />
            <Row label="Reference" value={latest.reference} mono />
          </div>
          <Link
            href={`/portal/payslips/${latest.id}`}
            className="mt-4 block rounded-lg bg-brand-600 py-2.5 text-center text-sm font-semibold text-white hover:bg-brand-700"
          >
            View &amp; download payslip
          </Link>
        </Card>
      ) : (
        <Card className="p-6 text-center">
          <p className="text-sm text-ink-500">
            No payslips yet. They appear here the moment you&apos;re paid.
          </p>
        </Card>
      )}
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
      <span className={`font-medium text-ink-900 ${mono ? "font-mono text-xs" : ""}`}>
        {value}
      </span>
    </div>
  );
}
