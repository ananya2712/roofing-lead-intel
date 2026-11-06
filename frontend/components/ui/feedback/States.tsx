// Error banner, empty state, loading rows and live status message.
import type { ReactNode } from "react";

/** Error message with an optional Try again button. */
export function ErrorBanner({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex items-center justify-between gap-3 rounded-md border border-danger/30 bg-danger-soft px-4 py-3 text-sm text-danger-ink">
      <span>{message}</span>
      {onRetry ? (
        <button type="button" onClick={onRetry} className="rounded bg-surface px-3 py-1 font-medium text-danger-ink ring-1 ring-danger/30 hover:bg-danger-soft focus-visible:outline focus-visible:outline-2 focus-visible:outline-danger">
          Try again
        </button>
      ) : null}
    </div>
  );
}

/** Message shown when a list has no rows. */
export function EmptyState({ title, action }: { title: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-3 px-4 py-10 text-center">
      <p className="text-sm text-ink-muted">{title}</p>
      {action}
    </div>
  );
}

/** Gray placeholder rows while data loads. */
export function SkeletonRows({ rows = 6 }: { rows?: number }) {
  return (
    <div className="space-y-2 p-4" aria-hidden="true">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-9 animate-pulse rounded bg-canvas" />
      ))}
    </div>
  );
}

/** A short message that screen readers announce. */
export function StatusMessage({ message, tone }: { message: string | null; tone: "success" | "danger" }) {
  return (
    <p role="status" aria-live="polite" className={`min-h-[18px] text-sm ${tone === "success" ? "text-success-ink" : "text-danger-ink"}`}>
      {message}
    </p>
  );
}
