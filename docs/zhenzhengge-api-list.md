# 证证鸽 API 文档

> 文档类型：前后端联调基线  
> 版本：v0.2  
> 更新时间：2026-04-11  
> 说明：本文档区分“当前已实现接口”和“规划中接口”。联调、测试、页面接线时，默认以“当前已实现接口”为准，不要拿规划接口直接开发。

## 1. 当前后端状态

当前 `apps/api` 里的后端是一个**可运行、可持久化、可联调**的 FastAPI 服务，但还不是完整业务后端。

当前已经真实存在的能力：

- FastAPI 服务可启动
- SQLite 持久化可用
- 案件创建、案件列表、案件详情可用
- 案件维度证据包列表、证据包详情可用
- 插件 intake 接口可用
- 文书模板列表可用
- 文书草稿生成、提交审核、通过/驳回、导出可用
- 监控任务创建、列表、启停、手动执行可用
- 接收方式列表、创建、测试可用
- 运行时模块状态接口可用
- 测试和 smoke test 已覆盖主链路

当前仍然是 stub / 占位的能力：

- Hermes 编排
- Playwright 真实抓取
- 大模型驱动的文书生成
- 大模型调用

所以，**后端目前是“半实装”状态**：

- `API + 存储` 是真的
- `LLM/Hermes/通知/抓取` 还没有接成真实执行链路

## 2. 服务入口

### 根入口

- `GET /`

返回：

```json
{
  "service": "证证鸽 API",
  "status": "ok",
  "docs": "/docs",
  "api_prefix": "/api/v1"
}
```

### 健康检查

- `GET /health`

返回：

```json
{
  "status": "ok",
  "service": "证证鸽 API"
}
```

## 3. 当前已实现接口

### 3.1 插件取证 intake

- `POST /api/v1/evidence/intake`

用途：

- 浏览器插件提交当前页面的取证请求
- 服务端创建案件
- 服务端创建证据包
- 触发 Hermes / Playwright stub

请求体：

```json
{
  "url": "https://example.com/item/1",
  "title": "阿波达斯商品页疑似仿冒",
  "capturedAt": "2026-04-11T08:00:00Z",
  "source": "browser-extension",
  "pageText": "页面正文内容",
  "html": "<html><body>mock</body></html>",
  "screenshotBase64": "data:image/png;base64,xxxx",
  "requestId": "req-0001"
}
```

返回体：

```json
{
  "case": {
    "case_id": "case-zhzg-0003",
    "title": "阿波达斯商品页疑似仿冒",
    "brand_name": "阿波达斯商品页疑似仿冒",
    "suspect_name": "阿波达斯商品页疑似仿冒-疑似主体",
    "platform": "browser-extension",
    "risk_score": 88,
    "risk_level": "high",
    "status": "open",
    "updated_at": "2026-04-11T08:00:00+00:00",
    "description": "……",
    "evidence_count": 1,
    "template_count": 0,
    "tags": ["插件取证", "browser-extension"],
    "monitoring_scope": ["https://example.com/item/1", "browser-extension"]
  },
  "evidence_pack": {
    "evidence_pack_id": "evidence-pack-0001",
    "case_id": "case-zhzg-0003",
    "source_url": "https://example.com/item/1",
    "source_title": "阿波达斯商品页疑似仿冒",
    "capture_channel": "browser-extension",
    "note": "req-0001",
    "hash_sha256": "xxxx",
    "snapshot_path": "captures/example.com_item_1.png",
    "html_path": "captures/example.com_item_1.html",
    "created_at": "2026-04-11T08:00:00+00:00",
    "status": "captured"
  }
}
```

### 3.2 案件列表

- `GET /api/v1/cases`

查询参数：

- `status`：可选，案件状态过滤
- `platform`：可选，平台过滤
- `limit`：默认 `20`

返回体：

```json
{
  "total": 2,
  "items": [
    {
      "case_id": "case-zhzg-0001",
      "title": "阿迪达斯变体商品页疑似仿冒",
      "brand_name": "阿迪达斯",
      "suspect_name": "阿波达斯",
      "platform": "淘宝",
      "risk_score": 92,
      "risk_level": "high",
      "status": "open",
      "updated_at": "2026-04-11T08:00:00+00:00"
    }
  ]
}
```

### 3.3 案件详情

- `GET /api/v1/cases/{case_id}`

返回体：

```json
{
  "case_id": "case-zhzg-0001",
  "title": "阿迪达斯变体商品页疑似仿冒",
  "brand_name": "阿迪达斯",
  "suspect_name": "阿波达斯",
  "platform": "淘宝",
  "risk_score": 92,
  "risk_level": "high",
  "status": "open",
  "updated_at": "2026-04-11T08:00:00+00:00",
  "description": "展示商标近似、图文混用和商品页信息留存流程的演示案件。",
  "evidence_count": 2,
  "template_count": 2,
  "tags": ["商标近似", "商品页", "国内电商"],
  "monitoring_scope": ["taobao.com", "tmall.com"]
}
```

### 3.4 案件下证据包列表

- `GET /api/v1/cases/{case_id}/evidence-packs`

返回体：

```json
[
  {
    "evidence_pack_id": "ep-0001",
    "case_id": "case-zhzg-0003",
    "source_url": "https://example.com/item/1",
    "source_title": "阿波达斯商品页疑似仿冒",
    "capture_channel": "browser-extension",
    "note": "req-0001",
    "hash_sha256": "xxxx",
    "snapshot_path": "evidence/case-zhzg-0003/snapshot-0001.png",
    "html_path": "evidence/case-zhzg-0003/page-0001.html",
    "created_at": "2026-04-11T08:00:00+00:00",
    "status": "captured"
  }
]
```

### 3.5 证据包列表

- `GET /api/v1/evidence-packs`

查询参数：

- `case_id`：可选，按案件过滤

返回体：

```json
[
  {
    "evidence_pack_id": "ep-0001",
    "case_id": "case-zhzg-0003",
    "source_url": "https://example.com/item/1",
    "source_title": "阿波达斯商品页疑似仿冒",
    "capture_channel": "browser-extension",
    "note": "req-0001",
    "hash_sha256": "xxxx",
    "snapshot_path": "evidence/case-zhzg-0003/snapshot-0001.png",
    "html_path": "evidence/case-zhzg-0003/page-0001.html",
    "created_at": "2026-04-11T08:00:00+00:00",
    "status": "captured"
  }
]
```

### 3.6 证据包详情

- `GET /api/v1/evidence-packs/{evidence_pack_id}`

### 3.7 创建证据包

- `POST /api/v1/evidence-packs`

请求体：

```json
{
  "case_id": "case-zhzg-0001",
  "source_url": "https://example.com/item/2",
  "source_title": "疑似侵权页面",
  "capture_channel": "browser_extension",
  "note": "manual-create"
}
```

返回体：

```json
{
  "item": {
    "evidence_pack_id": "ep-0002",
    "case_id": "case-zhzg-0001",
    "source_url": "https://example.com/item/2",
    "source_title": "疑似侵权页面",
    "capture_channel": "browser_extension",
    "note": "manual-create",
    "hash_sha256": "xxxx",
    "snapshot_path": "evidence/case-zhzg-0001/snapshot-0002.png",
    "html_path": "evidence/case-zhzg-0001/page-0002.html",
    "created_at": "2026-04-11T08:00:00+00:00",
    "status": "captured"
  }
}
```

### 3.8 文书模板列表

- `GET /api/v1/document-templates`

返回体：

```json
{
  "total": 3,
  "items": [
    {
      "template_key": "lawyer-letter",
      "name": "律师函",
      "category": "处置文书",
      "description": "用于向平台或相对方发出的侵权处置初稿。",
      "target_use": "法务审核前草稿",
      "output_formats": ["docx", "pdf"],
      "is_active": true
    }
  ]
}
```

### 3.9 文书草稿

- `GET /api/v1/document-drafts`
- `POST /api/v1/document-drafts`
- `GET /api/v1/document-drafts/{draft_id}`
- `POST /api/v1/document-drafts/{draft_id}/submit-review`
- `POST /api/v1/document-drafts/{draft_id}/approve`
- `POST /api/v1/document-drafts/{draft_id}/reject`
- `POST /api/v1/document-drafts/{draft_id}/export`

说明：

- 当前草稿内容由模板服务和案件信息拼装，是真实可用的占位生成，不依赖大模型
- 导出结果当前为 `Markdown` 文件，后续再扩到 `docx/pdf`

### 3.10 监控任务

- `GET /api/v1/monitor-tasks`
- `POST /api/v1/monitor-tasks`
- `GET /api/v1/monitor-tasks/{task_id}`
- `POST /api/v1/monitor-tasks/{task_id}/toggle`
- `POST /api/v1/monitor-tasks/{task_id}/run`

说明：

- 当前“手动执行一次监控任务”会更新任务执行时间
- 真实巡检、抓取、比对和建案仍待后续接入

### 3.11 接收方式

- `GET /api/v1/notification-channels`
- `POST /api/v1/notification-channels`
- `POST /api/v1/notification-channels/{channel_id}/test`

说明：

- 当前邮件已支持真实 SMTP 发送
- 未配置 SMTP 时会降级为 dry-run
- 钉钉支持 webhook 调用，但前端对外文案不直接暴露渠道实现

### 3.12 运行时模块状态

- `GET /api/v1/runtime/modules`

返回体：

```json
[
  {
    "name": "hermes_orchestrator",
    "status": "stub",
    "description": "后端工作流编排中枢预留位"
  },
  {
    "name": "playwright_worker",
    "status": "stub",
    "description": "页面抓取与截图预留位"
  },
  {
    "name": "notification_adapter",
    "status": "degraded",
    "description": "通知渠道已接入，可进行配置和测试；未配置 SMTP 时邮件发送会降级。"
  }
]
```

## 4. 当前未实现但已规划接口

以下接口**还没有在 `apps/api` 里实现**，只能作为后续开发规划，不能直接联调：

- 登录与鉴权
- 用户与角色接口
- 工作流状态查询
- 审核任务独立接口
- 通知日志接口
- 工作流运行记录接口

## 5. 当前联调约束

当前前后端联调，请遵守这几点：

1. 只依赖“当前已实现接口”
2. 不要假设 Hermes 已经真的调了大模型
3. 插件 intake 会真实保存 HTML 和截图文件；手工新建证据包仍只写元数据
4. 不要假设 Playwright 已经真的补抓了页面
5. 邮件只有在配置 SMTP 后才会真实发出
6. 当前文书草稿为模板拼装版，不是大模型生成版

## 6. 当前真实后端与规划后端的差异

| 模块 | 当前状态 | 是否真实可用 | 说明 |
| --- | --- | --- | --- |
| FastAPI 路由 | 已实现 | 是 | 可启动、可请求 |
| SQLite 持久化 | 已实现 | 是 | 数据会写入 `apps/api/data/zhenzhengge.db` |
| 插件 intake | 已实现 | 是 | 可创建案件和证据包 |
| 案件查询 | 已实现 | 是 | 列表与详情都可用 |
| 证据包创建 | 已实现 | 是 | intake 路径会真实写入 HTML 与截图 |
| 文书草稿 | 已实现 | 是 | 当前是模板拼装与 Markdown 导出 |
| 监控任务 | 已实现 | 是 | 当前是任务管理与执行留痕 |
| 接收方式 | 已实现 | 是 | 支持列表、创建、测试 |
| Hermes 编排 | stub | 否 | 只有排队结果，没有真实执行 |
| Playwright 抓取 | stub | 否 | 只返回预设路径 |
| 通知发送 | 部分实现 | 部分 | SMTP 配置后邮件可真实发送 |
| 文书生成 | 部分实现 | 部分 | 当前不依赖 LLM，只做模板拼装 |
| 鉴权/RBAC | 未实现 | 否 | 还没有登录和角色控制 |

## 7. 建议下一步

如果你说“继续开发”，接口线下一步建议按这个顺序做：

1. 真实 Playwright 补抓与监控执行链
2. 证据包详情与草稿详情前端接线
3. 审核任务与通知日志接口
4. 鉴权与角色接口
5. LLM 文书生成与案件摘要接口
