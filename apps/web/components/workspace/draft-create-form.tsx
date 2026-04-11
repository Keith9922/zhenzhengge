"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { postProxyJson } from "@/lib/client-api";

type DraftCreateFormProps = {
  defaultCaseId?: string;
};

type DraftCreateResponse = {
  draft_id: string;
};

const templateOptions = [
  { value: "lawyer-letter", label: "律师函" },
  { value: "platform-complaint", label: "平台投诉函" },
  { value: "evidence-index", label: "证据目录" },
];

export function DraftCreateForm({ defaultCaseId }: DraftCreateFormProps) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [caseId, setCaseId] = useState(defaultCaseId ?? "");
  const [templateKey, setTemplateKey] = useState("lawyer-letter");
  const [contact, setContact] = useState("");
  const [message, setMessage] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");

    startTransition(async () => {
      try {
        const response = await postProxyJson("document-drafts", {
          case_id: caseId,
          template_key: templateKey,
          variables_override: contact ? { contact } : {},
        });
        if (!response.ok) {
          throw new Error(await response.text());
        }
        const payload = (await response.json()) as DraftCreateResponse;
        router.push(`/workspace/drafts/${payload.draft_id}`);
        router.refresh();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "草稿创建失败");
      }
    });
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-ink">新建材料草稿</h2>
          <p className="mt-1 text-sm leading-6 text-slate-600">选择案件与材料类型，生成可进入审核流程的标准化初稿。</p>
        </div>
      </div>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-700">案件编号</span>
          <input
            required
            value={caseId}
            onChange={(event) => setCaseId(event.target.value)}
            placeholder="例如：case-zhzg-0001"
            className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
        </label>
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-700">材料类型</span>
          <select
            value={templateKey}
            onChange={(event) => setTemplateKey(event.target.value)}
            className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          >
            {templateOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label className="mt-4 block space-y-2 text-sm">
        <span className="font-medium text-slate-700">补充变量</span>
        <input
          value={contact}
          onChange={(event) => setContact(event.target.value)}
          placeholder="例如：法务部 / 联系窗口"
          className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
        />
      </label>
      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={pending}
          className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {pending ? "正在生成…" : "生成草稿"}
        </button>
        {message ? <p className="text-sm text-rose-600">{message}</p> : null}
      </div>
    </form>
  );
}
