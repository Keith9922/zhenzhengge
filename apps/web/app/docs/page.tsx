import Link from "next/link";
import { ArrowRight, ExternalLink } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { docEntries, getDocSourceUrl } from "@/lib/docs";
import { getRepoUrl } from "@/lib/env";

export default function DocsPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-5xl px-6 py-16 lg:px-8">
        <div className="rounded-[2rem] border border-white/70 bg-white/80 p-8 shadow-soft">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">资料中心</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight text-ink">开发与展示对齐文档</h1>
          <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
            这里汇总了证证鸽的 PRD、技术选型表和项目资料包。每个条目都可以进入独立文档页，源码仓库地址可通过环境变量配置。
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {docEntries.map((doc) => (
              <article key={doc.title} className="rounded-3xl border border-slate-200 bg-slate-50 p-5 transition hover:-translate-y-1 hover:border-brand-200">
                <Link href={doc.href} className="block">
                  <div className="flex items-center justify-between gap-3">
                    <h2 className="text-lg font-semibold text-ink">{doc.title}</h2>
                    <ExternalLink className="h-4 w-4 text-slate-400" />
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{doc.summary}</p>
                </Link>
                <a
                  href={getDocSourceUrl(doc.sourcePath)}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-4 inline-flex items-center gap-1 text-xs font-medium text-brand-700"
                >
                  查看源文件
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </article>
            ))}
          </div>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/" className="inline-flex items-center gap-2 text-sm font-medium text-brand-700 hover:text-brand-800">
              返回主站
            </Link>
            <a
              href={getRepoUrl()}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-brand-300 hover:text-ink"
            >
              打开源码仓库
              <ArrowRight className="h-4 w-4" />
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}
