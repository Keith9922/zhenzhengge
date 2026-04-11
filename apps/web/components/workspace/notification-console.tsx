"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { postProxyJson } from "@/lib/client-api";
import type { NotificationChannelItem } from "@/lib/notifications";

type NotificationConsoleProps = {
  items: NotificationChannelItem[];
};

export function NotificationConsole({ items }: NotificationConsoleProps) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [message, setMessage] = useState("");
  const [form, setForm] = useState({
    name: "",
    target: "",
    type: "email",
  });

  function runAction(path: string, payload: unknown) {
    setMessage("");
    startTransition(async () => {
      try {
        const response = await postProxyJson(path.replace(/^\/+/, ""), payload);
        if (!response.ok) {
          throw new Error(await response.text());
        }
        setMessage("操作已完成");
        router.refresh();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "操作失败");
      }
    });
  }

  function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    runAction("/notification-channels", {
      channel_type: form.type,
      name: form.name,
      target: form.target,
      enabled: true,
    });
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleCreate} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-ink">新增接收方式</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">配置处理线索时的默认接收入口，后续可用于预警和处理提醒。</p>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <input
            required
            value={form.name}
            onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
            placeholder="接收方式名称"
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
          <select
            value={form.type}
            onChange={(event) => setForm((current) => ({ ...current, type: event.target.value }))}
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          >
            <option value="email">邮件提醒</option>
            <option value="dingtalk">即时提醒 Webhook</option>
          </select>
          <input
            required
            value={form.target}
            onChange={(event) => setForm((current) => ({ ...current, target: event.target.value }))}
            placeholder="邮箱地址或 webhook"
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
        </div>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button type="submit" disabled={pending} className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-60">
            {pending ? "处理中…" : "保存接收方式"}
          </button>
          {message ? <p className="text-sm text-slate-600">{message}</p> : null}
        </div>
      </form>

      <div className="grid gap-4">
        {items.map((item) => (
          <article key={item.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-ink">{item.name}</h3>
                <p className="mt-1 text-sm leading-6 text-slate-600">{item.typeLabel} · {item.target}</p>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                {item.enabled ? "已启用" : "未启用"}
              </span>
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <span className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">最近更新：{item.updatedAt}</span>
              <button
                type="button"
                disabled={pending}
                onClick={() =>
                  runAction(`/notification-channels/${item.id}/test`, {
                    subject: "证证鸽测试提醒",
                    body: "这是一条用于校验接收方式可用性的测试消息。",
                  })
                }
                className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-60"
              >
                发送测试
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
