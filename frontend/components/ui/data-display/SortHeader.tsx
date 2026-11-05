"use client";

type Props = { label: string; sortKey: string; current: string; onSort: (key: string) => void; align?: "left" | "right" };

/** A table header button. aria-sort tells screen readers the current order. */
export function SortHeader({ label, sortKey, current, onSort, align = "left" }: Props) {
  const active = current === sortKey;
  return (
    <th scope="col" aria-sort={active ? (sortKey === "name" ? "ascending" : sortKey === "distance" ? "ascending" : "descending") : "none"} className={`px-3 py-2 font-medium ${align === "right" ? "text-right" : ""}`}>
      <button type="button" onClick={() => onSort(sortKey)} className={`inline-flex items-center gap-1 rounded px-1 py-0.5 uppercase tracking-wide hover:bg-surface hover:text-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand ${active ? "text-brand" : ""}`}>
        {label}
        <span aria-hidden="true" className={active ? "" : "opacity-30"}>{sortKey === "score" ? "↓" : "↑"}</span>
      </button>
    </th>
  );
}
