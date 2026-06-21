export default function StaffHomePage() {
  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Welcome back</p>
        <h1 className="mt-1 text-xl font-semibold text-gray-900">Your Payslip</h1>
      </div>

      <div className="rounded-2xl border border-border bg-white p-5 shadow-sm">
        <p className="text-xs text-gray-400">Latest salary</p>
        <p className="mt-1 text-3xl font-semibold text-gray-900">—</p>
        <p className="mt-1 text-sm text-gray-500">No payments recorded yet</p>
      </div>

      <div className="rounded-2xl border border-border bg-white p-5">
        <h2 className="text-sm font-medium text-gray-900">Recent Activity</h2>
        <p className="mt-3 text-sm text-gray-400">Your payment history will appear here.</p>
      </div>
    </div>
  );
}
