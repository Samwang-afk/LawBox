# Repository Instructions

## Legal Formal Deliverable Hard Gate

When a legal task involves a document, report, memo, case compilation, pleading, evidence list, legal opinion, client-facing material, court-facing material, or any `.docx` output, classify the deliverable before writing substantive content:

1. `工作草稿`: internal draft only; may be Markdown; must be named with `草稿` or `未出稿审查` if not reviewed.
2. `律师内部报告`: internal strategy analysis; may include risk assessment and litigation suggestions; must still include source boundary, reading review, and legal verification when it cites materials, cases, or law.
3. `提交法院/客户的正式材料`: court-facing or client-facing; must follow the applicable legal Skill template, stay clean and professional, and include required source boundary records.
4. `Word正式交付物`: any formal `.docx`; must pass the full legal export chain before being called final or formal.

For every legal `.docx` or formal legal deliverable, stop and verify these gate items before export:

- Current matter matches `【自定义工作目录】/_系统记录/当前事项.md`; if it does not, switch/build the matter first or ask before continuing.
- The correct legal Skill has been selected, including whether the output is a 法官版、律师版、诉讼文书、证据目录、法律意见 or other type.
- Before writing substantive content, the corresponding legal template/reference file has been identified and recorded, with its key format requirements stated. After generation, run a reverse structure check against that template. For `证据目录`, the controlling template is `诉讼文书起草/templates/证据目录格式.md`; it must use grouped textual paragraphs with `第一组证据` and `证明目的`, and must not be output as a table unless the user expressly overrides this template.
- All cited case/material files have a `读取复查摘要`.
- All cited statutes, regulations, judicial interpretations, or current legal rules have a `法规校验摘要`.
- A `来源边界记录` exists and states verified, unverified, and output boundaries.
- Any user choice that changes scope, version, strategy, amount, claim, authorization, or whether to include/exclude negative cases is recorded in `用户确认记录`.
- Formal Word output has `draft.html`, `preflight-meta.json`, `draft_checked.html`, `出稿前审查报告.md`, and the report status is `PASS` or `FIXED_PASS`.
- Formal Word output is generated only through `法律文书模板与导出` (`html_to_docx.py`) and passes `health_check.py`.

Never treat "content completed" as "legal work completed." A formal legal deliverable is complete only when the required matter routing, template confirmation, reverse structure check, source evidence files, preflight review, export chain, and health check are complete. Direct `pandoc md -> docx` export is allowed only for clearly labeled experiments or drafts, never for a formal legal deliverable.

## Legal Reasoning Layer

Every legal task gets a reasoning level (`推理等级`) before execution, chosen as the lowest sufficient level: L0 (direct answer for simple legal knowledge questions; no Matter Model, no adversarial review), L1 (standard case/contract/document work with a simplified Matter Model), L2 (deliberative: competing legal relationships/causes of action, disputed key facts, strategy or risk decisions), L3 (adversarial: major litigation, formal legal opinions, high-impact matters, or an explicit user request for a devil's-advocate stress test). The controlling protocols live in `skills/legal/法律工作总控/references/` (`reasoning-mode-protocol.md`, `legal-clarification-protocol.md`, `matter-model-protocol.md`, `adversarial-review-protocol.md`, `judgment-protocol.md`), with an executable reference implementation at `skills/legal/法律工作总控/scripts/reasoning_control.py`.

Hard rules:

- Every case fact carries an epistemic status: `CONFIRMED` / `ASSERTED` / `DISPUTED` / `INFERRED` / `UNKNOWN`. Never turn a user assertion (e.g. "he borrowed 200k from me") into an unconditional fact; user labels never auto-decide the legal relationship when contrary material exists.
- Only decision-relevant unknowns that cannot be resolved from existing material or research may be asked to the user (`Blocking Unknown`); at most 1-5 questions per round, ordered Decision > Scope > Evidence > Output > Formatting.
- For L2/L3 tasks, formal drafting of facts/claims/legal argument must happen after Ludus adversarial review and Judgment. The reviewer must produce specific failure mechanisms (Minimum Failure Set), never generic "there is still risk".
- Drafting permission is `PASS` / `CONDITIONAL` / `BLOCKED`. `BLOCKED` forbids formal drafting. `CONDITIONAL` requires explicit assumption/claim/unconfirmed markers in the draft. Preflight review (`preflight_check.py`) hard-blocks exports with `BLOCKED` and requires a Judgment record for declared L2/L3 documents.
- Internal reasoning artifacts (Matter Model, review, Judgment) stay in the system-record area (`推理记录/`) and must never be delivered to clients or written into formal documents.

## Shared Control Protocols

Formal legal matters additionally follow the shared protocols in `skills/legal/法律工作总控/references/`:

- `intake-conflict-protocol.md` — minimum intake checks and conflict awareness; if no real conflict database is connected, mark `组织级利益冲突检索：未执行 / 需人工确认`; never fake an institutional conflict check.
- `matter-lifecycle-protocol.md` — one lifecycle per matter: `INTAKE / ACTIVE / WAITING / REVIEW / DELIVERED / CLOSED` with `status / next_action / pending_from / deadline / owner`.
- `action-approval-protocol.md` — analysis is not authorization; sending, filing, signing, settling, spending, or any externally-effective action requires explicit user approval.
- `post-task-reflection-protocol.md` — reflection only records reusable, de-identified lessons into `knowledge/lessons.md`. The agent must never auto-modify any `SKILL.md`, protocol file, or system rule.
- `sop-contract.md` — business SOPs answer WHEN / INPUT / DO / DECIDE / APPROVE / OUTPUT / CLOSE.

## Verification

Do not claim completion just because steps were executed. Verify against materials, sources, business checks, preflight review, DOCX QC, or health checks where an actually verifiable result exists. On failure, classify the error as 事实 / 证据 / 法律 / 程序 / 执行 / 交付 and return to the corresponding stage; do not randomly retry or redo everything.
