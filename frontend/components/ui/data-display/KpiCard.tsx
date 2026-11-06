// KPI card and the grid that groups KPI cards.
import Link from "next/link";
import type { ReactNode } from "react";

import { Icon, type IconName } from "./Icon";

export type KpiTone = "lavender" | "mint" | "peach" | "sky" | "rose" | "butter";

const CHIP: Record<KpiTone, string> = {
  lavender: "bg-lavender-soft text-lavender-ink",
  mint: "bg-mint-soft text-mint-ink",
  peach: "bg-peach-soft text-peach-ink",
  sky: "bg-sky-soft text-sky-ink",
  rose: "bg-rose-soft text-rose-ink",
  butter: "bg-butter-soft text-butter-ink",
};

type Props = { label: string; value: ReactNode; hint?: ReactNode; icon: IconName; tone: KpiTone; href?: string; active?: boolean };

/** One summary number. Used inside KpiGroup, which draws the shared card and the dividers. */
export function KpiCard({ label, value, hint, icon, tone, href, active }: Props) {
  const body = (
    <div className={`group h-full px-4 py-3.5 transition-colors ${href ? "hover:bg-subtle" : ""} ${active ? "bg-subtle" : ""}`}>
      <p className="flex items-center gap-2 text-sm text-ink-muted">
        <span className={`inline-flex h-6 w-6 items-center justify-center rounded ${CHIP[tone]}`}><Icon name={icon} className="h-3.5 w-3.5" /></span>
        {label}
      </p>
      <p className="mt-2 flex items-baseline gap-2 text-2xl font-semibold tabular-nums text-ink">
        {value}
        {href ? <Icon name="arrow" className="h-3.5 w-3.5 text-ink-faint opacity-0 transition-opacity group-hover:opacity-100" /> : null}
      </p>
      {hint ? <p className="mt-0.5 text-xs text-ink-muted">{hint}</p> : null}
    </div>
  );
  return href ? (
    <Link href={href} className="block h-full focus-visible:outline focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-brand">{body}</Link>
  ) : body;
}

/** Responsive grid for KPI cards. */
export function KpiGroup({ children }: { children: ReactNode }) {
  return (
    <div className="grid grid-cols-2 divide-line overflow-hidden rounded-md border border-line bg-surface shadow-card lg:grid-cols-4 lg:divide-x [&>*:nth-child(odd)]:border-r [&>*:nth-child(odd)]:border-line lg:[&>*:nth-child(odd)]:border-r-0">
      {children}
    </div>
  );
}
