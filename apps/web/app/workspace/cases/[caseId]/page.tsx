import Link from "next/link";
import { DataSourceBanner } from "@/components/data-source-banner";
import { getCaseActionCenter, getCaseEvidenceClaimLinks } from "@/lib/case-actions";
import { getCaseById } from "@/lib/cases";

const priorityStyle: Record<string, string> = {
  high: "bg-rose-50 text-rose-700",
  medium: "bg-amber-50 text-amber-700",
  low: "bg-slate-100 text-slate-600",
};

function priorityLabel(p: string) {
  return { high: "高优", medium: "中优", low: "低优" }[p.toLowerCase()] ?? p;
}

export const dynamic = "force-dynamic";

type CaseDetailPageProps = {
  params: Promise<{ caseId: string }>;
};

export default async function CaseDetailPage({ params }: CaseDetailPageProps) {
  const { caseId } = await params;
  const [caseResult, actionCenterResult, claimLinksResult] = await Promise.all([
    getCaseById(caseId),
    getCaseActionCenter(caseId),
    getCaseEvidenceClaimLinks(caseId),
  ]);
  const { item, source, note } = caseResult;
  const actionCenter = actionCenterResult.item;
  const claimLinks = claimLinksResult.item;
  const bannerSource =
    source === "error" || actionCenterResult.source === "error" || claimLinksResult.source === "error" ? "error" : "api";
  const bannerNote = [note, actionCenterResult.note, claimLinksResult.note].filter(Boolean).join("；");

  if (!item) {
    return (
      <section className="space-y-6">
        <DataSourceBanner source="error" label="案件详情" note={bannerNote || note} />
        <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h1 className="text-2xl font-semibold tracking-tight text-ink">无法加载案件详情</h1>
          <p className="mt-3 text-sm leading-7 text-slate-600">当前未获取到可展示的案件数据，请检查后端服务后重试。</p>
          <div className="mt-5">
            <Link href="/workspace/cases" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
              返回案件列表
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <DataSourceBanner source={bannerSource} label="案件详情" note={bannerNote || undefined} />
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
              item.evidencePacks.map((pack, packIndex) => (
                <article key={`${pack.id || "evidence-pack"}-${packIndex}`} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
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
                  {claimLinks ? (
                    <div className="mt-4 rounded-2xl border border-brand-100 bg-brand-50 p-4">
                      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-700">证据引用主张</p>
                      {(() => {
                        const match = claimLinks.items.find((entry) => entry.evidencePackId === pack.id);
                        if (!match || !match.claimCount) {
                          return <p className="mt-2 text-sm text-slate-600">当前草稿尚未引用该证据。</p>;
                        }
                        return (
                          <ul className="mt-2 space-y-2 text-sm text-slate-700">
                            {match.claims.slice(0, 3).map((claim) => (
                              <li key={`${claim.draftId}-${claim.lineNo}`} className="rounded-xl bg-white px-3 py-2">
                                <Link
                                  href={`/workspace/drafts/${claim.draftId}`}
                                  className="font-medium text-brand-700 hover:text-brand-800"
                                >
                                  {claim.draftTitle}（第 {claim.lineNo} 行）
                                </Link>
                                <p className="mt-1 break-words text-xs leading-5 text-slate-600">{claim.claimText}</p>
                              </li>
                            ))}
                          </ul>
                        );
                      })()}
                    </div>
                  ) : null}
                  <div className="mt-4 flex flex-wrap gap-2">
                    {pack.items.map((entry, itemIndex) => (
                      <span key={`${pack.id || "evidence-pack"}-${itemIndex}-${entry}`} className="rounded-full bg-white px-3 py-1 text-xs text-slate-700">
                        {entry}
                      </span>
                    ))}
                  </div>
                  <div className="mt-4">
                    <Link
                      href={`/workspace/evidence-packs/${pack.id}`}
                      className="text-sm font-medium text-brand-700 hover:text-brand-800"
                    >
                      查看证据包详情
                    </Link>
                  </div>
                </article>
              ))
            ) : (
              <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm leading-6 text-slate-600">
                当前暂未拆分出独立证据包，先展示基础证据目录，方便继续补充和整理。
              </div>
            )}
          </div>
        </article>

        <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-lg font-semibold text-ink">案件动作中心</h2>
          <div className="mt-4 space-y-3">
            {actionCenter?.items?.length ? (
              actionCenter.items.map((action) => (
                <article key={action.actionId} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                  <p className="text-sm font-semibold text-ink">{action.title}</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{action.description}</p>
                  <div className="mt-3 flex items-center justify-between gap-2">
                    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${priorityStyle[action.priority?.toLowerCase()] ?? "bg-slate-100 text-slate-600"}`}>
                      {priorityLabel(action.priority ?? "")}
                    </span>
                    <Link href={action.href} className="text-sm font-medium text-brand-700 hover:text-brand-800">
                      {action.ctaLabel}
                    </Link>
                  </div>
                </article>
              ))
            ) : (
              item.nextActions.map((action, actionIndex) => (
                <div key={`next-action-${actionIndex}-${action}`} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                  {action}
                </div>
              ))
            )}
          </div>
          <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <h3 className="text-sm font-semibold text-ink">研判要点</h3>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-600">
              {item.notes.map((note, noteIndex) => (
                <li key={`note-${noteIndex}-${note}`} className="flex gap-2">
                  <span className="mt-2 h-1.5 w-1.5 rounded-full bg-brand-500" />
                  <span>{note}</span>
                </li>
              ))}
            </ul>
          </div>
          {claimLinks ? (
            <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <h3 className="text-sm font-semibold text-ink">证据-主张绑定概览</h3>
              <p className="mt-2 text-sm text-slate-600">
                证据包：{claimLinks.totalEvidence}，已绑定主张：{claimLinks.totalClaims}
              </p>
            </div>
          ) : null}
          <div className="mt-6 rounded-2xl border border-brand-100 bg-brand-50 p-4 text-sm leading-6 text-brand-800">
            当前文案只表示“疑似侵权线索”和“建议人工复核”，不直接给出最终法律结论。
          </div>
        </article>
      </div>

      <article className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <h2 className="text-lg font-semibold text-ink">基础证据目录</h2>
        <ul className="mt-4 grid gap-3 md:grid-cols-3">
          {item.evidenceItems.map((entry, entryIndex) => (
            <li key={`evidence-item-${entryIndex}-${entry}`} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
              {entry}
            </li>
          ))}
        </ul>
      </article>

      <div className="flex flex-wrap gap-3">
        <Link href="/workspace/cases" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
          返回案件列表
        </Link>
        <Link href={`/workspace/drafts?caseId=${item.id}`} className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white">
          生成草稿
        </Link>
        <Link href={`/workspace/evidence-packs?caseId=${item.id}`} className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
          查看证据包
        </Link>
        <Link href="/workspace/templates" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
          去模板页
        </Link>
      </div>
    </section>
  );
}
