"use client";

type Value = "" | "residential" | "commercial";

const OPTIONS: { value: Value; label: string; dot: string }[] = [
  { value: "", label: "All directories", dot: "bg-lavender-mid" },
  { value: "residential", label: "Residential", dot: "bg-sky-mid" },
  { value: "commercial", label: "Commercial", dot: "bg-butter-mid" },
];

type Props = { value: string; onChange: (v: Value) => void; counts?: Partial<Record<"residential" | "commercial", number>> };

/** Segmented control for the GAF directory. The filter itself runs in the backend SQL. */
export function DirectoryToggle({ value, onChange, counts }: Props) {
  const total = counts ? (counts.residential ?? 0) + (counts.commercial ?? 0) : undefined;
  return (
    <div role="group" aria-label="GAF directory" className="flex max-w-full flex-wrap rounded border border-line bg-surface p-0.5 shadow-card">
      {OPTIONS.map((o) => {
        const active = (value || "") === o.value;
        const n = o.value ? counts?.[o.value] : total;
        return (
          <button key={o.value || "all"} type="button" aria-pressed={active} onClick={() => onChange(o.value)}
            className={`inline-flex items-center gap-1.5 rounded px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand ${active ? "bg-brand-soft text-brand" : "text-ink-muted hover:bg-subtle hover:text-ink"}`}>
            <span className={`h-2 w-2 rounded-full ${o.dot}`} aria-hidden="true" />
            {o.label}
            {n !== undefined ? <span className="text-xs tabular-nums opacity-70">{n}</span> : null}
          </button>
        );
      })}
    </div>
  );
}
