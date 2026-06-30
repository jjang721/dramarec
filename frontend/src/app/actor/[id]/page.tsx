import Link from "next/link";
import { notFound } from "next/navigation";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { ShowCard } from "@/components/ShowCard";
import { getActor, type ActorDetail } from "@/lib/api";

export default async function ActorPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let data: ActorDetail | null = null;
  try {
    data = await getActor(Number(id));
  } catch {
    data = null;
  }
  if (!data) notFound();

  const { actor, shows } = data;

  return (
    <>
      <Header />
      <main className="mx-auto max-w-[1120px] px-6 pb-24 pt-12 md:px-10">
        <Link
          href="/"
          className="text-[12px] uppercase tracking-[0.14em] text-[var(--muted)] transition-colors hover:text-[var(--ink)]"
        >
          ← Back
        </Link>

        <p className="mt-10 text-[12px] uppercase tracking-[0.22em] text-[var(--muted)]">
          Actor
        </p>
        <h1 className="mt-3 font-serif text-[44px] font-light leading-[1.05] tracking-[-0.015em] md:text-[60px]">
          {actor.name}
        </h1>
        <p className="mt-4 text-[14px] text-[var(--muted)]">
          {actor.show_count} {actor.show_count === 1 ? "show" : "shows"} in the catalogue
        </p>

        <div className="mt-12 grid grid-cols-2 gap-x-5 gap-y-9 sm:grid-cols-3 lg:grid-cols-6">
          {shows.map((s) => (
            <ShowCard key={s.id} show={s} />
          ))}
        </div>
      </main>
      <Footer />
    </>
  );
}
