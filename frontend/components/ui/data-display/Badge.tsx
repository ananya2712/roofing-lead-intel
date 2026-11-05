import type { ReactNode } from "react";

export type Tone = "neutral" | "brand" | "lavender" | "mint" | "peach" | "sky" | "rose" | "butter";

const TONES: Record<Tone, string> = {
  neutral: "bg-subtle text-ink-muted ring-line",
  brand: "bg-brand-soft text-brand ring-brand/15",
  lavender: "bg-lavender-soft text-lavender-ink ring-lavender-mid/40",
  mint: "bg-mint-soft text-mint-ink ring-mint-mid/50",
  peach: "bg-peach-soft text-peach-ink ring-peach-mid/50",
  sky: "bg-sky-soft text-sky-ink ring-sky-mid/50",
  rose: "bg-rose-soft text-rose-ink ring-rose-mid/50",
  butter: "bg-butter-soft text-butter-ink ring-butter-mid/60",
};

const DOTS: Record<Tone, string> = {
  neutral: "bg-ink-faint", brand: "bg-brand", lavender: "bg-lavender-mid", mint: "bg-mint-mid",
  peach: "bg-peach-mid", sky: "bg-sky-mid", rose: "bg-rose-mid", butter: "bg-butter-mid",
};

/** A small text label. Color supports the text; the text always carries the meaning. */
export function Badge({ tone = "neutral", dot = false, children }: { tone?: Tone; dot?: boolean; children: ReactNode }) {
  return (
    <span className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded px-1.5 py-0.5 text-xs font-medium ring-1 ring-inset ${TONES[tone]}`}>
      {dot ? <span className={`h-1.5 w-1.5 rounded-full ${DOTS[tone]}`} aria-hidden="true" /> : null}
      {children}
    </span>
  );
}
