// Actor avatar: real TMDB profile photo when available, else a seeded duotone
// with initials. Designed to sit inside a `group` link so it lifts on hover.
export function ActorAvatar({
  name,
  seed,
  size = 64,
  profilePath = null,
}: {
  name: string;
  seed: number;
  size?: number;
  profilePath?: string | null;
}) {
  const common =
    "shrink-0 rounded-full ring-1 ring-black/10 transition-transform duration-300 ease-out group-hover:-translate-y-1";

  if (profilePath) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={`https://image.tmdb.org/t/p/w185${profilePath}`}
        alt={name}
        className={`${common} object-cover`}
        style={{ width: size, height: size }}
      />
    );
  }

  const hue = (seed * 67) % 360;
  const initials = name
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("");
  return (
    <div
      className={`${common} flex items-center justify-center font-serif text-white/85`}
      style={{
        width: size,
        height: size,
        fontSize: Math.round(size * 0.27),
        backgroundImage: `linear-gradient(150deg, hsl(${hue} 22% 44%), hsl(${(hue + 30) % 360} 26% 22%))`,
      }}
    >
      {initials}
    </div>
  );
}
