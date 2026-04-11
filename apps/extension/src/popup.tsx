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
  mode: "development" | "api"
  message: string
  requestId: string
  caseId: string
  evidencePackId: string
  workbenchUrl: string
}

const API_BASE_URL = process.env.PLASMO_PUBLIC_API_BASE_URL?.trim() ?? ""
const WEB_BASE_URL = process.env.PLASMO_PUBLIC_WEB_BASE_URL?.trim() ?? ""
const IS_PRODUCTION = process.env.NODE_ENV === "production"
const ALLOW_SIMULATED_SUBMISSION =
  process.env.PLASMO_PUBLIC_ALLOW_SIMULATED_SUBMISSION?.trim() === "true" || !IS_PRODUCTION
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
    source: "browser-extension",
    url: draft.url,
    title: draft.title,
    capturedAt: draft.capturedAt,
    notes: "通过证证鸽浏览器插件一键取证生成",
    pageText: draft.pageText,
    html: draft.rawHtml,
    screenshotBase64: draft.screenshotBase64,
    imageUrls: [],
    captureWarnings: draft.captureWarnings
  }
}

function parseIntakeResponse(responseBody: unknown) {
  if (!responseBody || typeof responseBody !== "object") {
    throw new Error("后端返回为空，无法解析 intake 契约")
  }

  const body = responseBody as {
    case?: { case_id?: string }
    evidence_pack?: { evidence_pack_id?: string }
  }
  const caseId = body.case?.case_id?.trim() ?? ""
  const evidencePackId = body.evidence_pack?.evidence_pack_id?.trim() ?? ""

  if (!caseId || !evidencePackId) {
    throw new Error("后端返回结构不符合 intake 契约，应包含 case.case_id 和 evidence_pack.evidence_pack_id")
  }

  return { caseId, evidencePackId }
}

async function submitEvidence(draft: EvidenceDraft): Promise<SubmitResult> {
  const requestId = `zzg_${Date.now()}`
  const payload = buildIntakePayload(draft, requestId)

  if (!API_BASE_URL) {
    if (!ALLOW_SIMULATED_SUBMISSION) {
      throw new Error("正式模式未配置后端 API_BASE_URL，无法提交取证")
    }

    await new Promise((resolve) => setTimeout(resolve, 500))
    return {
      ok: true,
      mode: "development",
      message: `【开发模式】当前页面 ${draft.title} 已生成本地取证草稿，未实际发送到后端。`,
      requestId,
      caseId: "",
      evidencePackId: "",
      workbenchUrl: ""
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

    const responseBody = await response.json().catch(() => null)
    const { caseId, evidencePackId } = parseIntakeResponse(responseBody)
    const workbenchUrl = WEB_BASE_URL
      ? `${WEB_BASE_URL.replace(/\/$/, "")}/workspace/cases/${encodeURIComponent(
          caseId
        )}`
      : ""

    return {
      ok: true,
      mode: "api",
      message: "【正式模式】当前页面已完成提交，可继续在工作台查看取证记录。",
      requestId,
      caseId,
      evidencePackId,
      workbenchUrl
    }
  } catch (error) {
    if (ALLOW_SIMULATED_SUBMISSION) {
      await new Promise((resolve) => setTimeout(resolve, 500))
      return {
        ok: true,
        mode: "development",
        message: `【开发模式】后端提交失败，已转为本地模拟提交：${
          error instanceof Error ? error.message : "unknown error"
        }`,
        requestId,
        caseId: "",
        evidencePackId: "",
        workbenchUrl: ""
      }
    }

    return {
      ok: false,
      mode: "api",
      message: `取证提交失败：${error instanceof Error ? error.message : "unknown error"}`,
      requestId,
      caseId: "",
      evidencePackId: "",
      workbenchUrl: ""
    }
  }
}

export default function Popup() {
  const [draft, setDraft] = useState<EvidenceDraft | null>(null)
  const [status, setStatus] = useState<string>("尚未开始取证")
  const [requestId, setRequestId] = useState<string>("")
  const [caseId, setCaseId] = useState<string>("")
  const [evidencePackId, setEvidencePackId] = useState<string>("")
  const [workbenchUrl, setWorkbenchUrl] = useState<string>("")
  const [submissionMode, setSubmissionMode] = useState<string>("未提交")
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

      const result = await submitEvidence(nextDraft)
      setRequestId(result.requestId)
      setCaseId(result.caseId)
      setEvidencePackId(result.evidencePackId)
      setWorkbenchUrl(result.workbenchUrl)
      setSubmissionMode(result.mode === "api" ? "正式模式" : "开发模式")
      setStatus(result.message)
    } catch (error) {
      setSubmissionMode("失败")
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
        <span style={styles.badge}>取证助手</span>
      </header>

      <p style={styles.description}>
        采集当前标签页的页面信息与截图，先完成取证留存，再继续进入工作台整理案件材料。
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
          <span style={styles.label}>取证编号</span>
          <span style={styles.value}>{requestId || "未生成"}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>提交模式</span>
          <span style={styles.value}>{submissionMode}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>案件编号</span>
          <span style={styles.value}>{caseId || "待生成"}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>证据包编号</span>
          <span style={styles.value}>{evidencePackId || "待生成"}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>页面正文</span>
          <span style={styles.value}>
            {draft?.pageText ? `已采集（${draft.pageText.length} 字）` : "未采集或为空"}
          </span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>页面 HTML</span>
          <span style={styles.value}>
            {draft?.rawHtml ? `已采集（${draft.rawHtml.length} 字符）` : "未采集或为空"}
          </span>
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

      {draft?.screenshotBase64 ? (
        <section style={styles.card}>
          <div style={styles.previewHeader}>
            <div style={styles.previewTitle}>截图预览</div>
            <div style={styles.previewMeta}>当前页面可视区</div>
          </div>
          <img alt="当前页面截图预览" src={draft.screenshotBase64} style={styles.previewImage} />
        </section>
      ) : null}

      {caseId && evidencePackId ? (
        <section style={styles.successCard}>
          <div style={styles.successTitle}>取证提交成功</div>
          <p style={styles.successText}>
            当前页面已经生成案件与证据包，后续可以直接进入工作台继续查看证据、草稿和处理进展。
          </p>
        </section>
      ) : null}

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

      {workbenchUrl ? (
        <a href={workbenchUrl} target="_blank" rel="noreferrer" style={styles.linkButton}>
          打开案件详情
        </a>
      ) : submissionMode === "development" && WEB_BASE_URL ? (
        <div style={styles.devHint}>开发模式下未生成真实案件链接，可在后端接通后继续查看。</div>
      ) : null}

      <footer style={styles.footer}>
        <span>建议完成当前页面取证后，进入工作台继续查看证据与处理进展。</span>
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
  successCard: {
    marginTop: 12,
    padding: 12,
    borderRadius: 14,
    background: "#ecfdf5",
    border: "1px solid rgba(16, 185, 129, 0.22)"
  },
  successTitle: {
    marginBottom: 6,
    fontSize: 12,
    fontWeight: 700,
    color: "#047857"
  },
  successText: {
    margin: 0,
    fontSize: 12,
    lineHeight: 1.6,
    color: "#065f46"
  },
  previewHeader: {
    display: "flex",
    alignItems: "baseline",
    justifyContent: "space-between",
    gap: 12,
    marginBottom: 10
  },
  previewTitle: {
    fontSize: 12,
    fontWeight: 700,
    color: "#0f172a"
  },
  previewMeta: {
    fontSize: 12,
    color: "#64748b"
  },
  previewImage: {
    display: "block",
    width: "100%",
    maxHeight: 180,
    objectFit: "cover",
    borderRadius: 12,
    border: "1px solid rgba(148, 163, 184, 0.24)",
    background: "#f8fafc"
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
  },
  linkButton: {
    display: "inline-flex",
    justifyContent: "center",
    alignItems: "center",
    width: "100%",
    marginTop: 12,
    padding: "12px 14px",
    borderRadius: 14,
    background: "#0f766e",
    color: "#fff",
    fontSize: 14,
    fontWeight: 700,
    textDecoration: "none",
    boxSizing: "border-box"
  },
  devHint: {
    marginTop: 12,
    padding: "10px 12px",
    borderRadius: 14,
    background: "#eff6ff",
    border: "1px solid rgba(59, 130, 246, 0.18)",
    color: "#1d4ed8",
    fontSize: 12,
    lineHeight: 1.6
  }
}
