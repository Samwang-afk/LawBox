<div align="center">

# LawBox

### One Legal Skill. The whole legal workflow.

**A Legal Work OS for AI Agents.**

万物皆插件，越做越聪明的自我进化法律skill内核&框架

[![Core](https://img.shields.io/badge/Core-v1.0.0-7f1d1d)](#)
[![Legal Skills](https://img.shields.io/badge/Legal%20Skills-58-374151)](#)
[![License](https://img.shields.io/badge/License-PolyForm%20NC%201.0.0-374151)](LICENSE)

</div>

> **LawBox doesn't teach AI to sound like a lawyer. It gives Agents a legal way of working.**

AI 已经会写合同、总结案情、找法条、生成文书。

真正的问题是：**它知不知道什么时候不该直接写？**

客户可能只讲了一半事实；法律关系可能被当事人叫错；关键证据可能缺失；法条可能失效；一份看起来完整的起诉状，事实、请求、要件与证据链却没有真正闭合。

LawBox 解决的不是“让答案更像律师”。

它把法律工作中最容易被模型跳过的部分——**澄清、事实状态、法律核验、反向复核、授权边界与交付质量**——变成 Agent 可以执行的工作协议。

**58 skills inside. One interface outside.**

---

## One Legal Skill is enough.

你不应该先学习几十个 Skill，再决定该调用哪一个。

```text
你
│
▼
LawBox
│
├─ 理解任务
├─ 判断风险与所需推理深度
├─ 只追问真正会改变结论的问题
├─ 路由专业 Legal Skills
├─ 核验关键法律来源
├─ Challenge 当前结论
└─ 控制正式交付与外部动作
│
▼
法律工作成果
```

仓库根目录 [`SKILL.md`](SKILL.md) 提供统一入口；[`法律工作总控`](skills/legal/法律工作总控/SKILL.md) 负责路由与共享协议。

**Complexity belongs inside the system, not inside the user's head.**

### 58 built-in skills

| 01–10 | 11–20 | 21–30 | 31–40 | 41–50 | 51–58 |
| --- | --- | --- | --- | --- | --- |
| 法律工作总控 | 立案管理 | 案件沟通记录 | 简易速裁程序 | 产品法务 | 破产清算 |
| 法律文书出稿前审查 | 诉讼文书起草 | 案件讨论与提纲 | 特殊程序 | 广告合规审核 | 破产和解程序 |
| 法律文书模板与导出 | 调查取证与证据管理 | 刑事辩护总调度 | 劳动争议诉讼 | 预包装食品标签合规 | 破产法律分析 |
| 案件材料生成专业文档 | 庭前准备 | 案件承接与委托 | 劳动争议仲裁程序管理 | 监管合规监测 | 破产文书生成 |
| 法律咨询助手 | 庭审与庭后工作 | 侦查阶段辩护 | 劳动争议证据体系 | 破产申请与受理 | 审理报告 |
| 初步法律分析 | 调解与和解 | 审查起诉阶段辩护 | 劳动关系认定与经济补偿计算 | 管理人工作 | 民事判决书 |
| 法规案例检索 | 结案归档 | 一审阶段辩护 | 用人单位劳动合规 | 债权申报与审查 | law-to-markdown |
| 法律Wiki知识库查询 | 诉讼案件管理 | 二审阶段辩护 | 合同审查 | 债权人会议 | 微信文章转换为markdown |
| 法律文章去AI味道 | 诉讼分析工具 | 未成年人案件 | 合同起草 | 财产调查与管理 |  |
| 民事一审诉讼 | 诉讼可视化 | 死刑案件 | 委托合同管理 | 重整程序 |  |

---

## Before trusting a conclusion, try to break it.

普通 Agent 往往是：

```text
Question → Reason → Answer
```

LawBox 在复杂事项中多一步：

```text
Question → Reason → Challenge → Judgment → Draft
```

这来自 LawBox 中的轻量 **Ludus Adversarial Review**。

它不是为了机械生成“正方 / 反方”，也不是 Multi-Agent 表演。

它只做一件事：**falsification**。

> 用户对法律关系的命名可能错吗？  
> 有没有另一套合理事实解释？  
> 对方最强的抗辩是什么？  
> 哪个事实、证据或法律要件一旦失败，结论就会倒塌？

复核最终要找到具体的 **Minimum Failure Set**，而不是一句“仍存在一定风险”。

简单问题不会被强行做重。LawBox 按 L0–L3 选择满足风险的最低充分推理等级。

**Use the smallest workflow that is sufficient for the risk.**

---

## Everything is a Plugin.

Core 负责“法律工作应该如何被完成”。

专业领域负责“你拥有什么专业能力”。

```text
LawBox Core
    │
    ├── built-in legal skills
    ├── Domain Packs
    └── Your Firm Pack
```

Domain Pack 可以挂载新的专业 Skill，并继承总控的 clarification、review、approval、lifecycle 与 delivery rules。

仓库已提供 [`packs/ip-law/`](packs/ip-law/) 作为 Pack 结构示例；当前仅为 skeleton，不包含完整 IP 法律内容。

这意味着未来可以把律所自己的 SOP、模板、审查方法与专业 know-how 放进 Pack，而不是不断侵入 Core。

**Core defines the method. Plugins bring the expertise.**

---

## What it feels like

### Litigation

```text
“这是客户发来的微信、借条和转账记录。
帮我判断现在起诉最大的风险是什么。”
```

LawBox 不会直接给一个胜诉率。

它会先区分已确认事实、当事人陈述、争议事实与未知信息，再检查证据、法律关系与请求权基础；如果属于复杂事项，再主动寻找最可能推翻当前判断的路径。

### Contract Review

```text
“我是乙方，帮我审这份 SaaS 服务合同。”
```

LawBox 先确认立场，再进入专业合同审查；需要正式 Word 交付时，继续经过预审、导出与质量检查，而不是把“内容生成完成”当作“法律工作完成”。

---

## Architecture

```text
User
 │
 ▼
LawBox / Legal Work OS
 │
 ├─ Routing
 ├─ Matter & Fact Model
 ├─ Clarification
 ├─ Legal Verification
 ├─ Professional Skills
 ├─ Ludus Review
 ├─ Approval Gate
 └─ Delivery QC
 │
 ▼
Deliverable
```

关键协议位于 [`skills/legal/法律工作总控/references/`](skills/legal/法律工作总控/references/)。

测试入口：

```bash
python tests/run_all_tests.py
```

---

## Install

```bash
git clone https://github.com/Samwang-afk/LawBox.git
```

将 `skills/legal/` 接入支持本地 Markdown Skill 的 Agent 环境，或使用仓库中的 `.codex-plugin/plugin.json`。

然后直接描述你的法律任务。

不是：

```text
“我要先调用哪个 Skill？”
```

而是：

```text
“帮我处理这个案子。”
```

---

## Professional boundary

LawBox 是法律工作辅助系统，不是“AI 律师”。

真实法律事项仍需要律师、法务或具备相应资格的专业人士完成事实判断、来源核验、策略选择、客户授权与最终文本复核。组织级利益冲突检索、商业数据库、外部系统写入等能力如果没有真实连接，LawBox 会明确标记未执行，而不是假装完成。

---

## License & attribution

当前项目维护者拥有版权的新创作内容采用 [PolyForm Noncommercial License 1.0.0](LICENSE)。

本项目包含或衍生自 [`pa1nrui1/legal-skills`](https://github.com/pa1nrui1/legal-skills) 的 MIT 授权内容；相关上游权利、Intermediate Fork Required Notice 与其他第三方说明见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) 和 [`LICENSES/`](LICENSES/)。

---

<div align="center">

**LawBox runs the work.**  
**Ludus challenges the conclusion.**  
**Everything else is a plugin.**

</div>
