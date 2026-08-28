---
name: legal-work-os-core
description: Chinese legal workflow skills for lawyers, legal counsel, litigation, criminal defense, labor disputes, bankruptcy, contract review, compliance, legal research, and legal document drafting, with lightweight Ludus adversarial review and unified SOP control.
---

# Legal Work OS Core

Use this skill when the user needs Chinese legal work support, including legal consultation, litigation analysis, criminal defense, labor disputes, bankruptcy, contract review, compliance review, legal research, evidence review, or legal document drafting.

## Workflow

1. Read `skills/legal/法律工作总控/SKILL.md` first. Treat it as the main router and shared quality gate for the legal workflow.
2. Let the main router choose the relevant Chinese sub-skill under `skills/legal/`.
3. When a referenced file path is relative, resolve it from this repository root.

## Shared rules

- Clarification, conflict checks, adversarial review, reflection, approval and lifecycle rules are owned by the main router's shared protocols under `skills/legal/法律工作总控/references/`; professional sub-skills must not re-implement them.
- License and attribution notices live in `README.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md` and `LICENSES/`.

Do not replace attorney review, client authorization, source verification, or jurisdiction-specific legal judgment. Outputs are working drafts unless a qualified professional reviews them.
