import { DataSourceBanner } from "@/components/data-source-banner";
import { MonitoringConsole } from "@/components/workspace/monitoring-console";
import { getMonitorTasks } from "@/lib/monitoring";

export const dynamic = "force-dynamic";

export default async function MonitoringPage() {
  const { items, source, note } = await getMonitorTasks();

  return (
    <section className="space-y-6">
      <DataSourceBanner source={source} label="监控任务" note={note} />
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">监控</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">监控任务</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          针对指定页面和站点建立持续观察，命中新线索后再进入整理、研判和后续材料流程。
        </p>
      </div>
      <MonitoringConsole items={items} />
    </section>
  );
}
