"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { Icon, type IconName } from "@/components/ui/data-display/Icon";
import { api } from "@/lib/api";

const LINKS: { href: string; label: string; icon: IconName; countKey?: "total" | "saved" }[] = [
  { href: "/", label: "Sales dashboard", icon: "home" },
  { href: "/prospects", label: "Prospects", icon: "search", countKey: "total" },
  { href: "/leads", label: "Saved leads", icon: "bookmark", countKey: "saved" },
];

export function Sidebar() {
  const path = usePathname();
  const [counts, setCounts] = useState<{ total: number; saved: number } | null>(null);

  // Counts refresh on each page change, so a new save shows in the badge.
  useEffect(() => {
    const ctrl = new AbortController();
    api.GET("/prospects/stats", { signal: ctrl.signal }).then(({ data }) => {
      if (data) setCounts({ total: data.total, saved: data.saved });
    }).catch(() => undefined);
    return () => ctrl.abort();
  }, [path]);

  const isActive = (href: string) => (href === "/" ? path === "/" : path.startsWith(href));
  return (
    <aside className="flex shrink-0 flex-col rounded-md border border-line bg-surface shadow-card md:sticky md:top-4 md:h-[calc(100vh-2rem)] md:w-60">
      <div className="flex items-center gap-2.5 border-b border-line px-4 py-4">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded bg-lavender-soft text-lavender-ink"><Icon name="layers" /></span>
        <div>
          <p className="text-sm font-semibold text-ink">Roofing Lead Intel</p>
          <p className="text-xs text-ink-muted">Distributor sales workspace</p>
        </div>
      </div>
      <nav aria-label="Main" className="flex flex-wrap gap-1 p-2 md:flex-col md:flex-nowrap">
        {LINKS.map((l) => {
          const active = isActive(l.href);
          return (
            <Link
              key={l.href}
              href={l.href}
              aria-current={active ? "page" : undefined}
              className={`flex items-center gap-2.5 rounded px-3 py-2 text-sm transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand ${active ? "bg-brand-soft font-semibold text-brand" : "text-ink-muted hover:bg-subtle hover:text-ink"}`}
            >
              <Icon name={l.icon} />
              <span className="flex-1">{l.label}</span>
              {l.countKey && counts ? (
                <span className={`rounded px-1.5 text-xs tabular-nums ${active ? "bg-surface text-brand" : "bg-subtle text-ink-muted"}`}>{counts[l.countKey]}</span>
              ) : null}
            </Link>
          );
        })}
      </nav>
      <div className="m-3 mt-auto hidden rounded border border-line bg-subtle p-3 text-xs leading-5 text-ink-muted md:block">
        <p className="font-medium text-ink">Data source</p>
        GAF contractor directory snapshot · ZIP 10013 · 50 mi · residential and commercial
      </div>
    </aside>
  );
}
