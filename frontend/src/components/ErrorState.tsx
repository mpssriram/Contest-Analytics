import { Link } from "react-router-dom";
import { RefreshIcon } from "./icons";

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry: () => void;
}

export function ErrorState({
  title = "We couldn't load this handle right now",
  message,
  onRetry
}: ErrorStateProps) {
  return (
    <section className="card-shell mx-auto max-w-2xl p-8 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-danger/10 text-danger">
        <RefreshIcon className="h-6 w-6" />
      </div>
      <h2 className="mt-5 font-display text-2xl font-semibold tracking-tight">{title}</h2>
      <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{message}</p>
      <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
        <button
          type="button"
          onClick={onRetry}
          className="rounded-2xl bg-secondary px-5 py-3 text-sm font-semibold text-secondary-foreground"
        >
          Try again
        </button>
        <Link
          to="/"
          className="rounded-2xl border border-border px-5 py-3 text-sm font-semibold text-slate-600 dark:text-slate-300"
        >
          Back to home
        </Link>
      </div>
    </section>
  );
}
