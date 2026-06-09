import type { ProfileResponse } from "../types/analytics";
import { formatRating, toTitleCase } from "../utils/formatters";
import { UserIcon } from "./icons";

interface ProfileCardProps {
  profile: ProfileResponse;
}

export function ProfileCard({ profile }: ProfileCardProps) {
  const rankLabel = profile.rank ? toTitleCase(profile.rank) : "Unrated";

  return (
    <section className="report-shell overflow-hidden">
      <div className="report-band">
        <p className="eyebrow">Profile</p>
      </div>

      <div className="report-body">
      <div className="flex flex-col gap-5">
        <div className="flex min-w-0 items-start gap-4">
          {profile.avatar ? (
            <img
              src={profile.avatar}
              alt={`${profile.handle} avatar`}
              className="h-16 w-16 flex-none rounded-2xl border border-border object-cover sm:h-20 sm:w-20"
            />
          ) : (
            <div className="flex h-16 w-16 flex-none items-center justify-center rounded-2xl border border-border bg-surface-muted text-primary sm:h-20 sm:w-20">
              <UserIcon className="h-9 w-9" />
            </div>
          )}

          <div className="min-w-0 flex-1">
            <h2 className="mt-1 truncate font-display text-2xl font-semibold tracking-tight">{profile.handle}</h2>
            <div className="mt-3 inline-flex rounded-full border border-border bg-surface-muted px-3 py-1 text-sm font-medium text-slate-600 dark:text-slate-300">
              {rankLabel}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between rounded-xl border border-border bg-surface-muted px-4 py-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Contribution</p>
          <p className="font-display text-2xl font-semibold">{profile.contribution}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <div className="metric-panel">
          <p className="text-sm text-slate-500 dark:text-slate-400">Current rating</p>
          <p className="mt-2 text-2xl font-semibold">{formatRating(profile.rating)}</p>
        </div>
        <div className="metric-panel">
          <p className="text-sm text-slate-500 dark:text-slate-400">Max rating</p>
          <p className="mt-2 text-2xl font-semibold">{formatRating(profile.maxRating)}</p>
        </div>
        <div className="metric-panel">
          <p className="text-sm text-slate-500 dark:text-slate-400">Country</p>
          <p className="mt-2 text-base font-semibold">{profile.country || "Not listed"}</p>
        </div>
        <div className="metric-panel">
          <p className="text-sm text-slate-500 dark:text-slate-400">Organization</p>
          <p className="mt-2 text-base font-semibold">{profile.organization || "Independent"}</p>
        </div>
      </div>
      </div>
    </section>
  );
}
