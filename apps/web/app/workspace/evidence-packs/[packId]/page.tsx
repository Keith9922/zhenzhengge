import Link from "next/link";
import { notFound } from "next/navigation";
import { DataSourceBanner } from "@/components/data-source-banner";
import { EvidencePackPreview } from "@/components/workspace/evidence-pack-preview";
import { getEvidencePackById } from "@/lib/evidence-packs";

export const dynamic = "force-dynamic";

type EvidencePackDetailPageProps = {
  params: Promise<{ packId: string }>;
};

export default async function EvidencePackDetailPage({ params }: EvidencePackDetailPageProps) {
  const { packId } = await params;
  const { item, source, note } = await getEvidencePackById(packId);

  if (!item) {
    notFound();
  }

  return (
    <section className="space-y-6">
      <DataSourceBanner source={source} label="证据包详情" note={note} />
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">证据包详情</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">{item.title}</h1>
            <p className="mt-3 text-sm leading-7 text-slate-600">{item.summary}</p>
          </div>
          <span className="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700">{item.status}</span>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm text-slate-500">关联案件</p>
          <p className="mt-2 text-lg font-semibold text-ink">{item.caseId}</p>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm text-slate-500">来源地址</p>
          <p className="mt-2 break-all text-sm font-medium text-ink">{item.sourceUrl || item.source}</p>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm text-slate-500">采集时间</p>
          <p className="mt-2 text-lg font-semibold text-ink">{item.capturedAt}</p>
        </div>
      </div>

      <EvidencePackPreview item={item} />

      <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <h2 className="text-lg font-semibold text-ink">归档内容</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {item.artifactPaths.length ? (
            item.artifactPaths.map((path) => (
              <div key={path} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                {path}
              </div>
            ))
          ) : (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-600">
              当前只保留了证据元数据，文件内容可在后续接入展示与下载。
            </div>
          )}
        </div>
      </article>

      <div className="flex flex-wrap gap-3">
        <Link href="/workspace/evidence-packs" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
          返回证据包列表
        </Link>
        <Link href={`/workspace/drafts?caseId=${item.caseId}`} className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white">
          基于该案件生成草稿
        </Link>
      </div>
    </section>
  );
}
