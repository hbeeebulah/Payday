// Demo Day seed data: "Mama Tunde's Pharmacy".
//
// Five distinct workers whose salaries sum to exactly ₦415,000, matching a
// pre-funded ALATPay Static Wallet of ₦415,000 — a perfect one-tap run.

import type { AppState, BusinessInfo, Wallet, Worker } from "./models";

export const DEMO_BUSINESS: BusinessInfo = {
  name: "Mama Tunde's Pharmacy",
  industry: "Pharmacy & Healthcare",
  payCycle: "monthly",
  payDay: 28,
  currency: "NGN",
};

export const DEMO_WALLET: Wallet = {
  balance: 415000,
  currency: "NGN",
  accountNumber: "0982221015",
  bankName: "Wema Bank",
  funded: true,
};

// Salaries: 150,000 + 95,000 + 70,000 + 60,000 + 40,000 = 415,000.
export const DEMO_WORKERS: Worker[] = [
  {
    id: "w_tunde",
    firstName: "Tunde",
    lastName: "Bakare",
    role: "Superintendent Pharmacist",
    phone: "+2348031110001",
    email: "tunde@mamatunde.ng",
    salary: 150000,
    bankName: "GTBank",
    bankCode: "058",
    accountNumber: "0123456701",
    status: "pending",
  },
  {
    id: "w_chidinma",
    firstName: "Chidinma",
    lastName: "Okeke",
    role: "Pharmacy Technician",
    phone: "+2348031110002",
    email: "chidinma@mamatunde.ng",
    salary: 95000,
    bankName: "Wema Bank",
    bankCode: "035", // Wema -> direct-debit rail
    accountNumber: "0123456702",
    status: "pending",
  },
  {
    id: "w_emeka",
    firstName: "Emeka",
    lastName: "Nwosu",
    role: "Sales Assistant",
    phone: "+2348031110003",
    email: "emeka@mamatunde.ng",
    salary: 70000,
    bankName: "Access Bank",
    bankCode: "044",
    accountNumber: "0123456703",
    status: "pending",
  },
  {
    id: "w_aisha",
    firstName: "Aisha",
    lastName: "Bello",
    role: "Cashier",
    phone: "+2348031110004",
    email: "aisha@mamatunde.ng",
    salary: 60000,
    bankName: "UBA",
    bankCode: "033",
    accountNumber: "0123456704",
    status: "pending",
  },
  {
    id: "w_yusuf",
    firstName: "Yusuf",
    lastName: "Ibrahim",
    role: "Inventory & Logistics",
    phone: "+2348031110005",
    email: "yusuf@mamatunde.ng",
    salary: 40000,
    bankName: "Zenith Bank",
    bankCode: "057",
    accountNumber: "0123456705",
    status: "pending",
  },
];

const BLANK_BUSINESS: BusinessInfo = {
  name: "",
  industry: "",
  payCycle: "monthly",
  payDay: 28,
  currency: "NGN",
};

const BLANK_WALLET: Wallet = {
  balance: 0,
  currency: "NGN",
  accountNumber: "",
  bankName: "Wema Bank",
  funded: false,
};

function idleRun() {
  return {
    id: "",
    state: "idle" as const,
    period: "",
    total: 0,
  };
}

/** A fresh demo state seeded with Mama Tunde's Pharmacy. */
export function createDemoState(): AppState {
  return {
    hydrated: false,
    demoMode: true,
    onboarded: true,
    business: { ...DEMO_BUSINESS },
    wallet: { ...DEMO_WALLET },
    workers: DEMO_WORKERS.map((w) => ({ ...w, status: "pending", reference: undefined })),
    run: idleRun(),
    payslips: [],
    notifications: [],
    currentStaffId: null,
  };
}

/** A clean slate for a real business going through onboarding. */
export function createBlankState(): AppState {
  return {
    hydrated: false,
    demoMode: false,
    onboarded: false,
    business: { ...BLANK_BUSINESS },
    wallet: { ...BLANK_WALLET },
    workers: [],
    run: idleRun(),
    payslips: [],
    notifications: [],
    currentStaffId: null,
  };
}
