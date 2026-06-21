export default function PayrollPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Payroll History</h1>
        <p className="mt-1 text-sm text-gray-500">
          Permanent record of every payroll run, funding total, and ALATPay transaction.
        </p>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-border bg-gray-50 text-xs uppercase tracking-wide text-gray-400">
            <tr>
              <th className="px-5 py-3 font-medium">Executed</th>
              <th className="px-5 py-3 font-medium">Total Funded</th>
              <th className="px-5 py-3 font-medium">ALATPay Ref</th>
              <th className="px-5 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={4} className="px-5 py-8 text-center text-gray-400">
                No payroll runs yet.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
