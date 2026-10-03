import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import type { FocusAreasData } from "../types/analytics";
import { toTitleCase } from "../utils/formatters";
import { TagsIcon, TargetIcon, TrophyIcon } from "./icons";

interface FocusAreasProps {
  focus: FocusAreasData;
  // passed to the Problems page so it can hide what this user already solved
  handle: string;
}

const HIGHEST_RATING = 3500;

function practiceLink(handle: string, tag: string | null, min: number, max: number): string {
  const params = new URLSearchParams();
  params.set("handle", handle);
  if (tag) {
    params.set("tag", tag);
  }
  params.set("min", String(min));
  params.set("max", String(Math.min(max, HIGHEST_RATING)));
  return `/problems?${params.toString()}`;
}

function percent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function SectionTitle({ icon, children }: { icon: ReactNode; children: string }) {
  return (
    <div className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300">
      {icon}
      {children}
    </div>
  );
}

function PracticeLink({ to }: { to: string }) {
  return (
    <Link to={to} className="flex-none text-xs font-medium text-primary transition hover:opacity-80">
      Practise →
    </Link>
  );
}

export function FocusAreas({ focus, handle }: FocusAreasProps) {
  const levelLabel = `${focus.levelLow}–${focus.levelHigh}`;

  return (
    <section className="report-shell overflow-hidden">
      <div className="report-band">
        <h2 className="font-display text-lg font-semibold tracking-tight">Focus areas</h2>
        <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">Compared with problems rated {levelLabel}, your level.</p>
      </div>

      <div className="report-body space-y-5">
        {!focus.enoughData ? (
          <div className="text-sm leading-6 text-slate-600 dark:text-slate-300">
            <p>Solve at least 20 rated problems and this will show which topics to work on.</p>
            <Link to={practiceLink(handle, null, 800, 1000)} className="mt-2 inline-block font-medium text-primary hover:opacity-80">
              Find problems rated 800–1000 →
            </Link>
          </div>
        ) : !focus.available ? (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Couldn&apos;t load the Codeforces problem list right now. Try again in a minute.
          </p>
        ) : (
          <>
            {focus.atTop ? (
              <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">
                No clear gaps. You&apos;re solving the hardest rated problems across every common topic.
              </p>
            ) : null}

            {!focus.atTop ? (
              <div>
                <SectionTitle icon={<TargetIcon className="h-4 w-4 text-warning" />}>Practised less than usual</SectionTitle>
                {focus.underPracticed.length > 0 ? (
                  <ul className="mt-2 space-y-2">
                    {focus.underPracticed.map((item) => (
                      <li key={item.tag} className="flex items-center justify-between gap-3 text-sm">
                        <div className="min-w-0">
                          <p className="font-medium text-foreground">{toTitleCase(item.tag)}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            {percent(item.levelShare)} of problems at your level, {percent(item.yourShare)} of yours
                          </p>
                        </div>
                        <PracticeLink to={practiceLink(handle, item.tag, focus.levelLow, focus.levelHigh)} />
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Your topic mix matches your level well.</p>
                )}
              </div>
            ) : null}

            {focus.ceilings.length > 0 ? (
              <div>
                <SectionTitle icon={<TagsIcon className="h-4 w-4 text-warning" />}>Where you hit a ceiling</SectionTitle>
                <ul className="mt-2 space-y-2">
                  {focus.ceilings.map((item) => (
                    <li key={item.tag} className="flex items-center justify-between gap-3 text-sm">
                      <div className="min-w-0">
                        <p className="font-medium text-foreground">{toTitleCase(item.tag)}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          Comfortable up to {item.comfortableRating}, overall you&apos;re at {focus.overallComfortable}
                        </p>
                      </div>
                      <PracticeLink to={practiceLink(handle, item.tag, item.comfortableRating, item.comfortableRating + 300)} />
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {focus.comfortable.length > 0 ? (
              <div>
                <SectionTitle icon={<TrophyIcon className="h-4 w-4 text-primary" />}>Comfortable</SectionTitle>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                  {focus.comfortable.map((item, index) => (
                    <span key={item.tag}>
                      {index > 0 ? " · " : ""}
                      {toTitleCase(item.tag)} <span className="font-semibold text-foreground">{item.comfortableRating}</span>
                    </span>
                  ))}
                </p>
              </div>
            ) : null}

            <p className="border-t border-border pt-3 text-xs text-slate-500 dark:text-slate-400">
              Based on {focus.comparedSolves}{" "}
              {focus.comparedAgainst === "level" ? `of your solves rated ${levelLabel}` : "rated solves (too few at your level to compare alone)"}.
              Comfortable means your 3rd hardest solve in that topic.
            </p>
          </>
        )}
      </div>
    </section>
  );
}
