"use client";

import { useState, useTransition } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { postProxyJson } from "@/lib/client-api";
import type { CaseSummary } from "@/lib/cases";
import type { DocumentTemplateItem } from "@/lib/document-templates";

type CapturedContent = {
  url?: string;
  title?: string;
  screenshotBase64?: string;
  capturedAt?: string;
  pageText?: string;
};

type DraftCreateFormProps = {
  defaultCaseId?: string;
  cases?: CaseSummary[];
  templates?: DocumentTemplateItem[];
  capturedContent?: CapturedContent;
};

type DraftCreateResponse = {
  draft_id: string;
};

const CATEGORY_ORDER = ["处置文书", "平台化输出", "案件材料"];

export function DraftCreateForm({
  defaultCaseId,
  cases = [],
  templates = [],
  capturedContent,
}: DraftCreateFormProps) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [caseId, setCaseId] = useState(defaultCaseId ?? "");
  const [templateKey, setTemplateKey] = useState(
    templates.find((t) => t.isActive)?.templateKey ?? "lawyer-letter",
  );
  const [contact, setContact] = useState("");
  const [message, setMessage] = useState("");

  // group by category
  const grouped = CATEGORY_ORDER.reduce<Record<string, DocumentTemplateItem[]>>((acc, cat) => {
    acc[cat] = templates.filter((t) => t.isActive && t.category === cat);
    return acc;
  }, {});
  // add anything not in the order
  templates.forEach((t) => {
    if (t.isActive && !CATEGORY_ORDER.includes(t.category)) {
      grouped[t.category] ??= [];
      grouped[t.category].push(t);
    }
  });

  const activeCategories = [...CATEGORY_ORDER, ...Object.keys(grouped).filter((c) => !CATEGORY_ORDER.includes(c))].filter(
    (c) => grouped[c]?.length,
  );

  const selectedTemplate = templates.find((t) => t.templateKey === templateKey);

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
        if (!response.ok) throw new Error(await response.text());
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
      <div>
        <h2 className="text-lg font-semibold text-ink">新建材料草稿</h2>
        <p className="mt-1 text-sm leading-6 text-slate-600">
          选择材料类型，AI 自动填写内容，生成可编辑初稿。
        </p>
      </div>

      {/* captured content preview */}
      {capturedContent && (capturedContent.url || capturedContent.title) && (
        <div className="mt-5 rounded-2xl border border-brand-200 bg-brand-50 p-4">
          <p className="text-xs font-medium uppercase tracking-wider text-brand-700">本次取证来源</p>
          <div className="mt-3 flex gap-4">
            {capturedContent.screenshotBase64 && (
              <Image
                src={capturedContent.screenshotBase64}
                alt="网页截图"
                width={160}
                height={96}
                className="h-24 w-auto rounded-xl border border-brand-200 object-cover"
              />
            )}
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-semibold text-ink">{capturedContent.title || "未命名页面"}</p>
              <p className="mt-1 break-all text-xs text-slate-600">{capturedContent.url}</p>
              {capturedContent.capturedAt && (
                <p className="mt-1 text-xs text-slate-500">
                  取证时间：{new Date(capturedContent.capturedAt).toLocaleString("zh-CN")}
                </p>
              )}
            </div>
          </div>
          {capturedContent.pageText && (
            <p className="mt-3 line-clamp-2 text-xs text-slate-600">
              {capturedContent.pageText.slice(0, 200)}...
            </p>
          )}
        </div>
      )}

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {/* case selector */}
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-700">关联案件编号</span>
          {cases.length > 0 ? (
            <select
              required
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
            >
              <option value="">请选择案件</option>
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </select>
          ) : (
            <input
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
              placeholder="输入案件 ID"
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
            />
          )}
        </label>

        {/* contact override */}
        <label className="space-y-2 text-sm">
          <span className="font-medium text-slate-700">补充变量</span>
          <input
            value={contact}
            onChange={(e) => setContact(e.target.value)}
            placeholder="例如：法务部 / 联系窗口"
            className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-brand-400"
          />
        </label>
      </div>

      {/* template selector */}
      <div className="mt-5 space-y-3">
        <p className="text-sm font-medium text-slate-700">选择文书模板</p>
        {activeCategories.length === 0 ? (
          <p className="text-sm text-slate-400">暂无可用模板，请检查后端服务</p>
        ) : (
          activeCategories.map((cat) => (
            <div key={cat}>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">{cat}</p>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {grouped[cat]?.map((tpl) => {
                  const selected = templateKey === tpl.templateKey;
                  return (
                    <button
                      key={tpl.templateKey}
                      type="button"
                      onClick={() => setTemplateKey(tpl.templateKey)}
                      className={`rounded-2xl border p-4 text-left transition ${
                        selected
                          ? "border-brand-400 bg-brand-50 ring-1 ring-brand-300"
                          : "border-slate-200 bg-white hover:border-brand-200 hover:bg-slate-50"
                      }`}
                    >
                      <p className={`text-sm font-semibold ${selected ? "text-brand-700" : "text-ink"}`}>
                        {tpl.name}
                      </p>
                      <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">{tpl.description}</p>
                      {tpl.outputFormats.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {tpl.outputFormats.map((fmt) => (
                            <span
                              key={fmt}
                              className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500"
                            >
                              {fmt.toUpperCase()}
                            </span>
                          ))}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </div>

      {/* selected template detail */}
      {selectedTemplate && (
        <div className="mt-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm">
          <span className="font-medium text-slate-700">用途：</span>
          <span className="text-slate-600">{selectedTemplate.targetUse}</span>
        </div>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={pending || !templateKey}
          className="rounded-full bg-ink px-5 py-2.5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {pending ? "AI 生成中…" : "生成草稿"}
        </button>
        {message && <p className="text-sm text-rose-600">{message}</p>}
      </div>
    </form>
  );
}
