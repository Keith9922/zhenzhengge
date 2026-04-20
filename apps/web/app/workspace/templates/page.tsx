import Link from "next/link";
import { DataSourceBanner } from "@/components/data-source-banner";
import { getDocumentTemplates } from "@/lib/document-templates";

export const dynamic = "force-dynamic";

export default async function TemplatesPage() {
  const { items, source, note } = await getDocumentTemplates();

  return (
    <section className="space-y-6">
      <DataSourceBanner source={source} label="文书模板" note={note} />
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">模板</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">文书模板</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">模板数据来自真实后端，直接用于草稿生成与后续审核流程。</p>
      </div>

      {items.length ? (
        <div className="grid gap-4 md:grid-cols-3">
          {items.map((item) => (
            <article key={item.templateKey} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="text-lg font-semibold text-ink">{item.name}</h2>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">{item.category}</span>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-600">{item.description}</p>
              <p className="mt-3 text-xs leading-6 text-slate-500">适用场景：{item.targetUse}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {item.outputFormats.length ? (
                  item.outputFormats.map((format) => (
                    <span key={`${item.templateKey}-${format}`} className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                      {format}
                    </span>
                  ))
                ) : (
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">未配置输出格式</span>
                )}
              </div>
              <p className="mt-4 text-xs text-slate-500">模板键：{item.templateKey} · {item.isActive ? "已启用" : "未启用"}</p>
            </article>
          ))}
        </div>
      ) : (
        <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-8 text-sm leading-7 text-slate-600">
          暂无可用模板。可先在后端配置模板后再回到此页查看。
        </div>
      )}

      <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-ink">继续生成草稿</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">模板用于选型，草稿的生成、编辑、审核和导出在草稿页完成。</p>
          </div>
          <Link href="/workspace/drafts" className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white">
            前往草稿页
          </Link>
        </div>
      </div>
    </section>
  );
}
