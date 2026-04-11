import { useMemo, useState } from "react"
import type { CSSProperties } from "react"

type EvidenceDraft = {
  title: string
  url: string
  capturedAt: string
  source: string
}

type SubmitResult = {
  ok: boolean
  mode: "simulated" | "api"
  message: string
  requestId: string
}

const API_BASE_URL = process.env.PLASMO_PUBLIC_API_BASE_URL?.trim() ?? ""

async function getActiveTabDraft(): Promise<EvidenceDraft> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })

  return {
    title: tab?.title?.trim() || "未命名页面",
    url: tab?.url?.trim() || "about:blank",
    capturedAt: new Date().toISOString(),
    source: "browser-extension"
  }
}

async function simulateSubmit(draft: EvidenceDraft): Promise<SubmitResult> {
  const requestId = `zzg_${Date.now()}`

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
    const response = await fetch(`${API_BASE_URL.replace(/\/$/, "")}/evidence/intake`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ...draft,
        requestId
      })
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

  const handleCapture = async () => {
    setLoading(true)
    setStatus("正在采集当前页面信息...")

    try {
      const nextDraft = await getActiveTabDraft()
      setDraft(nextDraft)
      setStatus("页面信息已采集，正在模拟提交...")

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
          <span style={styles.label}>当前状态</span>
          <span style={styles.value}>{status}</span>
        </div>
      </section>

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
  }
}
