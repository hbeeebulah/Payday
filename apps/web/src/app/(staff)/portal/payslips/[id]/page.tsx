"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { formatNaira, formatDate } from "@/lib/format";
import type { Payslip } from "@/lib/models";
import { useStore } from "@/lib/store";

export default function PayslipDetailPage() {
  const params = useParams<{ id: string }>();
  const { payslips, currentStaffId } = useStore();
  const payslip = payslips.find(
    (p) => p.id === params.id && p.employeeId === currentStaffId,
  );

  if (!payslip) {
    return (
      <div className="py-16 text-center">
        <p className="text-sm text-ink-500">Payslip not found.</p>
        <Link
          href="/portal/payslips"
          className="mt-3 inline-block text-sm font-medium text-brand-700"
        >
          Back to payslips
        </Link>
      </div>
    );
  }

  function download() {
    if (!payslip) return;
    const text = renderPayslipText(payslip);
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `payslip-${payslip.period.replace(/\s+/g, "-")}-${payslip.reference}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-4">
      <Link
        href="/portal/payslips"
        className="text-sm font-medium text-ink-500 hover:text-ink-900"
      >
        ← Payslips
      </Link>

      <Card className="overflow-hidden">
        <div className="bg-brand-600 px-5 py-5 text-white">
          <p className="text-sm text-brand-100">{payslip.businessName}</p>
          <h1 className="text-lg font-semibold">Payslip · {payslip.period}</h1>
        </div>
        <div className="space-y-3 px-5 py-5 text-sm">
          <Line label="Employee" value={payslip.employeeName} />
          <Line label="Role" value={payslip.role} />
          <Line label="Paid on" value={formatDate(payslip.paidAt)} />
          <Line label="Account" value={`${payslip.bankName} ${payslip.accountMasked}`} />
          <div className="my-2 border-t border-ink-100" />
          <Line label="Gross pay" value={formatNaira(payslip.gross)} />
          <Line label="Deductions" value={formatNaira(payslip.deductions)} />
          <div className="flex items-center justify-between pt-1">
            <span className="font-semibold text-ink-900">Net paid</span>
            <span className="text-lg font-semibold tabular-nums text-ink-900">
              {formatNaira(payslip.net)}
            </span>
          </div>
          <div className="my-2 border-t border-ink-100" />
          <Line label="ALATPay reference" value={payslip.reference} mono />
        </div>
      </Card>

      <Button className="w-full" size="lg" onClick={download}>
        Download payslip
      </Button>
      <p className="text-center text-xs text-ink-400">
        Keep this as proof of income for loans and tenancy applications.
      </p>
    </div>
  );
}

function renderPayslipText(p: Payslip): string {
  return [
    `${p.businessName} — PAYSLIP`,
    `Period: ${p.period}`,
    `Employee: ${p.employeeName} (${p.role})`,
    `Paid on: ${new Date(p.paidAt).toLocaleString("en-NG")}`,
    `Account: ${p.bankName} ${p.accountMasked}`,
    `--------------------------------`,
    `Gross pay: ${formatNaira(p.gross)}`,
    `Deductions: ${formatNaira(p.deductions)}`,
    `Net paid: ${formatNaira(p.net)}`,
    `--------------------------------`,
    `ALATPay reference: ${p.reference}`,
    `Issued by Payday · payday.ng`,
  ].join("\n");
}

function Line({
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
