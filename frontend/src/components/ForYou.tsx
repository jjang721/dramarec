"use client";

import { useEffect, useState } from "react";
import { recommendForUser, type ScoredShow, type Show } from "@/lib/api";
import { useTaste } from "@/lib/taste";
import { RecommendationStage } from "./RecommendationStage";
import { ShowCard } from "./ShowCard";

// How many shows the user picks before the feed personalizes.
const MIN_PICKS = 3;

export function ForYou({ picks }: { picks: Show[] }) {
  const { likedIds } = useTaste();
  const [recs, setRecs] = useState<ScoredShow[] | null>(null);

  // Refetch the feed whenever the taste set changes — this is the live loop.
  useEffect(() => {
    if (likedIds.length < MIN_PICKS) {
      setRecs(null);
      return;
    }
    let active = true;
    recommendForUser(likedIds, 12)
      .then((r) => active && setRecs(r))
      .catch(() => active && setRecs([]));
    return () => {
      active = false;
    };
  }, [likedIds]);

  // Onboarding: pick a few before the feed appears.
  if (likedIds.length < MIN_PICKS) {
    return (
      <section className="mx-auto max-w-[1120px] px-6 md:px-10">
        <div className="border-t border-[var(--line)] pt-8">
          <h2 className="font-serif text-[22px]">Build your feed</h2>
          <p className="mt-2 max-w-[50ch] text-[14px] leading-relaxed text-[var(--muted)]">
            Tap the ♥ on a few K-dramas you love and dramarec learns your taste,
            then recommends ones that feel the same.
          </p>
          <p className="mt-4 text-[11px] uppercase tracking-[0.16em] text-[var(--accent)]">
            {likedIds.length} of {MIN_PICKS} picked
          </p>
        </div>
        <div className="mt-8 grid grid-cols-2 gap-x-5 gap-y-9 sm:grid-cols-3 lg:grid-cols-6">
          {picks.slice(0, 12).map((s) => (
            <ShowCard key={s.id} show={s} />
          ))}
        </div>
      </section>
    );
  }

  // Brief loading state to avoid a layout jump on first personalization.
  if (recs === null) {
    return (
      <section className="mx-auto max-w-[1120px] px-6 md:px-10">
        <div className="border-t border-[var(--line)] pt-8">
          <h2 className="font-serif text-[22px]">For you</h2>
          <p className="mt-2 text-[14px] text-[var(--muted)]">finding shows you’ll love…</p>
        </div>
      </section>
    );
  }

  return (
    <RecommendationStage
      heading={
        <>
          For you{" "}
          <span className="text-[15px] text-[var(--muted)]">
            · based on {likedIds.length} you like
          </span>
        </>
      }
      items={recs}
    />
  );
}
