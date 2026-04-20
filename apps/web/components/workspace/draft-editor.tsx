"use client";

import { useRef, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { patchProxyJson } from "@/lib/client-api";
import { DraftMarkdown } from "@/components/workspace/draft-markdown";

type DraftEditorProps = {
  draftId: string;
  initialContent: string;
};

type EditorMode = "edit" | "preview";

export function DraftEditor({ draftId, initialContent }: DraftEditorProps) {
  const router = useRouter();
  const textAreaRef = useRef<HTMLTextAreaElement | null>(null);
  const [mode, setMode] = useState<EditorMode>("edit");
  const [content, setContent] = useState(initialContent);
  const [savedContent, setSavedContent] = useState(initialContent);
  const [message, setMessage] = useState("");
  const [pending, startTransition] = useTransition();

  const dirty = content !== savedContent;

  function applyReplace(start: number, end: number, replacement: string, selectStart?: number, selectEnd?: number) {
    const next = `${content.slice(0, start)}${replacement}${content.slice(end)}`;
    setContent(next);

    const nextSelectionStart = selectStart ?? start;
    const nextSelectionEnd = selectEnd ?? start + replacement.length;

    requestAnimationFrame(() => {
      const element = textAreaRef.current;
      if (!element) {
        return;
      }
      element.focus();
      element.setSelectionRange(nextSelectionStart, nextSelectionEnd);
    });
  }

  function prefixLines(prefix: string, numbered = false) {
    const element = textAreaRef.current;
    if (!element) {
      return;
    }

    const start = element.selectionStart;
    const end = element.selectionEnd;
    const lineStart = content.lastIndexOf("\n", Math.max(0, start - 1)) + 1;
    const lineEndIndex = content.indexOf("\n", end);
    const lineEnd = lineEndIndex === -1 ? content.length : lineEndIndex;

    const segment = content.slice(lineStart, lineEnd);
    const lines = segment.split("\n");
    const replaced = lines
      .map((line, index) => {
        if (!line.trim()) {
          return line;
        }

        if (numbered) {
          return `${index + 1}. ${line}`;
        }

        return `${prefix}${line}`;
      })
      .join("\n");

    applyReplace(lineStart, lineEnd, replaced, lineStart, lineStart + replaced.length);
  }

  function wrapSelection(before: string, after: string) {
    const element = textAreaRef.current;
    if (!element) {
      return;
    }

    const start = element.selectionStart;
    const end = element.selectionEnd;
    const selected = content.slice(start, end);
    const replacement = selected ? `${before}${selected}${after}` : `${before}${after}`;

    const cursorStart = selected ? start + before.length : start + before.length;
    const cursorEnd = selected ? start + before.length + selected.length : cursorStart;

    applyReplace(start, end, replacement, cursorStart, cursorEnd);
  }

  function insertCodeBlock() {
    const element = textAreaRef.current;
    if (!element) {
      return;
    }

    const start = element.selectionStart;
    const end = element.selectionEnd;
    const selected = content.slice(start, end);
    const replacement = selected ? `\n\`\`\`\n${selected}\n\`\`\`\n` : "\n```\n在这里输入代码\n```\n";
    const cursorStart = selected ? start + 5 : start + 5;
    const cursorEnd = selected ? start + 5 + selected.length : start + 11;

    applyReplace(start, end, replacement, cursorStart, cursorEnd);
  }

  function saveDraft() {
    setMessage("");
    startTransition(async () => {
      try {
        const response = await patchProxyJson(`document-drafts/${draftId}`, { content });
        if (!response.ok) {
          const detail = await response.text();
          throw new Error(detail || "保存失败");
        }

        const payload = (await response.json()) as { content?: string; item?: { content?: string } };
        const nextContent = payload.item?.content ?? payload.content ?? content;
        setContent(nextContent);
        setSavedContent(nextContent);
        setMessage("草稿已保存");
        router.refresh();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "保存失败");
      }
    });
  }

  return (
    <article className="min-w-0 overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-ink">草稿内容</h2>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setMode("edit")}
            className={`rounded-full px-3 py-1 text-xs font-medium ${mode === "edit" ? "bg-ink text-white" : "bg-slate-100 text-slate-700"}`}
          >
            编辑
          </button>
          <button
            type="button"
            onClick={() => setMode("preview")}
            className={`rounded-full px-3 py-1 text-xs font-medium ${mode === "preview" ? "bg-ink text-white" : "bg-slate-100 text-slate-700"}`}
          >
            预览
          </button>
        </div>
      </div>

      {mode === "edit" ? (
        <>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => prefixLines("# ")}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700"
            >
              标题1
            </button>
            <button
              type="button"
              onClick={() => prefixLines("## ")}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700"
            >
              标题2
            </button>
            <button
              type="button"
              onClick={() => prefixLines("- ")}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700"
            >
              无序列表
            </button>
            <button
              type="button"
              onClick={() => prefixLines("", true)}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700"
            >
              有序列表
            </button>
            <button
              type="button"
              onClick={() => prefixLines("> ")}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700"
            >
              引用
            </button>
            <button
              type="button"
              onClick={insertCodeBlock}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700"
            >
              代码块
            </button>
            <button
              type="button"
              onClick={() => wrapSelection("**", "**")}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700"
            >
              加粗
            </button>
            <button
              type="button"
              onClick={() => wrapSelection("`", "`")}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700"
            >
              行内代码
            </button>
          </div>

          <textarea
            ref={textAreaRef}
            value={content}
            onChange={(event) => setContent(event.target.value)}
            rows={18}
            className="mt-4 w-full rounded-3xl border border-slate-300 bg-slate-50 px-5 py-4 text-sm leading-7 text-slate-800 outline-none transition focus:border-brand-400"
            placeholder="请输入草稿内容"
          />
        </>
      ) : (
        <div className="mt-4 overflow-hidden rounded-3xl border border-slate-200 bg-slate-50 p-5">
          <DraftMarkdown content={content} />
        </div>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button
          type="button"
          disabled={!dirty || pending}
          onClick={saveDraft}
          className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          {pending ? "保存中…" : "保存草稿"}
        </button>
        <button
          type="button"
          disabled={!dirty || pending}
          onClick={() => {
            setContent(savedContent);
            setMessage("已撤销未保存修改");
          }}
          className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-60"
        >
          撤销修改
        </button>
        <p className="text-sm text-slate-500">{dirty ? "有未保存变更" : "内容已同步"}</p>
      </div>

      {message ? <p className="mt-3 text-sm text-slate-600">{message}</p> : null}
    </article>
  );
}
