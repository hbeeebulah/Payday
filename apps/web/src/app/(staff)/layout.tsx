import { BottomNav } from "@/components/staff/BottomNav";

export default function StaffLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Mobile-first: the portal is constrained to a phone-width column and stays
  // comfortable when viewed on a desktop too.
  return (
    <div className="min-h-screen bg-ink-100">
      <div className="mx-auto flex min-h-screen max-w-md flex-col bg-ink-50 shadow-card">
        <main className="flex-1 px-5 pb-6 pt-6">{children}</main>
        <BottomNav />
      </div>
    </div>
  );
}
