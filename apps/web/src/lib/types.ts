// Domain types mirroring the Payday FastAPI backend schemas.

export type EmployeeStatus = "active" | "inactive" | "suspended";

export type PayrollRunStatus =
  | "draft"
  | "funding"
  | "processing"
  | "completed"
  | "partially_completed"
  | "failed"
  | "cancelled";

export type DistributionState =
  | "pending"
  | "processing"
  | "successful"
  | "failed"
  | "reversed";

export interface Business {
  id: string;
  name: string;
  legal_name: string | null;
  registration_number: string | null;
  industry: string | null;
  email: string;
  phone: string | null;
  address: string | null;
  country: string;
  created_at: string;
  updated_at: string;
}

export interface Employee {
  id: string;
  business_id: string;
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string | null;
  role: string;
  department: string | null;
  salary: string;
  currency: string;
  bank_name: string | null;
  bank_account_number: string;
  bank_account_name: string | null;
  bank_routing_code: string;
  status: EmployeeStatus;
}

export interface TransactionReceipt {
  id: string;
  payroll_run_id: string;
  employee_id: string;
  amount: string;
  currency: string;
  distribution_state: DistributionState;
  alatpay_transaction_reference: string | null;
  processed_at: string | null;
  failure_reason: string | null;
}

export interface PayrollRun {
  id: string;
  business_id: string;
  period_label: string;
  status: PayrollRunStatus;
  total_funding_amount: string;
  currency: string;
  employee_count: number;
  executed_at: string | null;
  completed_at: string | null;
  created_at: string;
}
