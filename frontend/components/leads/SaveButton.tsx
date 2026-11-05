"use client";
import Link from "next/link";
import { useState } from "react";

import { api, unwrap, type ProspectDetail } from "@/lib/api";
import { titleCase } from "@/lib/format";

type Props = {
  prospectId: number;
  savedLeadId: number | null;
  savedVia: { prospect_id: number; directory: string } | null;
  onSaved?: (detail: ProspectDetail) => void;
  size?: "sm" | "md";
};

/** Save as lead. Shows the saved state, or a link when the company is saved through its other listing (D8). */
export function SaveButton({ prospectId, savedLeadId, savedVia, onSaved, size = "sm" }: Props) {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (savedLeadId) {
    return <span className="inline-flex items-center gap-1 text-sm font-medium text-success-ink">✓ Saved</span>;
  }
  if (savedVia) {
    return (
      <Link href={`/prospects/${savedVia.prospect_id}`} className="text-sm text-info-ink underline-offset-2 hover:underline">
        Saved via {titleCase(savedVia.directory)} listing
      </Link>
    );
  }

  async function save() {
    setPending(true);
    setError(null);
    try {
      const detail = await unwrap(
        api.POST("/prospects/{prospect_id}/save", { params: { path: { prospect_id: prospectId } } }),
        "The lead could not be saved. Try again.",
      );
      onSaved?.(detail);
    } catch (e) {
      setError(e instanceof Error ? e.message : "The lead could not be saved. Try again.");
    } finally {
      setPending(false);
    }
  }

  const pad = size === "md" ? "px-4 py-2" : "px-3 py-1.5";
  return (
    <span className="inline-flex flex-col items-start gap-1">
      <button
        type="button"
        onClick={save}
        disabled={pending}
        className={`whitespace-nowrap rounded bg-brand ${pad} text-sm font-medium text-white hover:bg-brand-hover disabled:cursor-wait disabled:opacity-70 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand`}
      >
        {pending ? "Saving…" : "Save as lead"}
      </button>
      {error ? <span role="alert" className="max-w-[220px] text-xs text-danger-ink">{error}</span> : null}
    </span>
  );
}
