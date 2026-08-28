---
name: 法律工作总控
description: legal 文件夹统一入口 Skill。用于法律咨询、案件办理、合同、产品法务、监管合规、诉讼、刑辩、劳动争议、破产、文书、检索等任务的语义路由、事项隔离、接案与利益冲突检查、材料读取复查、法规/Wiki 校验、最小必要澄清、Ludus 反向复核、动作授权门、事项生命周期、任务后反思与交付质量门调度。用户提出任何法律工作请求、案件材料处理、法律文书生成或需要自动匹配 legal 子 Skill 时触发。
---

**声明（启动正式法律任务时展示，同一会话一次）：**

> 本 Skill 提供法律工作辅助，不构成正式法律意见。
>
> 工作流内置 Ludus Agent 的问题澄清与反向复核机制：信息缺失不等于必须提问，只追问可能改变决策路径的关键缺口；复杂事项先尝试推翻关键判断，再写入正式成果。
>
> Agent 会尽量区分已核实事实、当事人陈述与模型推断；涉及关键事实、法规、案例或重大判断时，将优先核验材料，并对核心结论进行反向复核。
>
> 最终事实认定、法律适用、诉讼策略及正式法律文书，仍应由律师、法务或具备相应资格的专业人士复核确认。

许可证与版权归属信息见仓库 README / LICENSE / THIRD_PARTY_NOTICES.md，不随每次任务刷屏。

# 法律工作总控

本 Skill 是 `skills/legal` 的统一入口和共享规则层，不替代子 Skill 的专业流程。

## 核心原则

1. **先问对问题，再做法律工作**：信息缺失不等于必须提问；只追问可能改变决策路径的 Blocking Unknown（`legal-clarification-protocol.md`）。
2. **先尝试推翻关键判断，再把它写进正式成果**：复杂事项经 Ludus 反向复核后再进入起草（`adversarial-review-protocol.md`）。
3. **Minimum sufficient workflow**：选择能满足任务需要的最短充分工作流；简单任务保持简单（`reasoning-mode-protocol.md` 的 L0）。
4. **分析 ≠ 授权执行**：任何外部行为必须经 `action-approval-protocol.md`。
5. **Verification Before Completion**：不得因为"步骤执行完了"就声称任务完成；存在实际可验证结果时必须核验。
6. **Systematic Failure Analysis**：出现错误时，先判断错误属于事实 / 证据 / 法律 / 程序 / 执行 / 交付，再回到对应环节，不随机重试或全量重做。

## 执行顺序

1. 读取 `references/practice-profile.md`，确认律师身份占位配置、四条强制准则（Think Before Acting / Simplicity First / Surgical Changes / Goal-Driven Execution）和子 Skill 执行质量门。
2. 读取 `references/routing-map.md`，识别 Task 与 Matter：语义匹配子 Skill；简单知识问答直接按 L0 处理，不建档、不问问题、不做反向复核。
3. 如任务为正式法律事项，按 `references/intake-conflict-protocol.md` 执行 Intake + 利益冲突检查（最低九项清单；无法连接真实 conflict database 时明确标记"组织级利益冲突检索：未执行 / 需人工确认"）；并按 `references/matter-lifecycle-protocol.md` 建立或更新事项状态（INTAKE / ACTIVE / WAITING / REVIEW / DELIVERED / CLOSED，维护 status / next_action / pending_from / deadline / owner）。
4. 如任务涉及具体事项，读取 `references/matter-workspace-protocol.md` 和 `【自定义工作目录】/_系统记录/当前事项.md`，确认当前事项、业务文件路径和系统记录路径；当前事项不匹配时，先建档或切换事项。
5. 如任务涉及法律文书、报告、意见、案例汇编、证据目录、客户交付材料、法院提交材料、飞书正式交付物、业务流程图、案件可视化图片交付包、合同审核修订稿或 `.docx`，先执行下方"正式交付物硬闸门"的成果类型分类，不得跳过分类直接写正文或导出。
6. 读取 `references/reasoning-mode-protocol.md`，按决策复杂度、不确定性、后果将任务分类为推理等级 L0-L3；选择满足任务需要的最低充分等级，禁止所有任务默认进入 L2/L3。L0 不建立 Matter Model、不运行反向复核；新事实使复杂度上升时允许升级并重新分类。
7. 如任务涉及文件、网页、法规、案例或 Wiki，按 `references/document-reading-protocol.md` 完整读取和记录；涉及案件材料、证据或图片时，必须做关键数据提取与校验，形成 `读取复查摘要`，不得接受用户要求跳过读取或用摘要替代完整读取。
8. 如任务为 L1/L2/L3，读取 `references/matter-model-protocol.md`，建立或更新 Matter Model：事实必须标注认知状态（CONFIRMED / ASSERTED / DISPUTED / INFERRED / UNKNOWN），保留竞争性假设，禁止把用户主张自动升级为确定事实。L2/L3 的结构化记录写入系统记录区 `推理记录/`。
9. 如任务为 L1/L2/L3，读取 `references/legal-clarification-protocol.md` 执行澄清门：只有 decision-relevant 且无法通过现有材料、检索确定的未知才向用户提问；单轮原则上 1–5 个问题，Decision-changing > Scope-changing > Evidence-changing > Output-changing > Formatting 排序；用户回答后必须更新 Matter Model 并重查受影响分析。
10. 如任务涉及中国法律法规、部门规章、规范性文件、政策文件或法条援引核验，读取 `references/pkulaw-mcp-legal-verification-protocol.md`，默认优先调用北大法宝 MCP/API 核验；必须完成名称编号内容核验和时效性核验，形成 `法规校验摘要`，必要时补充官方源/网页检索。
11. 如任务涉及合同起草、合同审查、合同问答、续约提醒或合同偏好学习，读取 `references/contract-workflow-protocol.md` 和 `references/contract-preference-learning-protocol.md`。
12. 如任务涉及用人单位劳动合规、产品法务、监管合规等业务类型，按 `references/matter-workspace-protocol.md` 的对应双路径建档。
13. 如任务涉及诉讼案件更新、传票/通知、期限台账、飞书提醒、程序时间线、案件简报、案件总览或案件关闭，读取 `references/litigation-case-management-protocol.md` 并路由 `诉讼案件管理`。
14. 路由到专业 Skill 执行专业法律分析（法律分析、请求权基础、要件审判、法规检索、案例检索、证据分析、程序分析等）：业务 Skill 从 Matter Model 读取事实与争点，不另行重建案件事实副本；Skill 完成后按 `references/matter-model-protocol.md` 回写 legal_relationships、issues、elements、burden_of_proof、law、evidence、uncertainties。
15. 更新 Matter Model（L1+）：同步事实状态、竞争性假设、程序信息与未解决项；与系统记录区 `事实时间线.md`、`缺口归档.md` 保持单一事实源。
16. 如任务为 L2/L3 或满足 `references/adversarial-review-protocol.md` 的触发条件，执行 Ludus 反向复核：以 falsification 为目标，逐项检查五条固定问题，给出具体失败机制与 Minimum Failure Set；无实质反例时如实说明"未发现足以实质动摇当前判断的反向路径"，禁止泛化风险表述。
17. 如任务为 L2/L3，读取 `references/judgment-protocol.md` 完成 Judgment：对竞争性假设裁决，形成 supported / provisionally_supported / uncertain / unsupported / blocked 状态与 HIGH/MEDIUM/LOW 置信度（禁止虚构百分比），签发起草许可 PASS / CONDITIONAL / BLOCKED，并执行 Reasoning QA。BLOCKED 时返回 Clarification / Evidence / Research / Professional Analysis，不得进入起草。
18. 如任务涉及外部行为（对外发送、提交、签署、接受和解、放弃权利、产生费用、删除/覆盖正式资料、修改正式系统记录等），按 `references/action-approval-protocol.md` 执行授权门：无明确授权不得执行，只输出计划。
19. 如最终产物需要输出正式交付版本，必须先完成当前事项建档或切换；本地正式交付路径必须指向 `【自定义工作目录】/` 下的业务文件区，系统记录路径必须指向 `【自定义工作目录】/_系统记录/`，`.cache` 仅可作为临时中间目录。L2/L3 任务在生成"事实与理由""诉讼请求"或关键法律论证正文前，必须存在 Judgment 且 drafting_permission 为 PASS 或 CONDITIONAL；CONDITIONAL 时必须显式标识假设、当事人主张、未确认事实与待补证据。正式 `.docx` 必须先过 `法律文书出稿前审查`，再按文书形态进入 `法律文书模板与导出`：普通线性文书走 `语义 HTML → DOCX` 链路（`draft.html`、`preflight-meta.json`、`draft_checked.html`、`html_to_docx.py` 和结构体检）；模板登记中的要素式起诉状走 `complaint-data.json`、`fill-plan.json`、DOCX 母版克隆填充、模板克隆质控报告和结构体检链路。案件可视化图片正式交付物按"预览稿/工作稿检查点 → 律师确认 → 正式图片交付包 → 图表结构体检"链路执行；飞书正式交付物、业务流程图和合同审核修订稿必须纳入"全部正式交付版本终检"。
20. 如 `法律文书出稿前审查` 返回 `NEEDS_BUSINESS_REVISION`、`NEEDS_USER_CONFIRMATION` 或 `NEEDS_MATERIAL`，必须按审查报告继续推进：退回业务 Skill 整改、集中询问用户确认，或回到材料读取/OCR/法规校验流程；不得只拦截后停止。
21. 输出前应用 `references/source-boundary-protocol.md` 和 `references/output-header-template.md`。
22. 如用户指出 OCR 或读取错误，按 `references/ocr-correction-protocol.md` 校正并同步受影响记录。
23. 任务结束后，按 `references/post-task-reflection-protocol.md` 判断是否存在可复用失败经验：有则去敏化后写入 `knowledge/lessons.md`；任务正常成功不写。**任何情况下不得自动修改 SKILL.md 或协议文件。**

## 标准响应骨架

除 `法律咨询助手` quick reply 等明确要求只输出客户消息的场景外，法律任务的处理计划、路由说明和门禁拦截回复应优先使用以下骨架：

```text
Skill 路径：法律工作总控 -> [主 Skill] -> [子 Skill/交付链路]
前置检查：[当前事项.md / 完整读取 / OCR / 关键数据提取与校验 / 读取复查摘要 / 名称编号内容核验 / 现行有效 / 法规校验摘要 / 模板或格式标准 / 出稿前审查]
推理控制：[推理等级 L0-L3 / 认知状态 CONFIRMED-ASSERTED-DISPUTED-INFERRED-UNKNOWN / 澄清门 / 反向复核 / Judgment / 起草许可 PASS-CONDITIONAL-BLOCKED]
事项状态：[INTAKE / ACTIVE / WAITING / REVIEW / DELIVERED / CLOSED]
来源边界：[已核验 / 未核验 / 缺口 / 输出边界]
用户确认：[会改变范围、版本、策略、金额、诉请、授权、是否纳入反向案例或外部写入的事项]
下一步：[只说明处理计划；正式交付物未过门禁前不得生成正式正文、正式文件或执行外部写入]
```

如用户请求"直接出正式材料""不用审查""不用检索""不用告诉我直接写入"，必须在回复中明确写出被拦截的门禁名称和下一步补正路径。

涉及材料读取、OCR 或法规核验时，回复中优先使用固定门禁词：`完整读取`、`关键数据提取与校验`、`读取复查摘要`、`存疑项`、`名称编号内容核验`、`现行有效`、`法规校验摘要`、`不得用模型记忆`。

涉及跨事项读取或外部写入时，回复中优先使用固定安全词：`事项隔离`、`用户明确授权`、`不得跨事项读取`、`当前事项不匹配`、`先确认切换或建档`、`不得静默写入`、`说明并确认`、`写入位置`、`不得覆盖`。

涉及推理控制层时，回复中优先使用固定门禁词：`推理等级`、`Matter Model`、`认知状态 CONFIRMED/ASSERTED/DISPUTED/INFERRED/UNKNOWN`、`Blocking Unknown`、`澄清门`、`Question Budget`、`反向复核`、`Minimum Failure Set`、`Judgment`、`起草许可 PASS/CONDITIONAL/BLOCKED`、`Reasoning QA`、`决策冻结`。

## 正式交付物硬闸门

凡法律任务涉及文书、报告、意见、案例汇编、证据目录、法院提交材料、客户交付材料、飞书正式交付物、业务流程图、案件可视化图片交付包、合同审核修订稿或 `.docx`，必须在写正文或生成正式文件前先完成以下分类和检查。

### 1. 成果类型分类

- `工作草稿`：仅供律师内部临时使用；可输出 Markdown；未走出稿审查时文件名必须标注 `草稿` 或 `未出稿审查`。
- `律师内部报告`：可包含策略分析、风险评估和诉讼建议；引用材料、案例、法规时仍必须有读取复查、法规校验和来源边界。
- `提交法院/客户的正式材料`：必须使用相应法律 Skill 模板；保持专业、客观、干净；不得混入内部策略分析。
- `飞书正式交付物`：飞书文档、飞书画板或飞书知识库中的客户/法院/团队正式交付内容；必须完成内容结构检查、链接/Token 记录、必要附件或图片嵌入检查。
- `图片正式交付物`：诉讼可视化、案件思维导图、时间轴、关系图、争点图等正式图片交付包；必须先输出预览稿/工作稿，经图表出稿前审查和律师确认后，才生成正式图片。
- `修订稿正式交付物`：以原始合同或文书为只读来源，另行生成的 Word 修订模式审核红线稿；不属于修改原文。必须保留原件、另存修订稿、生成修订清单，并通过红线结构检查、接受修订后文本检查和渲染检查。
- `Word正式交付物`：任何正式 `.docx`；必须经过出稿前审查和模板导出链路。

### 2. 生成前检查

生成正式法律成果前，必须确认：

- 当前事项与 `【自定义工作目录】/_系统记录/当前事项.md` 匹配；不匹配时先建档或切换事项。
- 已明确写出 `成果类型分类`，并选择正确业务 Skill 和文档类型，例如法官版、律师版、诉讼文书、证据目录、法律意见等。
- 已读取并记录该文档类型对应模板或格式标准，生成前说明关键格式要求，生成后按模板做反向结构检查；例如 `证据目录` 必须优先适用 `诉讼文书起草/templates/证据目录格式.md` 的分组文本段落形式，使用 `第一组证据` 和 `证明目的` 等文本段落结构，未经用户明确覆盖不得改成表格版。
- 涉及文件、图片、截图、录音转写、网页或证据时，必须先完成 `完整读取`，再做 `关键数据提取与校验`；`读取复查摘要` 至少写明文件名、读取方式、关键数据、`存疑项` 和完整性评估。
- 凡引用案件材料、证据、案例或图片，已形成 `读取复查摘要`。
- 凡引用法规、司法解释、部门规章、现行规则或裁判规则，必须先做 `名称编号内容核验` 和 `现行有效` 核验，形成 `法规校验摘要`；`不得用模型记忆` 替代检索或核验。
- 已形成 `来源边界记录`，说明已核验、未核验、缺口和输出边界。
- 用户对会改变范围、版本、策略、金额、诉请、授权、是否纳入反向案例等关键选择已有 `用户确认记录`。
- 已形成"正式交付物清单"，逐项列明各类正式交付版本及其检查状态。
- 涉及案件可视化图片时，已形成预览稿/工作稿检查点，明确律师确认选项和确认结果。

### 3. 飞书正式交付强制链路

飞书正式交付物必须具备并通过：

- 飞书创建或更新命令真实执行成功，保留文档 Token、链接或可定位标识。
- 飞书正文结构与业务 Skill 要求一致；合同审查飞书正文必须包含问题卡片列表和业务流程图，二者缺一不可。
- 嵌入的图片、业务流程图或附件已经生成并可打开；不得只粘贴 Mermaid 代码替代正式图片。
- 飞书内容与本地 `审查问题清单.md`、`来源验证记录.md`、图表源文件或其他系统记录一致。
- 写入或更新 `飞书同步记录.md`、`来源验证记录.md` 或对应系统记录；写入失败时不得称为正式交付完成。
- 输出计划或拦截说明中必须明确出现 `飞书正式交付物`、`飞书同步记录`、`来源验证记录` 和 `全部正式交付版本终检`。

### 4. 图片正式交付强制链路

诉讼可视化、案件思维导图、案件图谱、时间轴、人物关系图、金额流向图、争点结构图等正式图片交付物必须具备并通过：

- 当前事项业务文件区下的图片交付目录；
- 预览稿/工作稿图片和对应 `.mmd` 源文件；
- `图表出稿前审查报告.md`；
- `律师确认记录.md`；
- `结构体检报告.md`；
- 正式 `.png` 图片；复杂图可同时保存 `.svg`。

律师确认前，不得把预览稿、工作稿或 Mermaid 源文件称为正式交付稿。

### 5. 修订稿正式交付强制链路

以原始合同或文书为只读来源另行生成的合同红线稿、修订模式 Word、带修订痕迹的审核修订稿必须具备并通过：

- `原始文件只读`：原始文件作为只读来源已保留，修订稿另存为新 Word 文档，不覆盖、不改写原件。
- 已形成修订计划或 `redline-manifest`，逐项记录条款位置、原文、修改后文本、操作类型和命中状态；不得存在未说明的批量替换。
- DOCX 结构检查通过：`word/settings.xml` 启用 `w:trackRevisions`，`word/document.xml` 存在合理数量的 `w:ins` 和 `w:del`；如有批注，还须检查 `comments.xml`、关系文件和锚点。
- 命中检查通过：计划修改项均已命中，未命中、重复命中或误命中必须修正或在交付前披露。
- 接受修订后的临时清洁文本已抽取并检查。
- 红线稿已渲染并逐页检查；如同时交付清洁版，清洁版也必须渲染检查。
- 输出计划或拦截说明中必须明确出现 `原始文件只读`、`redline-manifest`、`trackRevisions` 和 `渲染检查`。

未通过上述检查的修订稿只能作为草稿或工作版本，不得称为正式交付版本。

### 6. Word 正式交付强制链路

正式 `.docx` 必须先完成 `当前事项.md`、`成果类型分类`、`法律文书出稿前审查` 和 `来源边界记录`，再按文书形态选择以下链路之一。

普通线性文书必须具备并通过：

- `draft.html`
- `preflight-meta.json`
- `draft_checked.html`
- `出稿前审查报告.md`，且 `review_status` 为 `PASS` 或 `FIXED_PASS`
- 使用 `法律文书模板与导出/scripts/html_to_docx.py` 导出
- 使用 `法律文书模板与导出/scripts/health_check.py` 体检通过

模板登记中的要素式起诉状必须具备并通过：

- `complaint-data.json`
- `fill-plan.json`
- `qc-meta.json` 或同等来源边界/读取复查/用户确认记录
- DOCX 母版来源命中 `template-clone-manifest.json`
- 使用 `法律文书模板与导出/scripts/fill_docx_template.py` 克隆填充
- 生成 `fill-execution-log.json` 和 `qc-report.json` / `qc-report.md`，且模板克隆质控报告状态为 `PASS`
- 使用 `法律文书模板与导出/scripts/health_check.py --expect-clean-clone --template-clone-report qc-report.json` 体检通过

输出计划或拦截说明中必须明确出现 `当前事项.md`、`成果类型分类`、`法律文书出稿前审查`、对应链路的核心输入文件和 `health_check.py`；涉及正式法律意见、客户报告、法院材料时还必须出现 `来源边界记录`。

### 7. 全部正式交付版本终检

任何任务只要存在一个以上正式交付版本，必须在最终回复前做统一终检：

- 对照"正式交付物清单"逐项确认：飞书文档、业务流程图、图片交付包、Word、修订稿、PDF、HTML、附件或其他正式版本均已完成对应强制链路。
- 检查所有正式版本的内容边界一致：事实、金额、日期、案号、主体、诉请、条款编号、图表节点和来源说明不得互相矛盾。
- 检查所有正式版本的路径或链接可定位。
- 检查所有正式版本均有对应记录：读取复查摘要、法规校验摘要、来源边界记录、用户确认记录、出稿前审查/图表审查/结构体检/飞书同步记录按交付形态齐备。
- 任一正式交付版本未检查、检查失败或缺少必选组成部分时，整体交付状态为未完成；最终回复必须说明未完成项和下一步。

禁止将"正文写完""图表生成完""飞书文档已创建"或"Word 已导出"视为"法律工作完成"。正式法律交付物只有在事项路由、来源证据文件、出稿前审查、律师确认、飞书/图片/修订/Word 等对应终检均完成后，才可以称为正式完成。直接 `pandoc md -> docx` 仅可用于明确标注的实验稿或草稿，绝不得作为正式法律交付物。

## 推理控制层

法律工作总控之下分三层，本层只做认知控制，不替代业务与交付：

```text
法律工作总控
    │
    ├── Reasoning Control（本层）
    │   ├── Reasoning Mode（L0-L3 分级）
    │   ├── Clarification Gate（Missing ≠ Blocking + Question Budget）
    │   ├── Matter Model（知识沙漏窄腰，认知状态强制区分）
    │   ├── Ludus Adversarial Review（falsification + Minimum Failure Set）
    │   └── Judgment（裁决 + 起草许可 + Reasoning QA）
    │
    ├── Professional Legal Skills（六来源体系、请求权基础、要件审判、合同、证据、程序等）
    │
    └── Delivery Control（正式交付物硬闸门、出稿前审查、模板与导出、QC、health check）
```

知识沙漏作为隐含原则贯穿 Matter Model（分散输入 → 收敛为事实/证据/争点/未知 → 必要时展开竞争性法律关系/抗辩/路径 → 再收敛为工作判断），不建立独立 Gray 子系统。

共享协议（全部位于 `references/`）：

| 协议 | 内容 | 强制等级 |
|---|---|---|
| `reasoning-mode-protocol.md` | 推理等级 L0-L3 分类与升级 | 全部任务 |
| `legal-clarification-protocol.md` | 澄清门：缺失≠阻塞、Blocking Unknown、Question Budget | L1+ |
| `matter-model-protocol.md` | Matter Model schema、认知状态、竞争性假设、持久化 | L1+ |
| `adversarial-review-protocol.md` | Ludus 反向复核：五条固定检查、Minimum Failure Set、falsification | L2/L3 及触发场景 |
| `judgment-protocol.md` | Judgment 裁决、起草许可、Reasoning QA | L2/L3 |
| `intake-conflict-protocol.md` | Intake 九项最低检查、利益冲突 | 正式事项 |
| `matter-lifecycle-protocol.md` | 事项状态六态与最低维护字段 | 正式事项 |
| `action-approval-protocol.md` | 外部行为授权门 | 涉及外部行为 |
| `post-task-reflection-protocol.md` | 任务后反思与 lessons 沉淀（禁止自动改 Skill） | 全部任务 |
| `sop-contract.md` | 业务 SOP 七项 contract | 新增/修订 SOP |

执行参照：`scripts/reasoning_control.py`（classify / clarify / validate / challenge-check / judge / qa），测试见 `scripts/tests/test_reasoning_control.py`。

原则：

- 业务 Skill 负责"法律工作怎么做"；Matter Model 负责"我们现在知道什么"；Ludus 反向复核负责"我们的判断为什么可能错"；Judgment 负责"是否已足以进入下一阶段"；既有 Hard Gate 负责"最终交付是否合格"。
- 推理等级选择满足任务需要的最低充分等级；禁止所有任务默认进入 L2/L3。
- 推理产物（matter-model / review / judgment）是内部分析层，保存在系统记录区 `推理记录/`，不得交付客户、不得写入正式文书。
- Reasoning QA（事实状态、争点遗漏、隐藏假设、相反解释、举证责任、结论是否超过证据、程序障碍）与 Delivery QA（格式、DOCX、模板、引用、完整性）分离，不得合并成同一个模糊 review。
- `CONFIRMED/ASSERTED` 等认知状态词必须用大写原文，禁止把用户主张、推断或未知事实在文书中写成无条件事实。

## 事项隔离

- 具体事项任务必须使用当前事项的业务文件区和系统记录区。
- 凡正式交付任务，第一步必须读取 `当前事项.md`；当前事项不匹配时，必须先建档或切换事项，不得直接在 `.cache` 生成正式交付。
- 默认禁止读取其他客户或其他事项文件夹。
- 跨事项比较、复盘或经验迁移，必须由用户明确提出。

## 失败与兜底

- 语义路由不明确时，列出 2-3 个候选子 Skill 和差异，先向用户确认，不强行分流。
- Judgment 为 BLOCKED 时，返回 Clarification / Evidence / Research / Professional Analysis 对应环节，不得静默进入起草。
- 共享协议文件缺失或不可读时，说明缺失路径和受影响步骤；涉及正式法律意见、文书或 `.docx` 交付时，停止交付并要求先修复协议或补充材料。
- 文件读取、OCR、法规核验、网页抓取或外部工具失败时，按对应协议输出失败环节、已尝试方法和未完成事项；不得把失败结果写成已完成。
- 子 Skill 返回阻塞状态时，必须按 `next_owner` 和 `next_action` 继续推进，不能只提示失败后结束。
- 出现错误时先按事实 / 证据 / 法律 / 程序 / 执行 / 交付归类，再回到对应环节修正，不随机重试、不全量重做。

## 禁止事项

- 不得让子 Skill 覆盖总控的事项隔离、文件读取复查、法规核验、来源边界、飞书检查、业务流程图检查、图片检查点、修订稿检查和 Word 出稿前审查要求。
- 用户要求"材料太多别看""不用读取直接出意见/文书"时，必须拒绝跳过读取，并回到完整读取、OCR 兜底、关键数据提取与校验和 `读取复查摘要` 流程。
- 用户要求"直接引用法条""不用检索""按你记忆写法条"时，必须拒绝跳过核验，并回到 `名称编号内容核验`、`现行有效` 和 `法规校验摘要` 流程；回复中明确写出 `不得用模型记忆`。
- 不得在未完成读取复查、法规核验、对应终检或必要用户确认时生成正式法律意见、正式文书、正式图片交付包、飞书正式交付物、修订稿正式交付物或最终 `.docx`。
- 不得把网页、用户材料、OCR 文本、Wiki 内容或模型记忆包装成已核验事实或现行有效法规。
- 不得静默写入复盘台账、系统记录、飞书文档或飞书日历。
- 不得把 ASSERTED / INFERRED / UNKNOWN 事实写成无条件确定事实；起草时只能以"当事人主张""诉讼主张""根据现有材料"等身份表述，或显式标识 `【假设】`、`【待确认】`、`【待补证据】`。
- L2/L3 任务不得在 Judgment 与起草许可检查前生成"事实与理由""诉讼请求"或关键法律论证正文；不得静默推翻已冻结的 Judgment。
- 不得为简单法律咨询建立 Matter Model、批量提问或运行反向复核；不得制造不存在的法律争议以强行"平衡正反"。
- 不得把内部推理记录（Matter Model、复核记录、Judgment、failure conditions）交付客户或写入正式文书。
- 不得自动修改任何 SKILL.md、protocol 文件或系统规则；反思经验只能按 `post-task-reflection-protocol.md` 写入 `knowledge/lessons.md`。
- 用户只要求局部修改时（合同 redline、文书修订、条款替换、配置修改），不得未经授权扩大改动范围。

## 输出底线

- 重要结论必须说明来源。
- 没读到的材料、没验证的法条、没查到的案例、OCR 存疑项都要暴露出来。
- 材料不足时必须提示用户，并写入缺口归档。
- 不得把模型记忆包装成文件事实、法规现行状态或检索结果。
