const settings = [
  {
    title: "通知渠道",
    value: "钉钉 + 邮箱",
  },
  {
    title: "权限模型",
    value: "viewer / operator / reviewer / admin",
  },
  {
    title: "编排中枢",
    value: "Hermes Agent",
  },
];

export default function SettingsPage() {
  return (
    <section className="space-y-6">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">设置</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">系统设置</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">这里预留通知、权限和编排配置。后续接后端接口后可继续扩展。</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {settings.map((item) => (
          <article key={item.title} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">{item.title}</p>
            <p className="mt-3 text-lg font-semibold text-ink">{item.value}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
