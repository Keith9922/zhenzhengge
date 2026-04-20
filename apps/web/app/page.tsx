import Link from "next/link";
import { ArrowRight, BookOpen, ExternalLink, FileText, ScanSearch, ShieldCheck } from "lucide-react";
import { FeatureCard } from "@/components/feature-card";
import { LogoMark } from "@/components/logo";
import { SectionHeading } from "@/components/section-heading";
import { SiteHeader } from "@/components/site-header";
import { docsIndex } from "@/lib/site";

export default function HomePage() {
  const simplifiedWorkflow = [
    {
      title: "找到页面",
      detail: "先把疑似侵权页面记录下来。",
    },
    {
      title: "保存证据",
      detail: "截图、页面信息和说明一起留存。",
    },
    {
      title: "生成草稿",
      detail: "系统根据证据整理出草稿内容。",
    },
    {
      title: "人工确认",
      detail: "最后由业务或法务审核后再处理。",
    },
  ];

  const coreHighlights = [
    {
      title: "页面取证",
      description: "先把页面内容和截图拿到。",
      icon: ScanSearch,
    },
    {
      title: "证据归档",
      description: "把证据整理成一份可复查的记录。",
      icon: ShieldCheck,
    },
    {
      title: "草稿生成",
      description: "根据证据生成可继续修改的草稿。",
      icon: FileText,
    },
  ];

  const heroFlow = [
    {
      title: "打开页面",
      detail: "可以手动操作，也可以自动监控。",
    },
    {
      title: "保存证据",
      detail: "截图和页面信息一起留存。",
    },
    {
      title: "生成草稿",
      detail: "系统整理出可审核草稿。",
    },
    {
      title: "人工确认",
      detail: "确认后再进入正式处理。",
    },
  ];

  return (
    <div className="min-h-screen text-ink">
      <SiteHeader />
      <main>
        <section className="noise">
          <div className="mx-auto grid max-w-7xl gap-14 px-6 py-16 lg:grid-cols-[1.15fr_0.85fr] lg:px-8 lg:py-24">
            <div className="max-w-3xl">
              <span className="inline-flex items-center gap-3 rounded-full border border-brand-100 bg-white/90 px-3 py-2 text-sm font-medium text-brand-700 shadow-soft">
                <LogoMark className="h-8 w-8" />
                <span>证证鸽｜AI 知识产权侵权响应平台</span>
              </span>
              <h1 className="mt-6 text-5xl font-semibold tracking-tight text-ink sm:text-6xl">
                让疑似侵权页面
                <span className="block text-brand-700">更快变成可行动的案件材料</span>
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
                证证鸽面向知识产权侵权响应场景，帮助品牌方和法务团队把零散的网页线索快速转成标准化证据包、案件材料与可审核的法律文书草稿。
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link
                  href="/workspace"
                  className="inline-flex items-center gap-2 rounded-full bg-ink px-5 py-3 text-sm font-medium text-white transition hover:bg-slate-800"
                >
                  进入工作台
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  href="/docs"
                  className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-5 py-3 text-sm font-medium text-slate-700 transition hover:border-brand-300 hover:text-ink"
                >
                  查看产品资料
                  <BookOpen className="h-4 w-4" />
                </Link>
              </div>
              <div className="mt-10 grid gap-4 sm:grid-cols-3">
                {[
                  "网页取证",
                  "证据归档",
                  "草稿生成",
                ].map((item) => (
                  <div key={item} className="rounded-2xl border border-white/70 bg-white/80 px-4 py-3 shadow-soft">
                    <p className="text-sm font-semibold text-ink">{item}</p>
                    <p className="mt-1 text-xs text-slate-500">围绕侵权响应主链路逐步展开</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="absolute inset-0 -z-10 rounded-[2rem] bg-brand-100/40 blur-3xl" />
              <div className="rounded-[2rem] border border-white/80 bg-white/80 p-6 shadow-soft backdrop-blur">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-brand-700">怎么用</p>
                    <p className="text-xs text-slate-500">按四步走，先留证，再确认。</p>
                  </div>
                  <div className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                    公开网页场景
                  </div>
                </div>
                <div className="mt-6 space-y-4">
                  {heroFlow.map((step, index) => (
                    <div key={step.title} className="flex gap-4 rounded-2xl bg-slate-50 px-4 py-4">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-600 text-sm font-semibold text-white">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-semibold text-ink">{step.title}</p>
                        <p className="mt-1 text-sm leading-6 text-slate-600">{step.detail}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
                  <div className="flex items-center gap-2 text-sm font-semibold text-ink">
                    <ShieldCheck className="h-4 w-4 text-brand-700" />
                    说明
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-600">两种方式都会进入后续证据归档和草稿链路，正式处理前仍需人工确认。</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-6 py-6 lg:px-8">
          <SectionHeading
            eyebrow="核心能力"
            title="核心能力就三件事"
            description="取证、归档、出草稿。先把最常用的链路讲清楚。"
          />
          <div className="mt-8 grid gap-5 xl:grid-cols-3">
            {coreHighlights.map((item) => (
              <FeatureCard key={item.title} {...item} />
            ))}
          </div>
        </section>

        <section id="workflow" className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
          <SectionHeading
            eyebrow="功能链路"
            title="四步走完这条链路"
            description="先记下页面，再留证据，然后出草稿，最后人工确认。"
          />
          <div className="mt-8 grid gap-4 md:grid-cols-2">
            {simplifiedWorkflow.map((step, index) => (
              <div key={step.title} className="rounded-3xl border border-white/70 bg-white/80 p-5 shadow-soft">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-600 text-sm font-semibold text-white">
                    {index + 1}
                  </div>
                  <h3 className="text-base font-semibold text-ink">{step.title}</h3>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600">{step.detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="docs" className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
          <SectionHeading
            eyebrow="产品资料"
            title="先看产品概览、适用场景与能力边界"
            description="这里展示的是面向外部的产品资料，帮助用户快速理解证证鸽适合解决哪些问题，以及当前能力边界。"
          />
          <div className="mt-8 grid gap-5 lg:grid-cols-3">
            {docsIndex.map((doc) => (
              <Link
                key={doc.title}
                href={doc.href}
                className="rounded-3xl border border-white/70 bg-white/80 p-6 shadow-soft transition hover:-translate-y-1 hover:border-brand-200"
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-ink">{doc.title}</h3>
                  <ExternalLink className="h-4 w-4 text-slate-400" />
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600">{doc.summary}</p>
              </Link>
            ))}
          </div>
        </section>

        <section id="workspace" className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
          <div className="rounded-[2rem] border border-slate-200 bg-ink px-8 py-10 text-white shadow-soft">
            <div className="max-w-3xl">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-200">工作台入口</p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
                从主站进入工作台，继续查看案件、证据和草稿进展
              </h2>
              <p className="mt-4 text-base leading-7 text-slate-300">
                工作台承接案件查看、证据包整理、材料准备与后续协同，是证证鸽的核心操作入口。
              </p>
            </div>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/workspace"
                className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-medium text-ink transition hover:bg-slate-100"
              >
                进入工作台
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/workspace/cases"
                className="inline-flex items-center gap-2 rounded-full border border-white/20 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/10"
              >
                查看案件页
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
