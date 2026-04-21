import Link from "next/link";
import { DataSourceBanner } from "@/components/data-source-banner";
import { getCaseActionCenter } from "@/lib/case-actions";
import { getCaseInsights } from "@/lib/case-insights";
import { getCases } from "@/lib/cases";

export const dynamic = "force-dynamic";

export default async function ActionCenterPage() {
  const [casesResult, insightsResult] = await Promise.all([getCases(), getCaseInsights()]);
  const actionResults = await Promise.all(casesResult.items.map((item) => getCaseActionCenter(item.id)));
  const hasActionError = actionResults.some((result) => result.source === "error");
  const bannerSource = casesResult.source === "error" || insightsResult.source === "error" || hasActionError ? "error" : "api";
  const bannerNote = [
    casesResult.note,
    insightsResult.note,
    ...actionResults.map((result) => result.note).filter(Boolean),
  ]
    .filter(Boolean)
    .join("；");

  return (
    <section className="space-y-6">
      <DataSourceBanner source={bannerSource} label="案件动作中心" note={bannerNote || undefined} />

      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">动作中心</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">把线索推进为可执行动作</h1>
            <p className="mt-3 text-sm leading-7 text-slate-600">
              按案件给出明确下一步操作，优先处理“补证、审核、导出、发起投诉”这类可落地动作。
            </p>
          </div>
          <span className="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700">
            案件数：{casesResult.items.length}
          </span>
        </div>

        {insightsResult.item ? (
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm text-slate-500">TTA（小时）</p>
              <p className="mt-2 text-2xl font-semibold text-ink">{(insightsResult.item.ttaHours ?? 0).toFixed(2)}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Action Rate</p>
              <p className="mt-2 text-2xl font-semibold text-ink">{insightsResult.item.actionRate.toFixed(2)}%</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Evidence Pass Rate</p>
              <p className="mt-2 text-2xl font-semibold text-ink">{insightsResult.item.evidencePassRate.toFixed(2)}%</p>
            </div>
          </div>
        ) : null}
      </div>

      {casesResult.items.length ? (
        <div className="space-y-4">
          {casesResult.items.map((item, index) => {
            const actionCenter = actionResults[index]?.item;
            const actions = actionCenter?.items || [];
            return (
              <article key={item.id} className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h2 className="text-xl font-semibold text-ink">{item.title}</h2>
                    <p className="mt-2 text-sm text-slate-600">
                      {item.status} · {item.updatedAt}
                    </p>
                  </div>
                  <Link
                    href={`/workspace/cases/${item.id}`}
                    className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700"
                  >
                    查看案件详情
                  </Link>
                </div>

                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  {actions.length ? (
                    actions.map((action) => (
                      <article key={action.actionId} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                        <p className="text-sm font-semibold text-ink">{action.title}</p>
                        <p className="mt-1 text-sm leading-6 text-slate-600">{action.description}</p>
                        <div className="mt-3 flex items-center justify-between gap-2">
                          <span className="rounded-full bg-white px-2.5 py-1 text-xs text-slate-600">
                            优先级：{action.priority}
                          </span>
                          <Link href={action.href} className="text-sm font-medium text-brand-700 hover:text-brand-800">
                            {action.ctaLabel}
                          </Link>
                        </div>
                      </article>
                    ))
                  ) : (
                    <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600 md:col-span-2">
                      当前暂无可执行动作，建议先补充证据或生成草稿。
                    </div>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      ) : (
        <article className="rounded-[2rem] border border-dashed border-slate-300 bg-white p-8 text-sm leading-7 text-slate-600">
          当前暂无案件，先通过插件发起取证，系统会自动生成案件并在此提供下一步动作。
        </article>
      )}
    </section>
  );
}
