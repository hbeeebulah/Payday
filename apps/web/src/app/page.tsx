import Link from "next/link";
import { Logo } from "@/components/Logo";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-ink-50">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6">
        <Logo />
        <nav className="flex items-center gap-3 text-sm font-medium">
          <Link
            href="/portal"
            className="rounded-lg px-3 py-2 text-ink-600 hover:text-ink-900"
          >
            Staff portal
          </Link>
          <Link
            href="/dashboard"
            className="rounded-lg bg-brand-600 px-4 py-2 text-white hover:bg-brand-700"
          >
            Open dashboard
          </Link>
        </nav>
      </header>

      <section className="mx-auto max-w-3xl px-6 pb-16 pt-12 text-center">
        <span className="inline-flex items-center rounded-full bg-brand-100 px-3 py-1 text-xs font-medium text-brand-700">
          Payroll for Nigerian small businesses
        </span>
        <h1 className="mt-6 text-4xl font-bold tracking-tight text-ink-900 sm:text-5xl">
          Pay your whole team in a single tap.
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-lg text-ink-600">
          Payday pays every employee simultaneously, on time, every month — with
          automatic payslips and a clean digital record of every salary ever
          paid. Powered by ALATPay.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/onboarding"
            className="rounded-lg bg-brand-600 px-5 py-3 text-sm font-semibold text-white shadow-sm hover:bg-brand-700"
          >
            Set up in 10 minutes
          </Link>
          <Link
            href="/dashboard"
            className="rounded-lg border border-ink-200 bg-white px-5 py-3 text-sm font-semibold text-ink-700 hover:bg-ink-100"
          >
            One-Tap dashboard
          </Link>
          <Link
            href="/portal"
            className="rounded-lg px-5 py-3 text-sm font-semibold text-ink-600 hover:text-ink-900"
          >
            Staff portal
          </Link>
        </div>
      </section>

      <section className="mx-auto grid max-w-5xl gap-4 px-6 pb-24 sm:grid-cols-3">
        {[
          {
            title: "One tap, everyone paid",
            body: "Fund once and disburse to every employee in parallel through ALATPay.",
          },
          {
            title: "Automatic payslips",
            body: "Each payout pushes a WhatsApp/SMS payslip with its unique reference.",
          },
          {
            title: "Verified earnings",
            body: "Staff keep an auditable record to unlock loans and tenancy applications.",
          },
        ].map((f) => (
          <div
            key={f.title}
            className="rounded-xl border border-ink-200 bg-white p-6 shadow-card"
          >
            <h3 className="text-base font-semibold text-ink-900">{f.title}</h3>
            <p className="mt-2 text-sm text-ink-600">{f.body}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
