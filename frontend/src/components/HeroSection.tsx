import { SearchBar } from "./SearchBar";
import { EncryptedText } from "./ui/encrypted-text";

interface HeroSectionProps {
  onAnalyze: (handle: string) => void;
}

const EXAMPLE_HANDLES = ["tourist", "Benq", "jiangly"];

export function HeroSection({ onAnalyze }: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden rounded-[2rem] border border-border bg-surface/90 px-6 py-10 shadow-panel backdrop-blur-sm sm:px-10 sm:py-14 lg:px-14 lg:py-16">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.18),transparent_32%),radial-gradient(circle_at_bottom_right,rgba(20,184,166,0.12),transparent_30%)]" />
      <div className="relative max-w-3xl space-y-6">
        <h1 className="font-display text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
          <EncryptedText
            text="Contest Analytics"
            revealDelayMs={35}
            flipDelayMs={28}
            encryptedClassName="text-primary"
            revealedClassName="text-foreground"
          />
        </h1>
        <p className="max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
          See how you actually practice on Codeforces: which topics you solve, which ones you avoid, what
          difficulty you&apos;re comfortable at, and which problems are worth trying next.
        </p>

        <SearchBar onSubmit={onAnalyze} />

        <div className="flex flex-wrap items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
          <span>Or try</span>
          {EXAMPLE_HANDLES.map((handle) => (
            <button
              key={handle}
              type="button"
              onClick={() => onAnalyze(handle)}
              className="rounded-full border border-border bg-surface-muted px-3 py-1 font-medium text-foreground transition hover:border-primary/40 hover:text-primary"
            >
              {handle}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
