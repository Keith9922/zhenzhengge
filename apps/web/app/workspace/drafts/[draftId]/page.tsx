import Link from "next/link";
import { DataSourceBanner } from "@/components/data-source-banner";
import { DraftActions } from "@/components/workspace/draft-actions";
import { DraftEditor } from "@/components/workspace/draft-editor";
import { extractEvidenceReferences } from "@/lib/draft-content";
import { getDraftById } from "@/lib/drafts";

export const dynamic = "force-dynamic";

type DraftDetailPageProps = {
  params: Promise<{ draftId: string }>;
};

export default async function DraftDetailPage({ params }: DraftDetailPageProps) {
  const { draftId } = await params;
  const { item, source, note } = await getDraftById(draftId);
  const evidenceReferences = item ? extractEvidenceReferences(item.content) : [];

  if (!item) {
    return (
      <section className="space-y-6">
        <DataSourceBanner source="error" label="草稿详情" note={note} />
        <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h1 className="text-2xl font-semibold tracking-tight text-ink">无法加载草稿详情</h1>
          <p className="mt-3 text-sm leading-7 text-slate-600">当前未获取到可展示的草稿数据，请检查后端服务后重试。</p>
          <div className="mt-5">
            <Link href="/workspace/drafts" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
              返回草稿列表
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <DataSourceBanner source={source} label="草稿详情" note={note} />
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">草稿详情</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">{item.title}</h1>
            <p className="mt-3 text-sm leading-7 text-slate-600">
              关联案件：{item.caseId} · 模板：{item.templateKey}
            </p>
          </div>
          <span className="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700">{item.status}</span>
        </div>
      </div>

      <div className="space-y-6">
        <DraftEditor draftId={item.id} initialContent={item.content} />

        {evidenceReferences.length ? (
          <article className="min-w-0 overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-lg font-semibold text-ink">证据引用导航</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              每条主张都可回溯到 EvidenceID，便于法务复核时快速定位证据来源。
            </p>
            <ul className="mt-4 space-y-3">
              {evidenceReferences.map((ref, index) => (
                <li key={`${ref.evidenceId}-${ref.lineNo}-${index}`} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-sm font-semibold text-ink">EvidenceID={ref.evidenceId}</span>
                    <Link
                      href={`/workspace/evidence-packs/${ref.evidenceId}`}
                      className="text-sm font-medium text-brand-700 hover:text-brand-800"
                    >
                      查看证据包
                    </Link>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">草稿行号：{ref.lineNo}</p>
                  <p className="mt-2 break-words text-sm leading-6 text-slate-600">{ref.text}</p>
                </li>
              ))}
            </ul>
          </article>
        ) : null}

        {item.reviewComment ? (
          <article className="min-w-0 overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-lg font-semibold text-ink">最近备注</h2>
            <p className="mt-3 break-words text-sm leading-6 text-slate-600">{item.reviewComment}</p>
          </article>
        ) : null}

        <DraftActions draftId={item.id} status={item.status} />
      </div>

      <div className="flex flex-wrap gap-3">
        <Link href="/workspace/drafts" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
          返回草稿列表
        </Link>
        <Link href={`/workspace/cases/${item.caseId}`} className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white">
          返回案件详情
        </Link>
      </div>
    </section>
  );
}
