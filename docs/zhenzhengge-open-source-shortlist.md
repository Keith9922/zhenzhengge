# 证证鸽技术复用清单

> 目标：为证证鸽第一阶段开发列出可优先复用的开源项目、模块与代码库，减少重复造轮子。  
> 原则：优先选择官方仓库、活跃维护、许可清晰、能直接嵌入当前技术路线的组件。  
> 用法：这份文档作为后续技术选型和开发拆分的借鉴清单，不等于全部接入名单。初版仍以最小闭环为优先。

## 1. 选型结论

如果只看初版最值得复用的组合，推荐优先考虑：

1. `Plasmo`：浏览器插件框架
2. `Playwright`：页面抓取、截图、自动化浏览
3. `RapidFuzz + pypinyin`：品牌词近似比对
4. `imagehash`：图片近似判断
5. `docxtpl + python-docx`：Word 模板文书生成
6. `Apprise`：邮件和统一通知出口
7. `DingtalkChatbot` 或 `open-dingtalk/dingtalk-stream-sdk-python`：钉钉通知 / 机器人交互
8. `Hermes Agent`：后端任务编排中枢、监控与推送触发

对于增强版能力，再考虑：

- `changedetection.io`
- `Crawl4AI`
- `sentence-transformers`
- `openai/CLIP` 或 `mlfoundations/open_clip`
- `imagededup`
- `WeasyPrint` 或 `Gotenberg`

## 2. 初版优先复用清单

### 2.1 浏览器插件框架

#### `Plasmo`

- 适合用途：
  - 快速搭建 Chrome/Chromium 插件
  - 实现插件弹窗、内容脚本、后台脚本、消息通信
- 为什么适合：
  - 对浏览器插件开发友好
  - React + TypeScript 支持成熟
  - 比自己从零配 Manifest 和构建链更省时间
- 在证证鸽中的建议用途：
  - 插件弹窗
  - 当前页一键取证按钮
  - 页面内容采集与提交
- 官方仓库：
  - https://github.com/PlasmoHQ/plasmo
- 许可证：
  - MIT

### 2.2 页面抓取与截图

#### `Playwright`

- 适合用途：
  - 打开指定页面
  - 截图
  - 获取 HTML
  - 等待异步内容加载
  - 模拟页面交互
- 为什么适合：
  - 你们已经在当前项目环境里用过
  - 适合证据抓取、定时巡检和页面重放
  - 对动态网站支持比传统 requests/bs4 更强
- 在证证鸽中的建议用途：
  - 主动取证时的服务端补抓
  - 自动监测任务的页面抓取
  - 生成全页截图
- 官方仓库：
  - https://github.com/microsoft/playwright
- 许可证：
  - Apache-2.0

### 2.3 站点变化监测

#### `changedetection.io`

- 适合用途：
  - 对指定网站进行变化监测
  - 定时检查页面更新
  - 变化触发通知
- 为什么适合：
  - 它本身就是“指定页面持续监控”的成熟开源实现
  - 有很多“watch / selector / notification”上的现成思路
- 在证证鸽中的建议用途：
  - 参考其“监控任务”设计
  - 参考其页面变化检测策略和通知模型
  - 不一定要直接整套嵌入，可作为设计参考
- 官方仓库：
  - https://github.com/dgtlmoon/changedetection.io
- 许可证：
  - Apache-2.0
- 备注：
  - 如果你们核心流程已经由 Hermes + 自研任务服务承接，`changedetection.io` 更适合“借鉴”而不是“整套接入”。

### 2.4 文本近似比对

#### `RapidFuzz`

- 适合用途：
  - 字符串模糊匹配
  - Levenshtein / Jaro-Winkler / partial ratio 等近似度计算
- 为什么适合：
  - 对品牌词、店铺名、商品标题的近似判断很直接
  - 性能和工程成熟度都不错
- 在证证鸽中的建议用途：
  - “阿迪达斯 / 阿波达斯”这类商标近似检测
  - 标题、品牌字段、文案文本的第一层评分
- 官方仓库：
  - https://github.com/rapidfuzz/RapidFuzz
- 许可证：
  - MIT

#### `pypinyin`

- 适合用途：
  - 中文转拼音
  - 多音字处理
- 为什么适合：
  - 中文品牌冒用、谐音、拼音变体场景很常见
- 在证证鸽中的建议用途：
  - 品牌词标准化
  - 拼音辅助近似比对
  - 中文品牌词的规则增强
- 官方仓库：
  - https://github.com/mozillazg/python-pinyin
- 许可证：
  - MIT

### 2.5 图片近似与视觉比对

#### `imagehash`

- 适合用途：
  - 感知哈希
  - 图像近似快速判断
- 为什么适合：
  - 轻量、简单，适合 P0 阶段
  - 可用于 logo、商品图样的快速预筛
- 在证证鸽中的建议用途：
  - 商标图样初筛
  - 商品图近似预检测
- 官方仓库：
  - https://github.com/JohannesBuchner/imagehash
- 许可证：
  - BSD-2-Clause（以项目为准，接入前再核一次 LICENSE）

#### `pixelmatch`

- 适合用途：
  - 两张截图做像素级差异比对
- 为什么适合：
  - 如果要做“页面前后变化对比图”，很好用
- 在证证鸽中的建议用途：
  - 差异可视化
  - 监控任务中展示“页面哪一块变了”
- 官方仓库：
  - https://github.com/mapbox/pixelmatch
- 许可证：
  - ISC

## 3. 文书与导出能力

### 3.1 Word 模板渲染

#### `python-docx-template` / `docxtpl`

- 适合用途：
  - 基于 Word 模板填充变量
  - 输出律师函、投诉函、举报材料等 `.docx`
- 为什么适合：
  - 非常符合“模板 + 结构化案件数据”的文书生成模式
  - 比纯 LLM 自由生成更稳定
- 在证证鸽中的建议用途：
  - 文书模板引擎主力
  - 生成律师函 / 平台投诉函 / 举报材料草稿
- 官方仓库：
  - https://github.com/elapouya/python-docx-template
- 许可证：
  - LGPL-2.1
- 注意事项：
  - 这是个很好用的库，但因为许可证是 LGPL，正式商用前建议再做一次许可评估。

#### `python-docx`

- 适合用途：
  - 读写 `.docx`
  - 处理标题、段落、表格、格式
- 为什么适合：
  - 可以和 `docxtpl` 配合使用
  - 适合做导出后修整、附加证据目录等
- 在证证鸽中的建议用途：
  - 导出后补充格式
  - 插入证据摘要、页码、附录
- 官方仓库：
  - https://github.com/python-openxml/python-docx
- 许可证：
  - MIT

#### `Jinja`

- 适合用途：
  - 模板渲染
  - 文书变量填充
- 为什么适合：
  - `docxtpl` 底层就是基于 Jinja
- 官方仓库：
  - https://github.com/pallets/jinja
- 许可证：
  - BSD-3-Clause
- 注意事项：
  - 不建议把“用户可任意上传的 Jinja 模板”作为 P0 能力，因为 Jinja 的 sandbox 和模板执行安全需要额外谨慎处理。

### 3.2 PDF 导出

#### `WeasyPrint`

- 适合用途：
  - HTML/CSS 转 PDF
- 在证证鸽中的建议用途：
  - 把案件摘要或导出的 HTML 材料生成 PDF
- 官方仓库：
  - https://github.com/Kozea/WeasyPrint
- 许可证：
  - BSD

#### `Gotenberg`

- 适合用途：
  - 文档/HTML/Markdown 转 PDF
  - 统一文档输出服务
- 在证证鸽中的建议用途：
  - 服务化 PDF 导出
  - 将 Word / HTML 统一输出为 PDF
- 官方仓库：
  - https://github.com/gotenberg/gotenberg
- 许可证：
  - MIT
- 备注：
  - 如果第一版已经能通过 LibreOffice 稳定转 PDF，可以先不接 Gotenberg。

## 4. 通知与机器人

### 4.1 多通道通知

#### `Apprise`

- 适合用途：
  - 统一封装多种通知渠道
  - 邮件、Webhook、自定义 JSON 推送
- 为什么适合：
  - 你们第一版需要邮箱，而且后续可能还要扩展更多通道
- 在证证鸽中的建议用途：
  - 邮件发送
  - 通过 JSON/Webhook 转发到自建通知适配层
- 官方仓库：
  - https://github.com/caronc/apprise
- Wiki：
  - https://github.com/caronc/apprise/wiki
- 许可证：
  - BSD-2-Clause
- 备注：
  - 我当前没有查到 Apprise 官方 Wiki 里明确列出 DingTalk 原生插件，但它支持邮件和自定义 JSON / Webhook，这已经足够做通知总线。

#### `Apprise API`

- 适合用途：
  - 把 Apprise 包装成 REST 服务
- 在证证鸽中的建议用途：
  - 做成内部通知服务
- 官方仓库：
  - https://github.com/caronc/apprise-api

### 4.2 钉钉机器人

#### `DingtalkChatbot`

- 适合用途：
  - 钉钉群自定义机器人消息发送
  - Text / Markdown / ActionCard 等消息
- 为什么适合：
  - 第一版做通知和受限动作触发很方便
- 在证证鸽中的建议用途：
  - 风险预警推送
  - “查看详情”“生成律师函”等动作卡片
- 官方仓库：
  - https://github.com/zhuifengshen/DingtalkChatbot
- 备注：
  - 更适合“推送型机器人”

#### `open-dingtalk/dingtalk-stream-sdk-python`

- 适合用途：
  - 钉钉 Stream 模式机器人
  - 收消息、回调、交互式机器人
- 为什么适合：
  - 如果你们后续希望钉钉里做有限交互，这个比纯 webhook 更强
- 在证证鸽中的建议用途：
  - 受限动作型 Bot
  - 用户在钉钉里触发“生成材料”“查看摘要”
- 官方仓库：
  - https://github.com/open-dingtalk/dingtalk-stream-sdk-python
- 备注：
  - 第一版如果时间紧，先用 webhook 推送；交互式机器人可放到下一阶段。

## 5. 抓取与内容抽取增强

### 5.1 抓取框架

#### `Scrapy`

- 适合用途：
  - 批量抓取
  - 结构化抽取
  - 爬虫任务管理
- 为什么适合：
  - 如果后续页面抓取越来越多，可以把部分“站点巡检”从 Playwright 单跑升级为 Scrapy + Playwright 混合方案
- 官方仓库：
  - https://github.com/scrapy/scrapy
- 许可证：
  - BSD-3-Clause

#### `Crawl4AI`

- 适合用途：
  - LLM-friendly 网页爬取
  - 动态站点抓取
  - Markdown 提取、截图、结构化抽取
- 为什么适合：
  - 如果后续想把“网页 -> 结构化案件摘要”做得更强，可以直接借力
- 官方仓库：
  - https://github.com/unclecode/crawl4ai
- 许可证：
  - 以仓库 LICENSE 为准，接入前再核一次
- 备注：
  - 第一版不是必需，但很适合作为增强抓取层。

#### `Mercury Parser`

- 适合用途：
  - 提取网页正文、标题、摘要等“人类关心的内容”
- 官方仓库：
  - https://github.com/thoraxe/mercury-parser
- 适合场景：
  - 品牌官网文章、说明页、资讯页的正文抽取
- 备注：
  - 对电商商品页未必最优，但对于文章类侵权内容很有价值。

## 6. 语义与多模态增强

### 6.1 文本语义相似度

#### `sentence-transformers`

- 适合用途：
  - 句向量
  - 语义相似检索
- 为什么适合：
  - 如果后续不仅看品牌词，还要比较文案语义、侵权描述与案例文本相似性，它很有用
- 官方仓库：
  - https://github.com/huggingface/sentence-transformers
- 许可证：
  - Apache-2.0

### 6.2 图文联合相似

#### `openai/CLIP`

- 适合用途：
  - 图像和文本联合 embedding
- 官方仓库：
  - https://github.com/openai/CLIP

#### `mlfoundations/open_clip`

- 适合用途：
  - 开源 CLIP 实现
  - 模型选择更灵活
- 官方仓库：
  - https://github.com/mlfoundations/open_clip

#### `imagededup`

- 适合用途：
  - 图像近似、重复图像和近重复图像检测
  - 支持哈希和 CNN
- 为什么适合：
  - 比 `imagehash` 更完整，适合后续升级
- 官方仓库：
  - https://github.com/idealo/imagededup
- 许可证：
  - Apache-2.0

## 7. Agent / 工作流编排

### 7.1 当前主方案

#### `Hermes Agent`

- 适合用途：
  - 后端任务编排
  - 定时巡检
  - 消息推送触发
  - 工具调用
  - 文书生成与案件工作流串联
- 在证证鸽中的建议用途：
  - 作为后端编排中枢，而不是开放聊天入口
  - 自动监测模式主引擎
  - 文书生成任务编排
  - 通知触发
  - 驱动“取证 -> 风险分析 -> 推送 -> 文书草稿 -> 审核回流”的后台链路
- 官方仓库：
  - https://github.com/NousResearch/hermes-agent

### 7.2 可选替代 / 参考

#### `LangGraph`

- 适合用途：
  - 状态机式 Agent 编排
  - 人在回路
  - 长流程可视化
- 适合场景：
  - 如果后续发现 Hermes 不够适合复杂审批流，LangGraph 可作为替代或参考
- 官方仓库：
  - https://github.com/langchain-ai/langgraph

## 8. 推荐的初版技术组合

如果目标是尽快把第一版做出来，推荐如下：

### 8.1 P0 最小闭环

- 插件：`Plasmo`
- 页面抓取：`Playwright`
- 文本近似：`RapidFuzz + pypinyin`
- 图片近似：`imagehash`
- 文书：`docxtpl + python-docx`
- 通知：`Apprise + DingtalkChatbot`
- 编排：`Hermes Agent`

### 8.2 P1 增强

- 自动监测参考：`changedetection.io`
- 抓取增强：`Crawl4AI`
- 语义增强：`sentence-transformers`
- 图像增强：`imagededup`

## 9. 明确不建议第一版重度投入的方向

以下能力虽然有价值，但不建议在第一版花大量时间：

- 发明专利技术方案自动判侵
- 全量全网监控
- 多法域文书体系
- 完整公证/法院系统对接
- 开放式钉钉自由聊天机器人
- 大规模自训练模型

## 10. 接入注意事项

### 10.1 许可问题

重点注意：

- `python-docx-template` 为 LGPL-2.1，正式商用前建议再核一次合规策略
- 其他主力候选多数为 MIT / Apache / BSD，整体较友好

### 10.2 安全问题

- 不建议让用户上传任意可执行模板
- 不建议让机器人直接暴露底层 Agent 工具
- 所有文书生成结果都应进入人工审核流

### 10.3 第一版工程建议

不要试图“整合所有开源项目”。  
更好的方式是：

- 核心链路用最少组件打通
- 增强能力放在下一阶段
- 能直接落地的先上，重型平台先借鉴设计思路

## 11. 建议的下一步

基于这份清单，下一步最适合做的是：

1. 确认 `P0 技术栈`
2. 画出系统模块与调用关系
3. 拆分开发任务
4. 决定哪些能力“直接接入”，哪些能力“只借鉴”
