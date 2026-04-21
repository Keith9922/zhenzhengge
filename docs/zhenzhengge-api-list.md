# 证证鸽 API 文档

> 文档类型：前后端联调基线  
> 版本：v0.2  
> 更新时间：2026-04-21  
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
- 运行时模块状态/合规开关接口可用
- 组织级 ACL（`organization_id` 作用域）已在核心资源接口生效
- 可信时间戳（RFC3161）已接入，证据包支持时间戳回执下载
- 测试和 smoke test 已覆盖主链路

当前仍然是未完全产品化的能力：

- 注册登录/成员管理（当前为 token + 组织作用域）
- 平台投诉自动提交
- 电子签章/司法存证链路

所以，**后端当前是“可联调、可演示、部分真实能力已接通”的状态**：

- `API + 存储` 是真的
- `LLM/Hermes/抓取/通知` 已进入真实执行链路

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
- 触发 Hermes 编排与页面抓取链路

请求体：

```json
{
  "url": "https://example.com/item/1",
  "title": "阿波达斯商品页疑似仿冒",
  "capturedAt": "2026-04-11T08:00:00Z",
  "source": "browser-extension",
  "pageText": "页面正文内容",
  "html": "<html><body>sample-page</body></html>",
  "screenshotBase64": "data:image/png;base64,xxxx",
  "requestId": "req-0001"
}
```

兼容字段说明：

- `url` 同时兼容 `sourceUrl`
- `title` 同时兼容 `pageTitle`
- `html` 同时兼容 `rawHtml`
- `source` 同时兼容 `sourceType`

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

返回结构说明：

- 顶层固定返回 `case` 和 `evidence_pack`
- 插件侧应从 `case.case_id` 和 `evidence_pack.evidence_pack_id` 读取编号

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

### 3.3.1 案件处置指标

- `GET /api/v1/cases/insights`

### 3.3.2 案件动作中心

- `GET /api/v1/cases/{case_id}/action-center`

### 3.3.3 证据-主张关联

- `GET /api/v1/cases/{case_id}/evidence-claim-links`

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

### 3.7 证据包预览

- `GET /api/v1/evidence-packs/{evidence_pack_id}/preview`

用途：

- 返回截图是否存在
- 返回 HTML 是否存在
- 返回截图/HTML 下载地址
- 返回 HTML 片段，供前端详情页预览

### 3.8 证据包 HTML 归档

- `GET /api/v1/evidence-packs/{evidence_pack_id}/artifacts/html`

查询参数：

- `download=1` 时按文件下载

### 3.9 证据包截图归档

- `GET /api/v1/evidence-packs/{evidence_pack_id}/artifacts/screenshot`

查询参数：

- `download=1` 时按文件下载

### 3.10 创建证据包

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

- 当前草稿内容已接入 Hermes + LLM service
- 配置 MiMo/OpenAI 兼容模型且网络可达时，会走真实模型生成
- 比赛/生产可启用严格模式 `ZHZG_DRAFT_GENERATION_STRICT=true`，模型异常时直接失败
- 导出结果为可编辑 `docx` 文件

### 3.10 监控任务

- `GET /api/v1/monitor-tasks`
- `POST /api/v1/monitor-tasks`
- `GET /api/v1/monitor-tasks/{task_id}`
- `POST /api/v1/monitor-tasks/{task_id}/toggle`
- `POST /api/v1/monitor-tasks/{task_id}/run`

说明：

- 当前“手动执行一次监控任务”会真实抓取页面
- 命中阈值后，会创建案件、证据包并触发通知
- 已接入后台定时调度器（可通过配置开关），并支持任务执行历史查询

### 3.11 接收方式

- `GET /api/v1/notification-channels`
- `POST /api/v1/notification-channels`
- `POST /api/v1/notification-channels/{channel_id}/test`
- `GET /api/v1/notification-channels/logs`

说明：

- 当前邮件已支持真实 SMTP 发送
- 未配置 SMTP 时会明确返回 `failed` 并记录失败日志（不再假装发送成功）
- 钉钉支持 webhook 调用，但前端对外文案不直接暴露渠道实现

### 3.12 运行时模块状态

- `GET /api/v1/runtime/modules`
- `GET /api/v1/runtime/compliance`

返回体：

```json
[
  {
    "name": "hermes_orchestrator",
    "status": "ready",
    "description": "后端工作流编排中枢，LLM=ready"
  },
  {
    "name": "playwright_worker",
    "status": "ready",
    "description": "页面抓取与截图已接入，可执行真实页面采集"
  },
  {
    "name": "notification_adapter",
    "status": "degraded",
    "description": "通知渠道已接入，可进行配置和测试；未配置 SMTP 时邮件发送会降级。"
  }
]
```

`/runtime/compliance` 用于核验关键开关（鉴权、Demo Seed、严格模式、LLM、回退策略）是否满足现场合规要求。

## 4. 当前仍未实现或仅部分实现

以下能力当前仍属于后续规划，不能作为“已完成能力”对外承诺：

- 用户体系（注册/登录/租户/组织成员管理）
- 更细粒度权限模型（资源级 ACL，而非仅 token 角色）
- 审核任务中心（独立任务流、SLA、指派、催办）
- 多平台投诉材料自动映射（各平台表单字段与附件策略）
- 可信时间戳/电子签章等第三方法证能力

## 5. 当前联调约束

当前前后端联调，请遵守这几点：

1. 只依赖“当前已实现接口”
2. Hermes/Harness 编排已接入，但启用 Harness 需正确配置 `ZHZG_HARNESS_*` 与可用技能
3. 插件 intake 会真实保存 HTML 和截图文件；手工新建证据包也会触发抓取与归档
4. Playwright 已接入真实抓取，但网络失败时会回退到 HTTP 内容（不再写占位 HTML）
5. 邮件只有在配置 SMTP 后才会真实发出
6. 当前文书草稿优先走 Harness/LLM，异常时会回退文本模板；生产环境建议禁用回退并改为显式失败

## 6. 当前真实后端与规划后端的差异

| 模块 | 当前状态 | 是否真实可用 | 说明 |
| --- | --- | --- | --- |
| FastAPI 路由 | 已实现 | 是 | 可启动、可请求 |
| SQLite 持久化 | 已实现 | 是 | 数据会写入 `apps/api/data/zhenzhengge.db` |
| 插件 intake | 已实现 | 是 | 可创建案件和证据包 |
| 案件查询 | 已实现 | 是 | 列表与详情都可用 |
| 证据包创建 | 已实现 | 是 | intake 路径会真实写入 HTML 与截图 |
| 文书草稿 | 已实现 | 是 | 已接 Hermes + LLM，失败时回退模板 |
| 监控任务 | 已实现 | 是 | 当前支持手动执行、真实抓取、命中建案 |
| 监控调度器 | 已实现 | 是 | 后台线程可按频率调度任务，并写入执行历史 |
| 接收方式 | 已实现 | 是 | 支持列表、创建、测试 |
| Hermes/Harness 编排 | 已实现 | 是 | 已进入文书/摘要/监控链路，Harness 可配置启用 |
| Playwright 抓取 | 已实现 | 是 | 优先真实抓取，失败时回退 |
| 通知发送 | 部分实现 | 部分 | SMTP / 钉钉可真实发送，未配置时会记录失败日志 |
| 文书生成 | 部分实现 | 部分 | LLM/Harness 已接入，导出支持 docx，但生产文书策略仍需补强 |
| 鉴权/RBAC | 已实现 | 是 | token + 角色依赖（viewer/operator/admin） |
| 审计日志 | 已实现 | 是 | 关键动作记录 actor、resource、payload |

## 7. 建议下一步

如果你说“继续开发”，接口线下一步建议按这个顺序做：

1. 用户/组织体系与资源级权限
2. 审核任务中心（指派、状态流转、SLA）
3. 多平台投诉材料模板与导出策略
4. 可信时间戳与证据链签名能力
5. 生产可观测性（指标、告警、追踪）
