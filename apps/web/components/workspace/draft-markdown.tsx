import type { ReactNode } from "react";

type DraftMarkdownProps = {
  content: string;
};

function renderInlineMarkdown(text: string, keyPrefix: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const pattern = /(\*\*([^*]+)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\))/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null = pattern.exec(text);
  let segmentIndex = 0;

  while (match) {
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }

    if (match[2]) {
      nodes.push(
        <strong key={`${keyPrefix}-strong-${segmentIndex}`} className="font-semibold text-ink">
          {match[2]}
        </strong>,
      );
    } else if (match[3]) {
      nodes.push(
        <code
          key={`${keyPrefix}-code-${segmentIndex}`}
          className="rounded-lg bg-slate-100 px-1.5 py-0.5 font-mono text-[0.92em] text-brand-700"
        >
          {match[3]}
        </code>,
      );
    } else if (match[4] && match[5]) {
      nodes.push(
        <a
          key={`${keyPrefix}-link-${segmentIndex}`}
          href={match[5]}
          target="_blank"
          rel="noreferrer"
          className="text-brand-700 underline decoration-brand-200 underline-offset-4 hover:text-brand-800"
        >
          {match[4]}
        </a>,
      );
    }

    lastIndex = pattern.lastIndex;
    segmentIndex += 1;
    match = pattern.exec(text);
  }

  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }

  return nodes;
}

export function DraftMarkdown({ content }: DraftMarkdownProps) {
  const lines = content.replace(/\r\n/g, "\n").split("\n");
  const nodes: ReactNode[] = [];
  let index = 0;

  while (index < lines.length) {
    const currentLine = lines[index];
    const trimmed = currentLine.trim();

    if (!trimmed) {
      index += 1;
      continue;
    }

    if (trimmed.startsWith("```")) {
      const codeLines: string[] = [];
      index += 1;
      while (index < lines.length && !lines[index].trim().startsWith("```")) {
        codeLines.push(lines[index]);
        index += 1;
      }
      index += 1;
      nodes.push(
        <pre
          key={`code-${nodes.length}`}
          className="overflow-x-auto rounded-2xl bg-slate-950 px-4 py-4 text-sm leading-7 text-slate-100"
        >
          <code>{codeLines.join("\n")}</code>
        </pre>,
      );
      continue;
    }

    const headingMatch = trimmed.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const headingText = headingMatch[2];
      const headingClass =
        level === 1
          ? "text-3xl font-semibold tracking-tight text-ink"
          : level === 2
            ? "text-2xl font-semibold text-ink"
            : level === 3
              ? "text-xl font-semibold text-ink"
              : "text-lg font-semibold text-ink";

      nodes.push(
        <div key={`heading-${nodes.length}`} className="pt-2">
          <div className={headingClass}>{renderInlineMarkdown(headingText, `heading-${nodes.length}`)}</div>
        </div>,
      );
      index += 1;
      continue;
    }

    if (/^[-*+]\s+/.test(trimmed)) {
      const items: string[] = [];
      while (index < lines.length && /^[-*+]\s+/.test(lines[index].trim())) {
        items.push(lines[index].trim().replace(/^[-*+]\s+/, ""));
        index += 1;
      }
      nodes.push(
        <ul key={`ul-${nodes.length}`} className="space-y-2 pl-5 text-sm leading-7 text-slate-700">
          {items.map((item, itemIndex) => (
            <li key={`ul-item-${itemIndex}`} className="list-disc break-words">
              {renderInlineMarkdown(item, `ul-${nodes.length}-${itemIndex}`)}
            </li>
          ))}
        </ul>,
      );
      continue;
    }

    if (/^\d+\.\s+/.test(trimmed)) {
      const items: string[] = [];
      while (index < lines.length && /^\d+\.\s+/.test(lines[index].trim())) {
        items.push(lines[index].trim().replace(/^\d+\.\s+/, ""));
        index += 1;
      }
      nodes.push(
        <ol key={`ol-${nodes.length}`} className="space-y-2 pl-5 text-sm leading-7 text-slate-700">
          {items.map((item, itemIndex) => (
            <li key={`ol-item-${itemIndex}`} className="list-decimal break-words">
              {renderInlineMarkdown(item, `ol-${nodes.length}-${itemIndex}`)}
            </li>
          ))}
        </ol>,
      );
      continue;
    }

    if (trimmed.startsWith(">")) {
      const quoteLines: string[] = [];
      while (index < lines.length && lines[index].trim().startsWith(">")) {
        quoteLines.push(lines[index].trim().replace(/^>\s?/, ""));
        index += 1;
      }
      nodes.push(
        <blockquote
          key={`quote-${nodes.length}`}
          className="rounded-r-2xl border-l-4 border-brand-200 bg-brand-50 px-4 py-3 text-sm leading-7 text-slate-700"
        >
          {renderInlineMarkdown(quoteLines.join(" "), `quote-${nodes.length}`)}
        </blockquote>,
      );
      continue;
    }

    if (/^---+$/.test(trimmed)) {
      nodes.push(<hr key={`hr-${nodes.length}`} className="border-slate-200" />);
      index += 1;
      continue;
    }

    const paragraphLines: string[] = [];
    while (index < lines.length) {
      const line = lines[index];
      const lineTrimmed = line.trim();
      if (
        !lineTrimmed ||
        lineTrimmed.startsWith("```") ||
        /^(#{1,6})\s+/.test(lineTrimmed) ||
        /^[-*+]\s+/.test(lineTrimmed) ||
        /^\d+\.\s+/.test(lineTrimmed) ||
        lineTrimmed.startsWith(">") ||
        /^---+$/.test(lineTrimmed)
      ) {
        break;
      }
      paragraphLines.push(lineTrimmed);
      index += 1;
    }

    nodes.push(
      <p key={`p-${nodes.length}`} className="text-sm leading-7 text-slate-700 break-words">
        {renderInlineMarkdown(paragraphLines.join(" "), `p-${nodes.length}`)}
      </p>,
    );
  }

  return <div className="space-y-4 overflow-hidden">{nodes}</div>;
}
