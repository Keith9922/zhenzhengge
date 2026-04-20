import Link from "next/link";
import { DataSourceBanner } from "@/components/data-source-banner";
import { getRuntimeModules } from "@/lib/runtime";

export const dynamic = "force-dynamic";

const statusStyleMap: Record<string, string> = {
  ready: "bg-emerald-50 text-emerald-700",
  ok: "bg-emerald-50 text-emerald-700",
  degraded: "bg-amber-50 text-amber-700",
  fallback: "bg-amber-50 text-amber-700",
  stub: "bg-amber-50 text-amber-700",
  error: "bg-rose-50 text-rose-700",
};

export default async function SettingsPage() {
  const { items, source, note } = await getRuntimeModules();

  return (
    <section className="space-y-6">
      <DataSourceBanner source={source} label="运行时模块状态" note={note} />
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">设置</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">系统设置</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          这里展示运行时模块健康状态，并提供真实配置入口，便于联调和上线前自检。
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {items.length ? (
          items.map((item) => {
            const tone = statusStyleMap[item.status] ?? "bg-slate-100 text-slate-700";
            return (
              <article key={item.name} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm text-slate-500">{item.name}</p>
                  <span className={`rounded-full px-3 py-1 text-xs font-medium ${tone}`}>{item.status}</span>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600">{item.description}</p>
              </article>
            );
          })
        ) : (
          <article className="rounded-3xl border border-dashed border-slate-300 bg-white p-6 text-sm leading-6 text-slate-600 md:col-span-3">
            当前未拉取到模块状态，请先确认 API 运行并重试。
          </article>
        )}
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-ink">真实配置入口</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">以下入口直接连接到实际业务配置，不是静态占位页。</p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link href="/workspace/monitoring" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            管理监控任务
          </Link>
          <Link href="/workspace/notifications" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            管理接收方式
          </Link>
          <Link href="/workspace/templates" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            查看模板配置
          </Link>
        </div>
      </div>
    </section>
  );
}
