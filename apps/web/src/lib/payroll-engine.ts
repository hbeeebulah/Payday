// Payroll simulation engine for the live Demo Day sequence.
//
// On "Run Payroll", every worker row transitions Pending -> Sending -> Paid
// across a crisp ~8 second window. As each worker is confirmed paid, the wallet
// balance ticks down, a payslip is generated, and a WhatsApp/SMS payslip alert
// is dispatched (mocked) — mirroring concurrent webhook receipts.

import type { Payslip, Worker } from "./models";
import { buildNotification } from "./notifications";
import { getState, setState } from "./store";

// Per-worker timing (ms) tuned for five workers inside an 8s window.
const SENDING_AT = [500, 1400, 2300, 3200, 4100];
const PAID_AT = [3200, 4300, 5400, 6500, 7600];
const RUN_WINDOW = 8000;

let timers: ReturnType<typeof setTimeout>[] = [];

function clearTimers() {
  for (const t of timers) clearTimeout(t);
  timers = [];
}

function randomRef(): string {
  const hex = Math.random().toString(16).slice(2, 8).toUpperCase();
  return `ALT-${hex}`;
}

function periodLabel(): string {
  return new Date().toLocaleDateString("en-NG", {
    month: "long",
    year: "numeric",
  });
}

function maskAccount(accountNumber: string): string {
  return `••••${accountNumber.slice(-4)}`;
}

export function payrollTotal(workers: Worker[]): number {
  return workers.reduce((sum, w) => sum + w.salary, 0);
}

export function canRunPayroll(): boolean {
  const { workers, wallet, run } = getState();
  if (run.state === "running") return false;
  if (workers.length === 0) return false;
  return wallet.balance >= payrollTotal(workers);
}

/** Begin the simulated payroll run. */
export function startPayrollRun(): void {
  const snapshot = getState();
  if (snapshot.run.state === "running") return;

  const workers = snapshot.workers;
  if (workers.length === 0) return;

  const total = payrollTotal(workers);
  const period = periodLabel();
  const runId = `run_${Date.now()}`;

  clearTimers();

  // Reset every row to pending and open the run.
  setState((prev) => ({
    run: {
      id: runId,
      state: "running",
      period,
      total,
      startedAt: new Date().toISOString(),
    },
    workers: prev.workers.map((w) => ({ ...w, status: "pending", reference: undefined })),
    payslips: prev.payslips.filter((p) => p.runId !== runId),
    notifications: prev.notifications.filter((n) => !n.reference.startsWith(runId)),
  }));

  workers.forEach((worker, index) => {
    const sendingAt = SENDING_AT[index] ?? 500 + index * 700;
    const paidAt = PAID_AT[index] ?? 3200 + index * 1000;

    timers.push(
      setTimeout(() => {
        setState((prev) => ({
          workers: prev.workers.map((w) =>
            w.id === worker.id ? { ...w, status: "sending" } : w,
          ),
        }));
      }, sendingAt),
    );

    timers.push(
      setTimeout(() => {
        markPaid(worker, runId, period, index);
      }, paidAt),
    );
  });

  timers.push(
    setTimeout(() => {
      setState((prev) => ({
        run: { ...prev.run, state: "completed", completedAt: new Date().toISOString() },
      }));
    }, RUN_WINDOW),
  );
}

function markPaid(worker: Worker, runId: string, period: string, index: number): void {
  const reference = randomRef();
  const paidAt = new Date().toISOString();

  const payslip: Payslip = {
    id: `slip_${reference}`,
    runId,
    employeeId: worker.id,
    employeeName: `${worker.firstName} ${worker.lastName}`,
    role: worker.role,
    businessName: getState().business.name,
    period,
    gross: worker.salary,
    deductions: 0,
    net: worker.salary,
    currency: getState().wallet.currency,
    reference,
    paidAt,
    bankName: worker.bankName,
    accountMasked: maskAccount(worker.accountNumber),
  };

  const notification = buildNotification(worker, payslip, index);

  setState((prev) => ({
    workers: prev.workers.map((w) =>
      w.id === worker.id ? { ...w, status: "paid", reference } : w,
    ),
    wallet: { ...prev.wallet, balance: Math.max(0, prev.wallet.balance - worker.salary) },
    payslips: [payslip, ...prev.payslips.filter((p) => p.employeeId !== worker.id || p.runId !== runId)],
    notifications: [notification, ...prev.notifications],
  }));
}

/** Cancel any in-flight run and reset rows to pending (does not refund wallet). */
export function resetRun(): void {
  clearTimers();
  setState((prev) => ({
    run: { id: "", state: "idle", period: "", total: 0 },
    workers: prev.workers.map((w) => ({ ...w, status: "pending", reference: undefined })),
  }));
}
