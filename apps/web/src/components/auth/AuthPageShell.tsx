import type { ReactNode } from "react";
import { Logo } from "@/components/Logo";

interface AuthPageShellProps {
  title: string;
  subtitle: string;
  children: ReactNode;
  compact?: boolean;
}

export function AuthPageShell({
  title,
  subtitle,
  children,
  compact = false,
}: AuthPageShellProps) {
  return (
    <div
      className={`flex min-h-screen flex-col bg-ink-50 px-6 py-10 ${
        compact ? "mx-auto max-w-md" : "mx-auto max-w-lg"
      }`}
    >
      <Logo />
      <div className="mt-10">
        <h1 className="text-2xl font-semibold tracking-tight text-ink-900">{title}</h1>
        <p className="mt-1 text-sm text-ink-500">{subtitle}</p>
      </div>
      <div className="mt-8">{children}</div>
    </div>
  );
}
