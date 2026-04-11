# 证证鸽开发拆分表

> 版本：`v0.1`  
> 目标：把第一阶段工作拆成可以执行的 Sprint 和原子任务，方便多人并行开发与 Git 管理。

## 1. 拆分原则

1. 每个任务只解决一类问题。
2. 每个任务对应一个明确目录或模块，避免多人冲突。
3. 每个阶段完成后必须提交 Git commit。
4. 所有实现都要回对 PRD、技术选型和架构文档。

## 2. 角色分工建议

### 前端主站 / 工作台

负责目录：

- `apps/web`

### 插件开发

负责目录：

- `apps/extension`

### 后端 API / 数据层

负责目录：

- `apps/api`

### 集成与联调

负责内容：

- 接口对接
- 环境变量
- 页面联调
- 工作流串联

### 产品与文档

负责目录：

- `docs`
- 根目录工程说明

## 3. Sprint 规划

## 3.1 Sprint 0：基线搭建

目标：

- 建立独立 Git 仓库
- 固化 PRD 和技术文档
- 建立 monorepo 骨架

任务：

- 初始化 Git
- 增加 `.gitignore`
- 建立 `apps/` 与 `packages/` 目录
- 确认技术选型文档

验收：

- 仓库能独立开发
- 文档齐备

## 3.2 Sprint 1：主站与基础骨架

目标：

- 建好主站 Landing Page
- 建好工作台壳子
- 建好 API 骨架
- 建好插件骨架

任务：

- 主站首页
- 文档入口页
- 工作台基础导航
- FastAPI 健康检查和基础接口
- 插件 popup 和提交占位

验收：

- `apps/web` 可启动
- `apps/api` 可启动
- `apps/extension` 可开发调试

## 3.3 Sprint 2：主动取证闭环

目标：

- 跑通“页面 -> 取证 -> 案件 -> 证据包”

任务：

- 插件提交取证请求
- API 接收取证请求
- Playwright 补抓
- 保存截图、HTML、文本
- 工作台展示案件详情与证据包

验收：

- 点击插件后可以在工作台看到案件和证据

## 3.4 Sprint 3：风险分析与通知

目标：

- 跑通“证据 -> 风险评分 -> 通知”

任务：

- RapidFuzz + pypinyin
- imagehash
- 风险等级规则
- 钉钉通知
- 邮件通知

验收：

- 案件分析后能收到通知

## 3.5 Sprint 4：文书与审核

目标：

- 跑通“案件 -> 文书初稿 -> 审核 -> 导出”

任务：

- 模板列表
- 律师函模板
- 平台投诉函模板
- 审核状态机
- 导出流程

验收：

- 工作台可以生成并导出文书初稿

## 3.6 Sprint 5：Hermes 串联与自动监测预留

目标：

- 让后台链路由 Hermes 统一编排
- 预留自动监测入口

任务：

- 主动取证工作流
- 文书生成工作流
- 通知工作流
- 自动监测任务壳子

验收：

- 后台流程可通过 Hermes 串起来

## 4. 原子任务建议

### 前端主站 / 工作台

1. 搭建 Next.js 工程
2. 完成 Landing Page
3. 完成工作台基础布局
4. 完成案件列表页
5. 完成案件详情页
6. 完成证据包详情页
7. 完成模板页
8. 完成审核页

### 插件

1. 搭建 Plasmo 工程
2. 完成 popup 页面
3. 采集 URL / 标题 / 时间
4. 增加备注输入
5. 调用提交接口

### 后端

1. 搭建 FastAPI 工程
2. 增加健康检查
3. 增加案件接口
4. 增加证据包接口
5. 增加模板接口
6. 增加文书生成接口
7. 增加通知配置接口

### 联调

1. 插件接后端
2. 工作台接案件接口
3. 工作台接证据接口
4. 工作台接模板接口
5. 工作台接文书接口

## 5. Git 管理建议

建议每完成一个清晰子任务就提交一次，例如：

- `feat(web): add landing page shell`
- `feat(extension): scaffold plasmo popup capture flow`
- `feat(api): add cases and evidence stub endpoints`
- `feat(web): add workspace case detail pages`
- `feat(api): add draft generation stub`

## 6. 当前最重要的顺序

如果只按最短路径开发，优先级如下：

1. 主站与工作台骨架
2. 插件取证入口
3. API 基础接口
4. 证据包与案件展示
5. 风险分析
6. 通知
7. 文书与审核
8. Hermes 编排

## 7. 文档回写要求

每个 Sprint 完成后要同步更新：

- `zhenzhengge-prd.md`
- `zhenzhengge-tech-selection.md`
- `zhenzhengge-architecture-and-tasks.md`

确保：

- 已做功能和文档一致
- 暂未做功能不会被误写成已完成
