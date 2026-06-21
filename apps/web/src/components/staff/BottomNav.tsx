"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/portal", label: "Home", icon: "⌂" },
  { href: "/portal/payslips", label: "Payslips", icon: "▤" },
  { href: "/portal/profile", label: "Profile", icon: "○" },
];

export function BottomNav() {
  const pathname = usePathname();
  return (
    <nav className="sticky bottom-0 border-t border-ink-200 bg-white">
      <ul className="mx-auto flex max-w-md">
        {TABS.map((tab) => {
          const active =
            tab.href === "/portal"
              ? pathname === tab.href
              : pathname.startsWith(tab.href);
          return (
            <li key={tab.href} className="flex-1">
              <Link
                href={tab.href}
                className={`flex flex-col items-center gap-1 py-3 text-xs font-medium ${
                  active ? "text-brand-700" : "text-ink-400"
                }`}
              >
                <span className="text-lg leading-none">{tab.icon}</span>
                {tab.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
