import Link from "next/link";
import { getEvidencePacks } from "@/lib/evidence-packs";

export const dynamic = "force-dynamic";

export default async function EvidencePacksPage() {
  const { items } = await getEvidencePacks();

  return (
    <section className="space-y-6">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">证据包</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">证据包列表</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          这里集中查看已经完成整理的页面材料，便于回看来源、时间和后续可用的归档内容。
        </p>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {items.map((item) => (
          <Link
            key={item.id}
            href={`/workspace/evidence-packs/${item.id}`}
            className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-brand-200"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-ink">{item.title}</h2>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">{item.status}</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">{item.summary}</p>
            <p className="mt-4 text-xs text-slate-500">案件：{item.caseId} · 采集时间：{item.capturedAt}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
