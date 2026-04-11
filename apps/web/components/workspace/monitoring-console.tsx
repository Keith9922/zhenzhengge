"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { postProxyJson } from "@/lib/client-api";
import type { MonitorTaskItem } from "@/lib/monitoring";

type MonitoringConsoleProps = {
  items: MonitorTaskItem[];
};

export function MonitoringConsole({ items }: MonitoringConsoleProps) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [message, setMessage] = useState("");
  const [form, setForm] = useState({
    name: "",
    targetUrl: "",
    site: "",
    keywords: "",
    frequencyMinutes: "60",
    riskThreshold: "70",
  });

  function runAction(path: string, payload?: unknown) {
    setMessage("");
    startTransition(async () => {
      try {
        const response = await postProxyJson(path.replace(/^\/+/, ""), payload ?? {});
        if (!response.ok) {
          throw new Error(await response.text());
        }
        setMessage("任务操作已完成");
        router.refresh();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "任务操作失败");
      }
    });
  }

  function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    runAction("/monitor-tasks", {
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
            placeholder="站点名称"
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
          <input
            value={form.keywords}
            onChange={(event) => setForm((current) => ({ ...current, keywords: event.target.value }))}
            placeholder="关注词，逗号分隔"
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
          <input
            type="number"
            min={5}
            value={form.frequencyMinutes}
            onChange={(event) => setForm((current) => ({ ...current, frequencyMinutes: event.target.value }))}
            placeholder="频率（分钟）"
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
          <input
            type="number"
            min={0}
            max={100}
            value={form.riskThreshold}
            onChange={(event) => setForm((current) => ({ ...current, riskThreshold: event.target.value }))}
            placeholder="风险阈值"
            className="rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
        </div>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button type="submit" disabled={pending} className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-60">
            {pending ? "处理中…" : "保存任务"}
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
                <p className="mt-1 text-sm leading-6 text-slate-600">{item.site} · {item.targetUrl}</p>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
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
                disabled={pending}
                onClick={() => runAction(`/monitor-tasks/${item.id}/run`)}
                className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-60"
              >
                立即执行
              </button>
              <button
                type="button"
                disabled={pending}
                onClick={() => runAction(`/monitor-tasks/${item.id}/toggle`, { enabled: item.status !== "active" })}
                className="rounded-full bg-brand-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
              >
                {item.status === "active" ? "暂停任务" : "恢复任务"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
