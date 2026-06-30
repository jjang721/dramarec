import Link from "next/link";
import type { Actor } from "@/lib/api";
import { ActorAvatar } from "./ActorAvatar";

// Browse-by-cast: follow an actor to see everything they're in. This is the
// "people graph" recommendation signal, surfaced as a catalogue.
export function CastRow({ actors }: { actors: Actor[] }) {
  return (
    <section className="mx-auto max-w-[1120px] px-6 pt-16 md:px-10">
      <div className="flex items-baseline justify-between border-t border-[var(--line)] pt-8">
        <h2 className="font-serif text-[22px]">Browse by cast</h2>
        <span className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
          follow an actor
        </span>
      </div>

      <div className="mt-9 grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-3 lg:grid-cols-6">
        {actors.map((a) => (
          <Link
            key={a.id}
            href={`/actor/${a.id}`}
            className="group flex flex-col items-center gap-3 text-center"
          >
            <ActorAvatar name={a.name} seed={a.id} profilePath={a.profile_path} />
            <div>
              <p className="font-serif text-[15px] leading-tight">{a.name}</p>
              <p className="mt-0.5 text-[10px] uppercase tracking-[0.14em] text-[var(--muted)]">
                {a.show_count} {a.show_count === 1 ? "show" : "shows"}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
