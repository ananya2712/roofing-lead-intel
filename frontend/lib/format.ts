const TZ = "America/New_York"; // decision D15

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "Unknown";
  return new Date(iso).toLocaleDateString("en-US", { timeZone: TZ, month: "short", day: "numeric", year: "numeric" });
}

export function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", { timeZone: TZ, month: "short", day: "numeric" });
}

export function daysAgo(iso: string, now: Date = new Date()): number {
  return Math.floor((now.getTime() - new Date(iso).getTime()) / 86_400_000);
}

export function ago(iso: string): string {
  const d = daysAgo(iso);
  if (d <= 0) return "today";
  if (d === 1) return "1 day ago";
  return `${d} days ago`;
}

export function miles(v: number | null | undefined): string {
  return v === null || v === undefined ? "Unknown" : `${v.toFixed(1)} mi`;
}

export function titleCase(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function telHref(phone: string): string {
  return `tel:${phone.replace(/[^\d+]/g, "")}`;
}
