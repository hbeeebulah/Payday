"use client";

import { Card } from "@/components/ui/Card";
import type { PayslipNotification } from "@/lib/models";

const CHANNEL_LABEL: Record<string, string> = {
  whatsapp: "WhatsApp",
  sms: "SMS",
};

export function NotificationsFeed({
  notifications,
}: {
  notifications: PayslipNotification[];
}) {
  return (
    <Card>
      <div className="flex items-center justify-between border-b border-ink-200 px-5 py-4">
        <h2 className="text-sm font-semibold text-ink-900">Payslip alerts</h2>
        <span className="text-xs text-ink-400">{notifications.length} sent</span>
      </div>
      {notifications.length === 0 ? (
        <p className="px-5 py-8 text-center text-sm text-ink-400">
          Payslips are dispatched automatically as each worker is paid.
        </p>
      ) : (
        <ul className="max-h-80 divide-y divide-ink-100 overflow-y-auto">
          {notifications.map((n) => (
            <li key={n.id} className="px-5 py-3">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-ink-900">{n.employeeName}</p>
                <span
                  className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
                    n.channel === "whatsapp"
                      ? "bg-brand-100 text-brand-700"
                      : "bg-blue-100 text-blue-700"
                  }`}
                >
                  {CHANNEL_LABEL[n.channel]} → {n.to}
                </span>
              </div>
              <pre className="mt-1.5 whitespace-pre-wrap font-sans text-xs leading-relaxed text-ink-500">
                {n.body}
              </pre>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
