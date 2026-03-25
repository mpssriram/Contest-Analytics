import type { ProfileResponse } from "../types/analytics";
import { formatRating, toTitleCase } from "../utils/formatters";
import { UserIcon } from "./icons";

interface ProfileCardProps {
  profile: ProfileResponse;
}

export function ProfileCard({ profile }: ProfileCardProps) {
  const rankLabel = profile.rank ? toTitleCase(profile.rank) : "Unrated";

  return (
    <section className="card-shell p-6">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-center gap-4">
          {profile.avatar ? (
            <img
              src={profile.avatar}
              alt={`${profile.handle} avatar`}
              className="h-20 w-20 rounded-3xl border border-border object-cover"
            />
          ) : (
            <div className="flex h-20 w-20 items-center justify-center rounded-3xl border border-border bg-surface-muted text-primary">
              <UserIcon className="h-9 w-9" />
            </div>
          )}

          <div>
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Profile</p>
            <h2 className="mt-1 font-display text-2xl font-semibold tracking-tight">{profile.handle}</h2>
            <div className="mt-3 inline-flex rounded-full border border-border bg-surface-muted px-3 py-1 text-sm font-medium text-slate-600 dark:text-slate-300">
              {rankLabel}
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-border bg-surface-muted px-4 py-3 text-right">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Contribution</p>
          <p className="mt-1 font-display text-2xl font-semibold">{profile.contribution}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-border bg-surface-muted p-4">
          <p className="text-sm text-slate-500 dark:text-slate-400">Current rating</p>
          <p className="mt-2 text-2xl font-semibold">{formatRating(profile.rating)}</p>
        </div>
        <div className="rounded-2xl border border-border bg-surface-muted p-4">
          <p className="text-sm text-slate-500 dark:text-slate-400">Max rating</p>
          <p className="mt-2 text-2xl font-semibold">{formatRating(profile.maxRating)}</p>
        </div>
        <div className="rounded-2xl border border-border bg-surface-muted p-4">
          <p className="text-sm text-slate-500 dark:text-slate-400">Country</p>
          <p className="mt-2 text-base font-semibold">{profile.country || "Not listed"}</p>
        </div>
        <div className="rounded-2xl border border-border bg-surface-muted p-4">
          <p className="text-sm text-slate-500 dark:text-slate-400">Organization</p>
          <p className="mt-2 text-base font-semibold">{profile.organization || "Independent"}</p>
        </div>
      </div>
    </section>
  );
}
