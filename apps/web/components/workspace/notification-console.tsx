"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { postProxyJson } from "@/lib/client-api";
import type { NotificationChannelItem, NotificationLogItem } from "@/lib/notifications";

type NotificationConsoleProps = {
  items: NotificationChannelItem[];
  logs: NotificationLogItem[];
};

const statusConfig: Record<string, { label: string; style: string }> = {
  sent: { label: "发送成功", style: "bg-emerald-100 text-emerald-700" },
  "dry-run": { label: "模拟发送", style: "bg-slate-100 text-slate-600" },
  disabled: { label: "渠道停用", style: "bg-amber-100 text-amber-700" },
  failed: { label: "发送失败", style: "bg-rose-100 text-rose-700" },
};

const EMPTY_FORM = { name: "", target: "", type: "email" };

export function NotificationConsole({ items, logs }: NotificationConsoleProps) {
  const router = useRouter();
  const [createPending, startCreateTransition] = useTransition();
  const [testPending, startTestTransition] = useTransition();
  const [message, setMessage] = useState({ text: "", ok: true });
  const [form, setForm] = useState(EMPTY_FORM);

  function sendTest(channelId: string) {
    setMessage({ text: "", ok: true });
    startTestTransition(async () => {
      try {
        const response = await postProxyJson(`notification-channels/${channelId}/test`, {
          subject: "证证鸽测试提醒",
          body: "这是一条用于校验接收方式可用性的测试消息。",
        });
        if (!response.ok) throw new Error(await response.text());
        setMessage({ text: "测试消息已发送", ok: true });
        router.refresh();
      } catch (error) {
        setMessage({ text: error instanceof Error ? error.message : "发送失败", ok: false });
      }
    });
  }

  function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage({ text: "", ok: true });
    startCreateTransition(async () => {
      try {
        const response = await postProxyJson("notification-channels", {
          channel_type: form.type,
          name: form.name,
          target: form.target,
          enabled: true,
        });
        if (!response.ok) throw new Error(await response.text());
        setMessage({ text: "接收方式已创建", ok: true });
        setForm(EMPTY_FORM);
        router.refresh();
      } catch (error) {
        setMessage({ text: error instanceof Error ? error.message : "创建失败", ok: false });
      }
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
            placeholder={form.type === "email" ? "邮箱地址" : "Webhook 地址"}
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
        </div>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button type="submit" disabled={createPending} className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-60">
            {createPending ? "保存中…" : "保存接收方式"}
          </button>
          {message.text ? (
            <p className={`text-sm ${message.ok ? "text-emerald-600" : "text-rose-600"}`}>{message.text}</p>
          ) : null}
        </div>
      </form>

      <div className="grid gap-4">
        {items.length ? (
          items.map((item) => (
            <article key={item.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-lg font-semibold text-ink">{item.name}</h3>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{item.typeLabel} · {item.target}</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-medium ${item.enabled ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                  {item.enabled ? "已启用" : "未启用"}
                </span>
              </div>
              <div className="mt-4 flex flex-wrap items-center gap-3">
                <span className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">最近更新：{item.updatedAt}</span>
                <button
                  type="button"
                  disabled={testPending}
                  onClick={() => sendTest(item.id)}
                  className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-60"
                >
                  发送测试
                </button>
              </div>
            </article>
          ))
        ) : (
          <article className="rounded-3xl border border-dashed border-slate-300 bg-white p-6 text-sm leading-6 text-slate-600">
            当前暂无接收方式，请先创建至少一个渠道用于通知联调。
          </article>
        )}
      </div>

      <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <h2 className="text-lg font-semibold text-ink">通知日志</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">展示最近一次测试发送或监控任务命中后的提醒记录，用于联调和验收。</p>
        </div>
        <div className="mt-5 overflow-hidden rounded-2xl border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
              <tr>
                <th className="px-4 py-3">主题</th>
                <th className="px-4 py-3">事件</th>
                <th className="px-4 py-3">状态</th>
                <th className="px-4 py-3">时间</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {logs.length ? (
                logs.map((item) => {
                  const cfg = statusConfig[item.status] ?? { label: item.status, style: "bg-slate-100 text-slate-600" };
                  return (
                    <tr key={item.id}>
                      <td className="px-4 py-4 align-top">
                        <p className="font-medium text-ink">{item.subject}</p>
                        <p className="mt-1 text-xs leading-5 text-slate-500">{item.detail}</p>
                      </td>
                      <td className="px-4 py-4 align-top text-slate-600">{item.eventType}</td>
                      <td className="px-4 py-4 align-top">
                        <span className={`rounded-full px-3 py-1 text-xs font-medium ${cfg.style}`}>
                          {cfg.label}
                        </span>
                      </td>
                      <td className="px-4 py-4 align-top text-slate-600">{item.createdAt}</td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-500">
                    暂无通知日志
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
