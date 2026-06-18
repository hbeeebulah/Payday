import type { Metadata, Viewport } from "next";
import { StoreHydrator } from "@/components/StoreHydrator";
import "./globals.css";

export const metadata: Metadata = {
  title: "Payday — Pay your whole team in one tap",
  description:
    "Payday lets Nigerian small business owners pay every employee simultaneously, on time, every month — with automatic payslips and a clean record of every salary paid.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#059669",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans">
        <StoreHydrator />
        {children}
      </body>
    </html>
  );
}
