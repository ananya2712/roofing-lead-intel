import { Badge, type Tone } from "@/components/ui/data-display/Badge";

/** Split the one-line score reason into chips so the signals are easy to scan. */
export function ReasonChips({ reason, skipDistance = false }: { reason: string; skipDistance?: boolean }) {
  // skipDistance avoids a repeat when the row already shows the distance.
  const parts = reason.split(", ").filter((p) => p && !(skipDistance && / mi$/.test(p)));
  const tone = (p: string): Tone => (/ mi$/.test(p) ? "sky" : /elite|club|circle|certified|coatingspro/i.test(p) ? "lavender" : "neutral");
  return (
    <span className="flex flex-wrap gap-1">
      {parts.map((p) => <Badge key={p} tone={tone(p)}>{p}</Badge>)}
    </span>
  );
}
