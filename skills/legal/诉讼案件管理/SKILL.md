---
name: 诉讼案件管理
description: 民事、刑事及劳动争议诉讼共用的案件运营管理 Skill。用于案件更新、传票/开庭通知/举证通知/应诉通知/裁判文书处理、期限台账、飞书日历提醒、事实时间线和程序时间线维护、飞书思维导图同步、案件简报、诉讼案件总览、案件组合状态、案件关闭与结案归档检查。案件隔离、建档、材料读取复查、来源披露、OCR 校正、缺口归档和法规核验由法律工作总控统一处理。
---


## 法律工作总控规则（强制）

执行本 Skill 前，必须先遵循：
- skills/legal/法律工作总控/references/practice-profile.md
- skills/legal/法律工作总控/references/matter-workspace-protocol.md
- skills/legal/法律工作总控/references/document-reading-protocol.md
- skills/legal/法律工作总控/references/source-boundary-protocol.md
- skills/legal/法律工作总控/references/ocr-correction-protocol.md
- skills/legal/法律工作总控/references/pkulaw-mcp-legal-verification-protocol.md
- skills/legal/法律工作总控/references/litigation-case-management-protocol.md

本 Skill 不重复定义案件隔离、建档、材料读取复查、来源披露、OCR 校正和缺口归档；这些均由法律工作总控处理。

## 旧规则废止（强制）

- 旧文中直接写死的客户目录、阶段目录、旧式台账写入、旧本地读取协议均不作为执行规则。
- 事项路径、当前事项、系统记录、业务文件区和复盘台账统一以法律工作总控 `matter-workspace-protocol.md` 为准。
- 不得静默写入复盘台账；确需更新时，先确认属于复盘台账更新并向用户说明。


# 诉讼案件管理

本 Skill 是诉讼案件的共用运营管理层，适用于民事、刑事、劳动争议诉讼及破产诉讼相关程序管理事项。

## 任务分类

先判断用户任务属于哪一类：

1. **案件更新**：用户提供新进展、新材料、新沟通、新裁判结果。
2. **传票/通知处理**：传票、开庭通知、举证通知、应诉通知、缴费通知、判决/裁定/调解书、公安/检察通知等。
3. **期限台账和飞书提醒**：开庭、举证、答辩、上诉、缴费、提交材料、会见、阅卷等期限。
4. **时间线和可视化**：事实时间线、程序时间线、证据链、争议焦点、刑事阶段路线图。
5. **案件简报**：内部简报、客户简报、庭前简报。
6. **组合状态**：诉讼案件总览、多案件状态看板、风险等级和下一步动作。
7. **案件关闭**：结案检查、关闭状态、后续期限、归档记录。

## 按需读取参考文件

- 传票、通知、裁判文书处理：读取 [references/summons-and-notice.md](references/summons-and-notice.md)。
- 期限台账和飞书提醒：读取 [references/deadline-and-lark-reminder.md](references/deadline-and-lark-reminder.md)。
- 时间线和飞书思维导图：读取 [references/timeline-and-mindmap.md](references/timeline-and-mindmap.md)。
- 案件简报：读取 [references/case-brief.md](references/case-brief.md)。
- 组合状态和总览：读取 [references/portfolio-status.md](references/portfolio-status.md)。
- 案件关闭：读取 [references/case-close.md](references/case-close.md)。

## 专业 Skill 分工

- 民事阶段、起诉、答辩、庭前、庭审、判后分析：交给 `民事一审诉讼` 及其子 Skill。
- 刑事阶段路由、会见阅卷、侦查/审查起诉/一审/二审辩护：交给 `刑事辩护总调度` 及其子 Skill。
- 劳动争议诉讼专业问题：交给 `劳动争议诉讼` 及劳动子 Skill。
- 本 Skill 只负责跨民事/刑事/劳动争议的案件运营动作和记录同步。

## 飞书使用规则

- 传票/通知触发明确时间或期限时，必须优先调用 `lark-calendar` 创建飞书日历提醒。
- 材料准备、提交文书、联系客户等动作可按需调用 `lark-task` 创建任务。
- 时间线可视化优先用 Mermaid 生成 mindmap/flowchart，再用 `lark-doc` 保存为飞书文档；需要画板时使用 `lark-whiteboard`。
- 飞书文档或日历链接必须写入系统记录区的 `飞书同步记录.md`。

## 输出底线

所有正式输出前仍使用法律工作总控的来源与边界说明；诉讼管理输出中必须额外说明：

```markdown
- 已更新系统记录：
- 已创建飞书提醒：
- 未创建飞书提醒及原因：
- 已同步飞书文档/思维导图：
- 需要客户确认的期限或事实：
```

## 归档要求

不新增业务区路径。业务材料继续放入现有：

- `诉讼/民事/<客户或委托人>/<案件简称或案号>/...`
- `诉讼/刑事/<客户或委托人>/<案件简称或案号>/...`

本 Skill 只在系统记录区维护诉讼管理文件：

- `程序时间线.md`
- `期限台账.md`
- `传票与通知台账.md`
- `案件简报.md`
- `组合状态.md`
- `飞书同步记录.md`
- `结案归档记录.md`
