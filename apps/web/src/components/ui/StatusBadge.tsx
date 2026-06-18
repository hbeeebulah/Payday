const STYLES: Record<string, string> = {
  // Payout / run statuses
  paid: "bg-brand-100 text-brand-700",
  sending: "bg-blue-100 text-blue-700",
  pending: "bg-ink-100 text-ink-600",
  failed: "bg-rose-100 text-rose-700",
  // Payroll run statuses
  completed: "bg-brand-100 text-brand-700",
  partially_completed: "bg-amber-100 text-amber-700",
  processing: "bg-blue-100 text-blue-700",
  funding: "bg-blue-100 text-blue-700",
  draft: "bg-ink-100 text-ink-600",
  cancelled: "bg-ink-100 text-ink-500",
  successful: "bg-brand-100 text-brand-700",
  reversed: "bg-amber-100 text-amber-700",
  // Employee status
  active: "bg-brand-100 text-brand-700",
  inactive: "bg-ink-100 text-ink-500",
  suspended: "bg-rose-100 text-rose-700",
};

const LABELS: Record<string, string> = {
  partially_completed: "Partial",
};

const PULSE = new Set(["sending", "processing", "funding"]);

export function StatusBadge({ status }: { status: string }) {
  const cls = STYLES[status] ?? "bg-ink-100 text-ink-600";
  const label = LABELS[status] ?? status.replace(/_/g, " ");
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${cls}`}
    >
      {PULSE.has(status) ? (
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
      ) : null}
      {label}
    </span>
  );
}
