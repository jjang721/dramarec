import Link from "next/link";
import type { Show } from "@/lib/api";
import { LikeButton } from "./LikeButton";
import { PosterPlaceholder } from "./PosterPlaceholder";

// `meta` overrides the default genre line (used to surface the "why" on
// recommendation cards). `match` shows the similarity score when present.
export function ShowCard({
  show,
  match,
  meta,
}: {
  show: Show;
  match?: number;
  meta?: string;
}) {
  return (
    <Link href={`/show/${show.id}`} className="group block">
      <div className="relative overflow-hidden rounded-[3px] ring-1 ring-[var(--line)] transition-transform duration-300 ease-out group-hover:-translate-y-1">
        <LikeButton showId={show.id} />
        {show.poster_path ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`https://image.tmdb.org/t/p/w500${show.poster_path}`}
            alt={show.title}
            className="aspect-[2/3] w-full object-cover"
          />
        ) : (
          <PosterPlaceholder title={show.title} seed={show.id} />
        )}
      </div>

      <div className="mt-3 flex items-baseline justify-between gap-3">
        <p className="truncate text-[11px] uppercase tracking-[0.13em] text-[var(--muted)]">
          {meta ?? show.genres.slice(0, 2).join(" · ")}
        </p>
        {match != null && (
          <span className="shrink-0 font-serif text-[13px] text-[var(--accent)]">
            {match}%
          </span>
        )}
      </div>

      <h3 className="mt-1 font-serif text-[17px] leading-tight tracking-[-0.01em]">
        {show.title}
      </h3>
    </Link>
  );
}
