import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { demoEmployees, demoReceipts } from "@/lib/demo-data";
import { formatNaira, formatDate } from "@/lib/format";

export default function PayslipsPage() {
  const me = demoEmployees[0];
  const myReceipts = demoReceipts.filter((r) => r.employee_id === me.id);

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-semibold tracking-tight text-ink-900">
          Payslips
        </h1>
        <p className="text-sm text-ink-400">
          Every salary paid to you, on record.
        </p>
      </header>

      <div className="space-y-3">
        {myReceipts.map((rcpt) => (
          <Card key={rcpt.id} className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-ink-900">
                  {formatNaira(rcpt.amount)}
                </p>
                <p className="text-xs text-ink-400">
                  {formatDate(rcpt.processed_at)}
                </p>
              </div>
              <StatusBadge status={rcpt.distribution_state} />
            </div>
            <p className="mt-2 font-mono text-xs text-ink-400">
              {rcpt.alatpay_transaction_reference ?? "—"}
            </p>
          </Card>
        ))}
      </div>
    </div>
  );
}
