"use client";
// Saved leads (/leads): call lists, status cards, filters, sort, and a table or phone cards.
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";

import { DirectoryBadge, DistanceText, ScoreMeter } from "@/components/leads/Badges";
import { DirectoryToggle } from "@/components/leads/DirectoryToggle";
import { ReasonChips } from "@/components/leads/ReasonChips";
import { StatusSelect } from "@/components/leads/StatusSelect";
import { Badge } from "@/components/ui/data-display/Badge";
import { Icon, type IconName } from "@/components/ui/data-display/Icon";
import { Pagination } from "@/components/ui/data-display/Pagination";
import { SearchField, SelectField } from "@/components/ui/forms/Fields";
import { EmptyState, ErrorBanner, SkeletonRows } from "@/components/ui/feedback/States";
import { PageHeader } from "@/components/ui/layout/PageHeader";
import { api, LEAD_STATUSES, unwrap, type LeadStatus, type LeadSummary } from "@/lib/api";
import { ago, formatShortDate, telHref } from "@/lib/format";
import { useLoad } from "@/lib/useLoad";

const FILTER_KEYS = ["q", "scope", "status", "queue", "directory", "tier", "sort", "page"] as const;
type Filters = Record<(typeof FILTER_KEYS)[number], string>;

const STATUS_CARD: Record<LeadStatus, { label: string; ring: string; chip: string; icon: IconName }> = {
  new: { label: "New", ring: "border-sky-mid/50", chip: "bg-sky-soft text-sky-ink", icon: "clock" },
  contacted: { label: "Contacted", ring: "border-peach-mid/50", chip: "bg-peach-soft text-peach-ink", icon: "phone" },
  qualified: { label: "Qualified", ring: "border-mint-mid/60", chip: "bg-mint-soft text-mint-ink", icon: "check" },
  dismissed: { label: "Dismissed", ring: "border-line", chip: "bg-subtle text-ink-muted", icon: "x" },
};

type RowState = { kind: "ok" | "error"; text: string };

/** Phone link and the row's status message. Mark contacted is on the lead page only. */
function ContactActions({ lead, row }: { lead: LeadSummary; row?: RowState }) {
  return (
    <div className="flex flex-col items-start gap-1">
      {lead.phone ? (
        <a href={telHref(lead.phone)} className="inline-flex items-center gap-1 whitespace-nowrap rounded border border-sky-mid/60 bg-sky-soft px-2 py-1 text-xs font-medium text-sky-ink hover:brightness-95">
          <Icon name="phone" className="h-3 w-3" />{lead.phone}
        </a>
      ) : <span className="text-xs text-ink-faint">Phone unknown</span>}
      <p role="status" aria-live="polite" className={`min-h-[16px] text-xs ${row?.kind === "error" ? "text-danger-ink" : "text-success-ink"}`}>
        {row?.text ?? ""}
      </p>
    </div>
  );
}

/** Status control, time since the last change, and the Follow-up due badge. */
function StatusCell({ lead, onSaved, onMessage }: { lead: LeadSummary; onSaved: () => void; onMessage: (t: string, ok: boolean) => void }) {
  return (
    <div className="space-y-0.5">
      <StatusSelect key={`${lead.lead_id}-${lead.status}`} leadId={lead.lead_id} value={lead.status} label={`Status for ${lead.name}`} onSaved={onSaved} onMessage={onMessage} />
      <p className="text-xs text-ink-faint">Changed {ago(lead.status_changed_at)}</p>
      {lead.follow_up_due ? <Badge tone="peach" dot>Follow-up due</Badge> : null}
    </div>
  );
}

/** Saved leads view. Filters, sort and page are kept in the URL. */
function LeadsView() {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const filters = Object.fromEntries(FILTER_KEYS.map((k) => [k, sp.get(k) ?? ""])) as Filters;
  const page = Number(filters.page) || 1;
  const scope = (filters.scope || "active") as "active" | "all" | "dismissed";
  const [search, setSearch] = useState(filters.q);
  const [rows, setRows] = useState<Record<number, RowState>>({});

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

  const list = useLoad(
    (signal) =>
      unwrap(
        api.GET("/leads", {
          signal,
          params: {
            query: {
              q: filters.q || undefined,
              scope,
              status: (filters.status || undefined) as "new" | "contacted" | "qualified" | undefined,
              queue: (filters.queue || undefined) as "first_contact" | "follow_up_due" | undefined,
              directory: (filters.directory || undefined) as "residential" | "commercial" | undefined,
              tier: (filters.tier || undefined) as "high" | "medium" | "low" | undefined,
              sort: (filters.sort || "priority") as "priority" | "recently_saved" | "oldest_status_change",
              page,
              page_size: 25,
            },
          },
        }),
        "Saved leads could not be loaded.",
      ),
    sp.toString(),
  );

  const setRow = (id: number, state: RowState | null) =>
    setRows((r) => {
      const next = { ...r };
      if (state) next[id] = state;
      else delete next[id];
      return next;
    });

  const data = list.data;
  const counts = data?.status_counts;
  const queues: { key: string; label: string; count?: number; icon: IconName; tone: string }[] = [
    { key: "", label: "All", count: undefined, icon: "bookmark", tone: "text-brand" },
    { key: "first_contact", label: "Needs first contact", count: data?.queue_counts.first_contact, icon: "phone", tone: "text-sky-ink" },
    { key: "follow_up_due", label: "Follow-up due", count: data?.queue_counts.follow_up_due, icon: "clock", tone: "text-peach-ink" },
  ];
  const anyFilter = ["q", "status", "queue", "directory", "tier"].some((k) => filters[k as keyof Filters]) || scope !== "active";
  const clearAll = () => { setSearch(""); router.replace(pathname); };
  const rowFeedback = (lead: LeadSummary) => (text: string, ok: boolean) => setRow(lead.lead_id, { kind: ok ? "ok" : "error", text });

  return (
    <>
      <PageHeader title="Saved leads" subtitle="Who should I contact next? Start with the two call lists below."
        actions={<DirectoryToggle value={filters.directory} onChange={(v) => setFilters({ directory: v })} />} />

      <nav aria-label="Call lists" className="flex flex-wrap gap-2">
        {queues.map((q) => {
          const active = filters.queue === q.key;
          return (
            <button key={q.key || "all"} type="button" aria-pressed={active}
              onClick={() => setFilters({ queue: q.key, status: "", scope: q.key ? "" : filters.scope })}
              className={`inline-flex items-center gap-2 rounded border px-3 py-2 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand ${active ? "border-brand/40 bg-brand-soft text-brand" : "border-line bg-surface text-ink hover:bg-subtle"}`}>
              <Icon name={q.icon} className={`h-4 w-4 ${active ? "" : q.tone}`} />
              {q.label}
              {q.count !== undefined ? <span className={`rounded px-1.5 text-xs tabular-nums ${active ? "bg-surface" : "bg-subtle"}`}>{q.count}</span> : null}
            </button>
          );
        })}
      </nav>

      <section aria-label="All saved leads by status">
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-ink-muted">All saved {filters.directory ? `${filters.directory} ` : ""}leads · {data ? data.total_saved : "–"} total</p>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {LEAD_STATUSES.map((s) => {
            const active = s === "dismissed" ? scope === "dismissed" : filters.status === s;
            const pick = () =>
              s === "dismissed"
                ? setFilters({ scope: active ? "" : "dismissed", status: "", queue: "" })
                : setFilters({ status: active ? "" : s, scope: "", queue: "" });
            return (
              <button key={s} type="button" aria-pressed={active} onClick={pick}
                className={`rounded-md border bg-surface p-3.5 text-left shadow-card transition-shadow hover:shadow-lift focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand ${active ? "ring-2 ring-brand/40" : ""} ${STATUS_CARD[s].ring}`}>
                <p className="flex items-center gap-2 text-sm text-ink-muted">
                  <span className={`inline-flex h-6 w-6 items-center justify-center rounded ${STATUS_CARD[s].chip}`}><Icon name={STATUS_CARD[s].icon} className="h-3.5 w-3.5" /></span>
                  {STATUS_CARD[s].label}
                </p>
                <p className="mt-1.5 text-2xl font-semibold tabular-nums">{counts ? counts[s] ?? 0 : "–"}</p>
                <p className="text-xs text-ink-faint">{active ? "Filter on · click to remove" : "Click to show only these"}</p>
              </button>
            );
          })}
        </div>
      </section>

      <section className="overflow-hidden rounded-md border border-line bg-surface shadow-card" aria-label="Saved lead list">
        <div className="flex flex-wrap items-end gap-3 border-b border-line p-4">
          <SearchField id="lq" label="Search" value={search} placeholder="Company or city" onChange={setSearch} />
          <SelectField id="lscope" label="Leads" value={scope === "active" ? "" : scope} onChange={(v) => setFilters({ scope: v, status: v === "dismissed" ? "" : filters.status })}
            options={[{ value: "", label: "Active leads" }, { value: "all", label: "All leads" }, { value: "dismissed", label: "Dismissed" }]} />
          {scope !== "dismissed" ? (
            <SelectField id="lstatus" label="Status" value={filters.status} onChange={(v) => setFilters({ status: v, queue: "" })}
              options={[{ value: "", label: "Any status" }, { value: "new", label: "New" }, { value: "contacted", label: "Contacted" }, { value: "qualified", label: "Qualified" }]} />
          ) : null}
          <SelectField id="ltier" label="Priority" value={filters.tier} onChange={(v) => setFilters({ tier: v })}
            options={[{ value: "", label: "All" }, { value: "high", label: "High" }, { value: "medium", label: "Medium" }, { value: "low", label: "Low" }]} />
          <SelectField id="lsort" label="Sort by" value={filters.sort} onChange={(v) => setFilters({ sort: v })}
            options={[{ value: "", label: "Highest priority" }, { value: "recently_saved", label: "Recently saved" }, { value: "oldest_status_change", label: "Oldest status change" }]} />
        </div>

        <div className="flex flex-wrap items-center gap-2 border-b border-line bg-subtle px-4 py-2 text-sm">
          <span className="font-semibold tabular-nums text-ink">{data ? data.total : "…"}</span>
          <span className="text-ink-muted">matching {data?.total === 1 ? "lead" : "leads"}</span>
          {anyFilter ? <button type="button" onClick={clearAll} className="text-xs text-info-ink hover:underline">Clear filters</button> : null}
        </div>

        {list.error ? <div className="p-4"><ErrorBanner message={list.error} onRetry={list.reload} /></div> : null}
        {list.loading && !data ? <SkeletonRows /> : null}

        {data ? (
          data.items.length === 0 ? (
            data.total_saved === 0 ? (
              <EmptyState title="No saved leads yet. Save a prospect from the Prospects view." action={<Link href="/prospects" className="rounded bg-brand px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-hover">Open Prospects</Link>} />
            ) : filters.queue === "follow_up_due" ? (
              <EmptyState title="No follow-ups are due. A lead appears here 14 days after its status changed to Contacted." />
            ) : filters.queue === "first_contact" ? (
              <EmptyState title="Every saved lead has been contacted." />
            ) : (
              <EmptyState title="No saved leads match these filters." action={<button type="button" className="text-sm text-info-ink hover:underline" onClick={clearAll}>Clear filters</button>} />
            )
          ) : (
            <div className={`transition-opacity ${list.loading ? "opacity-60" : ""}`}>
              {/* Wide screens: table */}
              <table className="hidden w-full text-left text-sm md:table">
                <thead className="bg-subtle text-xs uppercase tracking-wide text-ink-muted">
                  <tr>
                    <th scope="col" className="px-4 py-2 font-medium">Company and why</th>
                    <th scope="col" className="px-3 py-2 font-medium">Priority</th>
                    <th scope="col" className="px-3 py-2 font-medium">Status</th>
                    <th scope="col" className="px-3 py-2 font-medium">Contact</th>
                    <th scope="col" className="px-4 py-2 font-medium">Saved</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {data.items.map((l) => (
                    <tr key={l.lead_id} className={`align-top transition-colors hover:bg-lavender-soft/40 ${l.follow_up_due ? "bg-peach-soft/30" : ""}`}>
                      <td className="px-4 py-2.5">
                        <Link href={`/prospects/${l.prospect_id}`} className="font-semibold text-ink hover:text-brand hover:underline">{l.name}</Link>
                        <p className="mt-0.5 flex flex-wrap items-center gap-1.5 text-xs text-ink-muted">
                          {[l.city, l.state].filter(Boolean).join(", ")} <DirectoryBadge directory={l.directory} /> <DistanceText miles={l.distance_mi} />
                        </p>
                        <div className="mt-1"><ReasonChips reason={l.top_reason} skipDistance /></div>
                      </td>
                      <td className="px-3 py-2.5"><ScoreMeter score={l.score} tier={l.tier} /></td>
                      <td className="px-3 py-2.5"><StatusCell lead={l} onSaved={() => list.reload()} onMessage={rowFeedback(l)} /></td>
                      <td className="px-3 py-2.5"><ContactActions lead={l} row={rows[l.lead_id]} /></td>
                      <td className="px-4 py-2.5 tabular-nums text-ink-muted">{formatShortDate(l.saved_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Narrow screens: compact cards with the same actions */}
              <ul className="divide-y divide-line md:hidden">
                {data.items.map((l) => (
                  <li key={l.lead_id} className={`space-y-2 px-4 py-3 ${l.follow_up_due ? "bg-peach-soft/30" : ""}`}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <Link href={`/prospects/${l.prospect_id}`} className="font-semibold text-ink hover:underline">{l.name}</Link>
                        <p className="flex flex-wrap items-center gap-1.5 text-xs text-ink-muted">{[l.city, l.state].filter(Boolean).join(", ")} <DistanceText miles={l.distance_mi} /></p>
                      </div>
                      <ScoreMeter score={l.score} tier={l.tier} />
                    </div>
                    <ReasonChips reason={l.top_reason} skipDistance />
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <StatusCell lead={l} onSaved={() => list.reload()} onMessage={rowFeedback(l)} />
                      <ContactActions lead={l} row={rows[l.lead_id]} />
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )
        ) : null}
        {data && data.total > 0 ? (
          <Pagination page={page} pageSize={data.page_size} total={data.total} onPage={(p) => setFilters({ page: String(p) })} />
        ) : null}
      </section>
    </>
  );
}

/** Route component for /leads. */
export default function LeadsPage() {
  return (
    // useSearchParams needs a Suspense boundary for the static build.
    <Suspense fallback={<SkeletonRows />}>
      <LeadsView />
    </Suspense>
  );
}
