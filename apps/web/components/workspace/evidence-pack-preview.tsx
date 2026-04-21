import type { EvidencePackListItem } from "@/lib/evidence-packs";

type EvidencePackPreviewProps = {
  item: EvidencePackListItem;
};

function TimestampBadge({ status }: { status?: string }) {
  if (status === "stamped") {
    return (
      <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">
        时间戳：已签发
      </span>
    );
  }
  if (status === "hash_only") {
    return (
      <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">
        时间戳：哈希存证
      </span>
    );
  }
  return (
    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500">
      时间戳：未存证
    </span>
  );
}

export function EvidencePackPreview({ item }: EvidencePackPreviewProps) {
  const isHashOnly = item.timestampStatus === "hash_only";
  const isStamped = item.timestampStatus === "stamped";

  return (
    <div className="space-y-6">
      <article className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-ink">截图预览</h2>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
            {item.screenshotAvailable ? "已采集预览" : "暂无截图归档"}
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
              <div className="max-h-[42rem] overflow-auto overscroll-contain">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={item.screenshotUrl} alt={item.title} className="block h-auto w-full object-contain object-top" />
              </div>
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
                  <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-100">暂无归档文件</span>
                )}
              </div>
            </div>
          )}
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-500">
          这里仅保留受约束的预览窗口，避免整页截图把版面撑开；如需核对完整原图，请直接下载截图文件。
        </p>
      </article>

      <article className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-ink">原始文件下载</h2>
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
              截图：{item.screenshotAvailable ? "已归档" : "未归档"}
            </span>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
              HTML：{item.htmlAvailable ? "已归档" : "未归档"}
            </span>
            <TimestampBadge status={item.timestampStatus} />
          </div>
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          HTML 文本片段不再直接铺在页面里，避免干扰主视图；如需核对原始页面内容，请通过下面的下载入口查看。
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
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
              截图暂不可下载
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
              HTML 暂不可下载
            </button>
          )}
          {isStamped && item.timestampDownloadUrl ? (
            <a
              href={item.timestampDownloadUrl}
              className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700"
            >
              下载时间戳回执
            </a>
          ) : (
            <button
              type="button"
              className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-500"
              disabled
            >
              {isHashOnly ? "哈希存证（无回执文件）" : "时间戳回执暂不可下载"}
            </button>
          )}
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">截图文件</p>
            <p className="mt-2 break-all text-sm leading-6 text-slate-700">{item.snapshotPath || "未归档截图文件"}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">HTML 文件</p>
            <p className="mt-2 break-all text-sm leading-6 text-slate-700">{item.htmlPath || "未归档 HTML 文件"}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              {isHashOnly ? "哈希链存证" : "时间戳回执"}
            </p>
            {isHashOnly ? (
              <>
                <p className="mt-2 break-all font-mono text-xs leading-5 text-slate-600">{item.timestampTokenPath || "—"}</p>
                <p className="mt-2 text-xs leading-5 text-slate-500">本地 SHA-256 哈希链，证明内容完整性</p>
                {item.timestampAt ? <p className="mt-1 text-xs text-slate-400">存证时间：{item.timestampAt}</p> : null}
              </>
            ) : (
              <>
                <p className="mt-2 break-all text-sm leading-6 text-slate-700">{item.timestampTokenPath || "未生成时间戳回执"}</p>
                {item.timestampAt ? <p className="mt-1 text-xs text-slate-500">签发时间：{item.timestampAt}</p> : null}
                {item.timestampMessage ? <p className="mt-1 text-xs text-slate-500">状态：{item.timestampMessage}</p> : null}
              </>
            )}
          </div>
        </div>
        {!item.htmlDownloadUrl || !item.screenshotDownloadUrl ? (
          <div className="mt-4 rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm leading-6 text-slate-600">
            当前证据包未返回全部文件下载能力，页面保留占位，避免误导为真实可下载。
          </div>
        ) : null}
      </article>
    </div>
  );
}
