import Link from "next/link";

const stats = [
  { label: "案件状态", value: "12" },
  { label: "证据包", value: "24" },
  { label: "待审核文书", value: "3" },
];

export default function WorkspaceHomePage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">总览</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">证证鸽工作台</h1>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-600">
          这里是案件、证据包、模板和审核流的统一操作中心。当前版本先提供骨架和导航，后续再接入真实接口和数据。
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/workspace/cases" className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white">
            查看案件
          </Link>
          <Link href="/workspace/templates" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            管理模板
          </Link>
        </div>
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        {stats.map((item) => (
          <div key={item.label} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">{item.label}</p>
            <p className="mt-3 text-3xl font-semibold text-ink">{item.value}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
