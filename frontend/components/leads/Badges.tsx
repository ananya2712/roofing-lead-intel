import { Badge, type Tone } from "@/components/ui/data-display/Badge";
import type { Directory, LeadStatus, Tier } from "@/lib/api";
import { titleCase } from "@/lib/format";

export const TIER_TONE: Record<Tier, Tone> = { high: "mint", medium: "lavender", low: "neutral" };
export const STATUS_TONE: Record<LeadStatus, Tone> = { new: "sky", contacted: "peach", qualified: "mint", dismissed: "neutral" };
export const DIRECTORY_TONE: Record<Directory, Tone> = { residential: "sky", commercial: "butter" };

// Chart colors that match the badge tones.
export const TIER_COLOR = { high: "#8EDBB0", medium: "#B9A8F5", low: "#CBD0DA" };
export const STATUS_COLOR = { new: "#94C8F2", contacted: "#F7B98C", qualified: "#8EDBB0", dismissed: "#CBD0DA" };
export const DIRECTORY_COLOR = { residential: "#94C8F2", commercial: "#F0D46A" };

export function PriorityBadge({ score, tier }: { score: number; tier: Tier }) {
  return (
    <Badge tone={TIER_TONE[tier]} dot>
      <span className="tabular-nums font-semibold">{score}</span> {titleCase(tier)}
    </Badge>
  );
}

/** Score as a number with a small meter, for tables. */
export function ScoreMeter({ score, tier }: { score: number; tier: Tier }) {
  return (
    <span className="inline-flex items-center gap-2" title={`Score ${score} of 100 · ${titleCase(tier)} priority`}>
      <PriorityBadge score={score} tier={tier} />
      <span className="hidden h-1.5 w-14 rounded-sm bg-subtle xl:block" aria-hidden="true">
        <span className="block h-1.5 rounded-sm" style={{ width: `${score}%`, background: TIER_COLOR[tier] }} />
      </span>
    </span>
  );
}

export function DirectoryBadge({ directory }: { directory: Directory }) {
  return <Badge tone={DIRECTORY_TONE[directory]}>{titleCase(directory)}</Badge>;
}

export function StatusBadge({ status }: { status: LeadStatus }) {
  return <Badge tone={STATUS_TONE[status]} dot>{titleCase(status)}</Badge>;
}

/** Colored distance: closer prospects stand out. */
export function DistanceText({ miles }: { miles: number | null }) {
  if (miles === null) return <span className="text-ink-faint">Unknown</span>;
  const color = miles <= 10 ? "bg-mint-mid" : miles <= 25 ? "bg-sky-mid" : "bg-lavender-mid";
  return (
    <span className="inline-flex items-center gap-1.5 tabular-nums">
      <span className={`h-2 w-2 rounded-full ${color}`} aria-hidden="true" />
      <span className={miles <= 10 ? "font-semibold text-ink" : "text-ink"}>{miles.toFixed(1)} mi</span>
    </span>
  );
}
