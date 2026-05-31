// Typed client for the Payday backend API.
//
// All requests go through the Next.js rewrite proxy (/api/* -> FastAPI), so the
// browser only ever talks to its own origin. Server components can pass an
// absolute base URL via the API_PROXY_URL env var.

import type {
  Business,
  Employee,
  PayrollRun,
  TransactionReceipt,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API ${res.status}: ${detail}`);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listBusinesses: () => request<Business[]>("/businesses"),
  getBusiness: (id: string) => request<Business>(`/businesses/${id}`),

  listEmployees: (businessId: string) =>
    request<Employee[]>(`/businesses/${businessId}/employees`),

  listPayrollRuns: (businessId: string) =>
    request<PayrollRun[]>(`/businesses/${businessId}/payroll-runs`),

  createPayrollRun: (businessId: string, periodLabel: string) =>
    request<PayrollRun>(`/businesses/${businessId}/payroll-runs`, {
      method: "POST",
      body: JSON.stringify({ period_label: periodLabel }),
    }),

  executePayrollRun: (businessId: string, runId: string) =>
    request<PayrollRun & { receipts: TransactionReceipt[] }>(
      `/businesses/${businessId}/payroll-runs/${runId}/execute`,
      { method: "POST" },
    ),
};
