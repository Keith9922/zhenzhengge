## 3. 后端架构与 Hermes Agent

### 3.1 后端不是单接口集合，而是一个可编排的工作流底座

当前后端采用 `FastAPI + SQLite + PlaywrightWorker + NotificationAdapter + OpenAI-compatible LLM + HermesOrchestrator` 的组合。

在 `apps/api/app/main.py` 中，系统会在启动时统一装配这些服务：

- `CaseService`：案件管理
- `EvidenceService`：证据包与采集产物管理
- `DocumentDraftService`：文书草稿生成与审核流转
- `MonitorTaskService`：监控任务配置与执行
- `PlaywrightWorker`：真实页面抓取与截图
- `NotificationAdapter`：消息通知与日志
- `HermesOrchestrator`：跨模块工作流编排中枢

<whiteboard type="blank"></whiteboard>

### 3.2 Hermes 在真实项目里的作用

这里需要特别说明：  
当前项目接入的是**项目内 `HermesOrchestrator`**，它承担了 Hermes Agent 风格的编排角色；当前阶段还没有直接接官方 `NousResearch/hermes-agent` gateway/runtime。

但它已经真实介入了三条核心链路：

1. **插件取证链路**
   - `IntakeService` 创建案件后调用 `hermes.submit_capture_workflow(case_id)`
   - 当插件 payload 不完整时，再由 `PlaywrightWorker` 进行补抓
2. **自动监控链路**
   - `MonitorTaskService` 调用 `PlaywrightWorker.capture(...)`
   - 命中阈值后调用 `hermes.generate_case_summary(...)`
   - 同时触发 `hermes.submit_capture_workflow(case_id)` 与通知分发
3. **文书草稿链路**
   - `DocumentDraftService` 调用 `hermes.submit_document_workflow(...)`
   - 再调用 `hermes.generate_document_draft(...)` 生成可审核初稿

换句话说，Hermes 不是摆设，也不是展示用概念词，而是当前后端里真正负责“把多步任务串起来”的编排层。

<whiteboard type="blank"></whiteboard>

### 3.3 为什么这个编排层重要

- 它把抓取、研判、通知、文书这些异构步骤拆开，又能统一编排
- 它让产品可以同时支持“主动取证”和“自动巡检”两种入口
- 它避免把复杂能力直接暴露给终端用户，仍然由平台 API 控制权限和流程
- 它为后续接入更多模型、更多通知渠道、更多监控任务留下了扩展位

### 3.4 当前运行时证明

当前运行中的 `/health` 已返回以下模块状态：

- `hermes_orchestrator: ready`
- `playwright_worker: ready`
- `notification_adapter: degraded`（未配置 SMTP 时邮件能力降级，但整体链路可运行）

其中 Hermes 当前连的是 **MiMo OpenAI-compatible LLM**，说明它已经不是一个静态示意图，而是处在实际服务运行中。

