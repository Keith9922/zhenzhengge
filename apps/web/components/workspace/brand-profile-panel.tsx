"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import type { BrandProfile, BrandProfileCreatePayload } from "@/lib/brand-profiles";
import { createBrandProfile, deleteBrandProfile, updateBrandProfile, suggestConfusable } from "@/lib/brand-profiles";

type Props = { items: BrandProfile[] };

const EMPTY_FORM: BrandProfileCreatePayload = {
  brand_name: "",
  trademark_classes: [],
  trademark_numbers: [],
  confusable_terms: [],
  protection_keywords: [],
};

function TagInput({
  label,
  values,
  onChange,
  placeholder,
}: {
  label: string;
  values: string[];
  onChange: (v: string[]) => void;
  placeholder?: string;
}) {
  const [input, setInput] = useState("");
  function add() {
    const trimmed = input.trim();
    if (trimmed && !values.includes(trimmed)) onChange([...values, trimmed]);
    setInput("");
  }
  return (
    <div>
      <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
      <div className="flex flex-wrap gap-1 mb-2 min-h-[28px]">
        {values.map((v) => (
          <span
            key={v}
            className="inline-flex items-center gap-1 rounded-full bg-brand-50 px-2 py-0.5 text-xs text-brand-700"
          >
            {v}
            <button
              type="button"
              onClick={() => onChange(values.filter((x) => x !== v))}
              className="hover:text-rose-600 leading-none"
            >
              ×
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), add())}
          placeholder={placeholder ?? "输入后按 Enter 添加"}
          className="flex-1 rounded-xl border border-slate-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-300"
        />
        <button
          type="button"
          onClick={add}
          className="rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          添加
        </button>
      </div>
    </div>
  );
}

export function BrandProfilePanel({ items }: Props) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [msg, setMsg] = useState({ text: "", ok: true });
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<BrandProfileCreatePayload>(EMPTY_FORM);
  const [suggestingId, setSuggestingId] = useState<string | null>(null);

  function resetForm() {
    setForm(EMPTY_FORM);
    setShowForm(false);
    setEditingId(null);
  }

  function startEdit(p: BrandProfile) {
    setForm({
      brand_name: p.brand_name,
      trademark_classes: p.trademark_classes,
      trademark_numbers: p.trademark_numbers,
      confusable_terms: p.confusable_terms,
      protection_keywords: p.protection_keywords,
    });
    setEditingId(p.profile_id);
    setShowForm(true);
  }

  function handleDelete(profileId: string, brandName: string) {
    if (!confirm(`确认删除品牌档案「${brandName}」？`)) return;
    startTransition(async () => {
      const ok = await deleteBrandProfile(profileId);
      setMsg({ text: ok ? "已删除" : "删除失败", ok });
      if (ok) router.refresh();
    });
  }

  function handleSuggest(p: BrandProfile) {
    setSuggestingId(p.profile_id);
    startTransition(async () => {
      const suggestions = await suggestConfusable(p.profile_id);
      setSuggestingId(null);
      if (!suggestions.length) {
        setMsg({ text: "未生成建议，请检查 LLM 配置", ok: false });
        return;
      }
      // merge into existing confusable_terms without duplicates
      const merged = Array.from(new Set([...p.confusable_terms, ...suggestions]));
      const updated = await updateBrandProfile(p.profile_id, { confusable_terms: merged });
      setMsg({ text: updated ? `AI 已生成 ${suggestions.length} 个近似词建议并合并` : "更新失败", ok: !!updated });
      if (updated) router.refresh();
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.brand_name.trim()) return;
    startTransition(async () => {
      if (editingId) {
        const updated = await updateBrandProfile(editingId, form);
        setMsg({ text: updated ? "已更新" : "更新失败", ok: !!updated });
        if (updated) { resetForm(); router.refresh(); }
      } else {
        const created = await createBrandProfile(form);
        setMsg({ text: created ? "品牌档案已创建" : "创建失败", ok: !!created });
        if (created) { resetForm(); router.refresh(); }
      }
    });
  }

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-ink">品牌权利档案</h2>
          <p className="mt-1 text-sm leading-6 text-slate-600">
            登记品牌商标信息，系统据此自动匹配采集线索的品牌方并优化风险评分。
          </p>
        </div>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="shrink-0 rounded-full border border-brand-600 bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            + 新增品牌
          </button>
        )}
      </div>

      {msg.text && (
        <p className={`mt-3 text-sm ${msg.ok ? "text-emerald-700" : "text-rose-700"}`}>{msg.text}</p>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-5 space-y-4">
          <p className="text-sm font-semibold text-slate-700">{editingId ? "编辑品牌档案" : "新增品牌档案"}</p>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">品牌名称 *</label>
            <input
              required
              value={form.brand_name}
              onChange={(e) => setForm((f) => ({ ...f, brand_name: e.target.value }))}
              placeholder="例：奥利奥 / OREO"
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-300"
            />
          </div>

          <TagInput
            label="商标注册类别（国际分类）"
            values={form.trademark_classes}
            onChange={(v) => setForm((f) => ({ ...f, trademark_classes: v }))}
            placeholder="例：第30类  按 Enter 添加"
          />

          <TagInput
            label="商标注册号"
            values={form.trademark_numbers}
            onChange={(v) => setForm((f) => ({ ...f, trademark_numbers: v }))}
            placeholder="例：1234567  按 Enter 添加"
          />

          <TagInput
            label="保护关键词（用于监控和风险评分命中）"
            values={form.protection_keywords}
            onChange={(v) => setForm((f) => ({ ...f, protection_keywords: v }))}
            placeholder="例：奥利奥、OREO、夹心饼干"
          />

          <TagInput
            label="形近/混淆词（可先保存后点 AI 生成）"
            values={form.confusable_terms}
            onChange={(v) => setForm((f) => ({ ...f, confusable_terms: v }))}
            placeholder="例：奥利悦、奥力奥、OLEIO"
          />

          <div className="flex gap-3 pt-1">
            <button
              type="submit"
              disabled={pending}
              className="rounded-full bg-brand-600 px-5 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {pending ? "保存中…" : "保存"}
            </button>
            <button
              type="button"
              onClick={resetForm}
              className="rounded-full border border-slate-300 bg-white px-5 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              取消
            </button>
          </div>
        </form>
      )}

      <div className="mt-5 space-y-3">
        {items.length === 0 && !showForm && (
          <p className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-500 text-center">
            暂无品牌档案，点击「新增品牌」开始登记
          </p>
        )}
        {items.map((p) => (
          <article key={p.profile_id} className="rounded-2xl border border-slate-200 bg-white p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-semibold text-ink">{p.brand_name}</p>
                {p.trademark_classes.length > 0 && (
                  <p className="mt-0.5 text-xs text-slate-500">
                    类别：{p.trademark_classes.join("、")}
                    {p.trademark_numbers.length > 0 && `　注册号：${p.trademark_numbers.join("、")}`}
                  </p>
                )}
              </div>
              <div className="flex gap-2 shrink-0">
                <button
                  onClick={() => handleSuggest(p)}
                  disabled={pending && suggestingId === p.profile_id}
                  className="rounded-full border border-violet-300 bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700 hover:bg-violet-100 disabled:opacity-50"
                >
                  {suggestingId === p.profile_id ? "生成中…" : "AI 生成近似词"}
                </button>
                <button
                  onClick={() => startEdit(p)}
                  className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                >
                  编辑
                </button>
                <button
                  onClick={() => handleDelete(p.profile_id, p.brand_name)}
                  className="rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-xs font-medium text-rose-700 hover:bg-rose-100"
                >
                  删除
                </button>
              </div>
            </div>

            {p.protection_keywords.length > 0 && (
              <div className="mt-3">
                <p className="text-xs text-slate-500 mb-1">保护关键词</p>
                <div className="flex flex-wrap gap-1">
                  {p.protection_keywords.map((kw) => (
                    <span key={kw} className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs text-emerald-700">{kw}</span>
                  ))}
                </div>
              </div>
            )}

            {p.confusable_terms.length > 0 && (
              <div className="mt-2">
                <p className="text-xs text-slate-500 mb-1">形近 / 混淆词</p>
                <div className="flex flex-wrap gap-1">
                  {p.confusable_terms.map((t) => (
                    <span key={t} className="rounded-full bg-amber-50 px-2 py-0.5 text-xs text-amber-700">{t}</span>
                  ))}
                </div>
              </div>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}
