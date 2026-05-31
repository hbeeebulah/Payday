import type { DistributionState, PayrollRunStatus } from "@/lib/types";

const STYLES: Record<string, string> = {
  // Payroll run statuses
  completed: "bg-brand-100 text-brand-700",
  partially_completed: "bg-amber-100 text-amber-700",
  processing: "bg-blue-100 text-blue-700",
  funding: "bg-blue-100 text-blue-700",
  draft: "bg-ink-100 text-ink-600",
  failed: "bg-rose-100 text-rose-700",
  cancelled: "bg-ink-100 text-ink-500",
  // Distribution states
  successful: "bg-brand-100 text-brand-700",
  pending: "bg-ink-100 text-ink-600",
  reversed: "bg-amber-100 text-amber-700",
  // Employee status
  active: "bg-brand-100 text-brand-700",
  inactive: "bg-ink-100 text-ink-500",
  suspended: "bg-rose-100 text-rose-700",
};

const LABELS: Record<string, string> = {
  partially_completed: "Partial",
};

export function StatusBadge({
  status,
}: {
  status: PayrollRunStatus | DistributionState | string;
}) {
  const cls = STYLES[status] ?? "bg-ink-100 text-ink-600";
  const label = LABELS[status] ?? status.replace(/_/g, " ");
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${cls}`}
    >
      {label}
    </span>
  );
}
