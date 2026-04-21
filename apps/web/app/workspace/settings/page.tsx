import Link from "next/link";
import { DataSourceBanner } from "@/components/data-source-banner";
import { getRuntimeCompliance, getRuntimeModules } from "@/lib/runtime";

export const dynamic = "force-dynamic";

const statusStyleMap: Record<string, string> = {
  ready: "bg-emerald-50 text-emerald-700",
  ok: "bg-emerald-50 text-emerald-700",
  degraded: "bg-amber-50 text-amber-700",
  fallback: "bg-amber-50 text-amber-700",
  stub: "bg-amber-50 text-amber-700",
  error: "bg-rose-50 text-rose-700",
};

export default async function SettingsPage() {
  const [modulesResult, complianceResult] = await Promise.all([getRuntimeModules(), getRuntimeCompliance()]);
  const { items, source, note } = modulesResult;
  const compliance = complianceResult.item;
  const bannerSource = source === "error" || complianceResult.source === "error" ? "error" : "api";
  const bannerNote = [note, complianceResult.note].filter(Boolean).join("；");

  const complianceChecks = compliance
    ? [
        { label: "鉴权已开启", ok: compliance.requireAuth, detail: "要求：ZHZG_REQUIRE_AUTH=true" },
        { label: "Demo Seed 已关闭", ok: !compliance.demoSeedEnabled, detail: "要求：ZHZG_ENABLE_DEMO_SEED=false" },
        { label: "文书严格模式", ok: compliance.draftGenerationStrict, detail: "要求：ZHZG_DRAFT_GENERATION_STRICT=true" },
        {
          label: "可信时间戳（如强制）",
          ok: !compliance.evidenceTimestampRequired || compliance.evidenceTimestampReady,
          detail: compliance.evidenceTimestampRequired
            ? "已开启强制时间戳，要求 TSA 可用"
            : "当前未强制时间戳（可按需启用）",
        },
        { label: "LLM 可用", ok: compliance.llmReady, detail: `当前提供方：${compliance.llmProvider}` },
        {
          label: "Hermes 编排器",
          ok: compliance.harnessAgentEnabled,
          detail: compliance.harnessAgentEnabled
            ? "Hermes CLI 已启用，优先走 CLI 生成"
            : "当前走 LLM 直连或本地模板（ZHZG_HARNESS_AGENT_ENABLED=false）",
        },
      ]
    : [];

  return (
    <section className="space-y-6">
      <DataSourceBanner source={bannerSource} label="运行时模块状态" note={bannerNote || undefined} />
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">设置</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">系统设置</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          这里展示运行时模块健康状态，并提供真实配置入口，便于联调和上线前自检。
        </p>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-ink">合规状态面板</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">用于比赛现场和上线前核验关键开关是否达标。</p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              compliance?.complianceReady ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
            }`}
          >
            {compliance?.complianceReady ? "基础合规达标" : "存在合规风险"}
          </span>
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {complianceChecks.length ? (
            complianceChecks.map((check) => (
              <article
                key={check.label}
                className={`rounded-2xl border px-4 py-3 ${
                  check.ok ? "border-emerald-200 bg-emerald-50" : "border-rose-200 bg-rose-50"
                }`}
              >
                <p className={`text-sm font-semibold ${check.ok ? "text-emerald-700" : "text-rose-700"}`}>{check.label}</p>
                <p className="mt-1 text-xs text-slate-600">{check.detail}</p>
              </article>
            ))
          ) : (
            <article className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-600 md:col-span-2">
              当前未获取到合规状态，请先确认 API 运行并重试。
            </article>
          )}
        </div>

        {compliance?.warnings.length ? (
          <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4">
            <p className="text-sm font-semibold text-amber-700">当前风险提示</p>
            <ul className="mt-2 space-y-1 text-sm text-amber-800">
              {compliance.warnings.map((warning, index) => (
                <li key={`${warning}-${index}`}>{warning}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {items.length ? (
          items.map((item) => {
            const tone = statusStyleMap[item.status] ?? "bg-slate-100 text-slate-700";
            return (
              <article key={item.name} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm text-slate-500">{item.name}</p>
                  <span className={`rounded-full px-3 py-1 text-xs font-medium ${tone}`}>{item.status}</span>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600">{item.description}</p>
              </article>
            );
          })
        ) : (
          <article className="rounded-3xl border border-dashed border-slate-300 bg-white p-6 text-sm leading-6 text-slate-600 md:col-span-3">
            当前未拉取到模块状态，请先确认 API 运行并重试。
          </article>
        )}
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-ink">真实配置入口</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">以下入口直接连接到实际业务配置，不是静态占位页。</p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link href="/workspace/monitoring" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            管理监控任务
          </Link>
          <Link href="/workspace/notifications" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            管理接收方式
          </Link>
          <Link href="/workspace/templates" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            查看模板配置
          </Link>
        </div>
      </div>
    </section>
  );
}
