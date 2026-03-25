export function LoadingDashboard() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="card-shell h-28" />
      <div className="grid gap-6 xl:grid-cols-[0.94fr_1.06fr]">
        <div className="space-y-6">
          <div className="card-shell h-80" />
          <div className="card-shell h-72" />
        </div>
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="card-shell h-36" />
            <div className="card-shell h-36" />
            <div className="card-shell h-36" />
            <div className="card-shell h-36" />
          </div>
          <div className="grid gap-6 xl:grid-cols-2">
            <div className="card-shell h-[22rem]" />
            <div className="card-shell h-[22rem]" />
            <div className="card-shell h-[22rem] xl:col-span-2" />
          </div>
        </div>
      </div>
      <div className="card-shell h-[30rem]" />
    </div>
  );
}
