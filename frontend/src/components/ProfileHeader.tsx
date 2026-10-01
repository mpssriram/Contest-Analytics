import type { ReactNode } from "react";
import type { ProfileResponse } from "../types/analytics";
import { formatRating, toTitleCase } from "../utils/formatters";
import { UserIcon } from "./icons";
import { EncryptedText } from "./ui/encrypted-text";

interface ProfileHeaderProps {
  profile: ProfileResponse;
  // shown on the right, e.g. the search bar for another handle
  action?: ReactNode;
}

export function ProfileHeader({ profile, action }: ProfileHeaderProps) {
  const rankLabel = profile.rank ? toTitleCase(profile.rank) : "Unrated";
  const details = [profile.country, profile.organization].filter(Boolean).join(" · ");

  return (
    <section className="report-shell overflow-hidden reveal-panel">
      <div className="flex flex-col gap-6 p-5 sm:p-6 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex min-w-0 items-center gap-4">
          {profile.avatar ? (
            <img
              src={profile.avatar}
              alt={`${profile.handle} avatar`}
              className="h-16 w-16 flex-none rounded-2xl border border-border object-cover"
            />
          ) : (
            <div className="flex h-16 w-16 flex-none items-center justify-center rounded-2xl border border-border bg-surface-muted text-primary">
              <UserIcon className="h-8 w-8" />
            </div>
          )}

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
              <h1 className="truncate font-display text-3xl font-semibold tracking-tight">
                <EncryptedText text={profile.handle} revealDelayMs={28} flipDelayMs={24} encryptedClassName="text-primary" />
              </h1>
              <span className="rounded-full border border-border bg-surface-muted px-3 py-1 text-sm font-medium text-slate-600 dark:text-slate-300">
                {rankLabel}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
              Rating <span className="font-semibold text-foreground">{formatRating(profile.rating)}</span>
              <span className="mx-2 text-slate-400">/</span>
              Max <span className="font-semibold text-foreground">{formatRating(profile.maxRating)}</span>
              {details ? <span className="text-slate-500 dark:text-slate-400"> · {details}</span> : null}
            </p>
          </div>
        </div>

        {action ? <div className="w-full xl:max-w-md">{action}</div> : null}
      </div>
    </section>
  );
}
