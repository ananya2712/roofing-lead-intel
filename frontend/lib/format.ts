// Display helpers.
const TZ = "America/New_York"; // Times are shown in New York time (decision D14).

/** Date as "Nov 5, 2026" in New York time, or "Unknown". */
export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "Unknown";
  return new Date(iso).toLocaleDateString("en-US", { timeZone: TZ, month: "short", day: "numeric", year: "numeric" });
}

/** Date as "Nov 5" in New York time. */
export function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", { timeZone: TZ, month: "short", day: "numeric" });
}

/** Whole days from the given time to now. */
export function daysAgo(iso: string, now: Date = new Date()): number {
  return Math.floor((now.getTime() - new Date(iso).getTime()) / 86_400_000);
}

/** Relative time: "today", "1 day ago" or "N days ago". */
export function ago(iso: string): string {
  const d = daysAgo(iso);
  if (d <= 0) return "today";
  if (d === 1) return "1 day ago";
  return `${d} days ago`;
}

/** Distance as "6.5 mi", or "Unknown". */
export function miles(v: number | null | undefined): string {
  return v === null || v === undefined ? "Unknown" : `${v.toFixed(1)} mi`;
}

/** First letter in upper case. */
export function titleCase(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** tel: link with only digits and +. */
export function telHref(phone: string): string {
  return `tel:${phone.replace(/[^\d+]/g, "")}`;
}
