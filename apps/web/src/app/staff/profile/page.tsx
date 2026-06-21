export default function StaffProfilePage() {
  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-gray-900">Profile</h1>
      <div className="rounded-2xl border border-border bg-white p-5 space-y-4">
        {[
          { label: "Full Name", value: "—" },
          { label: "Role", value: "—" },
          { label: "Bank Account", value: "—" },
        ].map((field) => (
          <div key={field.label}>
            <p className="text-xs text-gray-400">{field.label}</p>
            <p className="mt-0.5 text-sm font-medium text-gray-900">{field.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
