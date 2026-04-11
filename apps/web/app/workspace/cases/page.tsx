const cases = [
  {
    title: "阿波达斯商品页",
    status: "高风险",
    summary: "近似命名、品牌视觉混淆，已完成基础取证。",
  },
  {
    title: "品牌官网疑似仿冒页",
    status: "待复核",
    summary: "页面出现新内容，等待进一步固证与人工审核。",
  },
  {
    title: "京东店铺图文混用页",
    status: "处理中",
    summary: "已生成证据包，待推送给负责人。",
  },
];

export default function CasesPage() {
  return (
    <section className="space-y-6">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">案件</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">案件列表</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">后续这里会接入真实案件、证据包和风险分析结果。当前展示的是工作台骨架。</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        {cases.map((item) => (
          <article key={item.title} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-ink">{item.title}</h2>
              <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">{item.status}</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">{item.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
