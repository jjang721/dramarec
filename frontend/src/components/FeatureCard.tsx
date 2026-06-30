import Link from "next/link";
import type { ScoredShow } from "@/lib/api";
import { LikeButton } from "./LikeButton";
import { PosterPlaceholder } from "./PosterPlaceholder";

// The large, hero-sized recommendation card. Poster-forward, with the match
// score and the "why" given room to breathe.
export function FeatureCard({ show }: { show: ScoredShow }) {
  return (
    <Link href={`/show/${show.id}`} className="group block">
      <div className="relative overflow-hidden rounded-[4px] ring-1 ring-[var(--line)] transition-transform duration-300 ease-out group-hover:-translate-y-1.5">
        <LikeButton showId={show.id} />
        {show.poster_path ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`https://image.tmdb.org/t/p/w780${show.poster_path}`}
            alt={show.title}
            className="aspect-[2/3] w-full object-cover"
          />
        ) : (
          <PosterPlaceholder title={show.title} seed={show.id} />
        )}
      </div>

      <div className="mt-4 flex items-baseline justify-between gap-4">
        <p className="truncate text-[11px] uppercase tracking-[0.15em] text-[var(--muted)]">
          {show.genres.slice(0, 2).join(" · ")}
          {show.year ? ` · ${show.year}` : ""}
        </p>
        <span className="shrink-0 font-serif text-[18px] text-[var(--accent)]">
          {show.match}%
        </span>
      </div>

      <h3 className="mt-1.5 font-serif text-[24px] leading-[1.1] tracking-[-0.01em]">
        {show.title}
      </h3>
      <p className="mt-2 text-[14px] italic leading-relaxed text-[var(--muted)]">
        “{show.reason}”
      </p>
    </Link>
  );
}
