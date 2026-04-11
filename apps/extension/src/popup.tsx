import { useMemo, useState } from "react"
import type { CSSProperties } from "react"

type EvidenceDraft = {
  title: string
  url: string
  capturedAt: string
  source: string
  pageText: string
  rawHtml: string
  screenshotBase64: string
  captureWarnings: string[]
}

type SubmitResult = {
  ok: boolean
  mode: "simulated" | "api"
  message: string
  requestId: string
}

const API_BASE_URL = process.env.PLASMO_PUBLIC_API_BASE_URL?.trim() ?? ""
const INTAKE_PATH = "/api/v1/evidence/intake"

async function getActiveTabDraft(): Promise<EvidenceDraft> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })

  const tabId = tab?.id
  const captureWarnings: string[] = []
  let pageText = ""
  let rawHtml = ""
  let screenshotBase64 = ""

  if (typeof tabId === "number") {
    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId },
        func: () => {
          const bodyText = document.body?.innerText ?? ""
          const html = document.documentElement?.outerHTML ?? ""

          return {
            pageText: bodyText,
            rawHtml: html
          }
        }
      })

      const result = results?.[0]?.result
      pageText = result?.pageText ?? ""
      rawHtml = result?.rawHtml ?? ""
    } catch (error) {
      captureWarnings.push(
        `页面文本采集失败：${error instanceof Error ? error.message : "unknown error"}`
      )
    }

    try {
      screenshotBase64 = await captureVisibleTabBase64()
    } catch (error) {
      captureWarnings.push(
        `可视区截图失败：${error instanceof Error ? error.message : "unknown error"}`
      )
    }
  } else {
    captureWarnings.push("未获取到有效标签页 ID，跳过页面注入和截图采集。")
  }

  return {
    title: tab?.title?.trim() || "未命名页面",
    url: tab?.url?.trim() || "about:blank",
    capturedAt: new Date().toISOString(),
    source: "browser-extension",
    pageText,
    rawHtml,
    screenshotBase64,
    captureWarnings
  }
}

async function captureVisibleTabBase64(): Promise<string> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })

  if (!tab?.windowId && tab?.windowId !== 0) {
    throw new Error("未找到当前窗口，无法截图")
  }

  const screenshot = await chrome.tabs.captureVisibleTab(tab.windowId, {
    format: "png"
  })

  return screenshot ?? ""
}

function buildIntakePayload(draft: EvidenceDraft, requestId: string) {
  return {
    requestId,
    sourceType: "browser-extension",
    sourceUrl: draft.url,
    pageTitle: draft.title,
    capturedAt: draft.capturedAt,
    notes: "通过证证鸽浏览器插件一键取证生成",
    pageText: draft.pageText,
    rawHtml: draft.rawHtml,
    screenshotBase64: draft.screenshotBase64,
    imageUrls: [],
    captureWarnings: draft.captureWarnings
  }
}

async function simulateSubmit(draft: EvidenceDraft): Promise<SubmitResult> {
  const requestId = `zzg_${Date.now()}`
  const payload = buildIntakePayload(draft, requestId)

  if (!API_BASE_URL) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    return {
      ok: true,
      mode: "simulated",
      message: `已模拟提交到后端队列，等待后续 API 接入。当前页面 ${draft.title} 已生成取证草稿。`,
      requestId
    }
  }

  try {
    const response = await fetch(`${API_BASE_URL.replace(/\/$/, "")}${INTAKE_PATH}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    return {
      ok: true,
      mode: "api",
      message: "已提交到后端接口，等待后端生成证据包。",
      requestId
    }
  } catch (error) {
    return {
      ok: true,
      mode: "simulated",
      message: `后端接口暂不可用，已降级为本地模拟提交：${error instanceof Error ? error.message : "unknown error"}`,
      requestId
    }
  }
}

export default function Popup() {
  const [draft, setDraft] = useState<EvidenceDraft | null>(null)
  const [status, setStatus] = useState<string>("尚未开始取证")
  const [requestId, setRequestId] = useState<string>("")
  const [loading, setLoading] = useState(false)

  const capturedLabel = useMemo(() => {
    if (!draft) {
      return "等待取证"
    }

    return new Date(draft.capturedAt).toLocaleString("zh-CN", {
      hour12: false
    })
  }, [draft])

  const screenshotLabel = useMemo(() => {
    if (!draft) {
      return "等待采集"
    }

    return draft.screenshotBase64 ? "已采集可视区截图" : "截图未获取，已降级"
  }, [draft])

  const handleCapture = async () => {
    setLoading(true)
    setStatus("正在采集当前页面信息...")

    try {
      const nextDraft = await getActiveTabDraft()
      setDraft(nextDraft)
      setStatus(
        nextDraft.captureWarnings.length > 0
          ? `页面信息已采集，存在 ${nextDraft.captureWarnings.length} 条降级提示，正在提交...`
          : "页面信息已采集，正在提交..."
      )

      const result = await simulateSubmit(nextDraft)
      setRequestId(result.requestId)
      setStatus(result.message)
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "取证失败")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={styles.shell}>
      <header style={styles.header}>
        <div>
          <p style={styles.kicker}>证证鸽插件</p>
          <h1 style={styles.title}>当前页面一键取证</h1>
        </div>
        <span style={styles.badge}>{API_BASE_URL ? "API 已配置" : "模拟提交模式"}</span>
      </header>

      <p style={styles.description}>
        采集当前标签页的 URL、标题和时间戳，先完成取证草稿，再交给后端工作流处理。
      </p>

      <button disabled={loading} onClick={handleCapture} style={loading ? styles.buttonDisabled : styles.button}>
        {loading ? "处理中..." : "一键取证并提交"}
      </button>

      <section style={styles.card}>
        <div style={styles.row}>
          <span style={styles.label}>页面标题</span>
          <span style={styles.value}>{draft?.title ?? "未采集"}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>页面地址</span>
          <span style={styles.value}>{draft?.url ?? "未采集"}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>采集时间</span>
          <span style={styles.value}>{capturedLabel}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>请求编号</span>
          <span style={styles.value}>{requestId || "未生成"}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>页面正文</span>
          <span style={styles.value}>{draft?.pageText ? "已采集" : "未采集或为空"}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>页面 HTML</span>
          <span style={styles.value}>{draft?.rawHtml ? "已采集" : "未采集或为空"}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>可视区截图</span>
          <span style={styles.value}>{screenshotLabel}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>当前状态</span>
          <span style={styles.value}>{status}</span>
        </div>
      </section>

      {draft?.captureWarnings?.length ? (
        <section style={styles.warningCard}>
          <div style={styles.warningTitle}>降级提示</div>
          <ul style={styles.warningList}>
            {draft.captureWarnings.map((item) => (
              <li key={item} style={styles.warningItem}>
                {item}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <footer style={styles.footer}>
        <span>后续可继续扩展：截图、DOM 抽取、证据压缩包上传。</span>
      </footer>
    </main>
  )
}

const styles: Record<string, CSSProperties> = {
  shell: {
    width: 360,
    minHeight: 420,
    padding: 16,
    boxSizing: "border-box",
    background:
      "radial-gradient(circle at top left, rgba(99, 102, 241, 0.16), transparent 34%), linear-gradient(180deg, #fff 0%, #f8fafc 100%)",
    color: "#0f172a",
    fontFamily:
      'Inter, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", system-ui, sans-serif'
  },
  header: {
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: 12,
    marginBottom: 12
  },
  kicker: {
    margin: 0,
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: "#475569"
  },
  title: {
    margin: "4px 0 0",
    fontSize: 22,
    lineHeight: 1.2
  },
  badge: {
    display: "inline-flex",
    alignItems: "center",
    padding: "6px 10px",
    borderRadius: 999,
    background: "#e0e7ff",
    color: "#4338ca",
    fontSize: 12,
    fontWeight: 600,
    whiteSpace: "nowrap"
  },
  description: {
    margin: "0 0 16px",
    fontSize: 13,
    lineHeight: 1.6,
    color: "#334155"
  },
  button: {
    width: "100%",
    border: "none",
    borderRadius: 14,
    padding: "12px 14px",
    background: "linear-gradient(135deg, #1d4ed8 0%, #4f46e5 100%)",
    color: "#fff",
    fontSize: 14,
    fontWeight: 700,
    cursor: "pointer",
    boxShadow: "0 12px 30px rgba(37, 99, 235, 0.24)"
  },
  buttonDisabled: {
    width: "100%",
    border: "none",
    borderRadius: 14,
    padding: "12px 14px",
    background: "#94a3b8",
    color: "#fff",
    fontSize: 14,
    fontWeight: 700,
    cursor: "not-allowed"
  },
  card: {
    marginTop: 14,
    padding: 14,
    borderRadius: 16,
    background: "rgba(255, 255, 255, 0.85)",
    border: "1px solid rgba(148, 163, 184, 0.24)",
    boxShadow: "0 8px 22px rgba(15, 23, 42, 0.06)"
  },
  row: {
    display: "grid",
    gap: 4,
    marginBottom: 12
  },
  label: {
    fontSize: 12,
    color: "#64748b"
  },
  value: {
    fontSize: 13,
    lineHeight: 1.5,
    color: "#0f172a",
    wordBreak: "break-all"
  },
  footer: {
    marginTop: 14,
    fontSize: 12,
    lineHeight: 1.6,
    color: "#64748b"
  },
  warningCard: {
    marginTop: 12,
    padding: 12,
    borderRadius: 14,
    background: "#fff7ed",
    border: "1px solid rgba(249, 115, 22, 0.22)"
  },
  warningTitle: {
    marginBottom: 8,
    fontSize: 12,
    fontWeight: 700,
    color: "#9a3412"
  },
  warningList: {
    margin: 0,
    paddingLeft: 18,
    color: "#9a3412",
    fontSize: 12,
    lineHeight: 1.6
  },
  warningItem: {
    marginBottom: 6
  }
}
