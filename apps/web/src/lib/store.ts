"use client";

// A tiny global store shared across the employer dashboard and the staff
// portal. It is backed by localStorage and the browser `storage` event, so a
// payroll run on the dashboard streams "real-time" into any open portal tab.
//
// Components subscribe via `useStore()` (React's useSyncExternalStore); code
// outside React (the payroll simulation engine) uses `getState`/`setState`.

import { useSyncExternalStore } from "react";

import type { AppState, BusinessInfo, Wallet, Worker } from "./models";
import { createBlankState, createDemoState } from "./seed";

const STORAGE_KEY = "payday:state:v1";

// Stable snapshot used during SSR and the first client render (kept identical
// on both sides so there is no hydration mismatch).
const serverSnapshot: AppState = createDemoState();

let state: AppState = createDemoState();
const listeners = new Set<() => void>();

function emit() {
  for (const listener of listeners) listener();
}

function persist() {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore quota / serialization errors in this demo store.
  }
}

export function getState(): AppState {
  return state;
}

type Updater = Partial<AppState> | ((prev: AppState) => Partial<AppState>);

export function setState(updater: Updater): void {
  const partial = typeof updater === "function" ? updater(state) : updater;
  state = { ...state, ...partial };
  persist();
  emit();
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** Hydrate from localStorage. Call once on the client after mount. */
export function hydrate(): void {
  if (typeof window === "undefined") return;
  let next: AppState | null = null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw) next = JSON.parse(raw) as AppState;
  } catch {
    next = null;
  }
  state = { ...(next ?? state), hydrated: true };
  emit();

  window.addEventListener("storage", (event) => {
    if (event.key !== STORAGE_KEY || !event.newValue) return;
    try {
      state = { ...(JSON.parse(event.newValue) as AppState), hydrated: true };
      emit();
    } catch {
      // ignore malformed cross-tab payloads
    }
  });
}

export function useStore(): AppState {
  return useSyncExternalStore(
    subscribe,
    () => state,
    () => serverSnapshot,
  );
}

// --- Actions ---------------------------------------------------------------

export function loadDemo(): void {
  setState({ ...createDemoState(), hydrated: true });
}

export function clearToBlank(): void {
  setState({ ...createBlankState(), hydrated: true });
}

export function setBusiness(business: BusinessInfo): void {
  setState({ business });
}

export function setWallet(wallet: Wallet): void {
  setState({ wallet });
}

export function setWorkers(workers: Worker[]): void {
  setState({ workers });
}

export function completeOnboarding(payload: {
  business: BusinessInfo;
  workers: Worker[];
  wallet: Wallet;
}): void {
  setState({
    business: payload.business,
    workers: payload.workers.map((w) => ({ ...w, status: "pending", reference: undefined })),
    wallet: payload.wallet,
    onboarded: true,
    demoMode: false,
    run: { id: "", state: "idle", period: "", total: 0 },
    payslips: [],
    notifications: [],
  });
}

export function loginStaff(staffId: string): void {
  setState({ currentStaffId: staffId });
}

export function logoutStaff(): void {
  setState({ currentStaffId: null });
}
