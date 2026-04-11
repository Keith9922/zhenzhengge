import Link from "next/link";
import { notFound } from "next/navigation";
import { getCaseById } from "@/lib/cases";

type CaseDetailPageProps = {
  params: Promise<{ caseId: string }>;
};

export default async function CaseDetailPage({ params }: CaseDetailPageProps) {
  const { caseId } = await params;
  const item = await getCaseById(caseId);

  if (!item) {
    notFound();
  }

  return (
    <section className="space-y-6">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">案件详情</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">{item.title}</h1>
            <p className="mt-3 text-sm leading-7 text-slate-600">{item.summary}</p>
          </div>
          <span className="rounded-full bg-brand-50 px-4 py-2 text-sm font-medium text-brand-700">{item.status}</span>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-3xl bg-slate-50 p-5">
            <p className="text-sm text-slate-500">风险评分</p>
            <p className="mt-2 text-3xl font-semibold text-ink">{item.riskScore}</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-5">
            <p className="text-sm text-slate-500">证据包数量</p>
            <p className="mt-2 text-3xl font-semibold text-ink">{item.evidencePacks.length || item.evidenceCount}</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-5">
            <p className="text-sm text-slate-500">目标对象</p>
            <p className="mt-2 text-2xl font-semibold text-ink">{item.target}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-ink">证据包</h2>
            <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
              {item.evidencePacks.length || item.evidenceCount} 个
            </span>
          </div>
          <div className="mt-4 space-y-4">
            {item.evidencePacks.length ? (
              item.evidencePacks.map((pack) => (
                <article key={pack.id} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h3 className="text-base font-semibold text-ink">{pack.title}</h3>
                      <p className="mt-1 text-sm text-slate-600">
                        {pack.source} · {pack.capturedAt}
                      </p>
                    </div>
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700">
                      {pack.artifactCount} 项材料
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{pack.summary}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {pack.items.map((entry) => (
                      <span key={entry} className="rounded-full bg-white px-3 py-1 text-xs text-slate-700">
                        {entry}
                      </span>
                    ))}
                  </div>
                </article>
              ))
            ) : (
              <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm leading-6 text-slate-600">
                当前接口尚未返回独立证据包，已回退到基础证据目录展示。
              </div>
            )}
          </div>
        </article>

        <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-lg font-semibold text-ink">处理建议</h2>
          <div className="mt-4 space-y-3">
            {item.nextActions.map((action) => (
              <div key={action} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                {action}
              </div>
            ))}
          </div>
          <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <h3 className="text-sm font-semibold text-ink">研判要点</h3>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-600">
              {item.notes.map((note) => (
                <li key={note} className="flex gap-2">
                  <span className="mt-2 h-1.5 w-1.5 rounded-full bg-brand-500" />
                  <span>{note}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="mt-6 rounded-2xl border border-brand-100 bg-brand-50 p-4 text-sm leading-6 text-brand-800">
            当前文案只表示“疑似侵权线索”和“建议人工复核”，不直接给出最终法律结论。
          </div>
        </article>
      </div>

      <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <h2 className="text-lg font-semibold text-ink">基础证据目录</h2>
        <ul className="mt-4 grid gap-3 md:grid-cols-3">
          {item.evidenceItems.map((entry) => (
            <li key={entry} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
              {entry}
            </li>
          ))}
        </ul>
      </article>

      <div className="flex flex-wrap gap-3">
        <Link href="/workspace/cases" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
          返回案件列表
        </Link>
        <Link href="/workspace/templates" className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white">
          去模板页
        </Link>
      </div>
    </section>
  );
}
