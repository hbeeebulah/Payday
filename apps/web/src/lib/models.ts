// Client-side domain models for the interactive Payday UI.
// These power the shared store, the payroll simulation, and the staff portal.

export type PayoutStatus = "pending" | "sending" | "paid" | "failed";

export interface Worker {
  id: string;
  firstName: string;
  lastName: string;
  role: string;
  phone: string;
  email?: string;
  salary: number; // monthly gross, NGN
  bankName: string;
  bankCode: string; // 035 = Wema (direct-debit rail)
  accountNumber: string;
  status: PayoutStatus; // live status during a run
  reference?: string; // latest ALATPay transaction reference
}

export type PayCycle = "monthly" | "biweekly" | "weekly";

export interface BusinessInfo {
  name: string;
  industry: string;
  payCycle: PayCycle;
  payDay: number; // day of month
  currency: string;
}

export interface Wallet {
  balance: number;
  currency: string;
  accountNumber: string;
  bankName: string;
  funded: boolean;
}

export type RunState = "idle" | "running" | "completed";

export interface PayrollRunMeta {
  id: string;
  state: RunState;
  period: string;
  total: number;
  startedAt?: string;
  completedAt?: string;
}

export interface Payslip {
  id: string;
  runId: string;
  employeeId: string;
  employeeName: string;
  role: string;
  businessName: string;
  period: string;
  gross: number;
  deductions: number;
  net: number;
  currency: string;
  reference: string;
  paidAt: string;
  bankName: string;
  accountMasked: string;
}

export type NotificationChannel = "whatsapp" | "sms";

export interface PayslipNotification {
  id: string;
  channel: NotificationChannel;
  to: string;
  employeeId: string;
  employeeName: string;
  reference: string;
  body: string;
  sentAt: string;
}

export interface AppState {
  hydrated: boolean;
  demoMode: boolean;
  onboarded: boolean;
  business: BusinessInfo;
  wallet: Wallet;
  workers: Worker[];
  run: PayrollRunMeta;
  payslips: Payslip[];
  notifications: PayslipNotification[];
  currentStaffId: string | null;
}
