import Link from "next/link";
import { DataSourceBanner } from "@/components/data-source-banner";
import { getCaseInsights } from "@/lib/case-insights";
import { getCases } from "@/lib/cases";
import { getDrafts } from "@/lib/drafts";
import { getEvidencePacks } from "@/lib/evidence-packs";

export const dynamic = "force-dynamic";

export default async function WorkspaceHomePage() {
  const [casesResult, evidenceResult, draftsResult, insightsResult] = await Promise.all([
    getCases(),
    getEvidencePacks(),
    getDrafts(),
    getCaseInsights(),
  ]);

  const stats = [
    { label: "案件数", value: String(casesResult.items.length) },
    { label: "证据包数", value: String(evidenceResult.items.length) },
    { label: "草稿数", value: String(draftsResult.items.length) },
  ];

  const hasError = [casesResult.source, evidenceResult.source, draftsResult.source, insightsResult.source].includes("error");
  const errorNote = [casesResult.note, evidenceResult.note, draftsResult.note, insightsResult.note].filter(Boolean).join("；");
  const insights = insightsResult.item;
  const metricCards = [
    {
      label: "TTA（小时）",
      value: insights?.ttaHours !== undefined ? insights.ttaHours.toFixed(2) : "--",
      hint: "从发现线索到导出材料的平均耗时",
    },
    {
      label: "Action Rate",
      value: insights ? `${insights.actionRate.toFixed(2)}%` : "--",
      hint: "已进入处置动作的案件占比",
    },
    {
      label: "Evidence Pass Rate",
      value: insights ? `${insights.evidencePassRate.toFixed(2)}%` : "--",
      hint: "审核通过/导出的草稿占比",
    },
  ];

  return (
    <div className="space-y-6">
      {hasError ? <DataSourceBanner source="error" label="工作台总览" note={errorNote || undefined} /> : null}
      <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">总览</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">证证鸽工作台</h1>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-600">
          这里集中查看案件、证据包、模板和处理进展，帮助团队围绕同一条线索完成留证、整理和后续推进。
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/workspace/cases" className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white">
            查看案件
          </Link>
          <Link href="/workspace/evidence-packs" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            查看证据包
          </Link>
          <Link href="/workspace/drafts" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            查看草稿
          </Link>
          <Link href="/workspace/monitoring" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            监控任务
          </Link>
          <Link href="/workspace/notifications" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            通知设置
          </Link>
          <Link href="/workspace/templates" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            管理模板
          </Link>
        </div>
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        {stats.map((item) => (
          <div key={item.label} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">{item.label}</p>
            <p className="mt-3 text-3xl font-semibold text-ink">{item.value}</p>
          </div>
        ))}
      </section>

      <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">效率看板</p>
            <h2 className="mt-3 text-2xl font-semibold tracking-tight text-ink">处置效率指标</h2>
            <p className="mt-3 text-sm leading-7 text-slate-600">
              指标由后端真实案件数据统计，用于评估“线索到动作”的落地效率。
            </p>
          </div>
          {insights?.generatedAt ? (
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
              更新时间：{new Date(insights.generatedAt).toLocaleString("zh-CN")}
            </span>
          ) : null}
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {metricCards.map((item) => (
            <article key={item.label} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-sm text-slate-500">{item.label}</p>
              <p className="mt-2 text-3xl font-semibold text-ink">{item.value}</p>
              <p className="mt-2 text-xs leading-6 text-slate-500">{item.hint}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
