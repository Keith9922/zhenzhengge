# 证证鸽 LLM 接入说明

> 文档类型：后端大模型接入说明  
> 版本：v0.2  
> 更新时间：2026-04-12

## 1. 当前状态

当前后端已经具备真实 LLM 接入入口，但默认仍可在 `stub` 模式下运行。

现状分层如下：

- `FastAPI` 后端是真实可运行的
- `HermesOrchestrator` 已经可以调用 LLM service
- `LLM service` 支持 OpenAI 兼容客户端
- 文书草稿和案件摘要已经有统一的 LLM 编排入口
- 如果没有配置模型，系统会回退到本地模板文本，不会直接报死

这意味着：

- 你可以先不配模型，继续开发和联调
- 你一旦配置好 `provider / base_url / api_key / model`，Hermes 就可以真实调用模型

## 2. 支持的模型接入方式

当前实现走的是 **OpenAI 兼容协议**。

也就是说，只要你的模型平台支持以下调用方式，就可以接进来：

- `chat.completions`
- `api_key`
- `base_url`

这类平台可以是：

- 小米 MiMo Open Platform
- OpenAI 官方平台
- 任何 OpenAI-compatible 网关

## 3. 配置项

后端使用以下环境变量：

```env
ZHZG_LLM_PROVIDER=mimo
ZHZG_LLM_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
ZHZG_LLM_API_KEY=你的_API_KEY
ZHZG_LLM_MODEL=mimo-v2-pro
ZHZG_LLM_REASONING_MODEL=o1-mini
ZHZG_LLM_TTS_MODEL=
```

说明：

- `ZHZG_LLM_PROVIDER`：提供方标识，建议写 `mimo`、`openai` 或 `openai-compatible`
- `ZHZG_LLM_BASE_URL`：OpenAI 兼容接口地址，填你控制台实际给出的地址
- `ZHZG_LLM_API_KEY`：密钥，**不要写进仓库**
- `ZHZG_LLM_MODEL`：默认文本生成模型，当前推荐 `mimo-v2-pro`
- `ZHZG_LLM_REASONING_MODEL`：案件摘要等推理型任务使用的模型，当前默认也可直接填 `mimo-v2-pro`
- `ZHZG_LLM_TTS_MODEL`：TTS 预留位，当前主线还没接消费入口

如果你使用的是 MiMo 官方文档里的另一个兼容地址，例如 `https://api.xiaomimimo.com/v1`，也可以直接替换，只要它保持 OpenAI 协议即可。

当前本地开发已经验证过：

- 使用 `OpenAI(api_key=..., base_url=...)` 可以真实访问 MiMo 接口
- `mimo-v2-pro` 可正常返回 `chat.completions`
- 网络被沙箱限制时会自动回退本地模板，不会打断主链路

## 4. 安装依赖

后端已经新增 OpenAI Python SDK 依赖：

```toml
openai>=1.0.0
```

安装后，`OpenAI(...)` 客户端可以直接通过 `base_url` 连接到兼容网关。

## 5. Hermes 如何调用

当前 Hermes 已经从纯 stub 编排器升级为可调用 LLM service 的入口，并已经接入：

- 案件摘要生成
- 文书草稿生成
- 文书工作流编排入口

代码层提供了两个核心方法：

- `generate_case_summary(...)`
- `generate_document_draft(...)`

示例：

```python
from app.services.hermes import HermesOrchestrator

hermes = HermesOrchestrator()

summary = hermes.generate_case_summary(
    case_context={
        "title": "阿波达斯商品页疑似仿冒",
        "brand_name": "阿迪达斯",
        "suspect_name": "阿波达斯",
        "platform": "淘宝",
        "risk_level": "high",
        "description": "商品页出现近似品牌名和混淆性展示。",
    },
    evidence_context=[
        {
            "source_title": "商品详情页",
            "source_url": "https://example.com/listing",
            "note": "页面存在近似命名",
        }
    ],
)

print(summary.content)
```

文书草稿示例：

```python
draft = hermes.generate_document_draft(
    template_name="律师函",
    case_context={
        "title": "阿波达斯商品页疑似仿冒",
        "brand_name": "阿迪达斯",
        "suspect_name": "阿波达斯",
        "platform": "淘宝",
        "risk_level": "high",
        "description": "页面中存在近似品牌名和仿冒展示。",
    },
    variables_override={
        "contact": "法务部",
        "deadline": "3 个工作日内",
    },
)

print(draft.content)
```

当前默认路由是：

- 案件摘要优先走 `ZHZG_LLM_REASONING_MODEL`
- 文书草稿优先走 `ZHZG_LLM_MODEL`

## 6. 生成策略

当前实现遵循以下原则：

- 模型配置可用且网络可达时，走真实 OpenAI-compatible 调用
- 模型未配置时，走本地回退文本
- 远程调用失败时，自动回退本地模板，避免把整个流程打断

这对黑客松和联调比较关键，因为它保证了：

- 没配模型时也能跑
- 配上模型后能立刻看到真实差异
- 出问题时不会把工作台整条链路打崩

## 7. 推荐模型选择

文本摘要和文书初稿，优先推荐：

- `mimo-v2-pro`

推理型模型可以先保留：

- `o1-mini`

TTS 可以先作为后续扩展：

- 当前仓库已预留 `ZHZG_LLM_TTS_MODEL`
- 但主线流程还没接语音输出

## 8. 接入边界

当前 Hermes 负责的是编排，不是直接保存密钥，也不是用户开放聊天机器人。

你需要记住这几个边界：

- API Key 只放在本地 `.env`
- 不要提交到 Git
- 不要在前端暴露
- 不要把模型输出直接当最终法律结论

## 9. 验收标准

接入完成后，满足以下条件即可视为 LLM 路线打通：

- `runtime/modules` 能看到 Hermes/LLM 处于 `ready`
- Hermes 可以返回案件摘要文本
- Hermes 可以返回文书草稿文本
- 没配模型时依然能用本地回退文本完成联调
