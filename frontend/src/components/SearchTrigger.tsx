"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { searchShows, type Show } from "@/lib/api";

// Search icon → command-palette overlay with live, debounced results.
// Opens on click or "/"; closes on Esc or backdrop click.
export function SearchTrigger() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [results, setResults] = useState<Show[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const close = useCallback(() => {
    setOpen(false);
    setQ("");
    setResults([]);
  }, []);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const tag = (e.target as HTMLElement)?.tagName;
      const typing = tag === "INPUT" || tag === "TEXTAREA";
      if (e.key === "/" && !typing && !open) {
        e.preventDefault();
        setOpen(true);
      } else if (e.key === "Escape") {
        close();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, close]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  // Debounced search.
  useEffect(() => {
    if (timer.current) clearTimeout(timer.current);
    if (!q.trim()) {
      setResults([]);
      return;
    }
    timer.current = setTimeout(() => {
      searchShows(q, 8)
        .then(setResults)
        .catch(() => setResults([]));
    }, 220);
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [q]);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Search"
        className="rounded-full border border-[var(--line)] p-2 text-[var(--muted)] transition-colors hover:text-[var(--ink)]"
      >
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round">
          <circle cx="11" cy="11" r="7" />
          <path d="M21 21l-4.3-4.3" />
        </svg>
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex justify-center bg-black/40 px-4 pt-24 backdrop-blur-sm"
          onClick={close}
        >
          <div
            className="h-fit w-full max-w-[560px] overflow-hidden rounded-[6px] border border-[var(--line)] bg-[var(--surface)] shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 border-b border-[var(--line)] px-4">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" className="text-[var(--muted)]">
                <circle cx="11" cy="11" r="7" />
                <path d="M21 21l-4.3-4.3" />
              </svg>
              <input
                ref={inputRef}
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search K-dramas…"
                className="w-full bg-transparent py-4 text-[15px] outline-none placeholder:text-[var(--muted)]"
              />
            </div>

            {results.length > 0 && (
              <ul className="max-h-[60vh] overflow-auto py-2">
                {results.map((s) => (
                  <li key={s.id}>
                    <Link
                      href={`/show/${s.id}`}
                      onClick={close}
                      className="flex items-center gap-3 px-4 py-2 transition-colors hover:bg-[var(--bg)]"
                    >
                      <span className="h-12 w-8 shrink-0 overflow-hidden rounded-[2px] bg-[var(--line)]">
                        {s.poster_path && (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={`https://image.tmdb.org/t/p/w92${s.poster_path}`}
                            alt=""
                            className="h-full w-full object-cover"
                          />
                        )}
                      </span>
                      <span className="min-w-0">
                        <span className="block truncate font-serif text-[15px]">{s.title}</span>
                        <span className="block truncate text-[11px] uppercase tracking-[0.12em] text-[var(--muted)]">
                          {[s.year, s.genres.slice(0, 2).join(" · ")].filter(Boolean).join(" · ")}
                        </span>
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}

            {q.trim() && results.length === 0 && (
              <p className="px-4 py-6 text-[14px] text-[var(--muted)]">No matches for “{q}”.</p>
            )}
          </div>
        </div>
      )}
    </>
  );
}
