import Link from "next/link";
import { SiteHeader } from "@/components/site-header";
import { getPublicDocBySlug } from "@/lib/docs";

const doc = getPublicDocBySlug("project-package")!;

export default function ProjectPackageDocPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-5xl px-6 py-16 lg:px-8">
        <div className="rounded-[2rem] border border-white/70 bg-white/80 p-8 shadow-soft">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">产品资料</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight text-ink">{doc.title}</h1>
          <p className="mt-4 text-base leading-7 text-slate-600">{doc.summary}</p>
          <ul className="mt-8 space-y-3">
            {doc.bullets.map((bullet) => (
              <li key={bullet} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-700">
                {bullet}
              </li>
            ))}
          </ul>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/docs" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
              返回产品资料
            </Link>
            <Link href="/workspace" className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white">
              进入工作台
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
