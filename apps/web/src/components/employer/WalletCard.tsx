"use client";

import { Card } from "@/components/ui/Card";
import { formatNaira } from "@/lib/format";
import type { Wallet } from "@/lib/models";

export function WalletCard({
  wallet,
  required,
}: {
  wallet: Wallet;
  required: number;
}) {
  const sufficient = wallet.balance >= required;
  return (
    <Card className="overflow-hidden">
      <div className="bg-brand-600 p-6 text-white">
        <div className="flex items-center justify-between">
          <p className="text-sm text-brand-100">ALATPay Payroll Wallet</p>
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
              wallet.funded ? "bg-white/20 text-white" : "bg-rose-500/30 text-white"
            }`}
          >
            {wallet.funded ? "Funded" : "Unfunded"}
          </span>
        </div>
        <p className="mt-3 text-4xl font-semibold tracking-tight tabular-nums">
          {formatNaira(wallet.balance)}
        </p>
        <p className="mt-1 text-sm text-brand-100">
          {wallet.bankName} · {wallet.accountNumber || "—"}
        </p>
      </div>
      <div className="flex items-center justify-between px-6 py-4 text-sm">
        <span className="text-ink-500">Required this run</span>
        <span className="flex items-center gap-2 font-medium text-ink-900">
          {formatNaira(required)}
          <span
            className={`h-2 w-2 rounded-full ${sufficient ? "bg-brand-500" : "bg-rose-500"}`}
            aria-hidden
          />
        </span>
      </div>
    </Card>
  );
}
