import Link from "next/link";
import { notFound } from "next/navigation";
import { ActorAvatar } from "@/components/ActorAvatar";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { PosterPlaceholder } from "@/components/PosterPlaceholder";
import { RecommendationStage } from "@/components/RecommendationStage";
import { TrailerButton } from "@/components/TrailerButton";
import { getShow, getSimilar, type ScoredShow, type ShowDetail } from "@/lib/api";

export default async function ShowPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const showId = Number(id);

  let show: ShowDetail | null = null;
  let recommendations: ScoredShow[] = [];
  try {
    const [detail, similar] = await Promise.all([
      getShow(showId),
      getSimilar(showId, 12),
    ]);
    show = detail;
    recommendations = similar.results;
  } catch {
    show = null;
  }
  if (!show) notFound();

  const meta = [
    show.year?.toString(),
    show.genres.slice(0, 3).join(" · "),
    show.vote_average ? `★ ${show.vote_average.toFixed(1)}` : null,
  ]
    .filter(Boolean)
    .join("   ·   ");

  return (
    <>
      <Header />

      <main>
        <section className="mx-auto max-w-[1120px] px-6 pt-12 md:px-10">
          <Link
            href="/"
            className="text-[12px] uppercase tracking-[0.14em] text-[var(--muted)] transition-colors hover:text-[var(--ink)]"
          >
            ← Back
          </Link>

          <div className="mt-10 grid gap-10 md:grid-cols-[280px_1fr]">
            {/* Poster */}
            <div className="w-full max-w-[280px]">
              {show.poster_path ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={`https://image.tmdb.org/t/p/w500${show.poster_path}`}
                  alt={show.title}
                  className="aspect-[2/3] w-full rounded-[4px] object-cover ring-1 ring-[var(--line)]"
                />
              ) : (
                <PosterPlaceholder title={show.title} seed={show.id} />
              )}
            </div>

            {/* Info */}
            <div>
              <p className="text-[12px] uppercase tracking-[0.22em] text-[var(--muted)]">
                Series
              </p>
              <h1 className="mt-3 font-serif text-[40px] font-light leading-[1.05] tracking-[-0.015em] md:text-[56px]">
                {show.title}
              </h1>
              <p className="mt-4 text-[12px] uppercase tracking-[0.13em] text-[var(--muted)]">
                {meta}
              </p>
              {show.overview && (
                <p className="mt-6 max-w-[58ch] text-[15px] leading-relaxed text-[var(--ink)]/85">
                  {show.overview}
                </p>
              )}

              {show.trailer_key && (
                <div className="mt-7">
                  <TrailerButton youtubeKey={show.trailer_key} title={show.title} />
                </div>
              )}

              {show.cast.length > 0 && (
                <div className="mt-9">
                  <h2 className="text-[11px] uppercase tracking-[0.16em] text-[var(--muted)]">
                    Cast
                  </h2>
                  <div className="mt-5 flex flex-wrap gap-x-8 gap-y-5">
                    {show.cast.map((c) => (
                      <Link
                        key={c.id}
                        href={`/actor/${c.id}`}
                        className="group flex items-center gap-3"
                      >
                        <ActorAvatar name={c.name} seed={c.id} size={44} profilePath={c.profile_path} />
                        <span className="font-serif text-[15px] transition-colors group-hover:text-[var(--accent)]">
                          {c.name}
                        </span>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Recommendations for this show */}
        <div className="pt-20">
          <RecommendationStage
            heading={
              <>
                Because you liked{" "}
                <span className="italic text-[var(--accent)]">{show.title}</span>
              </>
            }
            items={recommendations}
          />
        </div>

        <div className="h-24" />
      </main>
      <Footer />
    </>
  );
}
