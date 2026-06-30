"use client";

import { motion, useScroll, useTransform } from "framer-motion";

// Full-screen intro that fades, lifts, and shrinks as you scroll — the page
// content scrolls up over it (it's fixed behind, pointer-events disabled).
export function HeroIntro() {
  const { scrollY } = useScroll();
  const opacity = useTransform(scrollY, [0, 420], [1, 0]);
  const y = useTransform(scrollY, [0, 420], [0, -40]);
  const scale = useTransform(scrollY, [0, 420], [1, 0.96]);

  return (
    <motion.section
      style={{ opacity, y, scale }}
      className="pointer-events-none fixed inset-0 z-0 flex flex-col items-center justify-center px-6 text-center"
    >
      <p className="text-[12px] uppercase tracking-[0.28em] text-[var(--muted)]">
        dramarec
      </p>
      <h1 className="mt-6 max-w-[14ch] font-serif text-[44px] font-light leading-[1.03] tracking-[-0.02em] md:text-[80px]">
        Shows that feel like the ones you love.
      </h1>
      <p className="mt-6 max-w-[46ch] text-[15px] leading-relaxed text-[var(--muted)]">
        A K-drama recommender that reads the tone and texture of what you love —
        and finds more of it.
      </p>

      <div className="absolute bottom-10 flex flex-col items-center gap-2 text-[var(--muted)]">
        <span className="text-[10px] uppercase tracking-[0.24em]">Scroll</span>
        <motion.svg
          width="18" height="18" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
        >
          <path d="M6 9l6 6 6-6" />
        </motion.svg>
      </div>
    </motion.section>
  );
}
