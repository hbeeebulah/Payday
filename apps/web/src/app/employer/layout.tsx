import Link from "next/link";

const navItems = [
  { href: "/employer", label: "Overview" },
  { href: "/employer/employees", label: "Employees" },
  { href: "/employer/payroll", label: "Payroll" },
];

export default function EmployerLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-56 shrink-0 border-r border-border bg-white md:block">
        <div className="border-b border-border px-5 py-4">
          <p className="text-sm font-semibold text-gray-900">Payday</p>
          <p className="text-xs text-gray-400">Employer</p>
        </div>
        <nav className="space-y-1 p-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block rounded-md px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <div className="flex flex-1 flex-col">
        <header className="border-b border-border bg-white px-6 py-4 md:hidden">
          <p className="text-sm font-semibold">Payday — Employer</p>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
