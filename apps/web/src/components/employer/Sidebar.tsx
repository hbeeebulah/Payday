"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo } from "@/components/Logo";
import { useStore } from "@/lib/store";

const NAV = [
  { href: "/dashboard", label: "Run Payroll", icon: "₦" },
  { href: "/dashboard/employees", label: "Employees", icon: "☷" },
  { href: "/dashboard/payroll", label: "History", icon: "▦" },
  { href: "/onboarding", label: "Setup wizard", icon: "✦" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { business } = useStore();

  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-ink-200 bg-white">
      <div className="px-6 py-6">
        <Logo />
      </div>
      <nav className="flex-1 space-y-1 px-3">
        {NAV.map((item) => {
          const active =
            item.href === "/dashboard"
              ? pathname === item.href
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? "bg-brand-50 text-brand-700"
                  : "text-ink-600 hover:bg-ink-100 hover:text-ink-900"
              }`}
            >
              <span className="w-4 text-center text-ink-400">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-ink-200 p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-ink-200 text-sm font-semibold text-ink-700">
            {(business.name || "P").charAt(0)}
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-ink-900">
              {business.name || "Payday"}
            </p>
            <p className="truncate text-xs text-ink-400">Employer account</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
