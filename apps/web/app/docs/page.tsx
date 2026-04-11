import Link from "next/link";
import { SiteHeader } from "@/components/site-header";
import { docsIndex } from "@/lib/site";

export default function DocsPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-5xl px-6 py-16 lg:px-8">
        <div className="rounded-[2rem] border border-white/70 bg-white/80 p-8 shadow-soft">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">资料中心</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight text-ink">开发与展示对齐文档</h1>
          <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
            这里汇总了证证鸽的 PRD、技术选型表和项目资料包。Landing Page 会把这里作为文档入口，后续可继续扩展到更细的实现说明。
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {docsIndex.map((doc) => (
              <a key={doc.title} href={doc.href} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                <h2 className="text-lg font-semibold text-ink">{doc.title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">{doc.summary}</p>
              </a>
            ))}
          </div>
          <div className="mt-8">
            <Link href="/" className="text-sm font-medium text-brand-700 hover:text-brand-800">
              返回主站
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
