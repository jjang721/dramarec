"use client";

import { useTaste } from "@/lib/taste";

// Heart overlay for a poster. Optimistic — state flips instantly via context.
// Stops the click from triggering the surrounding card link.
export function LikeButton({ showId }: { showId: number }) {
  const { isLiked, toggle } = useTaste();
  const liked = isLiked(showId);

  return (
    <button
      type="button"
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        toggle(showId);
      }}
      aria-pressed={liked}
      aria-label={liked ? "Remove from your taste" : "Add to your taste"}
      className="absolute right-2 top-2 z-10 grid h-8 w-8 place-items-center rounded-full bg-black/35 backdrop-blur-sm transition hover:bg-black/55"
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill={liked ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={liked ? "text-[var(--accent)]" : "text-white"}
      >
        <path d="M12 21s-7.5-4.6-10-9.2C.6 9.1 1.7 5.6 4.8 4.8 7 4.2 9 5.3 12 8c3-2.7 5-3.8 7.2-3.2 3.1.8 4.2 4.3 2.8 7C19.5 16.4 12 21 12 21z" />
      </svg>
    </button>
  );
}
