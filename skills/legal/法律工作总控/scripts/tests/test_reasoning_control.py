#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""推理控制层行为测试：覆盖 Case A-H 行为约定。"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "reasoning_control.py"
sys.path.insert(0, str(SCRIPT.parent))

from reasoning_control import (  # noqa: E402
    classify_mode,
    evaluate_unknowns,
    judge,
    reasoning_qa,
    validate_challenge,
    validate_matter_model,
)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


class CaseASimpleQuestionTests(unittest.TestCase):
    """Case A：简单法律咨询 → L0，不启动 Matter Model / Challenger。"""

    def test_simple_knowledge_question_is_l0(self) -> None:
        result = classify_mode({"task_type": "knowledge_question"})
        self.assertEqual(result["mode"], "L0")
        self.assertFalse(result["requires"]["matter_model"])
        self.assertFalse(result["requires"]["adversarial"])
        self.assertFalse(result["requires"]["judgment"])

    def test_l0_even_with_single_l2_flag_disabled(self) -> None:
        result = classify_mode(
            {
                "task_type": "knowledge_question",
                "competing_legal_relationships": False,
                "conclusion_depends_on_unknown_facts": False,
            }
        )
        self.assertEqual(result["mode"], "L0")

    def test_case_task_without_triggers_is_l1(self) -> None:
        result = classify_mode({"task_type": "case_task"})
        self.assertEqual(result["mode"], "L1")
        self.assertTrue(result["requires"]["matter_model"])
        self.assertFalse(result["requires"]["adversarial"])


class CaseBMaterialAlreadyAvailableTests(unittest.TestCase):
    """Case B：事实缺失但不阻塞——合同已上传，不得再问用户要合同。"""

    def test_from_material_unknown_never_asked(self) -> None:
        matter = {
            "unknowns": [
                {
                    "id": "U1",
                    "question": "合同具体条款内容",
                    "materiality": "critical",
                    "affects": ["legal_relationship"],
                    "resolution": "from_material",
                    "status": "open",
                }
            ]
        }
        result = evaluate_unknowns(matter)
        self.assertEqual(result["blocking_unknowns"], [])
        self.assertEqual(result["questions"], [])
        self.assertEqual(result["actions"][0]["action"], "read_material")

    def test_search_unknown_never_asked(self) -> None:
        matter = {
            "unknowns": [
                {
                    "id": "U2",
                    "question": "现行有效条文内容",
                    "materiality": "critical",
                    "affects": ["cause_of_action"],
                    "resolution": "search",
                    "status": "open",
                }
            ]
        }
        result = evaluate_unknowns(matter)
        self.assertEqual(result["blocking_unknowns"], [])
        self.assertEqual(result["actions"][0]["action"], "search")


class CaseCBlockingUnknownTests(unittest.TestCase):
    """Case C：只有转账记录，不得直接认定民间借贷。"""

    def _matter(self) -> dict:
        return {
            "facts": {
                "confirmed": [
                    {
                        "id": "F1",
                        "statement": "2025-03-01 甲向乙转账 20 万元",
                        "source": "银行流水",
                        "evidence": ["银行流水单"],
                    }
                ],
                "asserted": [
                    {
                        "id": "F2",
                        "statement": "用户主张款项性质为借款",
                        "asserted_by": "用户",
                        "source": "用户口述",
                    }
                ],
                "unknown": [
                    {
                        "id": "U3",
                        "question": "20 万元款项性质是什么",
                        "materiality": "critical",
                        "affects": ["legal_relationship", "cause_of_action"],
                        "resolution": "ask_user",
                        "status": "open",
                        "possible_values": ["借款", "投资", "货款", "垫付", "其他"],
                    }
                ],
            }
        }

    def test_transfer_only_matter_model_is_valid_and_blocking(self) -> None:
        matter = self._matter()
        validation = validate_matter_model(matter)
        self.assertTrue(validation["ok"], validation["errors"])
        result = evaluate_unknowns(matter)
        self.assertEqual(len(result["blocking_unknowns"]), 1)
        self.assertEqual(result["blocking_unknowns"][0]["id"], "U3")
        self.assertEqual(len(result["questions"]), 1)
        self.assertIn("借款", result["questions"][0]["options"])
        self.assertIn("不确定", result["questions"][0]["options"])

    def test_asserted_upgraded_to_confirmed_is_rejected(self) -> None:
        matter = self._matter()
        matter["facts"]["confirmed"].append(
            {
                "id": "F3",
                "statement": "被告向原告借款20万元",
                "source": "用户口述",
            }
        )
        validation = validate_matter_model(matter)
        self.assertFalse(validation["ok"])
        self.assertTrue(any("升级" in e or "口述" in e for e in validation["errors"]), validation["errors"])

    def test_question_budget_caps_at_five(self) -> None:
        unknowns = [
            {
                "id": f"U{i}",
                "question": f"问题{i}",
                "materiality": "critical",
                "affects": ["decision"],
                "resolution": "ask_user",
                "status": "open",
            }
            for i in range(8)
        ]
        plan = evaluate_unknowns({"unknowns": unknowns})
        self.assertEqual(len(plan["questions"]), 5)
        self.assertEqual(len(plan["deferred"]), 3)

    def test_dependency_prunes_questions(self) -> None:
        unknowns = [
            {
                "id": "A",
                "question": "款项性质",
                "materiality": "critical",
                "affects": ["decision"],
                "resolution": "ask_user",
                "status": "open",
            },
            {
                "id": "B",
                "question": "利息约定",
                "materiality": "high",
                "affects": ["output"],
                "resolution": "ask_user",
                "status": "open",
                "depends_on": ["A"],
            },
        ]
        plan = evaluate_unknowns({"unknowns": unknowns})
        self.assertEqual([q["id"] for q in plan["questions"]], ["A"])
        self.assertEqual([d["id"] for d in plan["deferred"]], ["B"])


class CaseDCompetingRelationshipsTests(unittest.TestCase):
    """Case D：出现『利润五五分』且用户主张借款 → L2，保留两个假设。"""

    def test_competing_relationship_classifies_l2(self) -> None:
        result = classify_mode(
            {
                "task_type": "case_task",
                "competing_legal_relationships": True,
                "disputed_key_facts": True,
            }
        )
        self.assertEqual(result["mode"], "L2")
        self.assertTrue(result["requires"]["adversarial"])
        self.assertTrue(result["requires"]["judgment"])

    def test_matter_model_keeps_two_hypotheses(self) -> None:
        matter = {
            "facts": {
                "confirmed": [
                    {"id": "F1", "statement": "20 万元转账", "source": "银行流水", "evidence": ["流水单"]},
                    {"id": "F2", "statement": "聊天记录出现『利润我们五五分』", "source": "聊天记录", "evidence": ["聊天截图"]},
                ],
                "asserted": [
                    {"id": "F3", "statement": "用户主张为借款", "asserted_by": "用户", "source": "用户口述"}
                ],
            },
            "legal_relationships": {"candidates": ["H1 民间借贷", "H2 投资/合作"], "current_view": None},
        }
        validation = validate_matter_model(matter)
        self.assertTrue(validation["ok"], validation["errors"])
        self.assertEqual(validation["warnings"], [])

    def test_premature_collapse_warns(self) -> None:
        matter = {
            "legal_relationships": {
                "candidates": ["H1 民间借贷", "H2 投资/合作"],
                "current_view": "H1 民间借贷",
                "confidence": "medium",
            }
        }
        validation = validate_matter_model(matter)
        self.assertTrue(any("过早收敛" in w for w in validation["warnings"]))


class CaseEChallengerSpecificityTests(unittest.TestCase):
    """Case E：Challenger 必须指出具体失败机制，不能只说『存在败诉风险』。"""

    def test_generic_risk_rejected(self) -> None:
        challenge = {
            "failure_conditions": [
                {
                    "id": "FC-G",
                    "condition": "仍存在败诉风险",
                    "type": "fact",
                    "impact": "high",
                    "current_support": "转账与催还聊天",
                    "weakness": "结果不确定",
                }
            ]
        }
        result = validate_challenge(challenge)
        self.assertFalse(result["valid"])
        self.assertTrue(any("泛化" in e for e in result["errors"]), result["errors"])

    def test_specific_failure_condition_accepted(self) -> None:
        challenge = {
            "failure_conditions": [
                {
                    "id": "FC-001",
                    "condition": "无法证明借款合意",
                    "type": "fact",
                    "current_support": "仅有转账记录",
                    "weakness": "转账本身无法必然证明款项性质",
                    "impact": "fatal",
                    "consequence": "民间借贷关系不成立",
                    "mitigation": "",
                    "needed": "借条 / 还款承诺 / 明确借款聊天 / 部分还款行为",
                }
            ]
        }
        result = validate_challenge(challenge)
        self.assertTrue(result["valid"], result["errors"])

    def test_empty_challenge_rejected(self) -> None:
        result = validate_challenge({})
        self.assertFalse(result["valid"])


class CaseFDraftingBlockedTests(unittest.TestCase):
    """Case F：关键法律关系不明 → drafting_permission = BLOCKED。"""

    def _deliberation(self, **overrides) -> dict:
        data = {
            "issue": "20 万元款项性质",
            "challenge": {
                "failure_conditions": [
                    {
                        "id": "FC-001",
                        "condition": "无法证明借款合意",
                        "type": "fact",
                        "current_support": "仅有转账记录",
                        "weakness": "转账本身无法必然证明款项性质",
                        "impact": "fatal",
                        "consequence": "民间借贷关系不成立",
                        "mitigation": "",
                    }
                ]
            },
            "unresolved": [{"id": "U3", "question": "款项性质", "materiality": "critical"}],
        }
        data.update(overrides)
        return data

    def test_critical_unresolved_blocks(self) -> None:
        result = judge(self._deliberation())
        self.assertEqual(result["judgment"]["drafting_permission"], "BLOCKED")
        self.assertEqual(result["judgment"]["status"], "blocked")

    def test_invalid_challenge_blocks(self) -> None:
        result = judge(
            {
                "issue": "测试",
                "challenge": {
                    "failure_conditions": [{"id": "G", "condition": "存在不确定性", "type": "fact", "impact": "low", "current_support": "x", "weakness": "y"}]
                },
            }
        )
        self.assertEqual(result["judgment"]["drafting_permission"], "BLOCKED")
        self.assertTrue(result["challenge_errors"])


class CaseGConditionalDraftTests(unittest.TestCase):
    """Case G：用户明确要求按借贷做内部草稿 → CONDITIONAL，条件必须显式。"""

    def test_user_requested_conditional_draft_allowed(self) -> None:
        deliberation = {
            "issue": "20 万元款项性质",
            "challenge": {
                "failure_conditions": [
                    {
                        "id": "FC-001",
                        "condition": "无法证明借款合意",
                        "type": "fact",
                        "current_support": "仅有转账记录",
                        "weakness": "转账本身无法必然证明款项性质",
                        "impact": "fatal",
                        "consequence": "民间借贷关系不成立",
                        "mitigation": "",
                    }
                ]
            },
            "unresolved": [{"id": "U3", "question": "款项性质", "materiality": "critical"}],
            "user_requested_conditional_draft": True,
            "assumptions": ["按用户主张暂以民间借贷构建草稿"],
        }
        result = judge(deliberation)
        self.assertEqual(result["judgment"]["drafting_permission"], "CONDITIONAL")
        self.assertTrue(result["judgment"]["conditions"])

    def test_supported_clean_case_passes(self) -> None:
        deliberation = {
            "issue": "借款返还请求权",
            "challenge": {
                "failure_conditions": [
                    {
                        "id": "FC-002",
                        "condition": "时效已过的低概率风险",
                        "type": "procedure",
                        "current_support": "借款日 2024-01-01",
                        "weakness": "时效起算点可能存在争议",
                        "impact": "low",
                        "mitigation": "已检索时效规则，未超过",
                    }
                ]
            },
            "unresolved": [],
        }
        result = judge(deliberation)
        self.assertEqual(result["judgment"]["drafting_permission"], "PASS")
        self.assertEqual(result["judgment"]["confidence"]["level"], "high")


class CaseHDeliveryGateRetainedTests(unittest.TestCase):
    """Case H：新推理层通过后，既有交付质量门必须继续运行。"""

    def test_pass_judgment_never_bypasses_delivery_chain(self) -> None:
        deliberation = {
            "issue": "测试争点",
            "challenge": {
                "failure_conditions": [
                    {
                        "id": "FC-003",
                        "condition": "对方可能主张显失公平",
                        "type": "law",
                        "current_support": "合同已签署",
                        "weakness": "合同签订背景不明",
                        "impact": "low",
                        "mitigation": "已检索类案",
                    }
                ]
            },
            "unresolved": [],
        }
        result = judge(deliberation)
        self.assertTrue(result["judgment"]["do_not_bypass_delivery_gates"])
        self.assertEqual(
            result["judgment"]["delivery_chain_required"],
            ["法律文书出稿前审查", "法律文书模板与导出", "health_check"],
        )

    def test_qa_blocks_pass_on_unresolved_jurisdiction(self) -> None:
        matter = {
            "facts": {"confirmed": []},
            "procedural": {"jurisdiction": {"status": "unknown"}, "limitation": {"status": "resolved"}},
        }
        judgment = {"drafting_permission": "PASS", "status": "supported"}
        result = reasoning_qa(matter, judgment)
        self.assertTrue(result["blocked"])
        self.assertTrue(any(f["check"] == "procedure_obstacle_ignored" for f in result["findings"]))

    def test_qa_catches_conclusion_beyond_evidence(self) -> None:
        matter = {
            "facts": {
                "asserted": [{"id": "F9", "statement": "用户主张借款", "asserted_by": "用户"}],
            }
        }
        judgment = {"decisive_facts": ["F9"], "status": "supported", "drafting_permission": "PASS"}
        result = reasoning_qa(matter, judgment)
        self.assertTrue(any(f["check"] == "conclusion_beyond_evidence" for f in result["findings"]))


class CliSmokeTests(unittest.TestCase):
    def test_classify_cli(self) -> None:
        with subprocess.Popen(
            [sys.executable, str(SCRIPT), "classify", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        ) as proc:
            stdout, _ = proc.communicate(json.dumps({"task_type": "knowledge_question"}, ensure_ascii=False))
        data = json.loads(stdout)
        self.assertEqual(data["mode"], "L0")

    def test_validate_cli_exit_code(self) -> None:
        bad = {"facts": {"confirmed": [{"id": "X", "statement": "借款", "source": "用户口述"}]}}
        with subprocess.Popen(
            [sys.executable, str(SCRIPT), "validate", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        ) as proc:
            stdout, _ = proc.communicate(json.dumps(bad, ensure_ascii=False))
        data = json.loads(stdout)
        self.assertFalse(data["ok"])


if __name__ == "__main__":
    unittest.main()
