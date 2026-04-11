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
            <p className="mt-2 text-3xl font-semibold text-ink">{item.evidenceCount}</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-5">
            <p className="text-sm text-slate-500">目标对象</p>
            <p className="mt-2 text-2xl font-semibold text-ink">{item.target}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-lg font-semibold text-ink">证据目录</h2>
          <ul className="mt-4 grid gap-3 md:grid-cols-2">
            {item.evidenceItems.map((entry) => (
              <li key={entry} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                {entry}
              </li>
            ))}
          </ul>
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
          <div className="mt-6 rounded-2xl border border-brand-100 bg-brand-50 p-4 text-sm leading-6 text-brand-800">
            当前文案只表示“疑似侵权线索”和“建议人工复核”，不直接给出最终法律结论。
          </div>
        </article>
      </div>

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
