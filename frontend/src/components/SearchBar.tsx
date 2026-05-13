import { useEffect, useState } from "react";
import { cn } from "../utils/cn";
import { ArrowRightIcon, SearchIcon } from "./icons";

interface SearchBarProps {
  onSubmit: (handle: string) => void;
  initialValue?: string;
  buttonLabel?: string;
  placeholder?: string;
  compact?: boolean;
  className?: string;
  disabled?: boolean;
}

export function SearchBar({
  onSubmit,
  initialValue = "",
  buttonLabel = "Analyze",
  placeholder = "Enter a Codeforces handle",
  compact = false,
  className,
  disabled = false
}: SearchBarProps) {
  const [handle, setHandle] = useState(initialValue);

  useEffect(() => {
    setHandle(initialValue);
  }, [initialValue]);

  const trimmedHandle = handle.trim();

  return (
    <form
      className={cn(
        "gooey-search flex w-full flex-col gap-3 rounded-2xl border border-border bg-surface p-2 shadow-soft md:flex-row md:items-center",
        compact && "rounded-xl p-1.5",
        className
      )}
      onSubmit={(event) => {
        event.preventDefault();
        if (!trimmedHandle || disabled) {
          return;
        }
        onSubmit(trimmedHandle);
      }}
    >
      <label className="flex flex-1 items-center gap-3 rounded-xl px-4 py-3 text-sm">
        <SearchIcon className="h-5 w-5 text-slate-400" />
        <input
          type="text"
          value={handle}
          onChange={(event) => setHandle(event.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full border-none bg-transparent text-sm text-foreground outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
          autoComplete="off"
          spellCheck={false}
        />
      </label>

      <button
        type="submit"
        disabled={!trimmedHandle || disabled}
        className="inline-flex items-center justify-center gap-2 rounded-xl bg-secondary px-5 py-3 text-sm font-semibold text-secondary-foreground transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {buttonLabel}
        <ArrowRightIcon className="h-4 w-4" />
      </button>
    </form>
  );
}
