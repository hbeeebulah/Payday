export default function EmployerDashboard() {
  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">Manage payroll for your team in one place.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { label: "Active Employees", value: "—" },
          { label: "Monthly Payroll", value: "—" },
          { label: "Last Run", value: "—" },
        ].map((stat) => (
          <div key={stat.label} className="rounded-xl border border-border bg-white p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-400">{stat.label}</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-border bg-white p-6">
        <h2 className="text-base font-medium text-gray-900">Run Payroll</h2>
        <p className="mt-1 text-sm text-gray-500">
          Pay every employee simultaneously with a single tap. All disbursements are logged permanently.
        </p>
        <button
          type="button"
          className="mt-4 rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-brand-700"
        >
          Start Payroll Run
        </button>
      </div>
    </div>
  );
}
