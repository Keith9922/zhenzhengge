import Link from "next/link";
import { DataSourceBanner } from "@/components/data-source-banner";
import { getCases } from "@/lib/cases";
import { getDrafts } from "@/lib/drafts";
import { getEvidencePacks } from "@/lib/evidence-packs";

export const dynamic = "force-dynamic";

export default async function WorkspaceHomePage() {
  const [casesResult, evidenceResult, draftsResult] = await Promise.all([getCases(), getEvidencePacks(), getDrafts()]);

  const stats = [
    { label: "案件数", value: String(casesResult.items.length) },
    { label: "证据包数", value: String(evidenceResult.items.length) },
    { label: "草稿数", value: String(draftsResult.items.length) },
  ];

  const hasError = [casesResult.source, evidenceResult.source, draftsResult.source].includes("error");
  const errorNote = [casesResult.note, evidenceResult.note, draftsResult.note].filter(Boolean).join("；");

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
    </div>
  );
}
