// Mock external alert service.
//
// In production this would call a WhatsApp Business / SMS provider. Here it
// composes the exact payslip message that would be pushed to each worker the
// moment their payout is confirmed paid.

import { formatNaira } from "./format";
import type {
  NotificationChannel,
  Payslip,
  PayslipNotification,
  Worker,
} from "./models";

export function pickChannel(index: number): NotificationChannel {
  // Alternate channels to showcase both rails.
  return index % 2 === 0 ? "whatsapp" : "sms";
}

export function buildPayslipMessage(payslip: Payslip): string {
  return [
    `${payslip.businessName} has paid your ${payslip.period} salary.`,
    `Gross: ${formatNaira(payslip.gross)}`,
    `Net: ${formatNaira(payslip.net)}`,
    `Ref: ${payslip.reference}`,
    `View & download your payslip: payday.ng/portal`,
  ].join("\n");
}

export function buildNotification(
  worker: Worker,
  payslip: Payslip,
  index: number,
): PayslipNotification {
  return {
    id: `ntf_${payslip.reference}`,
    channel: pickChannel(index),
    to: worker.phone,
    employeeId: worker.id,
    employeeName: `${worker.firstName} ${worker.lastName}`,
    reference: payslip.reference,
    body: buildPayslipMessage(payslip),
    sentAt: new Date().toISOString(),
  };
}
