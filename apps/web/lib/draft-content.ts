// ─── types ────────────────────────────────────────────────────────────────────

export type EvidenceReference = {
  evidenceId: string;
  lineNo: number;
  text: string;
};

// ─── internal helpers ─────────────────────────────────────────────────────────

const BLOCK_HTML_TAG_PATTERN =
  /<(?:p|div|h[1-6]|ul|ol|li|blockquote|br|hr|pre|strong|b|em|i|u|a|span)\b/i;

function decodeHtmlEntities(value: string) {
  return value
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'");
}

function normalizeNewlines(value: string) {
  return value.replace(/\r\n/g, "\n");
}

// ─── public helpers ───────────────────────────────────────────────────────────

/**
 * 判断内容是否为 HTML（旧版编辑器遗留格式）。
 */
export function looksLikeHtmlContent(content: string) {
  return BLOCK_HTML_TAG_PATTERN.test(content.trim());
}

/**
 * 将内容中的 HTML 标签剥离后，提取纯文本行（保留换行结构）。
 * 仅用于旧版 HTML 内容的兼容处理。
 */
export function contentToEvidenceLines(content: string) {
  if (!looksLikeHtmlContent(content)) {
    return normalizeNewlines(content);
  }

  const withLines = normalizeNewlines(content)
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/(?:p|div|li|blockquote|h[1-6]|ul|ol|pre)>/gi, "\n")
    .replace(/<[^>]+>/g, " ");

  return decodeHtmlEntities(withLines)
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n[ \t]+/g, "\n")
    .replace(/[ \t]{2,}/g, " ");
}

/**
 * 将草稿初始内容规范化为纯 Markdown 字符串。
 *
 * - 若内容为旧版 HTML（contentEditable 遗留），先剥离标签取纯文本。
 * - 若内容已是 Markdown，直接清理多余空行并 trim。
 * - 结果直接放入 <textarea> 编辑，保证所见即所存。
 */
export function normalizeInitialContent(content: string): string {
  const raw = (content ?? "").trim();
  if (!raw) return "";

  if (looksLikeHtmlContent(raw)) {
    // 旧版 HTML 内容：剥离标签，还原纯文本/简单 Markdown
    return contentToEvidenceLines(raw)
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  // 已是 Markdown：只做换行规范化
  return normalizeNewlines(raw)
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

// ─── evidence reference extraction ───────────────────────────────────────────

/**
 * 从草稿内容中提取所有 `EvidenceID=xxx` 引用，返回行号与上下文。
 * 同时兼容 Markdown 与旧版 HTML 内容。
 */
export function extractEvidenceReferences(content: string): EvidenceReference[] {
  const pattern = /EvidenceID\s*=\s*([A-Za-z0-9_-]+)/g;
  const lines = contentToEvidenceLines(content).split("\n");
  const refs: EvidenceReference[] = [];

  lines.forEach((line, index) => {
    const matches = [...line.matchAll(pattern)];
    matches.forEach((match) => {
      const evidenceId = match[1];
      if (!evidenceId) return;
      refs.push({
        evidenceId,
        lineNo: index + 1,
        text: line.trim().slice(0, 240),
      });
    });
  });

  return refs;
}
