import type { SummaryResponse } from "../types/analytics";
import { TargetIcon, TagsIcon } from "./icons";
import { TagList } from "./TagList";

interface FocusAreasProps {
  summary: SummaryResponse;
}

export function FocusAreas({ summary }: FocusAreasProps) {
  const notes = summary.observations || summary.recommendations || [];

  return (
    <section className="report-shell overflow-hidden">
      <div className="report-band">
        <h2 className="font-display text-lg font-semibold tracking-tight">Focus areas</h2>
      </div>

      <div className="report-body space-y-4">
        <div>
          <div className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300">
            <TargetIcon className="h-4 w-4 text-warning" />
            Topics you rarely solve
          </div>
          <TagList
            tags={summary.leastRepresentedTags || summary.weakestTags}
            emptyLabel="Not enough solved data yet."
            className="mt-2"
          />
        </div>

        <div>
          <div className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300">
            <TagsIcon className="h-4 w-4 text-primary" />
            Your strongest topics
          </div>
          <TagList tags={summary.strongestTags} emptyLabel="No strong topics yet." className="mt-2" />
        </div>

        {notes.length > 0 ? (
          <ul className="space-y-2 border-t border-border pt-4 text-sm leading-6 text-slate-600 dark:text-slate-300">
            {notes.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : null}
      </div>
    </section>
  );
}
