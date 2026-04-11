import Link from "next/link";
import { notFound } from "next/navigation";
import { ExternalLink } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { type DocSlug, getDocSourceUrl, getInternalDocBySlug } from "@/lib/docs";

type InternalDocPageProps = {
  params: Promise<{ slug: DocSlug }>;
};

export default async function InternalDocPage({ params }: InternalDocPageProps) {
  const { slug } = await params;
  const doc = getInternalDocBySlug(slug);

  if (!doc) {
    notFound();
  }

  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-5xl px-6 py-16 lg:px-8">
        <div className="rounded-[2rem] border border-white/70 bg-white/80 p-8 shadow-soft">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">内部文档</p>
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
            <a
              href={getDocSourceUrl(doc.sourcePath)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-full bg-ink px-4 py-2 text-sm font-medium text-white"
            >
              打开源文件
              <ExternalLink className="h-4 w-4" />
            </a>
            <Link href="/internal/docs" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
              返回内部资料
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
