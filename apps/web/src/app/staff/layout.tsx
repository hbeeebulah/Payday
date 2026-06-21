import Link from "next/link";

export default function StaffLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col bg-surface">
      <header className="sticky top-0 z-10 border-b border-border bg-white px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-gray-900">Payday</p>
            <p className="text-xs text-gray-400">Staff Portal</p>
          </div>
          <Link href="/" className="text-xs text-gray-400 hover:text-gray-600">
            Exit
          </Link>
        </div>
      </header>
      <main className="flex-1 px-4 py-5">{children}</main>
      <nav className="sticky bottom-0 border-t border-border bg-white px-4 py-2">
        <div className="flex justify-around">
          {[
            { href: "/staff", label: "Home" },
            { href: "/staff/payslips", label: "Payslips" },
            { href: "/staff/profile", label: "Profile" },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-md px-3 py-2 text-xs font-medium text-gray-500 hover:text-gray-900"
            >
              {item.label}
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
}
