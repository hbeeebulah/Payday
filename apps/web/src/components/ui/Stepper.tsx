export function Stepper({
  steps,
  current,
}: {
  steps: string[];
  current: number;
}) {
  return (
    <ol className="flex items-center gap-2">
      {steps.map((label, index) => {
        const done = index < current;
        const active = index === current;
        return (
          <li key={label} className="flex flex-1 items-center gap-2">
            <span
              className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
                done
                  ? "bg-brand-600 text-white"
                  : active
                    ? "bg-brand-100 text-brand-700 ring-2 ring-brand-500"
                    : "bg-ink-100 text-ink-400"
              }`}
            >
              {done ? "✓" : index + 1}
            </span>
            <span
              className={`hidden text-sm font-medium sm:inline ${
                active ? "text-ink-900" : "text-ink-400"
              }`}
            >
              {label}
            </span>
            {index < steps.length - 1 ? (
              <span
                className={`h-px flex-1 ${done ? "bg-brand-400" : "bg-ink-200"}`}
              />
            ) : null}
          </li>
        );
      })}
    </ol>
  );
}
