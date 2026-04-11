import Link from "next/link";
import { DraftCreateForm } from "@/components/workspace/draft-create-form";
import { getDrafts } from "@/lib/drafts";

export const dynamic = "force-dynamic";

type DraftsPageProps = {
  searchParams?: Promise<{ caseId?: string }>;
};

export default async function DraftsPage({ searchParams }: DraftsPageProps) {
  const params = searchParams ? await searchParams : undefined;
  const caseId = params?.caseId;
  const { items } = await getDrafts(caseId);

  return (
    <section className="space-y-6">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">草稿</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">材料草稿</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          在这里围绕案件生成标准化材料草稿，并把后续审核与导出统一收口。
        </p>
      </div>

      <DraftCreateForm defaultCaseId={caseId} />

      <div className="grid gap-4">
        {items.map((item) => (
          <Link
            key={item.id}
            href={`/workspace/drafts/${item.id}`}
            className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-brand-200"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-ink">{item.title}</h2>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">{item.status}</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600 line-clamp-3">{item.content}</p>
            <p className="mt-4 text-xs text-slate-500">案件：{item.caseId} · 更新时间：{item.updatedAt}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
