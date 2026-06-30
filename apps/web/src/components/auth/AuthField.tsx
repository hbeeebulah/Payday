import type { InputHTMLAttributes } from "react";

interface AuthFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function AuthField({ label, error, id, className = "", ...props }: AuthFieldProps) {
  const fieldId = id ?? label.toLowerCase().replace(/\s+/g, "-");

  return (
    <div>
      <label htmlFor={fieldId} className="block text-sm font-medium text-ink-700">
        {label}
      </label>
      <input
        id={fieldId}
        className={`mt-1.5 w-full rounded-lg border bg-white px-3 py-2.5 text-sm text-ink-900 outline-none transition-colors placeholder:text-ink-300 focus:border-brand-500 focus:ring-2 focus:ring-brand-100 ${
          error ? "border-rose-400" : "border-ink-200"
        } ${className}`}
        {...props}
      />
      {error ? <p className="mt-1 text-xs text-rose-600">{error}</p> : null}
    </div>
  );
}
