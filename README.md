# Legal Work OS Core（法律百宝箱 Core）

面向中国法律工作的模块化 **Legal Work OS**：

> 用专业 Legal Skills 执行业务，用 Ludus 反向复核做最小必要澄清与关键判断压力测试，用统一 SOP 控制任务生命周期，并在任务结束后沉淀可泛化失败经验。

它不是"全自动律师"，也不是一个超级 Prompt。它把真实法律服务中容易被模型忽略的流程、校验、分工和交付边界，拆解为可由 AI Agent 执行和复核的工作单元。

兼容 Codex、Claude Code、OpenCode、OpenAI Skills 以及其他支持本地 Markdown Skill 的 Agent 平台。

- 核心原则：**先问对问题，再做法律工作；先尝试推翻关键判断，再把它写进正式成果。**
- 版本：Core v1.0.0

> **重要提示：本项目不提供法律意见。** 本项目输出的任何内容都应视为供律师、法务或合格专业人士复核的工作草稿。真实法律事项必须由专业人士基于完整事实、有效授权、现行法律、可核验案例和具体语境作出独立判断。

---

## 核心能力

### 1. 专业法律 Skill（执行层）

58 个专业 Skill 覆盖：法律咨询、初步法律分析、法规案例检索、民事诉讼、刑事辩护（侦查/审查起诉/一审/二审/死刑/未成年人/简易速裁/特殊程序）、劳动争议、破产程序（申请受理/管理人/债权/重整/和解/清算/分析/文书）、合同审查与起草、委托合同管理、产品法务、广告与食品标签合规、监管合规监测、诉讼文书起草、调查取证、庭前/庭审/庭后、调解和解、立案管理、结案归档、诉讼可视化、法院文书（审理报告/判决书）、法律文书出稿前审查与 DOCX 导出等。

### 2. 统一总控（控制层）

`法律工作总控` 负责横向控制：

- **语义路由**：识别 Task / Matter，路由到正确专业 Skill。
- **Intake + Conflict**：正式事项九项最低检查；不连接真实 conflict database 时明确标记"组织级利益冲突检索：未执行 / 需人工确认"，不假装已通过。
- **Legal Clarification**：信息缺失不等于必须提问；只追问可能改变决策路径的 Blocking Unknown，单轮 1–5 个问题。
- **事实状态区分**：`CONFIRMED / ASSERTED / DISPUTED / INFERRED / UNKNOWN`，禁止把当事人主张静默升级为已核实事实。
- **Ludus 反向复核**：复杂事项在进入正式起草前，以 falsification 为目标检查五条固定问题，给出具体失败机制（Minimum Failure Set）。
- **Action / Approval Gate**：分析 ≠ 授权执行；对外发送、提交、签署等动作必须明确授权。
- **Matter Lifecycle**：统一六态（INTAKE / ACTIVE / WAITING / REVIEW / DELIVERED / CLOSED）与最低维护字段。
- **Post-task Reflection**：只把可复用、去敏化的失败经验写入 `knowledge/lessons.md`；**Agent 绝不自动修改任何 Skill**。
- **交付质量门**：正式文书必须经过出稿前审查、DOCX 导出链、redline 检查与 health check。

### 3. 交付管线（交付层）

- 真实 DOCX 导出：`draft.html → preflight-meta.json → draft_checked.html → html_to_docx.py → health_check.py`。
- 要素式起诉状 DOCX 母版克隆填充。
- 合同审查 Word 修订模式红线稿（trackRevisions + 批注 + redline QA）。
- 图片/图表交付包、修订稿交付、飞书交付的对应终检链路。

## 架构

```text
用户任务
  │
  ▼
法律工作总控
  - 语义路由
  - Intake / Conflict（正式事项）
  - 材料读取复查
  - Legal Clarification（只问 Blocking Unknown）
  - Matter Model（事实状态强制区分）
  - 事项生命周期
  │
  ▼
专业法律 Skill（58 个）
  │
  ▼
Ludus 反向复核（复杂事项：L2/L3 及触发场景）
  │
  ▼
Action / Approval Gate（外部行为）
  │
  ▼
交付质量门（出稿前审查 / DOCX / redline / QC / health check）
  │
  ▼
Post-task Reflection（有可复用失败经验时 → knowledge/lessons.md）
```

简单任务保持简单：例如"劳动合同试用期最长多久？"走 L0 —— 必要法律来源核验后直接回答，不触发 conflict、matter、追问、反向复核或反思记录。核心原则：**Minimum sufficient workflow**。

## Ludus 增强

Ludus 是轻量推理增强，不是新的 Agent Framework 依赖，也不是独立角色 Agent 群：

- **何时触发**：存在竞争性事实解释、多个合理法律关系、关键事实冲突、证据解释实质争议、用户要求诉讼策略/责任判断、高风险正式成果时。
- **做什么**：以 falsification 为目标检查五条固定问题（用户对法律关系的命名可能错吗 / 有无竞争性事实解释 / 对方最强抗辩 / 哪个要件失败会推翻结论 / 有无时效、管辖、主体、程序、举证责任障碍）。
- **不做什么**：不为显得客观强行写"一方面、另一方面"；无实质反例时如实说明"未发现足以实质动摇当前判断的反向路径"。

协议见 `skills/legal/法律工作总控/references/adversarial-review-protocol.md`，可执行参照实现见 `scripts/reasoning_control.py`。

## Post-task Reflection

任务结束后，仅当存在可复用的失败经验时（Agent 实际犯错被纠正、走过明显错误路径、发现稳定边界条件、反向复核发现易忽略的失败机制等），经过去个案化、去敏化后写入 `knowledge/lessons.md`。

- 不记录：普通任务摘要、客户姓名、案号、联系方式、个案金额、私密事实、一次性结论。
- **Agent 绝不自动修改 SKILL.md、protocol 或系统规则**；`lessons.md` 是唯一允许的沉淀位置。

## Skill 列表

| 分类 | Skill |
| :-- | :-- |
| 总控与交付 | 法律工作总控（核心）、法律文书出稿前审查（核心）、法律文书模板与导出（核心）、案件材料生成专业文档 |
| 咨询与研究 | 法律咨询助手、初步法律分析、法规案例检索、法律Wiki知识库查询、法律文章去AI味道 |
| 民事诉讼 | 民事一审诉讼（核心）、立案管理、诉讼文书起草（核心）、调查取证与证据管理、庭前准备、庭审与庭后工作、调解与和解、结案归档、诉讼案件管理、诉讼分析工具、诉讼可视化 |
| 刑事辩护 | 刑事辩护总调度（核心）、案件承接与委托、侦查阶段辩护、审查起诉阶段辩护、一审阶段辩护、二审阶段辩护、未成年人案件、死刑案件、简易速裁程序、特殊程序 |
| 劳动争议 | 劳动争议诉讼（核心）、劳动争议仲裁程序管理、劳动争议证据体系、劳动关系认定与经济补偿计算（核心）、用人单位劳动合规 |
| 合同与交易 | 合同审查（核心）、合同起草（核心）、委托合同管理 |
| 产品与监管 | 产品法务（核心）、广告合规审核、预包装食品标签合规、监管合规监测（核心） |
| 破产程序 | 破产申请与受理、管理人工作、债权申报与审查、债权人会议、财产调查与管理、重整程序、破产清算、破产和解程序、破产法律分析、破产文书生成 |
| 法院文书与工具 | 审理报告、民事判决书、law-to-markdown、微信文章转换为markdown |

完整说明见各 Skill 的 `SKILL.md` 与 `references/`。

### Domain Packs（万物皆插件）

专业领域扩展（IP、M&A、税务、证券、数据隐私等）以 **Domain Pack** 形式挂载到 `packs/`，不修改 Core：

- 安装 = 放入目录 + 把 `routes` 追加到总控 routing-map（写入前需用户确认）；
- pack 内 Skill 自动继承总控全部共享协议（澄清 / 反向复核 / 授权 / 生命周期 / 反思 / 交付门），只写专业内容；
- 卸载 = 删除目录 + 移除路由条目，无其他耦合。

约定见 `skills/legal/法律工作总控/references/sop-contract.md`；仓库内置 `packs/ip-law/` 示例骨架。

## 典型工作流

### 案件材料分析

```text
用户上传案件材料
→ 总控识别事项 → 正式事项时 Intake + Conflict
→ 完整读取 → 提取主体、金额、日期、证据、争点
→ 只对 Blocking Unknown 最小追问
→ 初步法律分析 / 证据分析 / 法规案例检索
→ 复杂事项 Ludus 反向复核 → Judgment → 起草许可
→ 诉讼方案 / 文书起草 / 其他专业 Skill
→ 交付质量门 → 完成
→ 有可复用失败经验？→ lessons.md
```

### 合同审查

```text
合同文本 → 确认审查立场（甲方/乙方/中立，hard gate）
→ 完整读取 → 合同审查 Skill → 风险等级 + 修改建议 + 需确认问题
→ 需要 Word 修订模式时：redline-plan.json → 真实修订/批注 → 红线 QA
```

### 正式文书交付

```text
业务 Skill 生成正文 / 语义 HTML / 要素式数据
→ 法律文书出稿前审查（PASS / FIXED_PASS 才可导出）
→ 普通文书：html_to_docx.py；要素式起诉状：fill_docx_template.py
→ health_check.py → DOCX + 质控报告 + 结构体检结果
```

## 安装

```bash
git clone <your-remote>/legal-work-os-core.git
```

将 `skills/legal/` 复制到你的 Agent 平台支持的 skills 目录，或通过平台插件机制安装（`.codex-plugin/plugin.json`）。

安装后直接调用：

```text
法律工作总控 帮我判断这个任务应该走哪个法律工作流。
```

```text
合同审查 审核这份合同，按风险等级输出修改建议。
```

真实业务使用前，请配置律师身份、工作区路径（`LEGAL_WORKSPACE`、`LEGAL_CURRENT_MATTER` 等环境变量）与模板库；不要把真实客户材料、API Key、商业数据库凭证或本机私有路径提交到公开仓库。

## 安全边界

- 不把模型记忆包装成文件事实、现行法规或已核验案例。
- 不把用户对法律关系的命名直接视为已确认的法律定性。
- 不把用户主张或模型推断静默升级为客观事实。
- 不静默写入台账、系统记录、云文档或日历；对外行为必须明确授权。
- 不替代律师、法务或专业人士对事实、证据、法律适用和最终文本的判断。
- 不承诺诉讼、仲裁、行政处理、交易谈判或监管沟通结果。

## License

- 新创作内容：**PolyForm Noncommercial License 1.0.0**（见 `LICENSE`）。除 `THIRD_PARTY_NOTICES.md`、`LICENSES/` 或文件自身声明另有规定的第三方/上游内容外，本项目中由当前项目维护者拥有版权的新创作内容依据该许可授权。
- 上游 MIT 内容：本项目包含或衍生自 MIT 授权的 `legal-skills`；上游 MIT License 原文见 `LICENSES/upstream-MIT.txt`，归属与必要通知见 `THIRD_PARTY_NOTICES.md`。PolyForm 许可不撤销上游原有 MIT 权利。

## 目录结构

```text
.
├── README.md
├── SKILL.md
├── AGENTS.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── CHANGELOG.md
├── LICENSES/
│   └── upstream-MIT.txt
├── knowledge/
│   └── lessons.md
├── skills/legal/
│   ├── 法律工作总控/
│   │   ├── SKILL.md
│   │   ├── references/     # 共享协议（澄清/反向复核/Intake/生命周期/授权/SOP/反思等）
│   │   └── scripts/        # reasoning_control.py + 测试
│   ├── 初步法律分析/
│   ├── 法律咨询助手/
│   ├── 合同审查/ 合同起草/
│   ├── 民事一审诉讼/ 刑事辩护总调度/ 劳动争议诉讼/
│   ├── 诉讼文书起草/ 调查取证与证据管理/
│   ├── 法律文书出稿前审查/ 法律文书模板与导出/
│   └── ...（共 58 个专业 Skill）
├── packs/                  # Domain Packs（IP/M&A/税务等扩展，示例：ip-law）
├── tests/
├── assets/
└── .codex-plugin/
```

## 致谢

本项目包含或衍生自 MIT 授权的 `legal-skills` 项目内容，感谢该项目的全部贡献者。第三方归属与必要通知详见 `THIRD_PARTY_NOTICES.md` 与 `LICENSES/upstream-MIT.txt`。
