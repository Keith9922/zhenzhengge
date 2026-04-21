"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { postProxyJson } from "@/lib/client-api";
import type { MonitorTaskItem } from "@/lib/monitoring";

type MonitoringConsoleProps = {
  items: MonitorTaskItem[];
};

const EMPTY_FORM = {
  name: "",
  targetUrl: "",
  site: "",
  keywords: "",
  frequencyMinutes: "60",
  riskThreshold: "70",
};

export function MonitoringConsole({ items }: MonitoringConsoleProps) {
  const router = useRouter();
  const [createPending, startCreateTransition] = useTransition();
  const [actionPending, startActionTransition] = useTransition();
  const [message, setMessage] = useState({ text: "", ok: true });
  const [form, setForm] = useState(EMPTY_FORM);

  function runTaskAction(path: string, payload?: unknown) {
    setMessage({ text: "", ok: true });
    startActionTransition(async () => {
      try {
        const response = await postProxyJson(path.replace(/^\/+/, ""), payload ?? {});
        if (!response.ok) throw new Error(await response.text());
        setMessage({ text: "操作已完成", ok: true });
        router.refresh();
      } catch (error) {
        setMessage({ text: error instanceof Error ? error.message : "操作失败", ok: false });
      }
    });
  }

  function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage({ text: "", ok: true });
    startCreateTransition(async () => {
      try {
        const response = await postProxyJson("monitor-tasks", {
          name: form.name,
          target_url: form.targetUrl,
          target_type: "page",
          site: form.site || "公开网页",
          brand_keywords: form.keywords
            .split(/[,，]/)
            .map((item) => item.trim())
            .filter(Boolean),
          frequency_minutes: Number(form.frequencyMinutes),
          risk_threshold: Number(form.riskThreshold),
        });
        if (!response.ok) throw new Error(await response.text());
        setMessage({ text: "任务已创建", ok: true });
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
        <h2 className="text-lg font-semibold text-ink">新增监控任务</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">针对指定页面或站点建立持续观察，命中新线索后再进入后续整理。</p>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <input
            required
            value={form.name}
            onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
            placeholder="任务名称"
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
          <input
            required
            value={form.targetUrl}
            onChange={(event) => setForm((current) => ({ ...current, targetUrl: event.target.value }))}
            placeholder="目标地址"
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
          <input
            value={form.site}
            onChange={(event) => setForm((current) => ({ ...current, site: event.target.value }))}
            placeholder="站点名称（选填）"
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
          <input
            value={form.keywords}
            onChange={(event) => setForm((current) => ({ ...current, keywords: event.target.value }))}
            placeholder="关注词，逗号分隔（选填）"
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
          <label className="space-y-1 text-sm">
            <span className="text-slate-500">巡查频率（分钟，最小 5）</span>
            <input
              type="number"
              min={5}
              value={form.frequencyMinutes}
              onChange={(event) => setForm((current) => ({ ...current, frequencyMinutes: event.target.value }))}
              className="block w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
            />
          </label>
          <label className="space-y-1 text-sm">
            <span className="text-slate-500">风险阈值（0-100）</span>
            <input
              type="number"
              min={0}
              max={100}
              value={form.riskThreshold}
              onChange={(event) => setForm((current) => ({ ...current, riskThreshold: event.target.value }))}
              className="block w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
            />
          </label>
        </div>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button type="submit" disabled={createPending} className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-60">
            {createPending ? "保存中…" : "保存任务"}
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
                  <p className="mt-1 text-sm leading-6 text-slate-600 break-all">{item.site} · {item.targetUrl}</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-medium ${item.status === "active" ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                  {item.status === "active" ? "运行中" : "已暂停"}
                </span>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">频率：{item.frequencyMinutes} 分钟</div>
                <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">阈值：{item.riskThreshold}</div>
                <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">最近执行：{item.lastRunAt || "暂无"}</div>
              </div>
              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  type="button"
                  disabled={actionPending}
                  onClick={() => runTaskAction(`/monitor-tasks/${item.id}/run`)}
                  className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-60"
                >
                  立即执行
                </button>
                <button
                  type="button"
                  disabled={actionPending}
                  onClick={() => runTaskAction(`/monitor-tasks/${item.id}/toggle`, { enabled: item.status !== "active" })}
                  className={`rounded-full px-4 py-2 text-sm font-medium text-white disabled:opacity-60 ${item.status === "active" ? "bg-amber-500" : "bg-brand-600"}`}
                >
                  {item.status === "active" ? "暂停任务" : "恢复任务"}
                </button>
              </div>
            </article>
          ))
        ) : (
          <article className="rounded-3xl border border-dashed border-slate-300 bg-white p-6 text-sm leading-6 text-slate-600">
            当前暂无监控任务，可使用上方表单创建第一条任务。
          </article>
        )}
      </div>
    </div>
  );
}
