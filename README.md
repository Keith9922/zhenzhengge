# 证证鸽

证证鸽是一个面向知识产权侵权响应场景的取证、固证、预警和文书辅助平台。

当前仓库规划包含：

- `apps/web`: 主站 Landing Page 与工作台
- `apps/extension`: 浏览器插件
- `apps/api`: 后端 API、任务编排与文书服务
- `docs`: PRD、技术选型、架构与开发文档

核心交付目标：

1. 浏览器插件：一键取证、提交案件
2. 主站：Landing Page、文档入口、工作台入口
3. 工作台：案件、证据包、风险分析、文书生成与审核
4. 后端：抓取、比对、通知、文书、Hermes 工作流编排

## 开发命令

- Web 主站与工作台：`pnpm dev:web`
- 浏览器插件：`pnpm dev:extension`
- 后端 API：`pnpm dev:api`
- Web 构建：`pnpm build:web`
- 插件构建：`pnpm build:extension`
- API 测试：`pnpm test:api`
- API 烟雾测试：`pnpm smoke:api`

## Web 运行时环境

生产态或本地联调时，`apps/web` 需要显式提供：

- `API_BASE_URL`：后端 API 根地址，例如 `http://127.0.0.1:8000`
- `NEXT_PUBLIC_REPO_URL`：仓库地址，用于 Landing Page 和文档入口

可参考：

- `apps/web/.env.example`

## API 运行时环境

推荐通过 `uv` 管理 Python 依赖与运行时，不再依赖本地手动 `source .venv/bin/activate`。

- 安装依赖：`uv --directory apps/api sync`
- 启动 API：`pnpm dev:api`
- 运行测试：`pnpm test:api`
