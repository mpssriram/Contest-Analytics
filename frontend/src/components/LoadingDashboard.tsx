export function LoadingDashboard() {
  return (
    <div className="animate-pulse space-y-5">
      <div className="report-shell h-52" />
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <div className="metric-panel h-36" />
        <div className="metric-panel h-36" />
        <div className="metric-panel h-36" />
        <div className="metric-panel h-36" />
        <div className="metric-panel h-36" />
      </div>
      <div className="grid gap-5 2xl:grid-cols-[22rem_minmax(0,1fr)]">
        <div className="space-y-5">
          <div className="report-shell h-80" />
          <div className="report-shell h-72" />
        </div>
        <div className="grid gap-5 xl:grid-cols-2">
          <div className="card-shell h-[28rem]" />
          <div className="card-shell h-[28rem]" />
          <div className="card-shell h-[22rem] xl:col-span-2" />
        </div>
      </div>
      <div className="report-shell h-[30rem]" />
    </div>
  );
}
