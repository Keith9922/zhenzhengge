import Link from "next/link";
import { ArrowRight, ExternalLink } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { publicDocEntries } from "@/lib/docs";

export default function DocsPage() {
  return (
    <div id="top" className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-5xl px-6 py-16 lg:px-8">
        <div className="rounded-[2rem] border border-white/70 bg-white/80 p-8 shadow-soft">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">资料中心</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight text-ink">产品资料</h1>
          <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
            这里汇总了证证鸽对外展示所需的核心资料，帮助用户快速理解产品价值、适用场景与当前能力边界。
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {publicDocEntries.map((doc) => (
              <article
                key={doc.title}
                className="rounded-3xl border border-slate-200 bg-slate-50 p-5 transition hover:-translate-y-1 hover:border-brand-200"
              >
                <Link href={doc.href} className="block">
                  <div className="flex items-center justify-between gap-3">
                    <h2 className="text-lg font-semibold text-ink">{doc.title}</h2>
                    <ExternalLink className="h-4 w-4 text-slate-400" />
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{doc.summary}</p>
                </Link>
              </article>
            ))}
          </div>
        </div>

        <div className="mt-10 space-y-6">
          {publicDocEntries.map((doc) => (
            <section
              key={doc.slug}
              id={doc.anchor}
              className="scroll-mt-28 rounded-[2rem] border border-white/70 bg-white/80 p-8 shadow-soft"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">资料分区</p>
                  <h2 className="mt-3 text-3xl font-semibold tracking-tight text-ink">{doc.title}</h2>
                  <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600">{doc.summary}</p>
                </div>
                <Link
                  href="#top"
                  className="inline-flex shrink-0 items-center gap-2 rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-brand-300 hover:text-ink"
                >
                  返回顶部
                </Link>
              </div>
              <ul className="mt-8 space-y-3">
                {doc.bullets.map((bullet) => (
                  <li key={bullet} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-700">
                    {bullet}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/" className="inline-flex items-center gap-2 text-sm font-medium text-brand-700 hover:text-brand-800">
            返回主站
          </Link>
          <Link
            href="/workspace"
            className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-brand-300 hover:text-ink"
          >
            进入工作台
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </main>
    </div>
  );
}
