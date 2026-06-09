import { formatCompactNumber, formatRating } from "../utils/formatters";
import { TagList } from "./TagList";

interface ProblemCardProps {
  id: string;
  name: string;
  contestId: number;
  index: string;
  rating: number | null;
  tags: string[];
  url?: string | null;
  solvedCount?: number;
  meta?: string;
}

export function ProblemCard({ id, name, contestId, index, rating, tags, url, solvedCount, meta }: ProblemCardProps) {
  return (
    <a
      key={id}
      href={url || `https://codeforces.com/problemset/problem/${contestId}/${index}`}
      target="_blank"
      rel="noreferrer"
      className="hover-lift rounded-xl border border-border bg-surface-muted p-4 transition hover:border-primary/40 hover:bg-surface"
    >
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <p className="font-medium text-foreground">{name}</p>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Contest {contestId} / Index {index}
            {meta ? ` / ${meta}` : ""}
          </p>
        </div>
        <div className="flex flex-wrap gap-2 text-sm">
          <span className="rounded-full border border-border bg-surface px-3 py-1 font-medium">
            {formatRating(rating)}
          </span>
          {typeof solvedCount === "number" ? (
            <span className="rounded-full border border-border bg-surface px-3 py-1 text-slate-500 dark:text-slate-400">
              {formatCompactNumber(solvedCount)} solves
            </span>
          ) : null}
        </div>
      </div>
      <TagList tags={tags} limit={6} className="mt-3" />
    </a>
  );
}
