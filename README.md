<div align="center">

# LawBox

### One Legal Skill. The whole legal workflow.

**A Legal Work OS for AI Agents.**

法律 Skill，一个就够了。

![Core](https://img.shields.io/badge/Core-v1.0.0-7f1d1d)
![Legal Skills](https://img.shields.io/badge/Legal%20Skills-58-374151)
![License](https://img.shields.io/badge/License-PolyForm%20NC%201.0.0-374151)

</div>

> **LawBox doesn't teach AI to sound like a lawyer. It gives Agents a legal way of working.**
>
> 从材料读取、事实状态、最小必要澄清、法律研究，到反向复核、授权边界和正式交付质量门——把真正决定法律工作可靠性的部分，变成 Agent 可以执行的工作协议。

**58 skills inside. One interface outside.**

> [!IMPORTANT]
> **LawBox 不提供法律意见，也不是“AI 律师”。** 输出应视为供律师、法务或具备相应资格的专业人士复核的工作草稿。真实法律事项仍需要基于完整事实、有效授权、现行法律、可核验案例与具体语境作出独立专业判断。

---

## AI 已经会写。真正危险的是，它太早开始写。

合同能改，案情能总结，法条能找到，起诉状也能生成。

但法律工作的失败，往往不是因为文字不够像律师，而是因为在生成文字之前，有些事情根本没有被处理：

- 客户只讲了一半事实，模型已经开始下结论；
- 当事人说“这是借贷”，模型就把法律关系当成已经确定；
- 一条看起来正确的法规，可能已经失效、适用地域错误，或者根本没有完成来源核验；
- 一个证据缺口足以让请求权基础失效，但没有人把它标成致命缺口；
- 合同还没确认代表甲方还是乙方，就开始“优化条款”；
- 起诉状写得很顺，却没有闭合事实、请求、要件、证据和举证责任；
- 模型完成了一套漂亮分析，却从来没有认真站到对方一侧尝试把它推翻；
- “分析完成”被误当成“已经获得发送、提交、签署或修改正式记录的授权”；
- 每个新任务都重新 Prompt、重新教 SOP、重新解释什么能做、什么不能做；
- 装了几十个法律 Skill，最后仍然要律师自己判断这次该调用哪个、按什么顺序调用。

**AI 不缺一个更长的 Prompt。它缺一套真正的工作方法。**

LawBox 把这套方法放在专业 Skills 之上。

---

## 30 秒理解 LawBox

LawBox 是面向中国法律工作的模块化 **Legal Work OS**。

它不是另一个法律聊天机器人，也不是把 58 个 Skill 摆在用户面前的工具箱。

用户面对的是一个统一入口；系统内部再决定工作如何完成。

```text
你的法律任务
    │
    ▼
  LawBox
    │
    ├─ 这到底是一个简单问题，还是一个正式 Matter？
    ├─ 现有材料够不够？哪些只是当事人主张？
    ├─ 哪几个未知信息真的会改变决策？
    ├─ 应该调用哪个专业法律 Skill？
    ├─ 法律依据是否完成核验？
    ├─ 当前结论最容易在哪里被推翻？
    ├─ 是否已经得到对外执行授权？
    └─ 正式交付物是否真正通过质量门？
    │
    ▼
  可复核的法律工作成果
```

仓库根目录的 [`SKILL.md`](SKILL.md) 是统一入口协议：它要求 Agent 首先读取 [`法律工作总控`](skills/legal/法律工作总控/SKILL.md)，由总控负责共享规则和路由，再进入具体专业 Skill。

**复杂留给系统，简单留给律师。**

---

# One Legal Skill is Enough.

传统 Skill Pack 常常把架构复杂度直接交给用户：

```text
用户
├─ 这次该用合同审查？
├─ 还是法规检索？
├─ 还是初步法律分析？
├─ 还是证据管理？
├─ 诉讼 Skill 应该先跑哪一个？
├─ 什么时候需要反方复核？
└─ 谁负责最后检查？
```

LawBox 的产品心智不同：

```text
用户
  │
  ▼
LawBox
  │
  ├─ 理解任务
  ├─ 选择最低充分推理等级
  ├─ 路由专业能力
  ├─ 只澄清 Blocking Unknown
  ├─ 必要时进行 Ludus Challenge
  ├─ 控制 Action / Approval Gate
  └─ 执行 Delivery QC
  │
  ▼
交付
```

LawBox 内部拥有大量专业法律 Skill，但你不需要先学习它们。

**58 个 Skills 是 LawBox 的能力，不是用户的认知负担。**

> **Complexity belongs inside the system, not inside the user's head.**

当然，开发者和专业用户仍然可以直接调用具体 Skill。统一入口是默认体验，不是对底层能力的封锁。

---

## 普通 AI 与 LawBox 的区别

### 普通 AI

```text
“帮我看看这个案子能不能赢”
        │
        ▼
读取部分材料
        │
        ▼
开始分析
        │
        ▼
生成一个很有自信的答案
```

### LawBox

```text
“帮我看看这个案子能不能赢”
        │
        ▼
识别 Task / Matter
        │
        ▼
完整读取与来源边界
        │
        ▼
事实状态建模
CONFIRMED / ASSERTED / DISPUTED / INFERRED / UNKNOWN
        │
        ▼
只追问真正改变决策的 Blocking Unknown
        │
        ▼
专业法律分析 / 证据分析 / 法源核验
        │
        ▼
Ludus：主动寻找推翻当前判断的路径
        │
        ▼
Judgment + 起草许可
PASS / CONDITIONAL / BLOCKED
        │
        ▼
需要外部行为？→ 用户明确授权
        │
        ▼
正式文书 → Preflight → DOCX / Redline → Health Check
```

这不是为了让流程更复杂。

这是为了让**该省略的步骤被省略，该阻断的风险被阻断**。

---

## Minimum Sufficient Workflow

专业 workflow 不应该等于 bureaucratic workflow。

LawBox 会先按任务的**决策复杂度、不确定性和后果**选择最低充分推理等级，而不是按任务长度决定“要不要上重流程”。

| Level | 仓库定义 | 典型情况 | 主要流程 |
| --- | --- | --- | --- |
| **L0 — Direct** | 简单、明确的法律知识问题 | 单一问题，几乎不依赖个案事实 | 必要事实确认 → 必要法律来源核验 → 直接回答 |
| **L1 — Standard** | 普通合同、简单案件、简单文书 | 事实结构较清楚，无显著竞争性路径 | 读取 → 简化 Matter Model → 必要澄清 → 专业 Skill |
| **L2 — Deliberative** | 存在竞争性法律关系、争议事实或策略选择 | 胜诉分析、责任判断、诉请/抗辩/程序策略 | 完整 Matter Model → Clarification → 分析 → Challenge → Judgment |
| **L3 — Adversarial** | 高影响、高不确定、重大或不可逆事项 | 重大诉讼、正式法律意见、重大交易风险等 | L2 + 反向法规/不利案例检索 + 最强对方论证 + Minimum Failure Set |

例如，“劳动合同试用期最长多久？”不应该启动完整 Matter、利益冲突检查和对抗审议。按仓库协议，它属于 L0：完成必要法律来源核验后直接回答。

> **Use the smallest workflow that is sufficient for the risk.**

详见 [`reasoning-mode-protocol.md`](skills/legal/法律工作总控/references/reasoning-mode-protocol.md)。

---

# Before trusting a conclusion, try to break it.

## Ludus-style Adversarial Reasoning

普通 Agent 的默认路径通常接近：

```text
Question → Reason → Answer
```

LawBox 为复杂法律事项增加一个关键动作：**Challenge**。

```text
Question
   │
   ▼
Reason
   │
   ▼
Challenge
   │
   ▼
Try to break the conclusion
   │
   ▼
Judgment
   │
   ▼
Draft / Decision
```

这里的 Ludus 不是为了机械地产生“正方 / 反方”，也不是为了让多个 Agent 表演讨论。

当前仓库实现的是一个**轻量反向复核机制**：由当前 Agent 以角色隔离方式执行，不要求额外的完整 Ludus Agent Framework，也不创建独立 Agent 群。

它只做一件事：**falsification**。

对核心判断固定检查：

```text
1. 用户对法律关系的命名可能错吗？
2. 有没有合理的竞争性事实解释？
3. 对方最强的抗辩是什么？
4. 哪个事实、证据或法律要件一旦失败会推翻结论？
5. 是否存在时效、管辖、主体、程序或举证责任障碍？
```

并进一步寻找 **Minimum Failure Set**：

> 让当前结论失效所需要否定、改变或无法证明的最小条件集合是什么？

所以这类输出没有意义：

```text
“仍存在一定风险。”
“法院可能有不同观点。”
“结果存在不确定性。”
```

LawBox 要求的是具体失败机制：**哪个要件、哪份证据、哪条规则、以什么方式让结论倒塌。**

如果不存在实质反例，也不制造“平衡感”：协议要求直接说明未发现足以实质动摇当前判断的反向路径。

完整规则见 [`adversarial-review-protocol.md`](skills/legal/法律工作总控/references/adversarial-review-protocol.md)。可执行的确定性参照实现位于 [`reasoning_control.py`](skills/legal/法律工作总控/scripts/reasoning_control.py)。

> LawBox implements a broader Ludus idea: **don't just make Agents answer better — make them challenge their own decisions.**

---

## 法律工作不是一句 Prompt

LawBox 的总控层把跨专业领域都需要的规则集中起来，让子 Skill 专注于专业业务本身。

### 1. Clarification：只问真正重要的问题

信息缺失不等于必须追问。

只有同时满足“会改变决策”且“无法从现有材料或研究解决”的未知，才成为 **Blocking Unknown**。单轮原则上只问 1–5 个，并按照：

```text
Decision-changing
    > Scope-changing
    > Evidence-changing
    > Output-changing
    > Formatting
```

排序。

### 2. Matter Model：主张不是事实

个案事实强制区分：

```text
CONFIRMED   已核实
ASSERTED    当事人主张
DISPUTED    存在争议
INFERRED    模型推断
UNKNOWN     未知
```

“对方借了我 20 万”不能因为用户这样描述，就被静默升级成“已经确认存在民间借贷法律关系”。

### 3. Legal Verification：来源边界优先于流畅表达

涉及中国法律法规、规章、政策文件和法条援引时，总控协议要求完成名称、编号、内容和时效性核验，并形成法规校验摘要。

仓库包含相应的北大法宝 MCP/API **核验协议**；它不等于仓库自带商业数据库权限、API 凭证或已经连接的外部服务。没有实际数据源时，不得假装已经核验。

### 4. Action / Approval Gate：分析不等于授权

发送、提交、签署、接受和解、放弃权利、产生费用、删除或覆盖正式资料等外部有效行为，需要明确授权。

### 5. Matter Lifecycle：案件不是一次性聊天

正式事项共享六个状态：

```text
INTAKE → ACTIVE → WAITING → REVIEW → DELIVERED → CLOSED
```

并维护 `status / next_action / pending_from / deadline / owner` 等最低字段。

### 6. Delivery QA：写完，不等于完成

正式 `.docx` 或正式法律成果需要经过对应模板、来源边界、出稿前审查和交付链。

普通线性 DOCX 的核心链路为：

```text
draft.html
    ↓
preflight-meta.json
    ↓
draft_checked.html
    ↓
html_to_docx.py
    ↓
health_check.py
```

要素式起诉状使用母版克隆填充；合同审查支持 Word 修订模式红线稿及 redline QA。正式成果只有通过对应 Gate 后，才应该被称为正式交付物。

---

# Everything is a Plugin.

## 万物皆插件。

法律专业领域会不断增长，但 Core 不应该无限膨胀。

LawBox 的方向是让 **Core 定义法律工作如何被可靠执行，Domain Pack 定义某个专业领域知道什么、怎么做。**

```text
LawBox Core
│
├── Built-in Legal Skills
│   ├── Litigation
│   ├── Criminal Defense
│   ├── Labor
│   ├── Contracts
│   ├── Bankruptcy
│   ├── Compliance
│   └── Legal Research / Delivery
│
└── Domain Packs
    ├── IP Law Pack          ← repository skeleton example
    ├── M&A Pack             ← possible extension, not bundled
    ├── Data Privacy Pack    ← possible extension, not bundled
    └── Your Firm Pack       ← architecture direction
```

Domain Pack 的目标是：

- 可安装；
- 可替换；
- 可卸载；
- 可组合；
- 尽量不侵入 Core；
- 专业 Skill 自动继承统一的 clarification / adversarial review / approval / lifecycle / reflection / delivery gate；
- 专业 Pack 只负责自己的业务知识与 SOP，不重复实现总控协议。

仓库已经提供 [`packs/ip-law/`](packs/ip-law/) 作为 **Domain Pack 示例骨架**，包含 `pack.json`、`README.md` 与 `skills/` 目录；当前状态是 `skeleton`，**不包含实际 IP 法律内容**。

### Your Firm Pack

这是插件化真正有价值的方向：把律所或法务团队自己的方法做成私有 Pack，而不是不停修改 Core。

例如可以承载：

```text
Your Firm Pack
├── 内部 SOP
├── 审查 checklist
├── 合同范本 / 文书模板
├── 行业 know-how
├── 专业领域 Skills
├── 私有知识源适配
├── 工具 / MCP 接入协议
└── 团队自己的路由规则
```

这些是 **Domain Pack 架构允许承载的扩展方向**，不是本仓库已经内置的私有数据库、MCP 或自动化服务。

> **Core defines how legal work is controlled. Plugins define the specialized work you bring into it.**

挂载约定见 [`sop-contract.md`](skills/legal/法律工作总控/references/sop-contract.md) 与 [`packs/ip-law/README.md`](packs/ip-law/README.md)。

---

## 把法律工作交给 LawBox，而不是调用命令

### Litigation — 找出真正会输在哪里

```text
这是客户发来的全部微信记录、借条和转账记录。
帮我判断现在起诉的最大风险是什么。
```

LawBox 会根据任务实际复杂度组织流程，例如：

```text
材料完整读取
→ Matter Model / 事实状态
→ Blocking Unknown
→ 法律关系与请求权基础
→ 证据链 / 举证责任
→ 法源核验
→ Ludus Challenge
→ Judgment
→ Litigation Strategy
```

重点不是给出一个“胜率数字”，而是识别**哪一个事实、证据、程序或法律要件最可能让当前方案失效**。

### Contract Review — 先确认你站哪边

```text
我是乙方，帮我审这份 SaaS 服务合同。
```

```text
审查立场确认
→ 完整读取
→ 条款风险
→ 商业风险
→ 修改建议
→ 需要时生成 Word redline
→ Redline QA
```

仓库的合同审查流程把甲方 / 乙方 / 中立立场作为前置硬门，而不是默认一个“看起来公平”的修改方向。

### Legal Research — 不把记忆当法源

```text
客户准备在中国大陆上线这个业务模式。
先帮我找出可能的监管问题和需要进一步核验的法律依据。
```

LawBox 会把“模型已有知识”“已读取材料”“已核验法律来源”和“仍未核验内容”分开处理，而不是让一段流畅回答掩盖来源边界。

### Formal Deliverable — 文本写完只是中间状态

```text
基于当前案件材料，整理一份准备提交客户的正式法律分析报告。
```

对于正式法律交付物，总控先分类成果类型，再要求读取/法规/模板/来源边界/用户确认记录满足相应硬门；需要 Word 交付时还必须经过 preflight、导出与结构体检。

---

## Built-in capabilities

你不需要逐个调用这些能力；LawBox 会进行语义路由。下面按工作域展示仓库现有能力，而不是把 58 个 Skill 全部堆在首屏。

| Domain | Built-in capabilities |
| --- | --- |
| **Control & Delivery** | 法律工作总控、出稿前审查、法律文书模板与 DOCX 导出、案件材料生成专业文档 |
| **Consulting & Research** | 法律咨询、初步法律分析、法规案例检索、法律 Wiki 查询 |
| **Civil Litigation** | 民事一审、立案、诉讼文书、调查取证与证据、庭前/庭审/庭后、调解和解、案件管理、诉讼分析与可视化 |
| **Criminal Defense** | 刑辩总调度、委托、侦查、审查起诉、一审、二审、未成年人、死刑、简易速裁、特殊程序 |
| **Labor** | 劳动争议诉讼、仲裁管理、证据体系、劳动关系与经济补偿、用人单位劳动合规 |
| **Contracts & Transactions** | 合同审查、合同起草、委托合同管理 |
| **Product & Compliance** | 产品法务、广告合规、预包装食品标签合规、监管合规监测 |
| **Bankruptcy** | 申请与受理、管理人、债权、债权人会议、财产、重整、清算、和解、法律分析、文书 |
| **Court Documents & Utilities** | 审理报告、民事判决书、law-to-markdown、微信文章转 Markdown |

<details>
<summary><strong>为什么不在这里展开 58 个 Skill？</strong></summary>

因为它们是实现层能力，而不是用户需要背下来的菜单。

如果你在开发、调试或定制路由，请直接查看 [`skills/legal/`](skills/legal/) 中各 Skill 的 `SKILL.md` 与 `references/`。

</details>

---

## Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                         User                            │
│              One legal-work entry point                │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  法律工作总控 / Core Control             │
│                                                         │
│  Routing · Intake · Matter · Reading · Clarification    │
│  Fact Status · Source Boundary · Lifecycle · Approval   │
└──────────────────────────┬──────────────────────────────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
┌────────────────────────┐  ┌────────────────────────────┐
│ Built-in Legal Skills  │  │ Domain Packs / Plugins     │
│ 58 professional skills │  │ optional specialist packs  │
└────────────┬───────────┘  └──────────────┬─────────────┘
             └──────────────┬──────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                 Reasoning Control                       │
│                                                         │
│  L0 Direct · L1 Standard · L2 Deliberative · L3 Adv.   │
│  Matter Model · Ludus Challenge · Judgment             │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 Action / Approval Gate                  │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Delivery Quality                     │
│   Preflight · DOCX · Redline QA · Health Check         │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                Post-task Reflection                     │
│  reusable + de-identified failures → knowledge/lessons │
└─────────────────────────────────────────────────────────┘
```

### Repository map

```text
.
├── README.md
├── SKILL.md                         # unified repository entry
├── AGENTS.md                        # repository-wide hard gates
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── LICENSES/
│   └── upstream-MIT.txt
├── knowledge/
│   └── lessons.md                   # de-identified reusable failures only
├── skills/legal/
│   ├── 法律工作总控/
│   │   ├── SKILL.md                 # router + shared control layer
│   │   ├── references/              # control protocols
│   │   └── scripts/                 # reasoning_control.py + tests
│   └── ...                          # 58 professional legal skills
├── packs/
│   └── ip-law/                      # Domain Pack skeleton example
├── tests/
│   ├── test_behavioral_benchmark.py
│   └── run_all_tests.py
├── assets/
└── .codex-plugin/
    └── plugin.json
```

---

## Installation

### 1. Clone

```bash
git clone https://github.com/Samwang-afk/LawBox.git
cd LawBox
```

### 2. Expose LawBox to your Agent runtime

LawBox is organized around Markdown `SKILL.md` files.

- The repository includes a Codex plugin manifest at [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json).
- For a runtime that supports local `SKILL.md`-style skills, load/copy the relevant repository or `skills/legal/` directory according to that runtime's own discovery rules.
- Runtime behavior differs. A generic Markdown Skill layout does **not** imply that every platform supports the same file access, scripts, MCP connections, DOCX tooling or approval semantics automatically.

### 3. Use one entry

Prefer the unified LawBox entry rather than manually selecting sub-skills:

```text
法律工作总控 帮我处理这个法律任务，并选择最低充分工作流。
```

Then describe the work normally:

```text
这是客户给我的全部材料。先不要写起诉状，先告诉我当前方案最可能在哪里失败。
```

```text
我是乙方。审这份合同，需要时给我 Word 修订稿，但任何对外发送都先问我。
```

```text
这是一个简单法律问题。核验现行依据后直接回答，不要把流程做重。
```

---

## Production setup

真实业务使用前，至少应完成：

- 律师 / 法务身份和工作方式配置；
- 工作区与当前事项路径配置，例如 `LEGAL_WORKSPACE`、`LEGAL_CURRENT_MATTER`；
- 适用模板库配置；
- 需要法律数据库或外部工具时，配置你实际有权使用的数据源 / MCP / API；
- 明确哪些行为需要人工批准；
- 确认本地运行环境具备对应的文档、OCR、DOCX 或其他外部工具依赖。

不要把真实客户材料、案件卷宗、API Key、商业数据库凭证、本机私有路径或其他敏感配置提交到公开仓库。

---

## Verification & tests

仓库包含：

- [`tests/test_behavioral_benchmark.py`](tests/test_behavioral_benchmark.py)：根级行为测试；
- [`tests/run_all_tests.py`](tests/run_all_tests.py)：运行根 benchmark 并发现各 Legal Skill 保留的 `test_*.py` 回归测试；
- 依赖外部 PDF/OCR 工具的测试在缺失对应环境依赖时按脚本规则区分 `ENV_SKIP` 与真实失败。

运行：

```bash
python tests/run_all_tests.py
```

这里的测试用于验证协议和脚本行为。**仓库当前 README 不声称任何未经公开测量支持的法律准确率、胜诉率或模型 benchmark。**

---

## Post-task Reflection, not self-modifying law

LawBox 会在任务结束后判断是否出现值得保留的失败经验，例如：

- Agent 实际犯错并被纠正；
- 走过稳定可识别的错误路径；
- 发现可泛化的边界条件；
- Ludus Challenge 找到了容易被忽略的致命失败机制。

只有可复用且已经去个案化、去敏化的经验才写入 [`knowledge/lessons.md`](knowledge/lessons.md)。

**Agent 不会自动修改 `SKILL.md`、protocol 或系统规则。**

这不是一个会自行篡改法律工作规则的“自进化 Agent”；它把失败经验沉淀为可审阅的知识记录，再由人决定是否升级 Core。

---

## Safety & professional boundary

LawBox 的控制协议明确要求：

- 不把模型记忆包装成文件事实、现行法规或已核验案例；
- 不把用户对法律关系的命名直接视为已确认法律定性；
- 不把当事人主张或模型推断静默升级为客观事实；
- 没有真实 conflict database 时，不得伪造“组织级利益冲突检查已通过”；
- 不把分析结果当成发送、提交、签署、和解、放弃权利、产生费用或修改正式记录的授权；
- 不因为通过 Ludus Review 就跳过正式交付质量门；
- 不替代律师、法务或专业人士对事实、证据、法律适用、诉讼策略和最终文本的判断；
- 不承诺诉讼、仲裁、行政处理、交易谈判或监管沟通结果。

**A workflow can reduce avoidable failure. It cannot remove professional responsibility.**

---

## License & attribution

本仓库不是“所有内容统一换成一个新许可证”。许可边界以文件自身声明、[`LICENSE`](LICENSE)、[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) 与 [`LICENSES/`](LICENSES/) 为准。

- **当前项目维护者拥有版权的新创作内容**：PolyForm Noncommercial License 1.0.0。
- **上游 `pa1nrui1/legal-skills` 内容**：继续适用其原始 MIT License；原文见 [`LICENSES/upstream-MIT.txt`](LICENSES/upstream-MIT.txt)。
- **Intermediate fork / Ludus 增强相关必要通知**：按 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) 保留 Required Notice。
- PolyForm 许可不得被解释为撤销、替代或缩小第三方依据原许可证直接享有的权利。

请在复制、修改、重新分发或制作衍生版本前阅读完整许可证与第三方通知。

---

## Build a Domain Pack

Domain Pack 的最小骨架：

```text
packs/your-pack/
├── pack.json
├── README.md
└── skills/
    └── your-specialist-skill/
        └── SKILL.md
```

一个 Pack 的专业 Skill 应按总控 [`sop-contract.md`](skills/legal/法律工作总控/references/sop-contract.md) 编写，并把路由挂载到 [`routing-map.md`](skills/legal/法律工作总控/references/routing-map.md)。

现有 [`packs/ip-law/`](packs/ip-law/) 展示了最小目录与挂载方式。它只是骨架，因此适合直接拿来做自己的领域 Pack 起点。

---

## Project principles

```text
One Legal Skill.
The whole legal workflow.

Ask only what can change the decision.
Never confuse an assertion with a fact.
Verify before claiming verification.
Before trusting a conclusion, try to break it.
Analysis is not authorization.
Writing is not delivery.
Use the smallest workflow sufficient for the risk.
Everything specialized can become a plugin.
```

**Ludus challenges the conclusion.**  
**LawBox runs the work.**  
**Everything else can stay modular.**

---

## Acknowledgements

LawBox contains or derives from content from [`pa1nrui1/legal-skills`](https://github.com/pa1nrui1/legal-skills), licensed under the MIT License. The project also retains required notices for intermediate `legal-skills-enhanced` / Ludus-related contributions and records other inspirations in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

Thank you to the upstream and contributing communities whose work made this repository possible.
