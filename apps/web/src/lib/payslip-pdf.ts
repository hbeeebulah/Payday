import { jsPDF } from "jspdf";

import { formatDate, formatNaira } from "./format";
import type { Payslip } from "./models";

const BRAND = { r: 5, g: 150, b: 105 };
const INK_900 = { r: 15, g: 23, b: 42 };
const INK_500 = { r: 100, g: 116, b: 139 };
const INK_200 = { r: 226, g: 232, b: 240 };

function payslipFilename(payslip: Payslip): string {
  const period = payslip.period.replace(/\s+/g, "-");
  return `payslip-${period}-${payslip.reference}.pdf`;
}

function drawRow(
  pdf: jsPDF,
  label: string,
  value: string,
  y: number,
  margin: number,
  pageWidth: number,
  options?: { mono?: boolean; bold?: boolean },
): number {
  pdf.setFont("helvetica", "normal");
  pdf.setFontSize(10);
  pdf.setTextColor(INK_500.r, INK_500.g, INK_500.b);
  pdf.text(label, margin, y);

  pdf.setFont("helvetica", options?.bold ? "bold" : "normal");
  pdf.setFontSize(options?.bold ? 12 : 10);
  pdf.setTextColor(INK_900.r, INK_900.g, INK_900.b);
  pdf.text(value, pageWidth - margin, y, { align: "right" });

  return y + 22;
}

function drawDivider(pdf: jsPDF, y: number, margin: number, pageWidth: number): number {
  pdf.setDrawColor(INK_200.r, INK_200.g, INK_200.b);
  pdf.setLineWidth(0.5);
  pdf.line(margin, y, pageWidth - margin, y);
  return y + 16;
}

export function downloadPayslipPdf(payslip: Payslip): void {
  const pdf = new jsPDF({ orientation: "p", unit: "pt", format: "a4" });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const margin = 48;
  const contentWidth = pageWidth - margin * 2;

  // Header band
  pdf.setFillColor(BRAND.r, BRAND.g, BRAND.b);
  pdf.roundedRect(margin, 40, contentWidth, 72, 8, 8, "F");

  pdf.setTextColor(255, 255, 255);
  pdf.setFont("helvetica", "normal");
  pdf.setFontSize(10);
  pdf.text(payslip.businessName, margin + 20, 68);

  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(16);
  pdf.text(`Payslip · ${payslip.period}`, margin + 20, 94);

  // Card body
  const cardTop = 128;
  const cardHeight = 280;
  pdf.setDrawColor(INK_200.r, INK_200.g, INK_200.b);
  pdf.setFillColor(255, 255, 255);
  pdf.setLineWidth(1);
  pdf.roundedRect(margin, cardTop, contentWidth, cardHeight, 8, 8, "FD");

  let y = cardTop + 32;
  y = drawRow(pdf, "Employee", payslip.employeeName, y, margin + 20, pageWidth - 20);
  y = drawRow(pdf, "Role", payslip.role, y, margin + 20, pageWidth - 20);
  y = drawRow(pdf, "Paid on", formatDate(payslip.paidAt), y, margin + 20, pageWidth - 20);
  y = drawRow(
    pdf,
    "Account",
    `${payslip.bankName} ${payslip.accountMasked}`,
    y,
    margin + 20,
    pageWidth - 20,
  );

  y = drawDivider(pdf, y, margin + 20, pageWidth - 20);
  y = drawRow(pdf, "Gross pay", formatNaira(payslip.gross), y, margin + 20, pageWidth - 20);
  y = drawRow(
    pdf,
    "Deductions",
    formatNaira(payslip.deductions),
    y,
    margin + 20,
    pageWidth - 20,
  );

  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(11);
  pdf.setTextColor(INK_900.r, INK_900.g, INK_900.b);
  pdf.text("Net paid", margin + 20, y);
  pdf.setFontSize(14);
  pdf.text(formatNaira(payslip.net), pageWidth - margin - 20, y, { align: "right" });
  y += 28;

  y = drawDivider(pdf, y, margin + 20, pageWidth - 20);
  pdf.setFont("courier", "normal");
  pdf.setFontSize(9);
  pdf.setTextColor(INK_500.r, INK_500.g, INK_500.b);
  pdf.text("ALATPay reference", margin + 20, y);
  pdf.setTextColor(INK_900.r, INK_900.g, INK_900.b);
  pdf.text(payslip.reference, pageWidth - margin - 20, y, { align: "right" });

  // Footer
  pdf.setFont("helvetica", "normal");
  pdf.setFontSize(9);
  pdf.setTextColor(INK_500.r, INK_500.g, INK_500.b);
  pdf.text(
    "Issued by Payday · Verified payslip for loans and tenancy applications",
    pageWidth / 2,
    cardTop + cardHeight + 36,
    { align: "center" },
  );

  pdf.save(payslipFilename(payslip));
}
