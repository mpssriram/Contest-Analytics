import { Link, NavLink } from "react-router-dom";
import type { ThemeMode } from "../hooks/useTheme";
import { cn } from "../utils/cn";
import { BrandIcon, MoonIcon, SunIcon } from "./icons";

interface NavbarProps {
  theme: ThemeMode;
  onToggleTheme: () => void;
}

export function Navbar({ theme, onToggleTheme }: NavbarProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-3 px-4 py-3 sm:px-6 sm:py-4 lg:px-8">
        <Link className="flex items-center gap-3" to="/">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-secondary text-secondary-foreground shadow-panel">
            <BrandIcon className="h-5 w-5" />
          </div>
          <div className="hidden sm:block">
            <p className="font-display text-base font-semibold tracking-tight">Contest Analytics</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Codeforces insights dashboard</p>
          </div>
        </Link>

        <div className="flex items-center gap-2 sm:gap-3">
          <nav className="flex items-center gap-1 rounded-full border border-border bg-surface/80 p-1 sm:gap-2 sm:p-1.5">
            {[
              { to: "/", label: "Home" },
              { to: "/problems", label: "Problems" },
              { to: "/compare", label: "Compare" },
              { to: "/dashboard/tourist", label: "Demo" }
            ].map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "rounded-full px-3 py-1.5 text-sm font-medium transition-colors sm:px-4 sm:py-2",
                    isActive
                      ? "bg-secondary text-secondary-foreground"
                      : "text-slate-600 hover:text-foreground dark:text-slate-300"
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <button
            type="button"
            onClick={onToggleTheme}
            className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-border bg-surface text-slate-600 transition hover:text-foreground dark:text-slate-300"
            aria-label="Toggle theme"
          >
            {theme === "dark" ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
          </button>
        </div>
      </div>
    </header>
  );
}
