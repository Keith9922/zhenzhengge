import Link from "next/link";
import { DataSourceBanner } from "@/components/data-source-banner";
import { getCases } from "@/lib/cases";

export const dynamic = "force-dynamic";

const statusStyle: Record<string, string> = {
  open: "bg-brand-50 text-brand-700",
  active: "bg-emerald-50 text-emerald-700",
  pending: "bg-amber-50 text-amber-700",
  closed: "bg-slate-100 text-slate-500",
  resolved: "bg-slate-100 text-slate-500",
};

function caseStatusStyle(status: string) {
  return statusStyle[status.toLowerCase()] ?? "bg-brand-50 text-brand-700";
}

export default async function CasesPage() {
  const { items, source, note } = await getCases();

  return (
    <section className="space-y-6">
      <DataSourceBanner source={source} label="案件列表" note={note} />
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">案件</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">案件列表</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          这里汇总当前线索和案件进展，便于团队快速查看状态、证据情况和下一步处理建议。
        </p>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        {items.length ? (
          items.map((item) => (
            <Link
              key={item.id}
              href={`/workspace/cases/${item.id}`}
              className="flex flex-col rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-brand-200"
            >
              <div className="flex items-start justify-between gap-3">
                <h2 className="text-base font-semibold text-ink leading-6">{item.title}</h2>
                <span className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium ${caseStatusStyle(item.status)}`}>
                  {item.status}
                </span>
              </div>
              <p className="mt-3 flex-1 text-sm leading-6 text-slate-600 line-clamp-3">{item.summary}</p>
              <p className="mt-4 text-xs text-slate-400">来源：{item.source} · 更新：{item.updatedAt}</p>
            </Link>
          ))
        ) : (
          <article className="rounded-3xl border border-dashed border-slate-300 bg-white p-6 text-sm leading-7 text-slate-600 lg:col-span-3">
            当前暂无案件数据，可先通过插件采集线索或在监控任务命中后自动建案。
          </article>
        )}
      </div>
    </section>
  );
}
