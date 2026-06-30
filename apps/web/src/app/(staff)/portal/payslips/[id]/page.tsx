"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { formatNaira, formatDate } from "@/lib/format";
import type { Payslip } from "@/lib/models";
import { downloadPayslipPdf } from "@/lib/payslip-pdf";
import { useStore } from "@/lib/store";

export default function PayslipDetailPage() {
  const params = useParams<{ id: string }>();
  const { payslips, currentStaffId } = useStore();
  const payslip = payslips.find(
    (p) => p.id === params.id && p.employeeId === currentStaffId,
  );
  const [downloading, setDownloading] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

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

  const slip = payslip;

  function downloadTxt() {
    const text = renderPayslipText(slip);
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `payslip-${slip.period.replace(/\s+/g, "-")}-${slip.reference}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  }

  function downloadPdf() {
    setPdfError(null);
    setDownloading(true);
    try {
      downloadPayslipPdf(slip);
    } catch (err) {
      setPdfError(
        err instanceof Error ? err.message : "Could not generate PDF. Please try again.",
      );
    } finally {
      setDownloading(false);
    }
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
          <p className="text-sm text-brand-100">{slip.businessName}</p>
          <h1 className="text-lg font-semibold">Payslip · {slip.period}</h1>
        </div>
        <div className="space-y-3 px-5 py-5 text-sm">
          <Line label="Employee" value={slip.employeeName} />
          <Line label="Role" value={slip.role} />
          <Line label="Paid on" value={formatDate(slip.paidAt)} />
          <Line label="Account" value={`${slip.bankName} ${slip.accountMasked}`} />
          <div className="my-2 border-t border-ink-100" />
          <Line label="Gross pay" value={formatNaira(slip.gross)} />
          <Line label="Deductions" value={formatNaira(slip.deductions)} />
          <div className="flex items-center justify-between pt-1">
            <span className="font-semibold text-ink-900">Net paid</span>
            <span className="text-lg font-semibold tabular-nums text-ink-900">
              {formatNaira(slip.net)}
            </span>
          </div>
          <div className="my-2 border-t border-ink-100" />
          <Line label="ALATPay reference" value={slip.reference} mono />
        </div>
      </Card>

      {pdfError ? (
        <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{pdfError}</p>
      ) : null}

      <Button className="w-full" size="lg" onClick={downloadPdf} disabled={downloading}>
        {downloading ? "Preparing PDF…" : "Download PDF"}
      </Button>
      <Button className="w-full" variant="secondary" onClick={downloadTxt}>
        Download TXT
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
