"use client";

import { Button } from "@/components/ui/Button";
import type { AppState } from "@/lib/models";
import { resetRun } from "@/lib/payroll-engine";
import { clearToBlank, loadDemo } from "@/lib/store";

export function DemoControls({ state }: { state: AppState }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span
        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${
          state.demoMode
            ? "bg-amber-100 text-amber-700"
            : "bg-ink-100 text-ink-500"
        }`}
      >
        <span className="h-1.5 w-1.5 rounded-full bg-current" />
        {state.demoMode ? "Demo data" : "Live data"}
      </span>
      <Button size="sm" variant="secondary" onClick={() => resetRun()}>
        Reset run
      </Button>
      <Button size="sm" variant="secondary" onClick={() => loadDemo()}>
        Load demo seed
      </Button>
      <Button size="sm" variant="ghost" onClick={() => clearToBlank()}>
        Clear
      </Button>
    </div>
  );
}
