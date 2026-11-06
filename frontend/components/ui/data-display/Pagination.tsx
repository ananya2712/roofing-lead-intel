type Props = { page: number; pageSize: number; total: number; onPage: (p: number) => void };

/** Previous and Next buttons with the shown range of the total. */
export function Pagination({ page, pageSize, total, onPage }: Props) {
  const pages = Math.max(1, Math.ceil(total / pageSize));
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(total, page * pageSize);
  const btn = "rounded border border-line bg-surface px-3 py-1.5 text-sm font-medium text-ink hover:bg-canvas disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand";
  return (
    <nav className="flex items-center justify-between gap-3 border-t border-line px-4 py-3" aria-label="Pagination">
      <p className="text-sm text-ink-muted tabular-nums">
        {from}–{to} of {total}
      </p>
      <div className="flex items-center gap-2">
        <button type="button" className={btn} disabled={page <= 1} onClick={() => onPage(page - 1)}>Previous</button>
        <span className="text-sm text-ink-muted tabular-nums">Page {page} of {pages}</span>
        <button type="button" className={btn} disabled={page >= pages} onClick={() => onPage(page + 1)}>Next</button>
      </div>
    </nav>
  );
}
