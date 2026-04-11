# 证证鸽 LLM 配置说明

> 文档类型：后端大模型接入说明  
> 版本：v0.1  
> 更新时间：2026-04-11

## 1. 当前状态

当前项目**还没有真正接入大模型**。

这句话要说清楚：

- `apps/api` 是真的后端
- `Hermes` 当前只是 stub 编排器
- 还没有真实调用 OpenAI、MiniMax 或其他模型
- 所以你现在**不需要登录大模型才能启动后端**
- 但你如果想让 `Hermes / 文书生成 / 智能研判` 真正工作，就必须补模型接入

代码依据：

- [config.py](/Users/ronggang/code/funcode/mofa/apps/api/app/core/config.py)
- [hermes.py](/Users/ronggang/code/funcode/mofa/apps/api/app/services/hermes.py)
- [runtime.py](/Users/ronggang/code/funcode/mofa/apps/api/app/api/v1/endpoints/runtime.py)

其中 `HermesOrchestrator.health()` 目前返回的是：

- `status = "stub"`

这说明它现在不是一个真正的大模型驱动编排器。

## 2. 你的理解对一半

你说“`Hermes Agent 需要大模型去驱动`”，这个方向是对的，但要区分两层：

### 2.1 Hermes 不是“大模型本身”

Hermes 更像：

- 编排层
- 工作流调度层
- 任务组织层

### 2.2 真正的智能能力来自模型调用

比如这些能力，最终都要由模型支撑：

- 疑似侵权描述整理
- 风险摘要生成
- 文书初稿生成
- 结构化案件材料抽取

所以更准确地说：

> Hermes 负责组织流程，LLM 负责生成和理解。

## 3. ChatGPT Plus 能不能直接当 API 用

**不能。**

你不能用 `ChatGPT Plus` 的网页登录态，直接拿来当 OpenAI API 的正式后端认证方案。

官方帮助中心明确写了：

- `ChatGPT Plus` 不包含 API 使用额度
- `ChatGPT` 与 `API platform` 是两套独立的计费和账号体系

官方来源：

- OpenAI Help Center: `What is ChatGPT Plus?`  
  https://help.openai.com/en/articles/6950777-chatgpt-plus
- OpenAI Help Center: `Billing settings in ChatGPT vs Platform`  
  https://help.openai.com/en/articles/9039756-billing-settings-in-chatgpt-vs-platform

这两篇里关键信息是：

- `API usage is separate and billed independently`
- `The ChatGPT platform and the API platform operate as two separate platforms`

所以结论很直接：

### 不能做的事

- 不要用 ChatGPT 网页 cookie / session 去伪装 API
- 不要把 Plus 当成后端 API 授权方式
- 不要依赖浏览器登录态做生产接入

### 正确做法

- 到 `platform.openai.com` 创建 API key
- 在 API 平台单独开通 billing
- 后端用标准 `OPENAI_API_KEY` 调 OpenAI API

## 4. OpenAI 正确配置方式

你如果要用 OpenAI 驱动证证鸽后端，建议这样配。

### 4.1 你需要准备的东西

1. OpenAI Platform 账号
2. API key
3. API 平台 billing
4. 选定默认模型

### 4.2 建议的环境变量

建议在 `apps/api/.env` 里新增这些字段：

```env
ZHZG_LLM_PROVIDER=openai
ZHZG_OPENAI_API_KEY=sk-...
ZHZG_OPENAI_BASE_URL=https://api.openai.com/v1
ZHZG_OPENAI_MODEL=gpt-5.4-mini
ZHZG_OPENAI_REASONING_MODEL=gpt-5.4
```

如果你只先接一个模型，最小配置可以是：

```env
ZHZG_LLM_PROVIDER=openai
ZHZG_OPENAI_API_KEY=sk-...
ZHZG_OPENAI_MODEL=gpt-5.4-mini
```

### 4.3 后端接入建议

建议把模型调用分成单独服务，不要直接写死在 Hermes 里。

推荐结构：

- `app/services/llm.py`
- `app/services/hermes.py`

职责分工：

- `llm.py`：封装 OpenAI SDK 调用
- `hermes.py`：组织取证、研判、文书生成流程

## 5. 推荐的代码接入方式

### 5.1 配置层

在 [config.py](/Users/ronggang/code/funcode/mofa/apps/api/app/core/config.py) 增加：

- `llm_provider`
- `openai_api_key`
- `openai_base_url`
- `openai_model`

### 5.2 新增 LLM Service

建议新增：

`apps/api/app/services/llm.py`

里面做：

- 客户端初始化
- 统一 prompt 封装
- 文书生成
- 风险摘要生成

### 5.3 Hermes 调用 LLM

在 `HermesOrchestrator` 中增加：

- `generate_risk_summary(...)`
- `generate_document_draft(...)`

但注意：

- Hermes 不负责保存 key
- Hermes 不负责用户认证
- Hermes 只负责调 LLM service

## 6. 第一阶段建议怎么用 OpenAI

我建议第一阶段先只让 OpenAI 做两件事：

### 6.1 案件摘要生成

输入：

- 页面标题
- 页面文本摘要
- 品牌名
- 疑似主体
- 风险等级

输出：

- 一段案件摘要
- 一组研判要点
- 一组建议动作

### 6.2 文书初稿生成

输入：

- 模板类型
- 案件结构化字段
- 证据目录

输出：

- 律师函初稿
- 平台投诉函初稿

不要第一步就让模型做：

- 最终法律认定
- 完整侵权判定
- 自动正式举报

## 7. 我对你当前方案的建议

如果你想尽快接起来，最稳的是：

1. 先保留现有 FastAPI + SQLite
2. 补 `OpenAI API key` 到 `.env`
3. 新增 `LLM service`
4. 先接“案件摘要生成”和“文书初稿生成”
5. 等这两块稳定，再把 Hermes 从 stub 改成真实编排

## 8. 这轮的实际判断

直接回答你的问题：

### 目前后端是否真实有效？

**部分真实有效。**

- API 是真的
- 数据库存储是真的
- intake 创建案件和证据包是真的
- Hermes 的“智能能力”目前不是真的

### 目前是否已经需要你登录大模型？

**不需要。**

因为现在项目还没有接真实 LLM。

### 如果你要让后端真的智能起来，是否必须配置 OpenAI API？

**是。**

而且要用 `platform.openai.com` 的 API key，不是 ChatGPT Plus 登录态。

