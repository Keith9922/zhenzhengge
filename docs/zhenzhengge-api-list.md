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
- 证据包创建、证据包列表可用
- 插件 intake 接口可用
- 文书模板列表接口可用
- 运行时模块状态接口可用
- 测试和 smoke test 已经覆盖基础链路

当前仍然是 stub / 占位的能力：

- Hermes 编排
- Playwright 真实抓取
- 通知发送
- 文书生成
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

### 3.4 证据包列表

- `GET /api/v1/evidence-packs`

查询参数：

- `case_id`：可选，按案件过滤

返回体：

```json
[
  {
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
]
```

### 3.5 创建证据包

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
    "evidence_pack_id": "evidence-pack-0002",
    "case_id": "case-zhzg-0001",
    "source_url": "https://example.com/item/2",
    "source_title": "疑似侵权页面",
    "capture_channel": "browser_extension",
    "note": "manual-create",
    "hash_sha256": "xxxx",
    "snapshot_path": "captures/example.com_item_2.png",
    "html_path": "captures/example.com_item_2.html",
    "created_at": "2026-04-11T08:00:00+00:00",
    "status": "captured"
  }
}
```

### 3.6 文书模板列表

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

### 3.7 运行时模块状态

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
    "status": "stub",
    "description": "钉钉 / 邮件通知预留位"
  }
]
```

## 4. 当前未实现但已规划接口

以下接口**还没有在 `apps/api` 里实现**，只能作为后续开发规划，不能直接联调：

- 文书草稿生成
- 草稿详情
- 草稿审核
- 草稿导出
- 监控任务增删改查
- 通知渠道配置
- 登录与鉴权
- 用户与角色接口
- 工作流状态查询

## 5. 当前联调约束

当前前后端联调，请遵守这几点：

1. 只依赖“当前已实现接口”
2. 不要假设 Hermes 已经真的调了大模型
3. 不要假设 Playwright 已经真的保存截图文件
4. 不要假设通知已经真的发出
5. 文书模板页当前只能拿模板列表，不能真正生成文书

## 6. 当前真实后端与规划后端的差异

| 模块 | 当前状态 | 是否真实可用 | 说明 |
| --- | --- | --- | --- |
| FastAPI 路由 | 已实现 | 是 | 可启动、可请求 |
| SQLite 持久化 | 已实现 | 是 | 数据会写入 `apps/api/data/zhenzhengge.db` |
| 插件 intake | 已实现 | 是 | 可创建案件和证据包 |
| 案件查询 | 已实现 | 是 | 列表与详情都可用 |
| 证据包创建 | 已实现 | 是 | 但文件路径是模拟生成 |
| Hermes 编排 | stub | 否 | 只有排队结果，没有真实执行 |
| Playwright 抓取 | stub | 否 | 只返回预设路径 |
| 通知发送 | stub | 否 | 不会真正发钉钉或邮件 |
| 文书生成 | 未实现 | 否 | 只有模板列表 |
| 鉴权/RBAC | 未实现 | 否 | 还没有登录和角色控制 |

## 7. 建议下一步

如果你说“继续开发”，接口线下一步建议按这个顺序做：

1. 文书草稿生成接口
2. 证据包详情接口
3. 监控任务接口
4. 通知配置接口
5. 鉴权与角色接口

