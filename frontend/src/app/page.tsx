import { CastRow } from "@/components/CastRow";
import { Footer } from "@/components/Footer";
import { ForYou } from "@/components/ForYou";
import { Header } from "@/components/Header";
import { HeroIntro } from "@/components/HeroIntro";
import { ShowCard } from "@/components/ShowCard";
import { getActors, getShows, type Actor, type Show } from "@/lib/api";

export default async function Home() {
  let catalogue: Show[] = [];
  let actors: Actor[] = [];
  let offline = false;

  try {
    const [shows, cast] = await Promise.all([getShows(40), getActors(12)]);
    catalogue = shows;
    actors = cast;
  } catch {
    offline = true;
  }

  return (
    <>
      {/* Full-screen intro, fixed behind; content scrolls up over it */}
      <HeroIntro />

      <div className="relative z-10 mt-[100vh] min-h-screen bg-[var(--bg)]">
        <Header />

        <main className="pt-8">
          {offline ? (
          <section className="mx-auto max-w-[1120px] px-6 md:px-10">
            <div className="rounded-[4px] border border-[var(--line)] p-8 text-[14px] text-[var(--muted)]">
              The API isn’t responding. Start it with{" "}
              <code className="font-serif text-[var(--ink)]">
                uvicorn api.main:app --port 8000
              </code>{" "}
              in <code className="font-serif text-[var(--ink)]">backend/</code>.
            </div>
          </section>
        ) : (
          <>
            {/* Personalized feed — onboarding picker until 3 likes, then live recs */}
            <ForYou picks={catalogue} />

            {/* Browse by cast */}
            <CastRow actors={actors} />

            {/* Catalogue */}
            <section className="mx-auto max-w-[1120px] px-6 pb-24 pt-16 md:px-10">
              <div className="flex items-baseline justify-between border-t border-[var(--line)] pt-8">
                <h2 className="font-serif text-[22px]">The catalogue</h2>
                <span className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
                  {catalogue.length} titles
                </span>
              </div>
              <div className="mt-8 grid grid-cols-2 gap-x-5 gap-y-9 sm:grid-cols-3 lg:grid-cols-6">
                {catalogue.map((s) => (
                  <ShowCard key={s.id} show={s} />
                ))}
              </div>
            </section>
          </>
          )}
        </main>

        <Footer />
      </div>
    </>
  );
}
