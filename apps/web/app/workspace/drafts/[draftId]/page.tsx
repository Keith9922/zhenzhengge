import Link from "next/link";
import { notFound } from "next/navigation";
import { DataSourceBanner } from "@/components/data-source-banner";
import { DraftActions } from "@/components/workspace/draft-actions";
import { getDraftById } from "@/lib/drafts";

export const dynamic = "force-dynamic";

type DraftDetailPageProps = {
  params: Promise<{ draftId: string }>;
};

export default async function DraftDetailPage({ params }: DraftDetailPageProps) {
  const { draftId } = await params;
  const { item, source, note } = await getDraftById(draftId);

  if (!item) {
    notFound();
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

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-lg font-semibold text-ink">草稿内容</h2>
          <pre className="mt-4 overflow-x-auto whitespace-pre-wrap rounded-3xl bg-slate-50 p-5 text-sm leading-7 text-slate-700">
            {item.content}
          </pre>
          {item.reviewComment ? (
            <div className="mt-5 rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <h3 className="text-sm font-semibold text-ink">最近备注</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.reviewComment}</p>
            </div>
          ) : null}
        </article>

        <DraftActions draftId={item.id} status={item.status} exportPath={item.exportPath} />
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
