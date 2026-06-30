"use client";

import { useState } from "react";
import type { ScoredShow } from "@/lib/api";
import { FeatureCard } from "./FeatureCard";

const PAGE_SIZE = 3;

// Shows recommendations 3 at a time as large cards. "Show me 3 more" pages
// through the ranked list so the choice never feels like an overwhelming wall.
export function RecommendationStage({
  heading,
  items,
}: {
  heading: React.ReactNode;
  items: ScoredShow[];
}) {
  const pages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
  const [page, setPage] = useState(0);

  const start = page * PAGE_SIZE;
  const current = items.slice(start, start + PAGE_SIZE);

  return (
    <section className="mx-auto max-w-[1120px] px-6 md:px-10">
      <div className="flex items-baseline justify-between border-t border-[var(--line)] pt-8">
        <h2 className="font-serif text-[22px]">{heading}</h2>
        <span className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
          {start + 1}–{Math.min(start + PAGE_SIZE, items.length)} of {items.length}
        </span>
      </div>

      {/* key re-mounts the grid each page so the fade-in replays */}
      <div
        key={page}
        className="mt-9 grid grid-cols-1 gap-x-8 gap-y-12 [animation:fadeUp_0.4s_ease] sm:grid-cols-2 lg:grid-cols-3"
      >
        {current.map((s) => (
          <FeatureCard key={s.id} show={s} />
        ))}
      </div>

      <div className="mt-11 flex items-center justify-center gap-6">
        <button
          onClick={() => setPage((p) => (p - 1 + pages) % pages)}
          aria-label="Previous recommendations"
          className="rounded-full border border-[var(--line)] p-2 text-[var(--muted)] transition-colors hover:text-[var(--ink)]"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>

        <div className="flex items-center gap-2">
          {Array.from({ length: pages }).map((_, i) => (
            <span
              key={i}
              className="h-1.5 w-1.5 rounded-full transition-colors"
              style={{ background: i === page ? "var(--accent)" : "var(--line)" }}
            />
          ))}
        </div>

        <button
          onClick={() => setPage((p) => (p + 1) % pages)}
          className="group/btn flex items-center gap-2 text-[12px] uppercase tracking-[0.16em] text-[var(--ink)] transition-colors hover:text-[var(--accent)]"
        >
          Show me 3 more
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" className="transition-transform group-hover/btn:translate-x-0.5">
            <path d="M9 18l6-6-6-6" />
          </svg>
        </button>
      </div>
    </section>
  );
}
