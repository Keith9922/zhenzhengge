"use client";

import { useCallback, useEffect, useRef, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { Table } from "@tiptap/extension-table";
import { TableRow } from "@tiptap/extension-table-row";
import { TableHeader } from "@tiptap/extension-table-header";
import { TableCell } from "@tiptap/extension-table-cell";
import { Underline } from "@tiptap/extension-underline";
import { TextAlign } from "@tiptap/extension-text-align";
import { Placeholder } from "@tiptap/extension-placeholder";
import { marked } from "marked";
import TurndownService from "turndown";
import { patchProxyJson } from "@/lib/client-api";

// ─── markdown ↔ html conversion ───────────────────────────────────────────────

const turndown = new TurndownService({ headingStyle: "atx", codeBlockStyle: "fenced" });
// preserve table markdown
turndown.addRule("table", {
  filter: ["table"],
  replacement(_content, node) {
    const el = node as HTMLTableElement;
    const rows = Array.from(el.querySelectorAll("tr"));
    if (!rows.length) return "";
    const toRow = (cells: NodeListOf<Element>, sep: string) =>
      `| ${Array.from(cells).map((c) => (c as HTMLElement).textContent?.trim() ?? "").join(" | ")} |${sep}`;
    const header = toRow(rows[0].querySelectorAll("th,td"), "");
    const divider = `| ${Array.from(rows[0].querySelectorAll("th,td")).map(() => "---").join(" | ")} |`;
    const body = rows.slice(1).map((r) => toRow(r.querySelectorAll("td"), "")).join("\n");
    return `\n${header}\n${divider}\n${body}\n`;
  },
});

function markdownToHtml(md: string): string {
  return marked.parse(md, { async: false }) as string;
}

function htmlToMarkdown(html: string): string {
  return turndown.turndown(html);
}

// ─── types ────────────────────────────────────────────────────────────────────

type DraftEditorProps = {
  draftId: string;
  initialContent: string;
};

// ─── toolbar button helpers ────────────────────────────────────────────────────

type IconButtonProps = {
  label: string;
  active?: boolean;
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
};

function ToolbarBtn({ label, active, disabled, onClick, children }: IconButtonProps) {
  return (
    <button
      type="button"
      title={label}
      disabled={disabled}
      onClick={onClick}
      className={`rounded px-2 py-1 text-sm transition-colors select-none disabled:opacity-30 ${
        active
          ? "bg-ink text-white"
          : "text-slate-600 hover:bg-slate-100 hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}

function Sep() {
  return <span className="h-5 w-px self-center bg-slate-200" />;
}

// ─── toolbar ─────────────────────────────────────────────────────────────────

function Toolbar({ editor }: { editor: ReturnType<typeof useEditor> | null }) {
  if (!editor) return null;

  return (
    <div className="flex flex-wrap items-center gap-0.5 border-b border-slate-100 bg-slate-50 px-3 py-2">
      {/* headings */}
      <ToolbarBtn label="标题 1" active={editor.isActive("heading", { level: 1 })} onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}>
        H1
      </ToolbarBtn>
      <ToolbarBtn label="标题 2" active={editor.isActive("heading", { level: 2 })} onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}>
        H2
      </ToolbarBtn>
      <ToolbarBtn label="标题 3" active={editor.isActive("heading", { level: 3 })} onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}>
        H3
      </ToolbarBtn>
      <Sep />
      {/* inline */}
      <ToolbarBtn label="粗体" active={editor.isActive("bold")} onClick={() => editor.chain().focus().toggleBold().run()}>
        <strong>B</strong>
      </ToolbarBtn>
      <ToolbarBtn label="斜体" active={editor.isActive("italic")} onClick={() => editor.chain().focus().toggleItalic().run()}>
        <em>I</em>
      </ToolbarBtn>
      <ToolbarBtn label="下划线" active={editor.isActive("underline")} onClick={() => editor.chain().focus().toggleUnderline().run()}>
        <u>U</u>
      </ToolbarBtn>
      <ToolbarBtn label="行内代码" active={editor.isActive("code")} onClick={() => editor.chain().focus().toggleCode().run()}>
        {"</>"}
      </ToolbarBtn>
      <Sep />
      {/* align */}
      <ToolbarBtn label="左对齐" active={editor.isActive({ textAlign: "left" })} onClick={() => editor.chain().focus().setTextAlign("left").run()}>
        ≡
      </ToolbarBtn>
      <ToolbarBtn label="居中" active={editor.isActive({ textAlign: "center" })} onClick={() => editor.chain().focus().setTextAlign("center").run()}>
        ☰
      </ToolbarBtn>
      <ToolbarBtn label="右对齐" active={editor.isActive({ textAlign: "right" })} onClick={() => editor.chain().focus().setTextAlign("right").run()}>
        ≡
      </ToolbarBtn>
      <Sep />
      {/* lists */}
      <ToolbarBtn label="无序列表" active={editor.isActive("bulletList")} onClick={() => editor.chain().focus().toggleBulletList().run()}>
        • 列表
      </ToolbarBtn>
      <ToolbarBtn label="有序列表" active={editor.isActive("orderedList")} onClick={() => editor.chain().focus().toggleOrderedList().run()}>
        1. 列表
      </ToolbarBtn>
      <ToolbarBtn label="引用块" active={editor.isActive("blockquote")} onClick={() => editor.chain().focus().toggleBlockquote().run()}>
        ❝
      </ToolbarBtn>
      <Sep />
      {/* table */}
      <ToolbarBtn
        label="插入表格"
        onClick={() => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()}
      >
        田 表格
      </ToolbarBtn>
      <ToolbarBtn
        label="在下方插入行"
        disabled={!editor.isActive("table")}
        onClick={() => editor.chain().focus().addRowAfter().run()}
      >
        +行
      </ToolbarBtn>
      <ToolbarBtn
        label="在右侧插入列"
        disabled={!editor.isActive("table")}
        onClick={() => editor.chain().focus().addColumnAfter().run()}
      >
        +列
      </ToolbarBtn>
      <ToolbarBtn
        label="删除表格"
        disabled={!editor.isActive("table")}
        onClick={() => editor.chain().focus().deleteTable().run()}
      >
        删表
      </ToolbarBtn>
      <Sep />
      {/* misc */}
      <ToolbarBtn label="分割线" onClick={() => editor.chain().focus().setHorizontalRule().run()}>
        ─ 分割线
      </ToolbarBtn>
      <ToolbarBtn label="撤销" onClick={() => editor.chain().focus().undo().run()}>
        ↩
      </ToolbarBtn>
      <ToolbarBtn label="重做" onClick={() => editor.chain().focus().redo().run()}>
        ↪
      </ToolbarBtn>
    </div>
  );
}

// ─── main component ───────────────────────────────────────────────────────────

export function DraftEditor({ draftId, initialContent }: DraftEditorProps) {
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [pending, startTransition] = useTransition();
  const savedMarkdownRef = useRef(initialContent);

  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit,
      Underline,
      TextAlign.configure({ types: ["heading", "paragraph"] }),
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
      Placeholder.configure({ placeholder: "请输入草稿内容…" }),
    ],
    content: markdownToHtml(initialContent),
    editorProps: {
      attributes: {
        class: "focus:outline-none",
      },
    },
  });

  // sync when initialContent changes (e.g. after external refresh)
  useEffect(() => {
    if (!editor) return;
    const html = markdownToHtml(initialContent);
    if (editor.getHTML() !== html) {
      editor.commands.setContent(html, { emitUpdate: false });
    }
    savedMarkdownRef.current = initialContent;
    setMessage("");
  }, [editor, initialContent]);

  const getCurrentMarkdown = useCallback(() => {
    if (!editor) return "";
    return htmlToMarkdown(editor.getHTML());
  }, [editor]);

  const dirty = useCallback(() => {
    return getCurrentMarkdown() !== savedMarkdownRef.current;
  }, [getCurrentMarkdown]);

  function saveDraft() {
    const content = getCurrentMarkdown();
    setMessage("");
    startTransition(async () => {
      try {
        const response = await patchProxyJson(`document-drafts/${draftId}`, { content });
        if (!response.ok) throw new Error((await response.text()) || "保存失败");
        savedMarkdownRef.current = content;
        setMessage("草稿已保存");
        router.refresh();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "保存失败");
      }
    });
  }

  async function downloadDocx() {
    setMessage("正在生成 Word 文件…");
    try {
      // First save current content
      const content = getCurrentMarkdown();
      const saveResp = await patchProxyJson(`document-drafts/${draftId}`, { content });
      if (!saveResp.ok) throw new Error("保存失败，无法导出");
      savedMarkdownRef.current = content;

      // Then export → browser downloads the file
      const exportResp = await fetch(`/api/proxy/document-drafts/${draftId}/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      });
      if (!exportResp.ok) throw new Error((await exportResp.text()) || "导出失败");

      const blob = await exportResp.blob();
      const disposition = exportResp.headers.get("content-disposition") ?? "";
      const nameMatch = disposition.match(/filename\*?=(?:UTF-8'')?([^;"\n]+)/i);
      const filename = nameMatch ? decodeURIComponent(nameMatch[1].replace(/"/g, "")) : `${draftId}.docx`;

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setMessage("Word 文件已下载");
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "导出失败");
    }
  }

  return (
    <article className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-sm">
      {/* header */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-8 pt-6 pb-3">
        <h2 className="text-lg font-semibold text-ink">草稿内容</h2>
        <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
          富文本编辑器
        </span>
      </div>

      {/* toolbar */}
      <Toolbar editor={editor} />

      {/* editor area */}
      <div className="tiptap-editor">
        <EditorContent editor={editor!} />
      </div>

      {/* action bar */}
      <div className="flex flex-wrap items-center gap-3 border-t border-slate-100 px-8 py-5">
        <button
          type="button"
          disabled={pending}
          onClick={saveDraft}
          className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {pending ? "保存中…" : "保存草稿"}
        </button>
        <button
          type="button"
          onClick={downloadDocx}
          className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:border-brand-300"
        >
          下载 Word 文档
        </button>
        <button
          type="button"
          onClick={() => {
            if (editor) {
              editor.commands.setContent(markdownToHtml(savedMarkdownRef.current), { emitUpdate: false });
              setMessage("已撤销未保存修改");
            }
          }}
          className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
        >
          撤销修改
        </button>
        {message && <span className="text-sm text-slate-600">{message}</span>}
      </div>
    </article>
  );
}
