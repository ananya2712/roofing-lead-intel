"use client";
// Prospects (/prospects): KPI cards, charts, filters and the paged prospect table.
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";

import { DIRECTORY_COLOR, DirectoryBadge, DistanceText, ScoreMeter, TIER_COLOR } from "@/components/leads/Badges";
import { DirectoryToggle } from "@/components/leads/DirectoryToggle";
import { ReasonChips } from "@/components/leads/ReasonChips";
import { SaveButton } from "@/components/leads/SaveButton";
import { Badge } from "@/components/ui/data-display/Badge";
import { BarList } from "@/components/ui/data-display/BarList";
import { Icon } from "@/components/ui/data-display/Icon";
import { KpiCard, KpiGroup } from "@/components/ui/data-display/KpiCard";
import { Pagination } from "@/components/ui/data-display/Pagination";
import { SortHeader } from "@/components/ui/data-display/SortHeader";
import { CheckboxField, SearchField, SelectField } from "@/components/ui/forms/Fields";
import { EmptyState, ErrorBanner, SkeletonRows, StatusMessage } from "@/components/ui/feedback/States";
import { PageHeader } from "@/components/ui/layout/PageHeader";
import { api, unwrap, type ProspectStats } from "@/lib/api";
import { formatDate, telHref, titleCase } from "@/lib/format";
import { useLoad } from "@/lib/useLoad";

const FILTER_KEYS = ["q", "directory", "tier", "max_distance", "state", "cert_tier", "hide_saved", "sort", "page"] as const;
type Filters = Record<(typeof FILTER_KEYS)[number], string>;

const CHIP_LABELS: Partial<Record<keyof Filters, (v: string) => string>> = {
  q: (v) => `Search: ${v}`,
  directory: (v) => titleCase(v),
  tier: (v) => `${titleCase(v)} priority`,
  max_distance: (v) => `≤ ${v} mi`,
  state: (v) => `State: ${v}`,
  cert_tier: (v) => ({ top: "Top GAF tier", certified: "GAF certified", none: "No certification" })[v] ?? v,
  hide_saved: () => "Hiding saved",
};

/** Prospects view. Filters, sort and page are kept in the URL. */
function ProspectsView() {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const filters = Object.fromEntries(FILTER_KEYS.map((k) => [k, sp.get(k) ?? ""])) as Filters;
  const page = Number(filters.page) || 1;
  const sort = filters.sort || "score";
  const [search, setSearch] = useState(filters.q);
  const [stats, setStats] = useState<ProspectStats | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  // Filters live in the URL, so the Back button returns to the same list.
  const setFilters = useCallback(
    (patch: Partial<Filters>) => {
      const next = new URLSearchParams(sp.toString());
      for (const [k, v] of Object.entries(patch)) {
        if (v) next.set(k, v);
        else next.delete(k);
      }
      if (!("page" in patch)) next.delete("page");
      router.replace(`${pathname}?${next.toString()}`, { scroll: false });
    },
    [sp, router, pathname],
  );

  // Wait 300 ms after typing, so each keystroke does not start a request.
  useEffect(() => {
    const t = setTimeout(() => {
      if (search !== filters.q) setFilters({ q: search });
    }, 300);
    return () => clearTimeout(t);
  }, [search, filters.q, setFilters]);

  const directory = (filters.directory || undefined) as "residential" | "commercial" | undefined;
  const loadStats = useCallback(async () => {
    try {
      setStats(await unwrap(api.GET("/prospects/stats", { params: { query: { directory } } }), "Summary counts could not be loaded."));
    } catch {
      setStats(null);
    }
  }, [directory]);
  useEffect(() => { void loadStats(); }, [loadStats]);

  const list = useLoad(
    (signal) =>
      unwrap(
        api.GET("/prospects", {
          signal,
          params: {
            query: {
              q: filters.q || undefined,
              directory,
              tier: (filters.tier || undefined) as "high" | "medium" | "low" | undefined,
              max_distance: filters.max_distance ? (Number(filters.max_distance) as 10 | 25 | 50) : undefined,
              state: filters.state || undefined,
              cert_tier: (filters.cert_tier || undefined) as "top" | "certified" | "none" | undefined,
              hide_saved: filters.hide_saved === "true" ? true : undefined,
              sort: sort as "score" | "distance" | "name",
              page,
              page_size: 25,
            },
          },
        }),
        "Prospects could not be loaded.",
      ),
    sp.toString(),
  );

  const chips = (Object.keys(CHIP_LABELS) as (keyof Filters)[]).filter((k) => filters[k]);
  const clearAll = () => { setSearch(""); router.replace(sort !== "score" ? `${pathname}?sort=${sort}` : pathname); };
  const toggle = (key: keyof Filters, value: string) => setFilters({ [key]: filters[key] === value ? "" : value });

  return (
    <>
      <PageHeader
        title="Prospects"
        subtitle={<>All GAF listings within 50 mi of ZIP 10013{stats?.snapshot_retrieved_at ? ` · retrieved ${formatDate(stats.snapshot_retrieved_at)}` : ""}</>}
        actions={<DirectoryToggle value={filters.directory} onChange={(v) => setFilters({ directory: v })} counts={stats?.directories} />}
      />

      <KpiGroup>
        <KpiCard icon="layers" tone="lavender" label="Prospects" value={stats?.total ?? "–"} hint={directory ? `${titleCase(directory)} listings only` : "Residential and commercial listings"} />
        <KpiCard icon="star" tone="mint" label="High priority" value={stats?.high ?? "–"} hint="Score 70 or more · click to filter" href="/prospects?tier=high" active={filters.tier === "high"} />
        <KpiCard icon="bookmark" tone="sky" label="Saved leads" value={stats?.saved ?? "–"} hint="Open the saved list" href="/leads" />
        <KpiCard icon="alert" tone="peach" label="High priority not saved" value={stats?.high_unsaved ?? "–"} hint="Candidates to review" href="/prospects?tier=high&hide_saved=true" />
      </KpiGroup>

      {stats ? (
        <div className="grid gap-3 md:grid-cols-3">
          <BarList title="Priority mix" subtitle="Click to filter" activeKey={filters.tier || null} onSelect={(k) => toggle("tier", k)}
            items={(["high", "medium", "low"] as const).map((t) => ({ key: t, label: titleCase(t), value: stats.tiers[t] ?? 0, color: TIER_COLOR[t] }))} />
          <BarList title="Directory" subtitle="Click to filter" activeKey={filters.directory || null} onSelect={(k) => toggle("directory", k)}
            items={(["residential", "commercial"] as const).map((d) => ({ key: d, label: titleCase(d), value: stats.directories[d] ?? 0, color: DIRECTORY_COLOR[d] }))} />
          <BarList title="Distance from ZIP 10013" subtitle="Click to filter" activeKey={filters.max_distance || null} onSelect={(k) => toggle("max_distance", k)}
            items={[
              { key: "10", label: "≤ 10 mi", value: stats.distance_bands["0-10"] ?? 0, color: "#8EDBB0" },
              { key: "25", label: "10–25 mi", value: stats.distance_bands["10-25"] ?? 0, color: "#94C8F2" },
              { key: "50", label: "25–50 mi", value: stats.distance_bands["25-50"] ?? 0, color: "#B9A8F5" },
            ]} />
        </div>
      ) : null}

      <section className="overflow-hidden rounded-md border border-line bg-surface shadow-card" aria-label="Prospect list">
        <div className="flex flex-wrap items-end gap-3 border-b border-line p-4">
          <SearchField id="q" label="Search" value={search} placeholder="Company or city" onChange={setSearch} />
          <SelectField id="tier" label="Priority" value={filters.tier} onChange={(v) => setFilters({ tier: v })}
            options={[{ value: "", label: "All" }, { value: "high", label: "High" }, { value: "medium", label: "Medium" }, { value: "low", label: "Low" }]} />
          <SelectField id="max_distance" label="Distance" value={filters.max_distance} onChange={(v) => setFilters({ max_distance: v })}
            options={[{ value: "", label: "Any (≤ 50 mi)" }, { value: "10", label: "≤ 10 mi" }, { value: "25", label: "≤ 25 mi" }]} />
          <SelectField id="state" label="State" value={filters.state} onChange={(v) => setFilters({ state: v })}
            options={[{ value: "", label: "All" }, ...(stats?.states ?? []).map((s) => ({ value: s, label: s }))]} />
          <SelectField id="cert_tier" label="Certification" value={filters.cert_tier} onChange={(v) => setFilters({ cert_tier: v })}
            options={[{ value: "", label: "All" }, { value: "top", label: "Top tier" }, { value: "certified", label: "Certified" }, { value: "none", label: "None listed" }]} />
          <CheckboxField id="hide_saved" label="Hide saved" checked={filters.hide_saved === "true"} onChange={(v) => setFilters({ hide_saved: v ? "true" : "" })} />
        </div>

        <div className="flex flex-wrap items-center gap-2 border-b border-line bg-subtle px-4 py-2 text-sm">
          <span className="font-semibold tabular-nums text-ink">{list.data ? list.data.total : "…"}</span>
          <span className="text-ink-muted">prospects</span>
          {chips.map((k) => (
            <button key={k} type="button" onClick={() => { if (k === "q") setSearch(""); setFilters({ [k]: "" }); }}
              className="inline-flex items-center gap-1 rounded bg-brand-soft px-2 py-0.5 text-xs font-medium text-brand hover:bg-lavender-soft focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand"
              aria-label={`Remove filter ${CHIP_LABELS[k]!(filters[k])}`}>
              {CHIP_LABELS[k]!(filters[k])} <Icon name="x" className="h-3 w-3" />
            </button>
          ))}
          {chips.length ? <button type="button" onClick={clearAll} className="text-xs text-info-ink hover:underline">Clear all</button> : null}
          <span className="ml-auto"><StatusMessage message={msg} tone="success" /></span>
        </div>

        {list.error ? <div className="p-4"><ErrorBanner message={list.error} onRetry={list.reload} /></div> : null}
        {list.loading && !list.data ? <SkeletonRows /> : null}

        {list.data ? (
          list.data.items.length === 0 ? (
            <EmptyState title="No prospects match these filters." action={<button type="button" className="text-sm text-info-ink hover:underline" onClick={clearAll}>Clear filters</button>} />
          ) : (
            <div className={`relative overflow-x-auto transition-opacity ${list.loading ? "opacity-60" : ""}`}>
              <table className="w-full min-w-[980px] text-left text-sm">
                <thead className="bg-subtle text-xs uppercase tracking-wide text-ink-muted">
                  <tr>
                    <SortHeader label="Company" sortKey="name" current={sort} onSort={(k) => setFilters({ sort: k === "score" ? "" : k })} />
                    <th scope="col" className="px-3 py-2 font-medium">Directory</th>
                    <SortHeader label="Distance" sortKey="distance" current={sort} onSort={(k) => setFilters({ sort: k })} />
                    <SortHeader label="Priority" sortKey="score" current={sort} onSort={() => setFilters({ sort: "" })} />
                    <th scope="col" className="px-3 py-2 font-medium">Why</th>
                    <th scope="col" className="px-3 py-2 font-medium">Rating</th>
                    <th scope="col" className="px-4 py-2 font-medium"><span className="sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {list.data.items.map((p) => (
                    <tr key={p.id} className="group transition-colors hover:bg-lavender-soft/40">
                      <td className="px-4 py-2.5">
                        <Link href={`/prospects/${p.id}`} className="font-semibold text-ink hover:text-brand hover:underline">{p.name}</Link>
                        <p className="mt-0.5 flex flex-wrap items-center gap-1.5 text-xs text-ink-muted">
                          <Icon name="pin" className="h-3 w-3" />
                          {[p.city, p.state].filter(Boolean).join(", ") || "Location unknown"}
                          {p.phone ? <a href={telHref(p.phone)} className="inline-flex items-center gap-1 text-info-ink hover:underline"><Icon name="phone" className="h-3 w-3" />{p.phone}</a> : null}
                          {p.also_listed_in ? <Link href={`/prospects/${p.also_listed_in.prospect_id}`}><Badge tone="butter">Also in {titleCase(p.also_listed_in.directory)}</Badge></Link> : null}
                        </p>
                      </td>
                      <td className="px-3 py-2.5"><DirectoryBadge directory={p.directory} /></td>
                      <td className="px-3 py-2.5"><DistanceText miles={p.distance_mi} /></td>
                      <td className="px-3 py-2.5"><ScoreMeter score={p.score} tier={p.tier} /></td>
                      <td className="max-w-[300px] px-3 py-2.5"><ReasonChips reason={p.top_reason} skipDistance /></td>
                      <td className="px-3 py-2.5 tabular-nums">
                        {p.rating !== null ? (
                          <span className="inline-flex items-center gap-1"><Icon name="star" className="h-3.5 w-3.5 text-butter-mid" /><span className="font-medium">{p.rating.toFixed(1)}</span><span className="text-xs text-ink-muted">({p.review_count ?? 0})</span></span>
                        ) : <span className="text-ink-faint">Unknown</span>}
                      </td>
                      <td className="px-4 py-2.5">
                        <span className="flex items-center justify-end gap-2">
                          <Link href={`/prospects/${p.id}`} className="rounded border border-line bg-surface px-2 py-1 text-xs text-ink-muted opacity-0 transition-opacity hover:text-ink focus:opacity-100 group-hover:opacity-100">View</Link>
                          <SaveButton prospectId={p.id} savedLeadId={p.saved_lead_id} savedVia={p.saved_via}
                            onSaved={() => { setMsg(`${p.name} saved as a lead.`); list.reload(); void loadStats(); }} />
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : null}
        {list.data && list.data.total > 0 ? (
          <Pagination page={page} pageSize={list.data.page_size} total={list.data.total} onPage={(p) => setFilters({ page: String(p) })} />
        ) : null}
      </section>
    </>
  );
}

/** Route component for /prospects. */
export default function ProspectsPage() {
  return (
    // useSearchParams needs a Suspense boundary for the static build.
    <Suspense fallback={<SkeletonRows />}>
      <ProspectsView />
    </Suspense>
  );
}
