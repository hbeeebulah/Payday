"use client";

import { useSyncExternalStore } from "react";

export type UserRole = "staff" | "employer";

export interface AuthUser {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  role: UserRole;
}

export interface AuthSession {
  token: string;
  user: AuthUser;
}

export interface RegisterInput {
  firstName: string;
  lastName: string;
  role: UserRole;
  phone: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

const AUTH_KEY = "payday:auth:v1";
const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";

let session: AuthSession | null = null;
let authHydrated = false;
const listeners = new Set<() => void>();

function emit() {
  for (const listener of listeners) listener();
}

function persist() {
  if (typeof window === "undefined") return;
  try {
    if (session) {
      window.localStorage.setItem(AUTH_KEY, JSON.stringify(session));
    } else {
      window.localStorage.removeItem(AUTH_KEY);
    }
  } catch {
    // ignore storage errors
  }
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function mapUser(raw: Record<string, unknown>): AuthUser {
  return {
    id: String(raw.id),
    firstName: String(raw.first_name),
    lastName: String(raw.last_name),
    email: String(raw.email),
    phone: String(raw.phone),
    role: raw.role as UserRole,
  };
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((item) => item.msg ?? JSON.stringify(item)).join(", ");
    }
  } catch {
    // fall through
  }
  return `Request failed (${res.status})`;
}

async function authRequest(path: string, init?: RequestInit): Promise<AuthSession> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(await parseError(res));
  }

  const data = (await res.json()) as {
    access_token: string;
    user: Record<string, unknown>;
  };

  return {
    token: data.access_token,
    user: mapUser(data.user),
  };
}

export function getAuthSession(): AuthSession | null {
  return session;
}

export function isAuthHydrated(): boolean {
  return authHydrated;
}

export function isAuthenticated(role?: UserRole): boolean {
  if (!session) return false;
  if (role && session.user.role !== role) return false;
  return true;
}

export function hydrateAuth(): void {
  if (typeof window === "undefined") return;
  try {
    const raw = window.localStorage.getItem(AUTH_KEY);
    session = raw ? (JSON.parse(raw) as AuthSession) : null;
  } catch {
    session = null;
  }
  authHydrated = true;
  emit();

  window.addEventListener("storage", (event) => {
    if (event.key !== AUTH_KEY) return;
    try {
      session = event.newValue ? (JSON.parse(event.newValue) as AuthSession) : null;
      emit();
    } catch {
      session = null;
      emit();
    }
  });
}

export function useAuth(): AuthSession | null {
  return useSyncExternalStore(subscribe, () => session, () => null);
}

export async function registerUser(input: RegisterInput): Promise<AuthSession> {
  const next = await authRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      first_name: input.firstName.trim(),
      last_name: input.lastName.trim(),
      role: input.role,
      phone: input.phone.trim(),
      email: input.email.trim().toLowerCase(),
      password: input.password,
      confirm_password: input.confirmPassword,
    }),
  });
  session = next;
  persist();
  emit();
  return next;
}

export async function loginUser(input: LoginInput): Promise<AuthSession> {
  const next = await authRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({
      email: input.email.trim().toLowerCase(),
      password: input.password,
    }),
  });
  session = next;
  persist();
  emit();
  return next;
}

export function logoutUser(): void {
  session = null;
  persist();
  emit();
}

export function authHeaders(): Record<string, string> {
  if (!session?.token) return {};
  return { Authorization: `Bearer ${session.token}` };
}
