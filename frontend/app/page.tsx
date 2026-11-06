"use client";
// Sales dashboard (/): pipeline counts, call lists and top unsaved prospects.
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";

import { DirectoryToggle } from "@/components/leads/DirectoryToggle";

import { DirectoryBadge, PriorityBadge, STATUS_COLOR } from "@/components/leads/Badges";
import { ReasonChips } from "@/components/leads/ReasonChips";
import { SaveButton } from "@/components/leads/SaveButton";
import { Icon, type IconName } from "@/components/ui/data-display/Icon";
import { KpiCard, KpiGroup } from "@/components/ui/data-display/KpiCard";
import { ErrorBanner, SkeletonRows, StatusMessage } from "@/components/ui/feedback/States";
import { PageHeader } from "@/components/ui/layout/PageHeader";
import { api, unwrap, type LeadSummary, type Overview } from "@/lib/api";
import { ago, formatDate, telHref } from "@/lib/format";

/** Titled dashboard panel with an icon and an optional action link. */
function Panel({ title, hint, icon, tone, action, children }: {
  title: string; hint?: string; icon: IconName; tone: string; action?: React.ReactNode; children: React.ReactNode;
}) {
  return (
    <section className="overflow-hidden rounded-md border border-line bg-surface shadow-card" aria-label={title}>
      <div className="flex items-center justify-between gap-2 border-b border-line px-4 py-3">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-ink">
          <span className={`inline-flex h-6 w-6 items-center justify-center rounded ${tone}`}><Icon name={icon} className="h-3.5 w-3.5" /></span>
          {title}
          {hint ? <span className="text-xs font-normal text-ink-faint">· {hint}</span> : null}
        </h2>
        {action}
      </div>
      {children}
    </section>
  );
}

/** Route component for / (Sales dashboard). */
export default function OverviewPage() {
  return (
    // useSearchParams needs a Suspense boundary for the static build.
    <Suspense fallback={<SkeletonRows rows={4} />}>
      <OverviewView />
    </Suspense>
  );
}

/** Sales dashboard view for the directory in the URL. */
function OverviewView() {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const directory = (sp.get("directory") || undefined) as "residential" | "commercial" | undefined;
  // Links keep the chosen directory, so Saved leads and Prospects open with the same filter.
  const withDir = (href: string) => (directory ? `${href}${href.includes("?") ? "&" : "?"}directory=${directory}` : href);
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState<{ text: string; ok: boolean } | null>(null);
  const [busy, setBusy] = useState<number | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      setData(await unwrap(api.GET("/overview", { params: { query: { directory } } }), "The overview could not be loaded."));
    } catch (e) {
      setError(e instanceof Error ? e.message : "The overview could not be loaded.");
    }
  }, [directory]);
  useEffect(() => { void load(); }, [load]);

  async function markContacted(lead: LeadSummary) {
    setBusy(lead.lead_id);
    try {
      await unwrap(
        api.POST("/leads/{lead_id}/status", { params: { path: { lead_id: lead.lead_id } }, body: { status: "contacted" } }),
        "The status could not be saved. Try again.",
      );
      setMsg({ text: `${lead.name} marked as contacted.`, ok: true });
      await load();
    } catch (e) {
      setMsg({ text: e instanceof Error ? e.message : "The status could not be saved.", ok: false });
    } finally {
      setBusy(null);
    }
  }

  const today = new Date().toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "long", month: "long", day: "numeric" });
  const total = data ? data.saved + data.dismissed : 0;
  const segments = data
    ? [
        { key: "new", label: "New", value: data.not_contacted, color: STATUS_COLOR.new },
        { key: "contacted", label: "Contacted", value: data.contacted - data.qualified, color: STATUS_COLOR.contacted },
        { key: "qualified", label: "Qualified", value: data.qualified, color: STATUS_COLOR.qualified },
        { key: "dismissed", label: "Dismissed", value: data.dismissed, color: STATUS_COLOR.dismissed },
      ]
    : [];

  return (
    <>
      <PageHeader
        title="Sales dashboard"
        subtitle={<>{today} · GAF snapshot, ZIP 10013, 50 mi{data?.snapshot_retrieved_at ? `, retrieved ${formatDate(data.snapshot_retrieved_at)}` : ""}</>}
        actions={<div className="flex flex-wrap items-center gap-2"><DirectoryToggle value={directory ?? ""} onChange={(v) => router.replace(v ? `${pathname}?directory=${v}` : pathname, { scroll: false })} /><Link href={withDir("/prospects?tier=high&hide_saved=true")} className="inline-flex items-center gap-1.5 rounded bg-brand px-3 py-2 text-sm font-medium text-white hover:bg-brand-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"><Icon name="search" />Find new prospects</Link></div>}
      />
      {error ? <ErrorBanner message={error} onRetry={load} /> : null}
      <StatusMessage message={msg?.text ?? null} tone={msg?.ok ? "success" : "danger"} />

      {!data && !error ? <SkeletonRows rows={4} /> : null}
      {data ? (
        <>
          <KpiGroup>
            <KpiCard icon="bookmark" tone="lavender" label="Saved leads" value={data.saved} hint="Not counting dismissed" href={withDir("/leads")} />
            <KpiCard icon="clock" tone="sky" label="Not contacted yet" value={data.not_contacted} hint="Status New · call these first" href={withDir("/leads?queue=first_contact")} />
            <KpiCard icon="phone" tone="peach" label="Contacted" value={<>{data.contacted}<span className="text-sm font-medium text-peach-ink">{data.contacted_pct}%</span></>} hint="Contacted or Qualified, share of saved leads" href={withDir("/leads?status=contacted")} />
            <KpiCard icon="check" tone="mint" label="Qualified" value={data.qualified} hint="Status Qualified" href={withDir("/leads?status=qualified")} />
          </KpiGroup>

          <section className="rounded-md border border-line bg-surface p-4 shadow-card" aria-label="Pipeline">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2 className="text-sm font-semibold text-ink">Pipeline by current status</h2>
              <p className="text-xs text-ink-faint">No status history is kept, so this shows today only.</p>
            </div>
            {total === 0 ? (
              <p className="mt-3 text-sm text-ink-muted">No saved leads yet. <Link className="text-info-ink underline" href="/prospects">Find prospects</Link>.</p>
            ) : (
              <>
                <div className="mt-3 flex h-4 gap-0.5 overflow-hidden rounded-sm">
                  {segments.filter((s) => s.value > 0).map((s) => (
                    <Link key={s.key} href={withDir(s.key === "dismissed" ? "/leads?scope=dismissed" : `/leads?status=${s.key}`)} title={`${s.label}: ${s.value}`}
                      aria-label={`${s.label}: ${s.value}`} className="transition-[filter] hover:brightness-95" style={{ width: `${(s.value / total) * 100}%`, background: s.color }} />
                  ))}
                </div>
                <ul className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
                  {segments.map((s) => (
                    <li key={s.key}>
                      <Link href={withDir(s.key === "dismissed" ? "/leads?scope=dismissed" : `/leads?status=${s.key}`)} className="flex items-center gap-2 rounded border border-line px-3 py-2 text-sm hover:bg-subtle">
                        <span className="h-3 w-3 rounded-sm" style={{ background: s.color }} />
                        <span className="text-ink-muted">{s.label}</span>
                        <span className="ml-auto font-semibold tabular-nums">{s.value}</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </section>

          <div className="grid gap-4 lg:grid-cols-2">
            <Panel title="Call next" hint="New leads, highest score first" icon="phone" tone="bg-sky-soft text-sky-ink"
              action={<Link href={withDir("/leads?queue=first_contact")} className="text-xs text-info-ink hover:underline">See all</Link>}>
              {data.call_next.length === 0 ? (
                <p className="px-4 py-6 text-sm text-ink-muted">No new leads to call. Save prospects to fill this list.</p>
              ) : (
                <ul className="divide-y divide-line">
                  {data.call_next.map((l) => (
                    <li key={l.lead_id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-2.5 hover:bg-subtle">
                      <div className="min-w-0">
                        <Link href={`/prospects/${l.prospect_id}`} className="font-semibold text-ink hover:text-brand hover:underline">{l.name}</Link>
                        <p className="mt-0.5 flex items-center gap-1.5 text-xs text-ink-muted">{[l.city, l.state].filter(Boolean).join(", ")} <PriorityBadge score={l.score} tier={l.tier} /></p>
                      </div>
                      <div className="flex items-center gap-2">
                        {l.phone ? <a href={telHref(l.phone)} className="inline-flex items-center gap-1 rounded border border-sky-mid/60 bg-sky-soft px-2.5 py-1 text-sm font-medium text-sky-ink hover:brightness-95"><Icon name="phone" className="h-3.5 w-3.5" />{l.phone}</a> : <span className="text-sm text-ink-faint">Phone unknown</span>}
                        <button type="button" disabled={busy === l.lead_id} onClick={() => markContacted(l)} className="rounded bg-brand px-2.5 py-1 text-sm font-medium text-white hover:bg-brand-hover disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand">
                          {busy === l.lead_id ? "Saving…" : "Mark contacted"}
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </Panel>

            <Panel title="Follow up" hint={`Contacted ${data.follow_up_days}+ days ago`} icon="clock" tone="bg-peach-soft text-peach-ink"
              action={<Link href={withDir("/leads?queue=follow_up_due")} className="text-xs text-info-ink hover:underline">See all</Link>}>
              {data.follow_up.length === 0 ? (
                <p className="px-4 py-6 text-sm text-ink-muted">No leads need a follow-up today.</p>
              ) : (
                <ul className="divide-y divide-line">
                  {data.follow_up.map((l) => (
                    <li key={l.lead_id} className="flex items-center justify-between gap-2 px-4 py-2.5 hover:bg-subtle">
                      <Link href={`/prospects/${l.prospect_id}`} className="font-semibold text-ink hover:text-brand hover:underline">{l.name}</Link>
                      <span className="rounded bg-peach-soft px-2 py-0.5 text-xs font-medium text-peach-ink">Contacted {ago(l.status_changed_at)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Panel>
          </div>

          <Panel title="Top prospects not saved" hint="High priority, score 70 or more" icon="star" tone="bg-mint-soft text-mint-ink"
            action={<Link href={withDir("/prospects?tier=high&hide_saved=true")} className="text-xs text-info-ink hover:underline">See all</Link>}>
            {data.top_unsaved.length === 0 ? (
              <p className="px-4 py-6 text-sm text-ink-muted">All high-priority prospects are saved.</p>
            ) : (
              <ul className="divide-y divide-line">
                {data.top_unsaved.map((p) => (
                  <li key={p.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 hover:bg-subtle">
                    <div className="min-w-0 space-y-1">
                      <p className="flex flex-wrap items-center gap-2">
                        <Link href={`/prospects/${p.id}`} className="font-semibold text-ink hover:text-brand hover:underline">{p.name}</Link>
                        <DirectoryBadge directory={p.directory} /> <PriorityBadge score={p.score} tier={p.tier} />
                      </p>
                      <ReasonChips reason={p.top_reason} />
                    </div>
                    <SaveButton prospectId={p.id} savedLeadId={p.saved_lead_id} savedVia={p.saved_via} onSaved={() => { setMsg({ text: `${p.name} saved as a lead.`, ok: true }); void load(); }} />
                  </li>
                ))}
              </ul>
            )}
          </Panel>
        </>
      ) : null}
    </>
  );
}
