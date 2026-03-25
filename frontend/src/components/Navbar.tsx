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
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link className="flex items-center gap-3" to="/">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-secondary text-secondary-foreground shadow-panel">
            <BrandIcon className="h-5 w-5" />
          </div>
          <div>
            <p className="font-display text-base font-semibold tracking-tight">Contest Analytics</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Codeforces insights dashboard</p>
          </div>
        </Link>

        <div className="flex items-center gap-2 sm:gap-3">
          <nav className="hidden items-center gap-2 rounded-full border border-border bg-surface/80 p-1.5 sm:flex">
            {[
              { to: "/", label: "Home" },
              { to: "/dashboard/tourist", label: "Demo" }
            ].map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "rounded-full px-4 py-2 text-sm font-medium transition-colors",
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

          <span className="hidden rounded-full border border-sky-500/20 bg-sky-500/10 px-3 py-1 text-xs font-medium text-sky-600 dark:text-sky-300 md:inline-flex">
            React + FastAPI
          </span>

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
