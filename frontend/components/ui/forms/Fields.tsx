"use client";
import type { ReactNode } from "react";

const control = "h-9 rounded border border-line bg-surface px-2.5 text-sm text-ink focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20";

type Option = { value: string; label: string };

export function SelectField({ id, label, value, options, onChange }: {
  id: string; label: string; value: string; options: Option[]; onChange: (v: string) => void;
}) {
  return (
    <label htmlFor={id} className="flex flex-col gap-1 text-xs font-medium text-ink-muted">
      {label}
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)} className={`${control} min-w-[130px]`}>
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </label>
  );
}

export function SearchField({ id, label, value, placeholder, onChange }: {
  id: string; label: string; value: string; placeholder: string; onChange: (v: string) => void;
}) {
  return (
    <label htmlFor={id} className="flex min-w-[200px] flex-1 flex-col gap-1 text-xs font-medium text-ink-muted">
      {label}
      <input id={id} type="search" value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} className={`${control} w-full`} />
    </label>
  );
}

export function CheckboxField({ id, label, checked, onChange }: {
  id: string; label: ReactNode; checked: boolean; onChange: (v: boolean) => void;
}) {
  return (
    <label htmlFor={id} className="flex h-9 items-center gap-2 self-end text-sm text-ink">
      <input id={id} type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} className="h-4 w-4 rounded border-line accent-brand" />
      {label}
    </label>
  );
}
