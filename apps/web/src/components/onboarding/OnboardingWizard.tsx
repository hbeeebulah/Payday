"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Stepper } from "@/components/ui/Stepper";
import { formatNaira } from "@/lib/format";
import type { BusinessInfo, PayCycle, Wallet, Worker } from "@/lib/models";
import { DEMO_WORKERS } from "@/lib/seed";
import { completeOnboarding } from "@/lib/store";

const STEPS = ["Business", "Team", "Payouts", "Review"];

interface WorkerDraft {
  id: string;
  firstName: string;
  lastName: string;
  role: string;
  phone: string;
  salary: string;
  bankName: string;
  bankCode: string;
  accountNumber: string;
}

function emptyWorker(): WorkerDraft {
  return {
    id: crypto.randomUUID(),
    firstName: "",
    lastName: "",
    role: "",
    phone: "",
    salary: "",
    bankName: "",
    bankCode: "",
    accountNumber: "",
  };
}

const inputCls =
  "w-full rounded-lg border border-ink-200 px-3 py-2 text-sm text-ink-900 outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500";

export function OnboardingWizard() {
  const router = useRouter();
  const [step, setStep] = useState(0);

  const [business, setBusinessState] = useState<BusinessInfo>({
    name: "",
    industry: "",
    payCycle: "monthly",
    payDay: 28,
    currency: "NGN",
  });

  const [workers, setWorkers] = useState<WorkerDraft[]>([emptyWorker()]);
  const [funding, setFunding] = useState("");

  const totalPayroll = workers.reduce(
    (sum, w) => sum + (Number(w.salary) || 0),
    0,
  );
  const fundingAmount = Number(funding) || 0;

  const validWorkers = workers.filter(
    (w) => w.firstName && w.lastName && Number(w.salary) > 0 && w.accountNumber,
  );

  const canContinue = [
    business.name.trim().length > 1,
    validWorkers.length > 0,
    true,
    true,
  ][step];

  function updateWorker(id: string, patch: Partial<WorkerDraft>) {
    setWorkers((prev) => prev.map((w) => (w.id === id ? { ...w, ...patch } : w)));
  }

  function loadDemoTeam() {
    setBusinessState((prev) => ({
      ...prev,
      name: prev.name || "Mama Tunde's Pharmacy",
      industry: prev.industry || "Pharmacy & Healthcare",
    }));
    setWorkers(
      DEMO_WORKERS.map((w) => ({
        id: w.id,
        firstName: w.firstName,
        lastName: w.lastName,
        role: w.role,
        phone: w.phone,
        salary: String(w.salary),
        bankName: w.bankName,
        bankCode: w.bankCode,
        accountNumber: w.accountNumber,
      })),
    );
    setFunding("415000");
  }

  function finish() {
    const finalWorkers: Worker[] = validWorkers.map((w) => ({
      id: w.id,
      firstName: w.firstName,
      lastName: w.lastName,
      role: w.role || "Staff",
      phone: w.phone,
      salary: Number(w.salary),
      bankName: w.bankName || "Wema Bank",
      bankCode: w.bankCode || "035",
      accountNumber: w.accountNumber,
      status: "pending",
    }));

    const wallet: Wallet = {
      balance: fundingAmount,
      currency: business.currency,
      accountNumber: "0982221015",
      bankName: "Wema Bank",
      funded: fundingAmount > 0,
    };

    completeOnboarding({ business, workers: finalWorkers, wallet });
    router.push("/dashboard");
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-ink-900">
          Set up Payday
        </h1>
        <p className="mt-1 text-sm text-ink-500">
          Configure your business and team — most owners finish in under 10 minutes.
        </p>
      </header>

      <Stepper steps={STEPS} current={step} />

      <Card className="p-6">
        {step === 0 ? (
          <div className="space-y-4">
            <Field label="Business name">
              <input
                className={inputCls}
                placeholder="e.g. Mama Tunde's Pharmacy"
                value={business.name}
                onChange={(e) =>
                  setBusinessState({ ...business, name: e.target.value })
                }
              />
            </Field>
            <Field label="Industry">
              <input
                className={inputCls}
                placeholder="e.g. Pharmacy & Healthcare"
                value={business.industry}
                onChange={(e) =>
                  setBusinessState({ ...business, industry: e.target.value })
                }
              />
            </Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Pay cycle">
                <select
                  className={inputCls}
                  value={business.payCycle}
                  onChange={(e) =>
                    setBusinessState({
                      ...business,
                      payCycle: e.target.value as PayCycle,
                    })
                  }
                >
                  <option value="monthly">Monthly</option>
                  <option value="biweekly">Bi-weekly</option>
                  <option value="weekly">Weekly</option>
                </select>
              </Field>
              <Field label="Pay day (of month)">
                <input
                  type="number"
                  min={1}
                  max={31}
                  className={inputCls}
                  value={business.payDay}
                  onChange={(e) =>
                    setBusinessState({
                      ...business,
                      payDay: Number(e.target.value) || 1,
                    })
                  }
                />
              </Field>
            </div>
          </div>
        ) : null}

        {step === 1 ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-ink-500">
                Add each employee, their salary and payout account.
              </p>
              <Button size="sm" variant="secondary" onClick={loadDemoTeam}>
                Load demo team
              </Button>
            </div>
            <div className="space-y-4">
              {workers.map((w, i) => (
                <div
                  key={w.id}
                  className="rounded-lg border border-ink-200 p-4"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <span className="text-xs font-medium text-ink-400">
                      Employee {i + 1}
                    </span>
                    {workers.length > 1 ? (
                      <button
                        className="text-xs font-medium text-rose-600 hover:underline"
                        onClick={() =>
                          setWorkers((prev) => prev.filter((x) => x.id !== w.id))
                        }
                      >
                        Remove
                      </button>
                    ) : null}
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <input
                      className={inputCls}
                      placeholder="First name"
                      value={w.firstName}
                      onChange={(e) =>
                        updateWorker(w.id, { firstName: e.target.value })
                      }
                    />
                    <input
                      className={inputCls}
                      placeholder="Last name"
                      value={w.lastName}
                      onChange={(e) =>
                        updateWorker(w.id, { lastName: e.target.value })
                      }
                    />
                    <input
                      className={inputCls}
                      placeholder="Role"
                      value={w.role}
                      onChange={(e) => updateWorker(w.id, { role: e.target.value })}
                    />
                    <input
                      className={inputCls}
                      placeholder="Monthly salary (₦)"
                      inputMode="numeric"
                      value={w.salary}
                      onChange={(e) =>
                        updateWorker(w.id, {
                          salary: e.target.value.replace(/[^0-9]/g, ""),
                        })
                      }
                    />
                    <input
                      className={inputCls}
                      placeholder="Bank name"
                      value={w.bankName}
                      onChange={(e) =>
                        updateWorker(w.id, { bankName: e.target.value })
                      }
                    />
                    <input
                      className={inputCls}
                      placeholder="Account number"
                      inputMode="numeric"
                      value={w.accountNumber}
                      onChange={(e) =>
                        updateWorker(w.id, {
                          accountNumber: e.target.value.replace(/[^0-9]/g, ""),
                        })
                      }
                    />
                  </div>
                </div>
              ))}
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setWorkers((prev) => [...prev, emptyWorker()])}
            >
              + Add another employee
            </Button>
          </div>
        ) : null}

        {step === 2 ? (
          <div className="space-y-4">
            <Field label="Pre-fund your ALATPay Payroll Wallet (₦)">
              <input
                className={inputCls}
                placeholder="e.g. 415000"
                inputMode="numeric"
                value={funding}
                onChange={(e) =>
                  setFunding(e.target.value.replace(/[^0-9]/g, ""))
                }
              />
            </Field>
            <div className="rounded-lg bg-ink-50 p-4 text-sm">
              <Row label="Employees" value={String(validWorkers.length)} />
              <Row label="Total monthly payroll" value={formatNaira(totalPayroll)} />
              <Row label="Wallet funding" value={formatNaira(fundingAmount)} />
              <div className="mt-2 border-t border-ink-200 pt-2">
                {fundingAmount >= totalPayroll ? (
                  <p className="text-brand-700">
                    Wallet fully covers one payroll run.
                  </p>
                ) : (
                  <p className="text-amber-600">
                    Funding is below one run — top up before paying.
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : null}

        {step === 3 ? (
          <div className="space-y-4">
            <div className="rounded-lg bg-ink-50 p-4 text-sm">
              <Row label="Business" value={business.name || "—"} />
              <Row label="Industry" value={business.industry || "—"} />
              <Row
                label="Pay schedule"
                value={`${business.payCycle}, day ${business.payDay}`}
              />
              <Row label="Employees" value={String(validWorkers.length)} />
              <Row label="Monthly payroll" value={formatNaira(totalPayroll)} />
              <Row label="Wallet funding" value={formatNaira(fundingAmount)} />
            </div>
            <p className="text-sm text-ink-500">
              You can edit any of this later from the dashboard.
            </p>
          </div>
        ) : null}

        <div className="mt-6 flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
          >
            Back
          </Button>
          {step < STEPS.length - 1 ? (
            <Button
              onClick={() => setStep((s) => s + 1)}
              disabled={!canContinue}
            >
              Continue
            </Button>
          ) : (
            <Button onClick={finish} disabled={validWorkers.length === 0}>
              Finish setup
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-ink-700">{label}</span>
      {children}
    </label>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-0.5">
      <span className="text-ink-500">{label}</span>
      <span className="font-medium text-ink-900">{value}</span>
    </div>
  );
}
