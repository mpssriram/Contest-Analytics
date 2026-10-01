export function LoadingDashboard() {
  return (
    <div className="animate-pulse space-y-5">
      <div className="report-shell h-28" />
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <div className="metric-panel h-32" />
        <div className="metric-panel h-32" />
        <div className="metric-panel h-32" />
        <div className="metric-panel h-32" />
        <div className="col-span-2 metric-panel h-32 lg:col-span-1" />
      </div>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
        <div className="report-shell h-[28rem]" />
        <div className="space-y-5">
          <div className="report-shell h-64" />
          <div className="report-shell h-52" />
        </div>
      </div>
      <div className="grid gap-5 xl:grid-cols-2">
        <div className="card-shell h-[26rem]" />
        <div className="card-shell h-[26rem]" />
      </div>
    </div>
  );
}
