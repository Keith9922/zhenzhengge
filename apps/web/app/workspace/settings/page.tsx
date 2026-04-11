import Link from "next/link";

const settings = [
  {
    title: "监控范围",
    value: "按站点、页面、店铺和品牌词整理关注目标",
  },
  {
    title: "材料偏好",
    value: "围绕常见处置场景整理说明材料和初稿",
  },
  {
    title: "资料查看",
    value: "统一查看产品资料、适用场景和能力边界",
  },
  {
    title: "接收方式",
    value: "管理处理提醒的默认接收入口与测试动作",
  },
];

export default function SettingsPage() {
  return (
    <section className="space-y-6">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">设置</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">系统设置</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">这里整理工作台常用的配置入口，方便团队围绕监控目标、材料偏好和资料查看统一管理。</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {settings.map((item) => (
          <article key={item.title} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">{item.title}</p>
            <p className="mt-3 text-lg font-semibold text-ink">{item.value}</p>
          </article>
        ))}
      </div>
      <div className="flex flex-wrap gap-3">
        <Link href="/workspace/monitoring" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
          管理监控任务
        </Link>
        <Link href="/workspace/notifications" className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">
          管理接收方式
        </Link>
      </div>
    </section>
  );
}
