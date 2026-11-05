"use client";
import { useState } from "react";

import { api, LEAD_STATUSES, unwrap, type LeadStatus, type ProspectDetail } from "@/lib/api";
import { titleCase } from "@/lib/format";

type Props = {
  leadId: number;
  value: LeadStatus;
  label: string;
  onSaved: (status: LeadStatus, detail: ProspectDetail) => void;
  onMessage?: (message: string, ok: boolean) => void;
};

const TINT: Record<LeadStatus, string> = {
  new: "border-sky-mid/60 bg-sky-soft text-sky-ink",
  contacted: "border-peach-mid/60 bg-peach-soft text-peach-ink",
  qualified: "border-mint-mid/70 bg-mint-soft text-mint-ink",
  dismissed: "border-line bg-subtle text-ink-muted",
};

/** Status dropdown. A change saves at once. On failure the old value comes back. */
export function StatusSelect({ leadId, value, label, onSaved, onMessage }: Props) {
  const [current, setCurrent] = useState<LeadStatus>(value);
  const [pending, setPending] = useState(false);

  async function change(next: LeadStatus) {
    const previous = current;
    setCurrent(next);
    setPending(true);
    try {
      const detail = await unwrap(
        api.POST("/leads/{lead_id}/status", { params: { path: { lead_id: leadId } }, body: { status: next } }),
        "The status could not be saved. Try again.",
      );
      onSaved(next, detail);
      onMessage?.("Status saved.", true);
    } catch (e) {
      setCurrent(previous);
      onMessage?.(e instanceof Error ? e.message : "The status could not be saved. Try again.", false);
    } finally {
      setPending(false);
    }
  }

  return (
    <select
      aria-label={label}
      value={current}
      disabled={pending}
      onChange={(e) => change(e.target.value as LeadStatus)}
      className={`h-8 rounded border px-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-brand/30 disabled:opacity-60 ${TINT[current]}`}
    >
      {LEAD_STATUSES.map((s) => (
        <option key={s} value={s}>{titleCase(s)}</option>
      ))}
    </select>
  );
}
