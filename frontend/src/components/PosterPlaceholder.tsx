// A typographic stand-in until real TMDB posters are ingested. A muted duotone
// gradient (seeded per show) with a large, faint serif initial — reads as an
// intentional design choice rather than a missing image.

export function PosterPlaceholder({ title, seed }: { title: string; seed: number }) {
  const hue = (seed * 53) % 360;
  const gradient = `linear-gradient(155deg, hsl(${hue} 24% 38%), hsl(${(hue + 26) % 360} 30% 15%))`;

  return (
    <div
      className="relative flex aspect-[2/3] w-full items-center justify-center overflow-hidden rounded-[3px]"
      style={{ backgroundImage: gradient }}
    >
      <span className="select-none font-serif text-[88px] font-light leading-none text-white/12">
        {title.charAt(0)}
      </span>
      <span className="absolute right-3 top-3 text-[9px] uppercase tracking-[0.22em] text-white/40">
        KR
      </span>
      <span className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/25 to-transparent" />
    </div>
  );
}
