"use client";

import { useEffect, useState } from "react";

// "Watch trailer" → modal with an embedded YouTube player.
export function TrailerButton({
  youtubeKey,
  title,
}: {
  youtubeKey: string;
  title: string;
}) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-2 rounded-full bg-[var(--ink)] px-5 py-2.5 text-[13px] font-medium text-[var(--bg)] transition hover:opacity-90"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <path d="M8 5v14l11-7z" />
        </svg>
        Watch trailer
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
          onClick={() => setOpen(false)}
        >
          <div
            className="relative aspect-video w-full max-w-[900px]"
            onClick={(e) => e.stopPropagation()}
          >
            <iframe
              className="h-full w-full rounded-[6px]"
              src={`https://www.youtube.com/embed/${youtubeKey}?autoplay=1`}
              title={`${title} — trailer`}
              allow="autoplay; encrypted-media; fullscreen"
              allowFullScreen
            />
          </div>
        </div>
      )}
    </>
  );
}
