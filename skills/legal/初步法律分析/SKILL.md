---
name: 初步法律分析
description: 基于"六来源体系"、请求权基础6步法与要件审判九步法融合框架，进行系统性法律分析，按总控当前事项记录和复盘台账衔接，生成法律服务建议书Word文档。当用户发送客户编号并提及"初步法律分析"、"法律分析"、"请求权分析"等指令时触发使用。
---


## 法律工作总控规则（强制）

执行本 Skill 前，必须先遵循：
- skills/legal/法律工作总控/references/practice-profile.md
- skills/legal/法律工作总控/references/matter-workspace-protocol.md
- skills/legal/法律工作总控/references/document-reading-protocol.md
- skills/legal/法律工作总控/references/source-boundary-protocol.md
- skills/legal/法律工作总控/references/ocr-correction-protocol.md
- skills/legal/法律工作总控/references/pkulaw-mcp-legal-verification-protocol.md

本 Skill 只处理「初步法律分析」专业任务；案件隔离、事项路径、文件读取、OCR 复查、来源披露、缺口归档、法规/案例/Wiki 核验和复盘台账更新均按法律工作总控共享协议执行。

## 旧规则废止（强制）

- 旧文中直接写死的客户目录、阶段目录、旧式台账写入、旧本地读取协议均不作为执行规则。
- 事项路径、当前事项、系统记录、业务文件区和复盘台账统一以法律工作总控 `matter-workspace-protocol.md` 为准。
- 不得静默写入复盘台账；确需更新时，先确认属于复盘台账更新并向用户说明。

# 初步法律分析Skill

## 与推理控制层的关系（Matter Model 接口）

- 总控推理控制层负责认知架构（事实状态、争点模型、不确定性与裁决门禁）；本 Skill 负责领域推理（六来源体系、请求权基础 6 步法、要件审判九步法）。二者不互相取代。
- 进入本 Skill 前，总控已按 `matter-model-protocol.md` 建立/更新 Matter Model；本 Skill 从中读取 facts / issues / legal_relationships，不另行重建案件事实副本。
- 本 Skill 完成后回写 Matter Model：`legal_relationships`（候选与 current_view）、`issues`（candidate_positions / elements / burden_of_proof）、`law`、`evidence`、`uncertainties`、`timeline`。
- 要件审判产出的是候选结论与支持/反对证据，不是最终裁决；L2/L3 的最终裁决由对抗审议与 Judgment 完成（见 `adversarial-review-protocol.md`、`judgment-protocol.md`）。
- 事实表述遵守认知状态（CONFIRMED / ASSERTED / DISPUTED / INFERRED / UNKNOWN），禁止把用户主张自动写成确定事实。

## 轻量入口

本文件是瘦身后的触发入口，只保留任务边界、执行顺序和按需读取索引。完整流程、模板、清单、专项规则和长示例已迁移至 `references/完整流程.md`。

## 何时使用

- 用户明确提到「初步法律分析」或本 Skill frontmatter 描述中的任务。
- 用户请求生成、审查、分析、计算、管理或推进与「初步法律分析」对应的法律工作成果。
- 法律工作总控或上游 Skill 路由到本 Skill。

## 执行顺序

1. 先按法律工作总控确认当前事项、业务文件区、系统记录区和来源边界。
2. 判断用户任务是否可以用本轻量入口完成；如只是路由、状态判断或简短提示，不默认读取完整流程。
3. 需要生成正式文书、报告、清单、计算结果、可视化、专项审查或复杂分析时，按需读取 `references/完整流程.md` 的相关章节。
4. 读取外置细节时，只读取当前任务需要的章节；不要为一个小问题整篇加载完整流程。
5. 输出前同步披露已读取材料、已核验内容、未核验/存疑内容、法规案例检索状态和需要用户判断事项。

## 按需读取索引

- `references/完整流程.md`：瘦身前完整正文，含详细流程、模板索引、专项规则、交互规范和注意事项。
- `references/`：本 Skill 的专业规则、清单、方法论和外置参考材料。
- `templates/`：文书、报告、表格等输出模板；仅在需要生成对应成果时读取。
- `assets/`、`scripts/`、`checklists/`、`reference/`：如目录存在，仅在完整流程或当前任务明确需要时读取。

## 输出底线

- 不跳过用户提供的材料；读取失败必须说明。
- 不用模型记忆替代法律法规核验；引用法规、案例、Wiki 或网页搜索时必须标注来源和核验状态。
- 材料不足时提示缺口，不悄悄补全。
- 需要写入系统记录、复盘台账、飞书文档或飞书日历时，按总控和对应飞书 Skill 规则执行。
