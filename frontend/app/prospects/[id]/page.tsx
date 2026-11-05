"use client";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import { DirectoryBadge, PriorityBadge } from "@/components/leads/Badges";
import { SaveButton } from "@/components/leads/SaveButton";
import { StatusSelect } from "@/components/leads/StatusSelect";
import { Badge } from "@/components/ui/data-display/Badge";
import { ErrorBanner, SkeletonRows, StatusMessage } from "@/components/ui/feedback/States";
import { api, unwrap, type ProspectDetail } from "@/lib/api";
import { ago, formatDate, miles, telHref, titleCase } from "@/lib/format";
import { useLoad } from "@/lib/useLoad";

const UNKNOWN = <span className="text-ink-faint">Unknown</span>;

function Card({ title, label, children }: { title: string; label?: string; children: React.ReactNode }) {
  return (
    <section className="overflow-hidden rounded-md border border-line bg-surface shadow-card" aria-label={title}>
      <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-line px-4 py-3">
        <h2 className="text-sm font-semibold text-ink">{title}</h2>
        {label ? <p className="text-xs text-ink-muted">{label}</p> : null}
      </div>
      <div className="p-4">{children}</div>
    </section>
  );
}

function Fact({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[140px_1fr] gap-3 py-1.5 text-sm">
      <dt className="text-ink-muted">{label}</dt>
      <dd className="min-w-0 break-words text-ink">{children}</dd>
    </div>
  );
}

function About({ text }: { text: string }) {
  const [open, setOpen] = useState(false);
  const long = text.length > 320;
  return (
    <div className="text-sm leading-6 text-ink">
      <p>{open || !long ? text : `${text.slice(0, 320)}…`}</p>
      {long ? (
        <button type="button" onClick={() => setOpen(!open)} aria-expanded={open} className="mt-1 text-sm text-info-ink hover:underline">
          {open ? "Show less" : "Read more"}
        </button>
      ) : null}
    </div>
  );
}

export default function ProspectPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const prospectId = Number(id);
  const [msg, setMsg] = useState<{ text: string; ok: boolean } | null>(null);
  const detail = useLoad(
    (signal) =>
      unwrap(api.GET("/prospects/{prospect_id}", { signal, params: { path: { prospect_id: prospectId } } }), "This prospect could not be loaded."),
    String(prospectId),
  );
  const p = detail.data;
  const update = (d: ProspectDetail) => detail.setData(() => d);
  const [marking, setMarking] = useState(false);

  async function markContacted(leadId: number) {
    setMarking(true);
    try {
      update(await unwrap(
        api.PATCH("/leads/{lead_id}/status", { params: { path: { lead_id: leadId } }, body: { status: "contacted" } }),
        "The status could not be saved. Try again.",
      ));
      setMsg({ text: "Marked as contacted.", ok: true });
    } catch (e) {
      setMsg({ text: e instanceof Error ? e.message : "The status could not be saved. Try again.", ok: false });
    } finally {
      setMarking(false);
    }
  }

  if (detail.error && !p) {
    return (
      <>
        <Link href="/prospects" className="text-sm text-info-ink hover:underline">← Prospects</Link>
        <ErrorBanner message={detail.error} onRetry={detail.reload} />
      </>
    );
  }
  if (!p) return <SkeletonRows rows={8} />;

  const pointsTotal = p.score_breakdown.reduce((a, i) => a + i.points, 0);

  return (
    <>
      <button type="button" onClick={() => router.back()} className="text-sm text-info-ink hover:underline">← Back</button>

      <header className="rounded-md border border-line bg-gradient-to-r from-lavender-soft via-surface to-sky-soft p-4 shadow-card">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl font-semibold text-ink">{p.name}</h1>
              <DirectoryBadge directory={p.directory} />
              <PriorityBadge score={p.score} tier={p.tier} />
            </div>
            <p className="mt-1 text-sm text-ink-muted">
              {[p.city, p.state].filter(Boolean).join(", ") || "Location unknown"} · {miles(p.distance_mi)} from ZIP 10013
            </p>
            <div className="mt-3 flex flex-wrap gap-2 text-sm">
              {p.phone ? <a href={telHref(p.phone)} className="rounded border border-line px-2.5 py-1 text-info-ink hover:bg-info-soft">Call {p.phone}</a> : null}
              {p.website_url ? <a href={p.website_url} target="_blank" rel="noopener noreferrer" className="rounded border border-line px-2.5 py-1 text-info-ink hover:bg-info-soft">Website ↗</a> : null}
              <a href={p.profile_url} target="_blank" rel="noopener noreferrer" className="rounded border border-line px-2.5 py-1 text-info-ink hover:bg-info-soft">View on GAF ↗</a>
            </div>
          </div>
          <div className="flex flex-col items-start gap-1 sm:items-end">
            {p.lead ? (
              <>
                <div className="flex flex-wrap items-center gap-2">
                  {p.lead.status === "new" ? (
                    <button type="button" onClick={() => markContacted(p.lead!.id)} disabled={marking}
                      className="whitespace-nowrap rounded bg-brand px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-hover disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand">
                      {marking ? "Saving…" : "Mark contacted"}
                    </button>
                  ) : null}
                  <StatusSelect
                    key={p.lead.status}
                    leadId={p.lead.id}
                    value={p.lead.status}
                    label="Lead status"
                    onSaved={(_, d) => update(d)}
                    onMessage={(text, ok) => setMsg({ text, ok })}
                  />
                </div>
                <p className="text-xs text-ink-muted">Saved {formatDate(p.lead.saved_at)} · status changed {ago(p.lead.status_changed_at)}</p>
              </>
            ) : (
              <SaveButton
                size="md"
                prospectId={p.id}
                savedLeadId={null}
                savedVia={p.saved_via}
                onSaved={(d) => { update(d); setMsg({ text: "Saved as a lead with status New.", ok: true }); }}
              />
            )}
            <StatusMessage message={msg?.text ?? null} tone={msg?.ok ? "success" : "danger"} />
          </div>
        </div>
      </header>

      <div className="grid gap-4 lg:grid-cols-[3fr_2fr]">
        <Card title="Source facts" label={`From GAF · retrieved ${formatDate(p.retrieved_at)}`}>
          <dl className="divide-y divide-line">
            <Fact label="Address">{p.address ?? UNKNOWN}</Fact>
            <Fact label="Phone">{p.phone ?? UNKNOWN}</Fact>
            <Fact label="Website">{p.website_url ? <a className="text-info-ink hover:underline" href={p.website_url} target="_blank" rel="noopener noreferrer">{p.website_url}</a> : UNKNOWN}</Fact>
            <Fact label="Distance">{p.distance_mi !== null ? miles(p.distance_mi) : UNKNOWN}</Fact>
            <Fact label="Google rating">{p.rating !== null ? `${p.rating.toFixed(1)} · ${p.review_count ?? 0} reviews` : UNKNOWN}</Fact>
            <Fact label="Years in business">{p.years_in_business ?? UNKNOWN}</Fact>
            <Fact label="Distinctions">
              {p.distinctions.length ? <span className="flex flex-wrap gap-1.5">{p.distinctions.map((d) => <Badge key={d} tone="brand">{d}</Badge>)}</span> : UNKNOWN}
            </Fact>
            <Fact label={p.directory === "commercial" ? "Technologies" : "Specialties"}>
              {p.specialties.length ? <span className="flex flex-wrap gap-1.5">{p.specialties.map((s) => <Badge key={s}>{s}</Badge>)}</span> : UNKNOWN}
            </Fact>
            <Fact label="GAF ID">{p.gaf_source_id}</Fact>
            {p.also_listed_in ? (
              <Fact label="Other listing">
                <Link className="text-info-ink hover:underline" href={`/prospects/${p.also_listed_in.prospect_id}`}>Also listed in {titleCase(p.also_listed_in.directory)} →</Link>
              </Fact>
            ) : null}
          </dl>
          <div className="mt-4 border-t border-line pt-3">
            <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-ink-muted">About (written by the contractor)</h3>
            {p.about_text ? <About text={p.about_text} /> : <p className="text-sm">{UNKNOWN}</p>}
          </div>
        </Card>

        <div className="space-y-4">
          <Card title="Why this priority" label={`Total ${pointsTotal} / 100`}>
            <ul className="space-y-2.5">
              {p.score_breakdown.map((i) => (
                <li key={i.key} className="text-sm">
                  <div className="flex items-baseline justify-between gap-2">
                    <span className="font-medium text-ink">{i.label}</span>
                    <span className={`tabular-nums ${i.points === 0 ? "text-ink-faint" : "text-ink"}`}>{i.points} / {i.max}</span>
                  </div>
                  <div className="mt-1 h-1.5 rounded-full bg-canvas">
                    <div className="h-1.5 rounded-full" style={{ width: `${(i.points / i.max) * 100}%`, background: i.points === i.max ? "#8EDBB0" : i.points > 0 ? "#B9A8F5" : "transparent" }} />
                  </div>
                  <p className={`mt-0.5 text-xs ${i.unknown ? "text-caution-ink" : "text-ink-muted"}`}>{i.unknown ? "Unknown: " : ""}{i.reason}</p>
                </li>
              ))}
            </ul>
            <p className="mt-3 border-t border-line pt-2 text-xs text-ink-muted">
              Fixed rules calculate the score from GAF data (rule version v1). Ratings and reviews are not scored. A GAF listing does not show purchase intent or business size.
            </p>
          </Card>

          <Card title="What we don't know">
            {p.unknown_fields.length ? (
              <>
                <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">Missing from the GAF listing</p>
                <ul className="mt-1 flex flex-wrap gap-1.5">{p.unknown_fields.map((f) => <Badge key={f} tone="peach">{f}</Badge>)}</ul>
              </>
            ) : <p className="text-sm text-ink-muted">The GAF listing has all tracked fields.</p>}
            <p className="mt-3 text-xs font-medium uppercase tracking-wide text-ink-muted">Not available from public sources</p>
            <ul className="mt-1 list-disc pl-5 text-sm text-ink">{p.not_in_public_sources.map((f) => <li key={f}>{f}</li>)}</ul>
            <p className="mt-2 text-xs text-ink-muted">Ask about these during the first call.</p>
          </Card>
        </div>
      </div>
    </>
  );
}
