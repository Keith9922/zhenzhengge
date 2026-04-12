import Link from "next/link";
import { DataSourceBanner } from "@/components/data-source-banner";
import { DraftCreateForm } from "@/components/workspace/draft-create-form";
import { getDrafts } from "@/lib/drafts";
import { getCases } from "@/lib/cases";
import { getEvidencePacks } from "@/lib/evidence-packs";

export const dynamic = "force-dynamic";

type DraftsPageProps = {
  searchParams?: Promise<{ caseId?: string; url?: string; title?: string }>;
};

export default async function DraftsPage({ searchParams }: DraftsPageProps) {
  const params = searchParams ? await searchParams : undefined;
  const caseId = params?.caseId;
  const capturedUrl = params?.url;
  const capturedTitle = params?.title;
  const { items, source, note } = await getDrafts(caseId);
  const { items: cases } = await getCases();

  // 获取最新证据包作为捕获内容
  let capturedContent;
  if (caseId) {
    const { items: packs } = await getEvidencePacks();
    // 找到关联案件的最新证据包
    const relatedPacks = packs.filter((p) => p.caseId === caseId);
    const latestPack = relatedPacks.length > 0 ? relatedPacks[0] : null;
    if (latestPack) {
      capturedContent = {
        url: latestPack.sourceUrl,
        title: latestPack.title,
        capturedAt: latestPack.capturedAt,
      };
    }
  }

  // 如果 URL 参数有捕获内容，优先使用
  if (capturedUrl || capturedTitle) {
    capturedContent = {
      url: capturedUrl,
      title: capturedTitle,
      capturedAt: new Date().toISOString(),
    };
  }

  return (
    <section className="space-y-6">
      <DataSourceBanner source={source} label="草稿列表" note={note} />
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">草稿</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">材料草稿</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          在这里围绕案件生成标准化材料草稿，并把后续审核与导出统一收口。
        </p>
      </div>

      <DraftCreateForm defaultCaseId={caseId} cases={cases} capturedContent={capturedContent} />

      <div className="grid gap-4">
        {items.map((item) => (
          <Link
            key={item.id}
            href={`/workspace/drafts/${item.id}`}
            className="block rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-brand-200 overflow-hidden"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-ink truncate">{item.title}</h2>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700 whitespace-nowrap">{item.status}</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600 line-clamp-2 break-words">{item.content}</p>
            <div className="mt-4 flex flex-wrap gap-4 text-xs text-slate-500">
              <span className="truncate">案件：{item.caseId}</span>
              <span className="whitespace-nowrap">更新时间：{item.updatedAt}</span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
