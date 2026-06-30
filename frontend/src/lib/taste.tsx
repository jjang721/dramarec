"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

// The user's liked show ids, persisted to localStorage. No login required —
// this is enough to drive a personalized feed for the demo.
const STORAGE_KEY = "dramarec.liked";

type TasteContextValue = {
  likedIds: number[];
  isLiked: (id: number) => boolean;
  toggle: (id: number) => void;
};

const TasteContext = createContext<TasteContextValue | null>(null);

export function TasteProvider({ children }: { children: React.ReactNode }) {
  const [likedIds, setLikedIds] = useState<number[]>([]);
  const [hydrated, setHydrated] = useState(false);

  // Load once on mount (server render starts empty to avoid hydration mismatch).
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setLikedIds(JSON.parse(raw));
    } catch {}
    setHydrated(true);
  }, []);

  // Persist after hydration (guarded so the initial empty state can't clobber).
  useEffect(() => {
    if (!hydrated) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(likedIds));
    } catch {}
  }, [likedIds, hydrated]);

  const toggle = useCallback((id: number) => {
    setLikedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }, []);

  const isLiked = useCallback((id: number) => likedIds.includes(id), [likedIds]);

  return (
    <TasteContext.Provider value={{ likedIds, isLiked, toggle }}>
      {children}
    </TasteContext.Provider>
  );
}

export function useTaste(): TasteContextValue {
  const ctx = useContext(TasteContext);
  if (!ctx) throw new Error("useTaste must be used within TasteProvider");
  return ctx;
}
