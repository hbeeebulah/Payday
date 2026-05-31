import { Card } from "@/components/ui/Card";
import { demoEmployees } from "@/lib/demo-data";
import { initials } from "@/lib/format";

export default function ProfilePage() {
  const me = demoEmployees[0];

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-semibold tracking-tight text-ink-900">
          Profile
        </h1>
        <p className="text-sm text-ink-400">Your details on file.</p>
      </header>

      <Card className="flex flex-col items-center p-6 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-100 text-lg font-semibold text-brand-700">
          {initials(me.first_name, me.last_name)}
        </div>
        <p className="mt-3 text-base font-semibold text-ink-900">
          {me.first_name} {me.last_name}
        </p>
        <p className="text-sm text-ink-400">{me.role}</p>
      </Card>

      <Card className="divide-y divide-ink-100">
        <Field label="Email" value={me.email ?? "—"} />
        <Field label="Phone" value={me.phone ?? "—"} />
        <Field label="Department" value={me.department ?? "—"} />
        <Field label="Bank" value={me.bank_name ?? "—"} />
        <Field
          label="Account"
          value={`•••• ${me.bank_account_number.slice(-4)}`}
        />
      </Card>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between px-5 py-3 text-sm">
      <span className="text-ink-400">{label}</span>
      <span className="font-medium text-ink-900">{value}</span>
    </div>
  );
}
