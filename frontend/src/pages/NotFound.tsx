import { Link } from "react-router-dom";

export function NotFound() {
  return (
    <section className="card-shell mx-auto max-w-2xl p-8 text-center">
      <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">404</p>
      <h1 className="mt-3 font-display text-3xl font-semibold tracking-tight">Page not found</h1>
      <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
        The page you requested does not exist inside this Contest Analytics frontend.
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex rounded-2xl bg-secondary px-5 py-3 text-sm font-semibold text-secondary-foreground"
      >
        Back to home
      </Link>
    </section>
  );
}
