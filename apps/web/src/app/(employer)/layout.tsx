import { Sidebar } from "@/components/employer/Sidebar";

export default function EmployerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-ink-50">
      <Sidebar />
      <div className="flex-1 overflow-x-hidden">
        <div className="mx-auto max-w-5xl px-8 py-8">{children}</div>
      </div>
    </div>
  );
}
