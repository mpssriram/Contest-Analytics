import { cn } from "../utils/cn";
import { toTitleCase } from "../utils/formatters";

interface TagListProps {
  tags: string[];
  limit?: number;
  emptyLabel?: string;
  className?: string;
  tagClassName?: string;
}

export function TagList({ tags, limit, emptyLabel, className, tagClassName }: TagListProps) {
  const visibleTags = limit ? tags.slice(0, limit) : tags;

  if (visibleTags.length === 0) {
    return emptyLabel ? <span className="text-sm text-slate-500 dark:text-slate-400">{emptyLabel}</span> : null;
  }

  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {visibleTags.map((tag) => (
        <span
          key={tag}
          className={cn("rounded-full border border-border bg-surface px-3 py-1 text-xs font-medium", tagClassName)}
        >
          {toTitleCase(tag)}
        </span>
      ))}
    </div>
  );
}
