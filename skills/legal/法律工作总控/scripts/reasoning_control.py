#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""推理控制层可执行参照实现。

对应协议：
- reasoning-mode-protocol.md            -> classify
- legal-clarification-protocol.md       -> clarify
- matter-model-protocol.md              -> validate
- adversarial-review-protocol.md  -> challenge-check
- judgment-protocol.md                  -> judge / qa

本脚本只实现协议中可确定的决策规则；事实判断、检索与法律推理仍由 Agent 完成。
仅依赖 Python 标准库。

用法示例：
  python reasoning_control.py classify attrs.json
  python reasoning_control.py clarify matter.json
  python reasoning_control.py validate matter.json
  python reasoning_control.py challenge-check challenge.json
  python reasoning_control.py judge deliberation.json
  python reasoning_control.py qa matter.json judgment.json
输入文件可用 '-' 表示从 stdin 读取 JSON。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

L0, L1, L2, L3 = "L0", "L1", "L2", "L3"

FACT_BUCKETS = ["confirmed", "asserted", "disputed", "inferred", "unknown"]

L3_TRIGGER_KEYS = [
    "major_litigation",
    "formal_legal_opinion",
    "high_impact_contract",
    "major_transaction_risk",
    "critical_criminal_defense",
    "irreversible_procedure",
    "user_requested_adversarial",
    "high_uncertainty",
    "severe_error_consequence",
]

L2_TRIGGER_KEYS = [
    "competing_legal_relationships",
    "competing_causes_of_action",
    "disputed_key_facts",
    "competing_evidence_readings",
    "claim_selection_needed",
    "defense_selection_needed",
    "procedure_strategy_needed",
    "win_analysis_requested",
    "liability_judgment_requested",
    "litigation_strategy_requested",
    "risk_comparison_requested",
    "conclusion_depends_on_unknown_facts",
]

L3_TRIGGER_LABELS = {
    "major_litigation": "重大诉讼",
    "formal_legal_opinion": "正式法律意见",
    "high_impact_contract": "高影响合同",
    "major_transaction_risk": "重大交易风险",
    "critical_criminal_defense": "关键刑事辩护策略",
    "irreversible_procedure": "不可逆程序决定",
    "user_requested_adversarial": "用户要求反方压力测试",
    "high_uncertainty": "初步判断高度不确定",
    "severe_error_consequence": "错误结论可能造成严重后果",
}

L2_TRIGGER_LABELS = {
    "competing_legal_relationships": "存在两个以上合理法律关系",
    "competing_causes_of_action": "存在两个以上合理请求权基础",
    "disputed_key_facts": "关键事实存在争议",
    "competing_evidence_readings": "证据存在竞争性解释",
    "claim_selection_needed": "需要选择诉请",
    "defense_selection_needed": "需要选择抗辩",
    "procedure_strategy_needed": "需要判断程序策略",
    "win_analysis_requested": "用户要求胜诉分析",
    "liability_judgment_requested": "用户要求责任判断",
    "litigation_strategy_requested": "用户要求诉讼策略",
    "risk_comparison_requested": "用户要求法律风险比较",
    "conclusion_depends_on_unknown_facts": "结论高度依赖未知事实",
}

GENERIC_RISK_RE = re.compile(
    r"(存在.{0,8}风险|风险.{0,4}(?:仍)?存在|结果不确定|存在不确定性|"
    r"可能.{0,8}不同|败诉风险|有败诉可能|法院可能|裁判可能|尚不确定)"
)

MATERIALITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}

AFFECTS_RANK = {
    "decision": 5,
    "legal_relationship": 5,
    "cause_of_action": 5,
    "scope": 4,
    "evidence": 3,
    "evidence_requirement": 3,
    "output": 2,
    "formatting": 1,
}


def _truthy(attributes: dict[str, Any], key: str) -> bool:
    return bool(attributes.get(key))


def classify_mode(attributes: dict[str, Any]) -> dict[str, Any]:
    l3_hits = [L3_TRIGGER_LABELS[k] for k in L3_TRIGGER_KEYS if _truthy(attributes, k)]
    l2_hits = [L2_TRIGGER_LABELS[k] for k in L2_TRIGGER_KEYS if _truthy(attributes, k)]
    task_type = str(attributes.get("task_type") or "knowledge_question")

    if l3_hits:
        mode = L3
    elif l2_hits:
        mode = L2
    elif task_type == "knowledge_question":
        mode = L0
    else:
        mode = L1

    requires = {
        "matter_model": mode != L0,
        "clarification_gate": mode != L0,
        "adversarial": mode in {L2, L3},
        "judgment": mode in {L2, L3},
        "reverse_research": mode == L3,
        "persist_reasoning": mode in {L2, L3},
    }
    return {
        "mode": mode,
        "l3_triggers": l3_hits,
        "l2_triggers": l2_hits,
        "requires": requires,
        "note": "满足任务需要的最低充分推理等级；新事实出现后重新分类，允许 L0→L1→L2→L3 升级。",
    }


def _resolve_rank(unknown: dict[str, Any]) -> int:
    affects = unknown.get("affects") or []
    if not isinstance(affects, list):
        affects = []
    ranks = [AFFECTS_RANK.get(str(a), 0) for a in affects]
    return min(ranks) if ranks else 0


def plan_questions(
    unknowns: list[dict[str, Any]],
    max_questions: int = 5,
    all_unknowns: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    open_unknowns = [u for u in unknowns if str(u.get("status") or "open") == "open"]
    context = all_unknowns if all_unknowns is not None else unknowns
    by_id = {str(u.get("id") or ""): u for u in context if u.get("id")}

    def ready(u: dict[str, Any]) -> bool:
        deps = u.get("depends_on") or []
        if isinstance(deps, str):
            deps = [deps]
        for dep in deps:
            dep_id = str(dep)
            if dep_id in by_id and str(by_id[dep_id].get("status") or "open") == "open":
                return False
        return True

    ordered = sorted(
        open_unknowns,
        key=lambda u: (
            -MATERIALITY_RANK.get(str(u.get("materiality") or "low"), 0),
            -_resolve_rank(u),
            str(u.get("question") or ""),
        ),
    )
    questions: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    for u in ordered:
        if not ready(u):
            deferred.append(u)
            continue
        if len(questions) >= max_questions:
            deferred.append(u)
            continue
        options = u.get("possible_values") or []
        if not isinstance(options, list):
            options = []
        question = {
            "id": u.get("id"),
            "question": u.get("question"),
            "options": list(options) + ["不确定"],
            "materiality": u.get("materiality"),
            "affects": u.get("affects"),
        }
        questions.append(question)
    return {
        "questions": questions,
        "deferred": [{"id": u.get("id"), "question": u.get("question"), "reason": "依赖其他问题先解决或超出单轮预算"} for u in deferred],
        "budget_rule": f"单轮原则上 1–{max_questions} 个问题，按 Decision > Scope > Evidence > Output > Formatting 排序",
    }


def evaluate_unknowns(matter: dict[str, Any]) -> dict[str, Any]:
    unknowns = matter.get("unknowns") or matter.get("facts", {}).get("unknown") or []
    if not isinstance(unknowns, list):
        unknowns = []
    blocking: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for u in unknowns:
        if not isinstance(u, dict):
            continue
        if str(u.get("status") or "open") != "open":
            continue
        resolution = str(u.get("resolution") or "ask_user")
        materiality = str(u.get("materiality") or "low")
        if resolution == "from_material":
            actions.append({"id": u.get("id"), "action": "read_material", "detail": "先从现有材料/工作区/已读文件确定，不得直接问用户"})
        elif resolution == "search":
            actions.append({"id": u.get("id"), "action": "search", "detail": "先完成法规/案例/Wiki 检索，再评估是否仍需提问"})
        elif resolution == "assumption_allowed":
            actions.append({"id": u.get("id"), "action": "record_assumption", "detail": "显式记录假设，不提问"})
        elif materiality in {"critical", "high"}:
            blocking.append(u)
        else:
            actions.append({"id": u.get("id"), "action": "note_non_blocking", "detail": "materiality 为 medium/low，写入缺口归档，不阻塞、不提问"})
    plan = plan_questions(blocking, all_unknowns=unknowns)
    return {
        "blocking_unknowns": [{"id": u.get("id"), "question": u.get("question"), "materiality": u.get("materiality")} for u in blocking],
        "questions": plan["questions"],
        "deferred": plan["deferred"],
        "actions": actions,
        "rule": "只有 decision-relevant 且无法通过现有信息解决（critical/high 且 resolution=ask_user）才向用户提问",
    }


def _check_fact_item(bucket: str, item: dict[str, Any], idx: int, errors: list[str], warnings: list[str]) -> None:
    fid = str(item.get("id") or f"{bucket}#{idx}")
    if bucket == "unknown":
        statement = str(item.get("question") or item.get("statement") or "").strip()
    else:
        statement = str(item.get("statement") or item.get("proposition") or "").strip()
    if not statement:
        key = "question" if bucket == "unknown" else "statement"
        errors.append(f"{fid}: 缺少 {key}")
    if bucket == "confirmed":
        source = str(item.get("source") or "")
        evidence = item.get("evidence") or []
        if not source:
            errors.append(f"{fid}: CONFIRMED 事实缺少 source")
        if not isinstance(evidence, list) or not evidence:
            if "用户口述" in source or "当事人陈述" in source or "用户陈述" in source:
                errors.append(f"{fid}: CONFIRMED 事实仅有用户口述来源且无证据，禁止把当事人主张升级为确定事实")
            else:
                warnings.append(f"{fid}: CONFIRMED 事实未列明证据，建议补充 evidence")
    elif bucket == "asserted":
        if not item.get("asserted_by"):
            errors.append(f"{fid}: ASSERTED 事实缺少 asserted_by")
    elif bucket == "disputed":
        if not item.get("positions"):
            errors.append(f"{fid}: DISPUTED 事实缺少 positions")
    elif bucket == "inferred":
        if not item.get("based_on"):
            errors.append(f"{fid}: INFERRED 事实缺少 based_on")
    elif bucket == "unknown":
        if not item.get("materiality"):
            errors.append(f"{fid}: UNKNOWN 缺少 materiality")
        if not item.get("affects"):
            errors.append(f"{fid}: UNKNOWN 缺少 affects")
        if not item.get("question"):
            errors.append(f"{fid}: UNKNOWN 缺少 question")


def validate_matter_model(matter: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    facts = matter.get("facts") or {}
    if not isinstance(facts, dict):
        errors.append("matter.facts 必须是对象")
        facts = {}

    seen_ids: set[str] = set()
    for bucket in FACT_BUCKETS:
        items = facts.get(bucket) or []
        if not isinstance(items, list):
            errors.append(f"facts.{bucket} 必须是数组")
            continue
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"facts.{bucket}[{idx}] 必须是对象")
                continue
            _check_fact_item(bucket, item, idx, errors, warnings)
            fid = str(item.get("id") or "")
            if fid:
                if fid in seen_ids:
                    errors.append(f"{fid}: 同一事实 id 出现在多个认知状态桶中（双重事实源，禁止）")
                seen_ids.add(fid)

    rels = matter.get("legal_relationships") or {}
    candidates = rels.get("candidates") or []
    if not isinstance(candidates, list):
        errors.append("legal_relationships.candidates 必须是数组")
        candidates = []
    current_view = rels.get("current_view")
    confidence = str(rels.get("confidence") or "").lower()
    if len(candidates) >= 2 and current_view and confidence != "low":
        warnings.append("存在多个候选法律关系且已选 current_view 但非 low confidence：不得过早收敛竞争性假设")

    issues = matter.get("issues") or []
    if not isinstance(issues, list):
        errors.append("issues 必须是数组")
        issues = []

    judgment = matter.get("judgment")
    if judgment and isinstance(judgment, dict):
        permission = judgment.get("drafting_permission")
        if permission and permission not in {"PASS", "CONDITIONAL", "BLOCKED"}:
            errors.append(f"judgment.drafting_permission 非法：{permission}")
        level = judgment.get("confidence", {})
        if isinstance(level, dict) and level.get("level") not in {"high", "medium", "low", None}:
            errors.append(f"judgment.confidence.level 非法：{level.get('level')}（禁止虚构百分比）")
    elif judgment is not None:
        errors.append("judgment 必须是对象")

    meta = matter.get("meta") or {}
    mode = str(meta.get("reasoning_mode") or "")
    if mode and mode not in {L1, L2, L3}:
        errors.append(f"meta.reasoning_mode 非法：{mode}")

    return {"ok": not errors, "errors": errors, "warnings": warnings}


def validate_challenge(challenge: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    fcs = challenge.get("failure_conditions") or []
    if not isinstance(fcs, list):
        errors.append("failure_conditions 必须是数组")
        fcs = []
    if not fcs:
        errors.append("缺少 failure_conditions：不得以『存在风险/结果不确定』等泛化表述替代具体失败机制")
        return {"valid": False, "errors": errors, "failure_conditions": []}
    for i, fc in enumerate(fcs):
        if not isinstance(fc, dict):
            errors.append(f"failure_conditions[{i}] 必须是对象")
            continue
        condition = str(fc.get("condition") or "").strip()
        if not condition:
            errors.append(f"failure_conditions[{i}] 缺少 condition")
            continue
        if GENERIC_RISK_RE.search(condition):
            errors.append(f"failure_conditions[{i}] 为泛化风险表述，必须指出具体失败机制（哪一要件/哪一证据/哪一法条）：{condition}")
        if fc.get("type") not in {"fact", "evidence", "law", "procedure"}:
            errors.append(f"failure_conditions[{i}] type 非法：{fc.get('type')}（fact|evidence|law|procedure）")
        if fc.get("impact") not in {"low", "medium", "high", "fatal"}:
            errors.append(f"failure_conditions[{i}] impact 非法：{fc.get('impact')}（low|medium|high|fatal）")
        if not fc.get("current_support"):
            errors.append(f"failure_conditions[{i}] 缺少 current_support")
        if not fc.get("weakness"):
            errors.append(f"failure_conditions[{i}] 缺少 weakness")
    return {"valid": not errors, "errors": errors, "failure_conditions": fcs}


def judge(deliberation: dict[str, Any]) -> dict[str, Any]:
    challenge = deliberation.get("challenge") or {}
    challenge_result = validate_challenge(challenge)
    fcs = challenge_result["failure_conditions"]

    unresolved = deliberation.get("unresolved") or []
    if not isinstance(unresolved, list):
        unresolved = []
    critical_unresolved = [u for u in unresolved if str(u.get("materiality") or "") == "critical"]
    unmitigated_fatal = [fc for fc in fcs if fc.get("impact") == "fatal" and not fc.get("mitigation")]
    high_fcs = [fc for fc in fcs if fc.get("impact") in {"fatal", "high"}]

    user_requested_conditional = bool(deliberation.get("user_requested_conditional_draft"))
    user_forbids_conditional = bool(deliberation.get("user_forbids_conditional"))

    if not challenge_result["valid"]:
        status, confidence, permission = "blocked", "low", "BLOCKED"
        next_best_action = ["重跑 Challenger：必须给出具体 failure_conditions，禁止泛化风险表述"]
    elif critical_unresolved or unmitigated_fatal:
        status, confidence = "blocked", "low"
        if user_requested_conditional:
            permission = "CONDITIONAL"
            next_best_action = ["显式列明假设与未确认事实后按条件稿继续", "补充材料或澄清后重新 Judgment"]
        else:
            permission = "BLOCKED"
            next_best_action = ["返回 Clarification / Evidence / Research / Professional Analysis 解决关键未知或致命失败条件"]
    elif high_fcs:
        status, confidence = "provisionally_supported", "medium"
        if user_forbids_conditional:
            permission = "BLOCKED"
            next_best_action = ["先解决 high/fatal failure conditions 再起草"]
        else:
            permission = "CONDITIONAL"
            next_best_action = ["按条件稿起草并显式标识假设、用户主张、未确认事实、待补证据"]
    else:
        status, confidence = "supported", "high"
        permission = "CONDITIONAL" if deliberation.get("conditions") else "PASS"
        next_best_action = ["进入正式业务起草", "交付仍须通过法律文书出稿前审查与导出链路"]

    conditions = []
    note = ""
    if permission == "CONDITIONAL":
        conditions.extend([{"failure_condition": fc.get("id"), "condition": fc.get("condition"), "impact": fc.get("impact")} for fc in high_fcs])
        conditions.extend([{"unresolved": u.get("id"), "question": u.get("question")} for u in critical_unresolved])
        conditions.extend(deliberation.get("assumptions") or [])
        if status == "blocked":
            note = "仅允许显式条件性内部草稿；正式交付仍被阻塞，补齐材料或澄清后须重新 Judgment。"

    return {
        "judgment": {
            "issue": deliberation.get("issue"),
            "status": status,
            "confidence": {
                "level": confidence,
                "note": "epistemic confidence，不是胜诉概率；禁止虚构百分比",
            },
            "failure_conditions": fcs,
            "unresolved": unresolved,
            "drafting_permission": permission,
            "conditions": conditions,
            "note": note,
            "next_best_action": next_best_action,
            "delivery_chain_required": ["法律文书出稿前审查", "法律文书模板与导出", "health_check"],
            "do_not_bypass_delivery_gates": True,
        },
        "challenge_errors": challenge_result["errors"],
    }


def reasoning_qa(matter: dict[str, Any], judgment: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    facts = matter.get("facts") or {}
    if not isinstance(facts, dict):
        facts = {}
    confirmed_ids = {str(f.get("id")) for f in (facts.get("confirmed") or []) if isinstance(f, dict) and f.get("id")}
    fact_status = {}
    for bucket in FACT_BUCKETS:
        for f in facts.get(bucket) or []:
            if isinstance(f, dict) and f.get("id"):
                fact_status.setdefault(str(f.get("id")), bucket)

    decisive = judgment.get("decisive_facts") or []
    acknowledged = {str(x) for x in (judgment.get("acknowledged_non_confirmed") or judgment.get("acknowledged_non_established") or [])}
    unresolved_ids = {str(u.get("id") if isinstance(u, dict) else u) for u in (judgment.get("unresolved") or [])}
    for df in decisive:
        fid = str(df.get("id")) if isinstance(df, dict) else str(df)
        if fid and fid not in confirmed_ids and fid not in acknowledged and fid not in unresolved_ids:
            findings.append({
                "level": "P1",
                "check": "conclusion_beyond_evidence",
                "detail": f"决定性事实 {fid} 当前状态为 {fact_status.get(fid, '未知')}，非 CONFIRMED 且未在结论中披露，结论可能超过证据",
            })

    for issue in matter.get("issues") or []:
        if not isinstance(issue, dict):
            continue
        has_conclusion = bool(issue.get("provisional_conclusion")) or judgment.get("status") in {"supported", "provisionally_supported"}
        if has_conclusion and not issue.get("burden_of_proof"):
            findings.append({
                "level": "P1",
                "check": "burden_of_proof_missing",
                "detail": f"争点 {issue.get('id')} 已有结论但缺少举证责任分配（burden_of_proof）",
            })

    procedural = matter.get("procedural") or {}
    for key, label in [("jurisdiction", "管辖"), ("limitation", "时效")]:
        value = procedural.get(key)
        if isinstance(value, dict) and value.get("status") == "unknown" and judgment.get("drafting_permission") == "PASS":
            findings.append({
                "level": "P0",
                "check": "procedure_obstacle_ignored",
                "detail": f"{label}未解决但起草许可为 PASS，程序障碍可能使正式文书产生实质错误",
            })

    if facts.get("inferred") and not judgment.get("assumptions") and judgment.get("status") == "provisionally_supported":
        findings.append({
            "level": "P2",
            "check": "unexposed_assumptions",
            "detail": "Matter Model 存在推断事实但 Judgment 未列明假设",
        })

    rels = matter.get("legal_relationships") or {}
    candidates = rels.get("candidates") or []
    competing = judgment.get("competing_positions") or []
    if len(candidates) >= 2 and judgment.get("status") == "supported" and not competing:
        findings.append({
            "level": "P0",
            "check": "competing_hypothesis_collapse",
            "detail": "Matter Model 存在多个候选法律关系，但 Judgment 未展示竞争性立场，存在过早收敛风险",
        })

    p0 = [f for f in findings if f.get("level") == "P0"]
    return {"findings": findings, "p0_count": len(p0), "blocked": bool(p0)}


def _load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else open(path, "r", encoding="utf-8").read()
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("输入必须是 JSON 对象")
    return data


def main() -> int:
    for stream in (sys.stdin, sys.stdout):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    parser = argparse.ArgumentParser(description="推理控制层可执行参照实现")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("classify", help="推理等级分类")
    p.add_argument("attrs", help="任务属性 JSON 文件（- 表示 stdin）")

    p = sub.add_parser("clarify", help="澄清门：判定 blocking unknowns 与提问计划")
    p.add_argument("matter", help="Matter Model JSON 文件（- 表示 stdin）")

    p = sub.add_parser("validate", help="校验 Matter Model schema 与认知状态")
    p.add_argument("matter", help="Matter Model JSON 文件（- 表示 stdin）")

    p = sub.add_parser("challenge-check", help="校验 Challenger 输出是否给出具体失败机制")
    p.add_argument("challenge", help="Challenger 输出 JSON 文件（- 表示 stdin）")

    p = sub.add_parser("judge", help="Judgment 与起草许可派生")
    p.add_argument("deliberation", help="审议输入 JSON 文件（- 表示 stdin）")

    p = sub.add_parser("qa", help="Reasoning QA（与交付 QA 分离）")
    p.add_argument("matter", help="Matter Model JSON 文件（- 表示 stdin）")
    p.add_argument("judgment", help="Judgment JSON 文件（- 表示 stdin）")

    args = parser.parse_args()
    try:
        if args.command == "classify":
            result = classify_mode(_load(args.attrs))
        elif args.command == "clarify":
            result = evaluate_unknowns(_load(args.matter))
        elif args.command == "validate":
            result = validate_matter_model(_load(args.matter))
        elif args.command == "challenge-check":
            result = validate_challenge(_load(args.challenge))
        elif args.command == "judge":
            result = judge(_load(args.deliberation))
        else:
            result = reasoning_qa(_load(args.matter), _load(args.judgment))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
