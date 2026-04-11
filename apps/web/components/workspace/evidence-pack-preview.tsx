import type { EvidencePackListItem } from "@/lib/evidence-packs";

function buildHtmlSnippet(item: EvidencePackListItem) {
  if (item.htmlSnippet) {
    return item.htmlSnippet;
  }

  return [
    `<article class="evidence-card" data-source="${item.source}">`,
    `  <header>`,
    `    <h1>${item.title}</h1>`,
    `    <p>来源：${item.source}</p>`,
    `    <time>${item.capturedAt}</time>`,
    `  </header>`,
    `  <section>`,
    `    <p>${item.summary}</p>`,
    `  </section>`,
    `</article>`,
  ].join("\n");
}

type EvidencePackPreviewProps = {
  item: EvidencePackListItem;
};

export function EvidencePackPreview({ item }: EvidencePackPreviewProps) {
  const htmlSnippet = buildHtmlSnippet(item);

  return (
    <div className="grid gap-6 lg:grid-cols-[1.12fr_0.88fr]">
      <article className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-ink">截图预览</h2>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
            {item.screenshotAvailable ? "已采集预览" : "预览占位"}
          </span>
        </div>
        <div className="mt-4 overflow-hidden rounded-[1.75rem] border border-slate-200 bg-slate-950 p-4 text-white shadow-inner">
          <div className="flex items-center gap-2 border-b border-white/10 pb-3">
            <span className="h-2.5 w-2.5 rounded-full bg-rose-400" />
            <span className="h-2.5 w-2.5 rounded-full bg-amber-300" />
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-300" />
            <span className="ml-2 text-xs text-white/60">页面截图预览</span>
          </div>
          {item.screenshotUrl ? (
            <div className="mt-4 overflow-hidden rounded-[1.5rem] bg-slate-900 ring-1 ring-white/10">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={item.screenshotUrl} alt={item.title} className="h-auto w-full object-cover" />
            </div>
          ) : (
            <div className="mt-4 rounded-[1.5rem] bg-gradient-to-br from-slate-800 via-slate-900 to-slate-950 p-5 ring-1 ring-white/10">
              <p className="text-[11px] uppercase tracking-[0.28em] text-cyan-200/80">Captured evidence</p>
              <h3 className="mt-3 text-xl font-semibold leading-8">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-200">{item.summary}</p>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl bg-white/10 px-4 py-3">
                  <p className="text-xs text-slate-300">来源</p>
                  <p className="mt-1 text-sm font-medium text-white">{item.source}</p>
                </div>
                <div className="rounded-2xl bg-white/10 px-4 py-3">
                  <p className="text-xs text-slate-300">采集时间</p>
                  <p className="mt-1 text-sm font-medium text-white">{item.capturedAt}</p>
                </div>
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                {item.artifactPaths.length ? (
                  item.artifactPaths.map((path) => (
                    <span key={path} className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-100">
                      {path}
                    </span>
                  ))
                ) : (
                  <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-100">待接入真实文件</span>
                )}
              </div>
            </div>
          )}
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-500">
          这里展示证据截图预览；如果后端未返回真实截图，会自动显示占位版式，避免空白页。
        </p>
      </article>

      <article className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-ink">HTML 文本片段</h2>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
            {item.htmlAvailable ? "已归档" : "预览占位"}
          </span>
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          这里展示结构化 HTML 文本片段，便于核对页面标题、来源信息和正文要点。
        </p>
        <pre className="mt-4 overflow-x-auto rounded-[1.75rem] border border-slate-200 bg-slate-950 p-5 text-sm leading-7 text-slate-100">
          {htmlSnippet}
        </pre>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {item.screenshotDownloadUrl ? (
            <a
              href={item.screenshotDownloadUrl}
              className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700"
            >
              下载截图
            </a>
          ) : (
            <button
              type="button"
              className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-500"
              disabled
            >
              截图下载待接入
            </button>
          )}
          {item.htmlDownloadUrl ? (
            <a
              href={item.htmlDownloadUrl}
              className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700"
            >
              下载 HTML
            </a>
          ) : (
            <button
              type="button"
              className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-500"
              disabled
            >
              HTML 下载待接入
            </button>
          )}
        </div>
        {!item.htmlDownloadUrl || !item.screenshotDownloadUrl ? (
          <div className="mt-4 rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm leading-6 text-slate-600">
            当前证据包未返回全部文件下载能力，页面会保留占位，避免误导为真实可下载。
          </div>
        ) : null}
      </article>
    </div>
  );
}
