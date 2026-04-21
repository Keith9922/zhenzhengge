# 证证鸽｜AI 知识产权侵权响应平台

<div align="center">
  <img src="apps/web/public/branding/zzge-logo-full.png" alt="证证鸽 Logo" width="600"/>
</div>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135+-green.svg)](https://fastapi.tiangolo.com/)

</div>

> **面向品牌方与法务团队的 AI 知识产权侵权响应平台**

## 一句话定位

**从发现侵权线索到沉淀证据包、生成可审核的法律文书草稿，一站式串联。**

---

## 两大核心用户操作链路

### 链路一：主动取证 → 一键生成文书

```
[1] 发现疑似侵权页面
           ↓
[2] 点击浏览器插件「一键取证」
           ↓
[3] 系统自动采集：URL、标题、正文、HTML、截图、抓取时间
           ↓
[4] 系统自动创建「案件」+「证据包」
           ↓
[5] AI 自动生成 Word 文书草稿（律师函 / 平台投诉函）
           ↓
[6] 人工审核 → 导出并进入后续处置
```

**适用场景**：法务人员主动巡查、人工发现疑似侵权页面

---

### 链路二：智能监控 → 自动生成文书

```
[1] 配置监控任务：目标站点 + 关键词 + 巡检频率 + 风险阈值
           ↓
[2] 系统自动巡检，持续发现高风险页面
           ↓
[3] 命中规则 → 自动创建「案件」+「证据包」
           ↓
[4] AI 自动生成 Word 文书草稿
           ↓
[5] 人工审核 → 导出并进入后续处置
```

**适用场景**：品牌方持续监测竞品侵权、电商平台监测假冒店铺

---

## AI 价值

| 传统方式 | 使用证证鸽后 |
|---------|-------------|
| 人工收集截图、整理证据 | 插件一键，后台自动抓取 |
| 人工撰写文书 | AI 参照模板自动生成结构化草稿 |
| 多人多次传递 | 全流程自动衔接，律师聚焦审核与处置 |

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
├────────────────┬────────────────┬───────────────────────────┤
│   浏览器插件     │    Web 工作台   │        移动端（预留）       │
│    (Plasmo)    │   (Next.js)    │                           │
└───────┬────────┴───────┬────────┴───────────────────────────┘
        │                │
        └───────┬────────┘
                ▼
┌─────────────────────────────────────────────────────────────┐
│                     API 网关 (FastAPI)                       │
├────────────────┬────────────────┬───────────────────────────┤
│     Hermes     │   LLM Service  │       Playwright          │
│    任务编排      │  文书生成/摘要  │        页面抓取/截图         │
├────────────────┴────────────────┴───────────────────────────┤
│                    数据层                                    │
├────────────────┬────────────────┬───────────────────────────┤
│      SQLite    │    通知推送     │       文件存储              │
│    案件/证据包   │  邮件/Webhook  │      截图/HTML             │
└────────────────┴────────────────┴───────────────────────────┘
```

### 技术选型

| 层级 | 技术选型 |
|------|---------|
| 浏览器插件 | Plasmo (Chrome MV3) |
| Web 前端 | Next.js 15, React 19, TailwindCSS, Tiptap |
| 后端 API | FastAPI, Python 3.13+ |
| 数据库 | SQLite (WAL 模式) |
| 页面抓取 | Playwright |
| 大语言模型 | OpenAI-compatible API（默认 MiMo，可替换） |
| 任务编排 | Hermes Orchestrator（CLI → LLM → 本地模板三层兜底） |
| 通知推送 | Email (SMTP) / Webhook |

---

## 部署运行

### 前置依赖

| 依赖 | 版本要求 | 安装方式 |
|------|---------|---------|
| **Python** | 3.13+ | [python.org](https://www.python.org/downloads/) |
| **uv** | 最新版 | `pip install uv` 或见下方说明 |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **pnpm** | 10+ | `npm install -g pnpm` |
| **Git** | 任意版本 | [git-scm.com](https://git-scm.com/) |

> **说明**：`uv` 是 Python 包管理器，用于管理后端依赖和虚拟环境，比 pip/poetry 更快。

---

### macOS / Linux 部署

#### 第一步：安装工具

```bash
# 安装 uv（Python 包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 pnpm（Node.js 包管理器）
npm install -g pnpm

# 验证
python3 --version   # 需要 3.13+
uv --version
node --version      # 需要 18+
pnpm --version
```

#### 第二步：克隆项目

```bash
git clone https://github.com/Keith9922/zhenzhengge.git
cd zhenzhengge
```

#### 第三步：配置后端

```bash
cd apps/api

# 复制环境变量配置文件
cp .env.example .env

# 编辑配置（至少填写 LLM API Key，否则使用本地 fallback 模板）
# nano .env 或用任意编辑器打开
```

关键配置项（`.env`）：

```env
# LLM AI 生成（填入你的 API Key 后 AI 功能生效，否则使用本地模板）
ZHZG_LLM_PROVIDER=mimo
ZHZG_LLM_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
ZHZG_LLM_API_KEY=your_api_key_here
ZHZG_LLM_MODEL=mimo-v2-pro

# 开发用鉴权 Token（可保持默认）
ZHZG_AUTH_TOKENS=dev-admin-token:admin,dev-operator-token:operator,dev-viewer-token:viewer
```

#### 第四步：安装后端依赖并启动

```bash
# 在 apps/api 目录下
uv sync                              # 安装 Python 依赖
uv run playwright install chromium  # 安装 Playwright 浏览器（页面抓取用）

# 启动后端（保持此终端窗口运行）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

#### 第五步：配置并启动前端

**新开一个终端窗口：**

```bash
# 回到项目根目录
cd zhenzhengge

# 安装所有 Node.js 依赖
pnpm install

# 配置前端环境变量
cd apps/web
cp .env.example .env.local
# .env.local 默认值已指向 localhost:8000，一般不需要修改
```

```bash
# 启动前端开发服务器（保持此终端窗口运行）
pnpm dev
```

前端启动后访问：http://localhost:3006

#### 第六步：安装浏览器插件（可选）

```bash
# 新开终端，进入插件目录
cd zhenzhengge/apps/extension
cp .env.example .env

# 构建插件
pnpm build
```

在 Chrome 中安装：
1. 打开 `chrome://extensions/`
2. 开启右上角「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择目录 `apps/extension/build/chrome-mv3-prod`

---

### Windows 部署

> Windows 用户请使用 **PowerShell**（以管理员身份运行）或 **Windows Terminal**。

#### 第一步：安装工具

**安装 Python 3.13+：**
1. 访问 https://www.python.org/downloads/
2. 下载 Windows 安装包（选择 64 位）
3. 安装时勾选 **"Add Python to PATH"**（重要）
4. 验证：`python --version`

**安装 uv：**
```powershell
# PowerShell 中执行
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 验证
uv --version
```

**安装 Node.js：**
1. 访问 https://nodejs.org/ 下载 LTS 版本（18+）
2. 运行安装程序，按默认选项安装
3. 验证：`node --version`

**安装 pnpm：**
```powershell
npm install -g pnpm
pnpm --version
```

**安装 Git：**
1. 访问 https://git-scm.com/download/win
2. 下载并安装，使用默认选项

#### 第二步：克隆项目

```powershell
git clone https://github.com/Keith9922/zhenzhengge.git
cd zhenzhengge
```

#### 第三步：配置后端

```powershell
cd apps\api

# 复制配置文件（Windows 用 copy 命令）
copy .env.example .env

# 用记事本或 VS Code 编辑 .env
notepad .env
# 或：code .env
```

填写 `.env` 中的关键配置（同 macOS 说明，至少填写 `ZHZG_LLM_API_KEY`）。

#### 第四步：安装后端依赖并启动

```powershell
# 在 apps\api 目录下
uv sync
uv run playwright install chromium

# 启动后端（保持此 PowerShell 窗口运行）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 第五步：配置并启动前端

**新开一个 PowerShell 窗口：**

```powershell
# 回到项目根目录
cd zhenzhengge

# 安装 Node.js 依赖
pnpm install

# 配置前端
cd apps\web
copy .env.example .env.local

# 启动前端开发服务器
pnpm dev
```

前端启动后访问：http://localhost:3006

#### 第六步：安装浏览器插件（可选）

```powershell
cd zhenzhengge\apps\extension
copy .env.example .env
pnpm build
```

在 Chrome 中安装（同 macOS 步骤）：
1. 打开 `chrome://extensions/`
2. 开启「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择目录 `apps\extension\build\chrome-mv3-prod`

#### Windows 常见问题

**问题：`uv` 命令找不到**
- 关闭并重新打开 PowerShell，让 PATH 生效
- 或手动添加：`$env:PATH += ";$env:USERPROFILE\.local\bin"`

**问题：`playwright install` 失败或 Chromium 下载超时**
- 设置代理或手动下载 Chromium
- 临时禁用取证抓取功能，系统其他功能仍正常工作

**问题：`pnpm install` 报错 `ENOENT` 或权限问题**
- 以管理员身份运行 PowerShell
- 或执行：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**问题：Python 版本不满足（需要 3.13+）**
- Windows 可使用 `uv python install 3.13` 自动安装所需版本，无需手动操作

---

### 使用根目录快捷命令

在项目根目录，可以用以下 pnpm 脚本一键操作（macOS/Linux/Windows 通用）：

```bash
pnpm dev:api          # 启动后端 API（端口 8000）
pnpm dev:web          # 启动前端（端口 3006）
pnpm test:api         # 运行后端单元测试
pnpm smoke:api        # 运行冒烟测试（需后端已启动）
pnpm build:web        # 构建前端生产版本
pnpm build:extension  # 构建浏览器插件
```

---

## 环境变量说明

### 后端 `apps/api/.env`

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ZHZG_LLM_PROVIDER` | `stub` | LLM 提供商，`stub` 表示使用本地 fallback 模板，不调用 AI |
| `ZHZG_LLM_BASE_URL` | OpenAI URL | OpenAI 兼容接口地址 |
| `ZHZG_LLM_API_KEY` | _(空)_ | API Key，填写后 AI 功能生效 |
| `ZHZG_LLM_MODEL` | `mimo-v2-pro` | 使用的模型名称 |
| `ZHZG_AUTH_TOKENS` | 见下方 | 鉴权 Token，格式：`token:role,token:role` |
| `ZHZG_REQUIRE_AUTH` | `true` | 是否开启鉴权 |
| `ZHZG_ENABLE_DEMO_SEED` | `false` | 是否启动时写入演示数据 |
| `ZHZG_HARNESS_AGENT_ENABLED` | `false` | 是否启用 Hermes CLI 编排器 |
| `ZHZG_EVIDENCE_TIMESTAMP_ENABLED` | `false` | 是否启用可信时间戳（TSA） |
| `ZHZG_SMTP_HOST` | _(空)_ | 邮件通知 SMTP 服务器 |

**开发默认 Token：**

| Token | 角色 | 权限 |
|-------|------|------|
| `dev-admin-token` | admin | 全部权限，含审计日志 |
| `dev-operator-token` | operator | 取证、创建草稿、导出 |
| `dev-viewer-token` | viewer | 只读 |

### 前端 `apps/web/.env.local`

```env
API_BASE_URL=http://127.0.0.1:8000      # 后端地址
API_AUTH_TOKEN=dev-admin-token          # 前端调用 API 使用的 Token
NEXT_PUBLIC_REPO_URL=https://github.com/Keith9922/zhenzhengge
```

### 浏览器插件 `apps/extension/.env`

```env
PLASMO_PUBLIC_API_BASE_URL=http://127.0.0.1:8000   # 后端地址
PLASMO_PUBLIC_WEB_BASE_URL=http://localhost:3006    # 前端地址
PLASMO_PUBLIC_API_TOKEN=dev-operator-token          # 插件调用 API 的 Token
PLASMO_PUBLIC_ALLOW_SIMULATED_SUBMISSION=false      # true 时不发请求，仅模拟
```

---

## 项目结构

```
zhenzhengge/
├── apps/
│   ├── api/                    # FastAPI 后端
│   │   ├── app/
│   │   │   ├── api/           # API 路由（auth/cases/evidence/drafts/...）
│   │   │   ├── core/          # 核心配置（config/storage）
│   │   │   ├── schemas/       # 数据模型
│   │   │   └── services/      # 业务服务（hermes/llm/drafts/evidence/...）
│   │   ├── tests/             # 集成测试
│   │   ├── scripts/           # 工具脚本（smoke_test.py）
│   │   ├── .env.example       # 环境变量模板
│   │   └── pyproject.toml     # Python 依赖
│   │
│   ├── web/                    # Next.js 15 前端
│   │   ├── app/workspace/     # 工作台页面（cases/evidence/drafts/...）
│   │   ├── components/        # UI 组件（Tiptap 编辑器/监控控制台/...）
│   │   ├── lib/               # API 调用函数
│   │   ├── .env.example       # 环境变量模板
│   │   └── package.json
│   │
│   └── extension/              # Chrome 浏览器插件（Plasmo MV3）
│       ├── src/popup.tsx      # 插件弹窗（一键取证）
│       ├── .env.example       # 环境变量模板
│       └── package.json
│
├── docs/                       # 文档
├── .github/workflows/          # CI/CD（API 测试/前端构建）
├── README.md
└── LICENSE
```

---

## 功能模块

| 模块 | 说明 | 状态 |
|------|------|------|
| 浏览器插件取证 | 一键采集 URL、标题、正文、HTML、截图 | ✅ 已完成 |
| 案件管理 | 案件列表、详情、风险评分、处理建议 | ✅ 已完成 |
| 证据包管理 | 证据沉淀、截图预览、哈希存证 | ✅ 已完成 |
| 智能监控 | 配置站点、关键词、频率、风险阈值 | ✅ 已完成 |
| AI 文书生成 | 律师函、平台投诉函、证据目录（三层兜底） | ✅ 已完成 |
| 富文本编辑器 | Tiptap 编辑器，支持表格/标题/列表/撤销 | ✅ 已完成 |
| Word 导出 | 一键导出标准 .docx，浏览器直接下载 | ✅ 已完成 |
| 草稿审核流 | 提交审核 → 通过/驳回 → 归档 | ✅ 已完成 |
| 邮件/Webhook 通知 | 命中规则后自动推送 | ✅ 已完成 |
| 鉴权与角色 | viewer / operator / admin 三级隔离 | ✅ 已完成 |
| 审计日志 | intake/草稿/导出等关键动作可追溯 | ✅ 已完成 |
| 可信时间戳 | 取证固证时间认证（当前降级为本地哈希存证） | 🔜 规划中 |

---

## 后续规划

- [ ] **可信时间戳固证**：正式投产后接入 RFC3161 TSA，提升留痕精度
- [ ] **平台化投诉导出**：补齐多平台投诉材料模板与附件规则
- [ ] **证据链法务校验**：证据链完整性校验、链路签名与复核规则
- [ ] **组织化协作流**：多人审核流、指派、SLA 与审批状态看板

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 证证鸽

证证鸽是一个面向知识产权侵权响应场景的取证、固证、预警和文书辅助平台。

**核心目标**：把「网页侵权线索」，变成「可继续审核、可继续完善、可继续导出的案件材料与法律文书草稿」。
