# 证证鸽 API

证证鸽后端骨架，负责案件、证据包、文书模板、通知与 Hermes 工作流编排的基础接口。

## 功能

- 健康检查
- 案件列表和案件详情
- 证据包创建
- 文书模板列表
- 预留 Hermes / Playwright / 通知适配层

## 本地启动

```bash
cd apps/api
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

如果你想通过 `uv` 管理依赖：

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 接口

- `GET /health`
- `GET /api/v1/cases`
- `GET /api/v1/cases/{case_id}`
- `POST /api/v1/evidence-packs`
- `GET /api/v1/document-templates`
- `GET /api/v1/runtime/modules`

