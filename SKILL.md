---
name: legal-work-os-core
description: Chinese legal workflow skills for lawyers, legal counsel, litigation, criminal defense, labor disputes, bankruptcy, contract review, compliance, legal research, and legal document drafting, with lightweight Ludus adversarial review and unified SOP control.
---

# Legal Work OS Core

Use this skill when the user needs Chinese legal work support, including legal consultation, litigation analysis, criminal defense, labor disputes, bankruptcy, contract review, compliance review, legal research, evidence review, or legal document drafting.

## 首次启用声明

当本 Skill 在一个会话中首次启用、首次被调用或首次进入法律工作流时，必须先展示以下声明。每个会话只展示一次；如果已经展示，不得重复。

> **声明**
>
> 本 Skill 提供法律工作辅助，不构成正式法律意见。
>
> 本项目基于 [pa1nrui1/legal-skills](https://github.com/pa1nrui1/legal-skills)（MIT License）重建；在此基础上，**Samwang-afk** 引入 Ludus Agent 的问题澄清与反向复核机制，Ludus Agent 贡献者包括 [@xiayuzizhuo666](https://github.com/xiayuzizhuo666) 与 [@samwang-afk](https://github.com/samwang-afk)。信息缺失不等于必须提问，只追问可能改变决策路径的关键缺口；复杂事项先尝试推翻关键判断，再写入正式成果。
>
> 许可：本仓库中由当前项目维护者拥有版权的新创作内容依据 PolyForm Noncommercial License 1.0.0 授权；上游 MIT 内容保留其原始 MIT License；具体归属见 `THIRD_PARTY_NOTICES.md`。
>
> Agent 会尽量区分已核实事实、当事人陈述与模型推断；涉及关键事实、法规、案例或重大判断时，将优先核验材料，并对核心结论进行反向复核。
>
> 最终事实认定、法律适用、诉讼策略及正式法律文书，仍应由律师、法务或具备相应资格的专业人士复核确认。

展示声明后，如果用户尚未提供具体法律任务，只需邀请用户直接描述法律任务或提交材料；不要为了展示澄清机制而机械提问。真正的澄清问题仍按主路由的 Blocking Unknown / Question Budget 规则，在具体任务中按需触发。

## Workflow

1. Read `skills/legal/法律工作总控/SKILL.md` first. Treat it as the main router and shared quality gate for the legal workflow.
2. Let the main router choose the relevant Chinese sub-skill under `skills/legal/`.
3. When a referenced file path is relative, resolve it from this repository root.

## Shared rules

- Clarification, conflict checks, adversarial review, reflection, approval and lifecycle rules are owned by the main router's shared protocols under `skills/legal/法律工作总控/references/`; professional sub-skills must not re-implement them.
- License and attribution notices live in `README.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md` and `LICENSES/`.

Do not replace attorney review, client authorization, source verification, or jurisdiction-specific legal judgment. Outputs are working drafts unless a qualified professional reviews them.
