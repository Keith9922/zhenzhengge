"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { postProxyJson } from "@/lib/client-api";

type DraftActionsProps = {
  draftId: string;
  status: string;
};

export function DraftActions({ draftId, status }: DraftActionsProps) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [comment, setComment] = useState("");
  const [message, setMessage] = useState("");

  function trigger(path: string, payload?: Record<string, string>) {
    setMessage("");
    startTransition(async () => {
      try {
        const response = await postProxyJson(path.replace(/^\/+/, ""), payload ?? {});
        if (!response.ok) {
          throw new Error(await response.text());
        }
        const result = (await response.json()) as { item?: Record<string, unknown> };
        void result;
        setMessage("操作已完成");
        router.refresh();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "操作失败");
      }
    });
  }

  return (
    <div className="min-w-0 overflow-hidden rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-ink">审核与导出</h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">当前状态：{status}。正式对外动作前，请先完成内部确认。</p>
      <label className="mt-4 block space-y-2 text-sm">
        <span className="font-medium text-slate-700">审核备注</span>
        <textarea
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          rows={4}
          placeholder="补充审核意见或整理说明"
          className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
        />
      </label>
      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          disabled={pending}
          onClick={() => trigger(`/document-drafts/${draftId}/submit-review`, { comment })}
          className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-60"
        >
          提交审核
        </button>
        <button
          type="button"
          disabled={pending}
          onClick={() => trigger(`/document-drafts/${draftId}/approve`, { comment })}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          通过
        </button>
        <button
          type="button"
          disabled={pending}
          onClick={() => trigger(`/document-drafts/${draftId}/reject`, { comment })}
          className="rounded-full bg-rose-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          驳回
        </button>
      </div>
      {message ? <p className="mt-4 break-all text-sm leading-6 text-slate-600">{message}</p> : null}
    </div>
  );
}
