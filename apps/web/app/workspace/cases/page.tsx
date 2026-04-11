import Link from "next/link";
import { getCases } from "@/lib/cases";

export const dynamic = "force-dynamic";

export default async function CasesPage() {
  const { items } = await getCases();

  return (
    <section className="space-y-6">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">案件</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">案件列表</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          这里汇总当前线索和案件进展，便于团队快速查看状态、证据情况和下一步处理建议。
        </p>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        {items.map((item) => (
          <Link
            key={item.id}
            href={`/workspace/cases/${item.id}`}
            className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-brand-200"
          >
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-ink">{item.title}</h2>
              <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">{item.status}</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">{item.summary}</p>
            <p className="mt-4 text-xs text-slate-500">来源：{item.source} · 更新：{item.updatedAt}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
