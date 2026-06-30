import { SearchTrigger } from "./SearchTrigger";
import { ThemeToggle } from "./ThemeToggle";

export function Header() {
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--line)] bg-[var(--bg)]/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1120px] items-center justify-between px-6 py-5 md:px-10">
        <a href="/" className="font-serif text-[22px] tracking-tight">
          dramarec<span className="text-[var(--accent)]">.</span>
        </a>
        <nav className="flex items-center gap-5 text-[13px] text-[var(--muted)]">
          <a href="/" className="hidden transition-colors hover:text-[var(--ink)] sm:inline">
            Home
          </a>
          <SearchTrigger />
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}
