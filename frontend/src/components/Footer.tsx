export function Footer() {
  return (
    <footer className="mt-8 border-t border-[var(--line)]">
      <div className="mx-auto flex max-w-[1120px] flex-col gap-2 px-6 py-8 text-[11px] text-[var(--muted)] md:flex-row md:items-center md:justify-between md:px-10">
        <span className="font-serif text-[14px]">dramarec</span>
        <span className="tracking-[0.03em]">
          content-based + cast-graph recommendations · pgvector + bge embeddings
        </span>
      </div>
      <div className="mx-auto max-w-[1120px] px-6 pb-8 text-[10px] leading-relaxed text-[var(--muted)] md:px-10">
        This product uses the TMDB API but is not endorsed or certified by TMDB.
      </div>
    </footer>
  );
}
