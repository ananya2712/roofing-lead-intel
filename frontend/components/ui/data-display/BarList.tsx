"use client";

export type BarItem = { key: string; label: string; value: number; color: string };

type Props = { title: string; subtitle?: string; items: BarItem[]; activeKey?: string | null; onSelect?: (key: string) => void };

/** Horizontal bars with counts and shares. A click on a row applies that value as a filter. */
export function BarList({ title, subtitle, items, activeKey, onSelect }: Props) {
  const max = Math.max(1, ...items.map((i) => i.value));
  const total = items.reduce((a, i) => a + i.value, 0) || 1;
  return (
    <section className="rounded-md border border-line bg-surface p-4 shadow-card" aria-label={title}>
      <div className="flex items-baseline justify-between gap-2">
        <h2 className="text-sm font-semibold text-ink">{title}</h2>
        {subtitle ? <p className="text-xs text-ink-faint">{subtitle}</p> : null}
      </div>
      <ul className="mt-3 space-y-1">
        {items.map((i) => {
          const active = activeKey === i.key;
          const share = Math.round((i.value / total) * 100);
          return (
            <li key={i.key}>
              <button
                type="button"
                onClick={() => onSelect?.(i.key)}
                disabled={!onSelect}
                aria-pressed={onSelect ? active : undefined}
                title={onSelect ? (active ? "Click to remove this filter" : `Click to filter: ${i.label}`) : undefined}
                className={`group grid w-full grid-cols-[84px_1fr_64px] items-center gap-2 rounded px-1.5 py-1 text-left text-sm transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand ${onSelect ? "hover:bg-subtle" : ""} ${active ? "bg-brand-soft ring-1 ring-brand/25" : ""}`}
              >
                <span className={`truncate ${active ? "font-medium text-brand" : "text-ink-muted"}`}>{i.label}</span>
                <span className="h-2.5 rounded-sm bg-subtle">
                  <span className="block h-2.5 rounded-sm transition-all group-hover:brightness-95" style={{ width: `${Math.max(2, (i.value / max) * 100)}%`, background: i.color }} />
                </span>
                <span className="text-right tabular-nums">
                  <span className="font-semibold text-ink">{i.value}</span>
                  <span className="ml-1 text-xs text-ink-faint">{share}%</span>
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
