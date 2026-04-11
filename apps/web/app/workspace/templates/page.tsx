import Link from "next/link";

const templates = [
  {
    name: "律师函",
    desc: "用于发送初步权利主张与整改要求。",
  },
  {
    name: "平台投诉函",
    desc: "用于平台侧下架、投诉和申诉准备。",
  },
  {
    name: "举报材料草稿",
    desc: "作为后续可选动作的材料预留入口。",
  },
];

export default function TemplatesPage() {
  return (
    <section className="space-y-6">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">模板</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">文书模板</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">围绕常见处置场景提供标准化模板，便于快速整理说明材料和初稿。</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {templates.map((item) => (
          <article key={item.name} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-ink">{item.name}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">{item.desc}</p>
          </article>
        ))}
      </div>
      <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-ink">继续生成草稿</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">模板目录用于选型，真正的生成与审核在草稿页内进行。</p>
          </div>
          <Link href="/workspace/drafts" className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white">
            前往草稿页
          </Link>
        </div>
      </div>
    </section>
  );
}
