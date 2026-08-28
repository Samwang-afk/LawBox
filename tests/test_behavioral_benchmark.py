#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Legal Work OS Core — 行为测试基准（Benchmark）。

覆盖：
  Case 01-03 简单法律咨询（不 overthink、不乱问）
  Case 04-05 模糊欠款（不自动认定民间借贷；款项性质为 Blocking Unknown）
  Case 06    文件已上传（不重复让用户上传）
  Case 07-08 用户法律定性冲突（保留竞争性解释）
  Case 09    合同局部修订（surgical change）
  Case 10    合同审查立场 hard gate
  Case 11    Formal Word / DOCX 管线不失效
  Case 12    External Action 无授权不执行
  Case 13    Matter Conflict 不做假
  Case 14-15 Reflection（正常成功不写；可泛化错误去敏化后写）
  Case 16    Privacy（lessons.md 不泄露个案信息）
  Case 17-24 仓库结构 / License / 清理 / 协议存在性 / 禁止自动改 Skill
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROUTER = REPO / "skills" / "legal" / "法律工作总控"
REFS = ROUTER / "references"
RC_SCRIPT = ROUTER / "scripts" / "reasoning_control.py"

sys.path.insert(0, str(RC_SCRIPT.parent))
from reasoning_control import (  # noqa: E402
    classify_mode,
    evaluate_unknowns,
    judge,
    validate_matter_model,
)


def read(p: Path) -> str:
    with io.open(p, encoding="utf-8") as f:
        return f.read()


def router_text() -> str:
    return read(ROUTER / "SKILL.md")


def ref(name: str) -> str:
    return read(REFS / name)


# ---------------------------------------------------------------- 简单咨询

class Case01SimpleConsultation(unittest.TestCase):
    """简单法律咨询不得复杂化：L0，不建档、不问问题、不反向复核。"""

    def test_simple_knowledge_question_is_l0(self):
        result = classify_mode({"task_type": "knowledge_question"})
        self.assertEqual(result["mode"], "L0")
        self.assertFalse(result["requires"]["matter_model"])
        self.assertFalse(result["requires"]["clarification_gate"])
        self.assertFalse(result["requires"]["adversarial"])
        self.assertFalse(result["requires"]["judgment"])

    def test_router_keeps_simple_tasks_simple(self):
        text = router_text()
        self.assertIn("Minimum sufficient workflow", text)
        self.assertIn("简单任务保持简单", text)
        self.assertIn("不得为简单法律咨询建立 Matter Model", text)

    def test_l0_has_no_question_flow(self):
        # 简单知识问题没有任何 unknown 时，澄清层必须返回空提问计划。
        result = evaluate_unknowns({"unknowns": []})
        self.assertEqual(result["questions"], [])
        self.assertEqual(result["blocking_unknowns"], [])


# ---------------------------------------------------------------- 模糊欠款

class Case02VagueDebt(unittest.TestCase):
    """“帮我起诉他还20万”不得自动认定民间借贷。"""

    def _matter(self):
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

    def test_payment_nature_is_blocking_unknown(self):
        matter = self._matter()
        validation = validate_matter_model(matter)
        self.assertTrue(validation["ok"], validation["errors"])
        result = evaluate_unknowns(matter)
        self.assertEqual(len(result["blocking_unknowns"]), 1)
        self.assertEqual(result["blocking_unknowns"][0]["id"], "U3")

    def test_question_budget_caps_at_five(self):
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

    def test_user_assertion_never_upgraded_to_confirmed(self):
        matter = self._matter()
        matter["facts"]["confirmed"].append(
            {"id": "F3", "statement": "被告向原告借款20万元", "source": "用户口述"}
        )
        validation = validate_matter_model(matter)
        self.assertFalse(validation["ok"])
        self.assertTrue(any("升级" in e or "口述" in e for e in validation["errors"]))

    def test_matter_model_uses_confirmed_naming(self):
        text = ref("matter-model-protocol.md")
        self.assertIn("CONFIRMED", text)
        self.assertNotIn("ESTABLISHED", text)


# ---------------------------------------------------------------- 文件已上传

class Case03MaterialAlreadyUploaded(unittest.TestCase):
    """文件已上传时不得重复让用户上传。"""

    def test_from_material_unknown_never_asked(self):
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

    def test_ask_before_ask_rule_present(self):
        text = ref("legal-clarification-protocol.md")
        self.assertIn("Missing Information ≠ Blocking Unknown", text)
        self.assertIn("提问前必须先自行获取", text)
        self.assertIn("能从现有材料确定的信息，不得再问用户", text)
        self.assertIn("Decision-changing", text)
        self.assertIn("Scope-changing", text)


# ---------------------------------------------------------------- 定性冲突

class Case04CompetingInterpretation(unittest.TestCase):
    """用户说“借款”但材料出现“利润五五分”→ 保留投资/合作竞争性解释。"""

    def test_competing_relationship_classifies_l2(self):
        result = classify_mode(
            {
                "task_type": "case_task",
                "competing_legal_relationships": True,
                "disputed_key_facts": True,
            }
        )
        self.assertEqual(result["mode"], "L2")
        self.assertTrue(result["requires"]["adversarial"])

    def test_two_hypotheses_kept_and_premature_collapse_warns(self):
        matter = {
            "legal_relationships": {
                "candidates": ["H1 民间借贷", "H2 投资/合作"],
                "current_view": "H1 民间借贷",
                "confidence": "medium",
            }
        }
        validation = validate_matter_model(matter)
        self.assertTrue(any("过早收敛" in w for w in validation["warnings"]))

    def test_adversarial_review_has_five_fixed_checks(self):
        text = ref("adversarial-review-protocol.md")
        for probe in ["用户对法律关系的命名可能错吗", "竞争性事实解释", "对方最强的抗辩", "推翻结论", "时效、管辖、主体、程序或举证责任障碍"]:
            self.assertIn(probe, text)
        self.assertIn("falsification", text)
        self.assertIn("Minimum Failure Set", text)
        self.assertIn("未发现足以实质动摇当前判断的反向路径", text)


# ---------------------------------------------------------------- 局部修订

class Case05SurgicalChanges(unittest.TestCase):
    """合同局部修订：surgical change，不整份重写。"""

    def test_surgical_changes_rule_present(self):
        text = read(ROUTER / "references" / "practice-profile.md")
        self.assertIn("Surgical Changes", text)
        self.assertIn("不顺手改进相邻内容", text)

    def test_router_forbids_scope_creep(self):
        text = router_text()
        self.assertIn("用户只要求局部修改时", text)
        self.assertIn("不得未经授权扩大改动范围", text)


# ---------------------------------------------------------------- 合同审查 hard gate

class Case06ContractReviewGate(unittest.TestCase):
    """合同审查立场 hard gate 不得失效。"""

    def test_review_position_gate_present(self):
        text = ref("contract-workflow-protocol.md")
        self.assertIn("审查立场", text)

    def test_router_keeps_contract_workflow_reference(self):
        self.assertIn("contract-workflow-protocol.md", router_text())


# ---------------------------------------------------------------- Formal Word

class Case07FormalWord(unittest.TestCase):
    """既有 DOCX 管线不失效。"""

    def test_docx_pipeline_files_present(self):
        export = REPO / "skills" / "legal" / "法律文书模板与导出" / "scripts"
        for f in ["html_to_docx.py", "fill_docx_template.py", "health_check.py", "select_legal_template.py"]:
            self.assertTrue((export / f).exists(), f)

    def test_preflight_script_present(self):
        self.assertTrue(
            (REPO / "skills" / "legal" / "法律文书出稿前审查" / "scripts" / "preflight_check.py").exists()
        )

    def test_router_keeps_word_hard_gate(self):
        text = router_text()
        self.assertIn("html_to_docx.py", text)
        self.assertIn("health_check.py", text)
        self.assertIn("出稿前审查报告.md", text)

    def test_redline_pipeline_present(self):
        redline = REPO / "skills" / "legal" / "合同审查" / "scripts" / "redline"
        for f in ["apply_redline_plan.py", "qa_redline.py"]:
            self.assertTrue((redline / f).exists(), f)


# ---------------------------------------------------------------- External Action

class Case08ExternalActionGate(unittest.TestCase):
    """无明确授权不发送/提交。"""

    def test_action_approval_protocol_present(self):
        text = ref("action-approval-protocol.md")
        self.assertIn("分析 ≠ 授权执行", text)
        for probe in ["对外发送", "向法院、仲裁机构、行政机关提交", "接受和解", "放弃权利", "产生费用"]:
            self.assertIn(probe, text)

    def test_router_references_action_gate(self):
        self.assertIn("action-approval-protocol.md", router_text())


# ---------------------------------------------------------------- Conflict

class Case09MatterConflict(unittest.TestCase):
    """无真实 conflict DB 时不假装已通过。"""

    def test_intake_protocol_never_fakes_conflict_check(self):
        text = ref("intake-conflict-protocol.md")
        self.assertIn("组织级利益冲突检索：未执行 / 需人工确认", text)
        self.assertIn("不得假装完成了机构级利益冲突检索", text)

    def test_intake_minimum_checklist(self):
        text = ref("intake-conflict-protocol.md")
        for probe in ["委托方是谁", "对方是谁", "授权范围", "是否存在已知利益冲突"]:
            self.assertIn(probe, text)


# ---------------------------------------------------------------- Reflection

class Case10Reflection(unittest.TestCase):
    """正常成功不写 lessons；可泛化错误去敏化后写；绝不自动改 Skill。"""

    def test_reflection_protocol_forbids_auto_skill_edit(self):
        text = ref("post-task-reflection-protocol.md")
        self.assertIn("绝不授权 Agent 自动修改 Skill", text)
        for probe in ["改写 SKILL.md", "改写 protocol", "安装新 Skill", "修改权重", "修改系统规则"]:
            self.assertIn(probe, text)

    def test_reflection_only_records_reusable_failures(self):
        text = ref("post-task-reflection-protocol.md")
        self.assertIn("任务正常成功时，不写 lessons", text)
        self.assertIn("不记录", text)

    def test_router_forbids_auto_skill_edit(self):
        text = router_text()
        self.assertIn("不得自动修改任何 SKILL.md、protocol 文件或系统规则", text)
        self.assertIn("knowledge/lessons.md", text)

    def test_lessons_file_exists_with_privacy_header(self):
        lessons = read(REPO / "knowledge" / "lessons.md")
        self.assertIn("去敏化", lessons)
        self.assertIn("绝不自动修改任何 SKILL.md", lessons)


# ---------------------------------------------------------------- Privacy

class Case11Privacy(unittest.TestCase):
    """lessons.md 不出现客户名/案号/联系方式/个案敏感事实。"""

    def test_lessons_has_no_case_specific_data(self):
        lessons = read(REPO / "knowledge" / "lessons.md")
        for pat in [
            r"\d{4}[-年]\d{1,2}[-月]\d{1,2}日?",  # 具体日期
            r"\(\d{4}\)[A-Za-z0-9]+\d+号",          # 案号样式
            r"1[3-9]\d{9}",                          # 手机号
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        ]:
            self.assertIsNone(re.search(pat, lessons), pat)

    def test_repo_has_no_personal_qr(self):
        self.assertFalse((REPO / "assets" / "wechat-qr.png").exists())
        for p in REPO.rglob("*.png"):
            self.assertNotIn("qr", p.name.lower())


# ---------------------------------------------------------------- 结构 / License / 清理

class Case12RepoStructure(unittest.TestCase):
    def test_license_trifecta_exists(self):
        self.assertTrue((REPO / "LICENSE").exists())
        self.assertTrue((REPO / "LICENSES" / "upstream-MIT.txt").exists())
        self.assertTrue((REPO / "THIRD_PARTY_NOTICES.md").exists())

    def test_license_scope_statement(self):
        lic = read(REPO / "LICENSE")
        self.assertIn("PolyForm Noncommercial License 1.0.0", lic)
        self.assertIn("THIRD_PARTY_NOTICES.md", lic)
        self.assertIn("不意味着本仓库全部历史内容均由当前项目维护者拥有完整版权", lic)

    def test_third_party_notices_preserve_mit(self):
        notice = read(REPO / "THIRD_PARTY_NOTICES.md")
        self.assertIn("MIT License", notice)
        self.assertIn("不得被解释为撤销", notice)
        self.assertIn("upstream-MIT.txt", notice)

    def test_required_notice_preserved(self):
        notice = read(REPO / "THIRD_PARTY_NOTICES.md")
        self.assertIn("Required Notice: Copyright (c) 2026 Samwang-afk and applicable Ludus Agent contributors.", notice)

    def test_no_personal_branding_outside_notices(self):
        forbidden = {
            "panrui": re.compile(r"panrui", re.I),
            "samwang": re.compile(r"samwang", re.I),
            "xiayuzizhuo": re.compile(r"xiayuzizhuo", re.I),
            "ludus_closed_framework": re.compile(r"Ludus Agent 为独立开发的闭源框架"),
        }
        allowed_files = {
            "THIRD_PARTY_NOTICES.md",
            "LICENSES/upstream-MIT.txt",
            "skills/legal/法律工作总控/SKILL.md",  # 总控声明保留作者与许可归属
        }
        for p in REPO.rglob("*"):
            if not p.is_file() or p.name in {".gitignore"}:
                continue
            rel = p.relative_to(REPO).as_posix()
            if rel in allowed_files or rel.startswith(".git/") or rel.startswith("tests/"):
                continue
            try:
                text = read(p)
            except (UnicodeDecodeError, OSError):
                continue
            for key, pat in forbidden.items():
                self.assertIsNone(pat.search(text), f"{key} found in {rel}")

    def test_no_quai_in_paths(self):
        self.assertFalse([p for p in REPO.rglob("*") if "quai" in p.name])
        self.assertTrue((REPO / "skills" / "legal" / "法律文章去AI味道" / "SKILL.md").exists())

    def test_all_new_protocols_exist(self):
        for f in [
            "legal-clarification-protocol.md",
            "adversarial-review-protocol.md",
            "intake-conflict-protocol.md",
            "matter-lifecycle-protocol.md",
            "action-approval-protocol.md",
            "post-task-reflection-protocol.md",
            "sop-contract.md",
        ]:
            self.assertTrue((REFS / f).exists(), f)

    def test_lifecycle_protocol_states(self):
        text = ref("matter-lifecycle-protocol.md")
        for s in ["INTAKE", "ACTIVE", "WAITING", "REVIEW", "DELIVERED", "CLOSED"]:
            self.assertIn(s, text)
        for field in ["status", "next_action", "pending_from", "deadline", "owner"]:
            self.assertIn(field, text)

    def test_sop_contract_seven_items(self):
        text = ref("sop-contract.md")
        for s in ["WHEN", "INPUT", "DO", "DECIDE", "APPROVE", "OUTPUT", "CLOSE"]:
            self.assertIn(s, text)

    def test_pack_convention_documented(self):
        text = ref("sop-contract.md")
        self.assertIn("Domain Pack 挂载约定", text)
        self.assertIn("packs/", text)
        self.assertIn("routing-map.md", text)
        self.assertIn("不是新框架", text)

    def test_example_pack_manifest_valid(self):
        pack = REPO / "packs" / "ip-law" / "pack.json"
        self.assertTrue(pack.exists())
        data = json.loads(read(pack))
        for key in ["id", "name", "version", "description", "skills_dir", "routes"]:
            self.assertIn(key, data)
        self.assertEqual(data["id"], "ip-law")
        self.assertTrue((REPO / "packs" / "ip-law" / "README.md").exists())

    def test_no_established_naming_remains(self):
        for p in [RC_SCRIPT, REFS / "matter-model-protocol.md", REFS / "judgment-protocol.md"]:
            text = read(p)
            self.assertNotIn("ESTABLISHED", text, p.name)
        self.assertNotIn("ESTABLISHED", router_text())
        self.assertNotIn("ESTABLISHED", read(REPO / "AGENTS.md"))

    def test_skill_count_preserved(self):
        skills_dir = REPO / "skills" / "legal"
        dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
        self.assertGreaterEqual(len(dirs), 58)

    def test_router_declaration_is_clean(self):
        text = router_text()
        self.assertIn("本 Skill 提供法律工作辅助，不构成正式法律意见", text)
        self.assertIn("Ludus Agent 的问题澄清与反向复核机制", text)
        self.assertIn("PolyForm Noncommercial License 1.0.0", text)
        self.assertIn("THIRD_PARTY_NOTICES.md", text)
        self.assertNotIn("Ludus Agent 为独立开发的闭源框架", text)

    def test_subskill_skills_have_no_branding_declaration(self):
        for sk in (REPO / "skills" / "legal").glob("*/SKILL.md"):
            if sk.name == "SKILL.md" and "法律工作总控" in str(sk):
                continue  # 总控声明保留作者与许可归属，单独由 test_router_declaration_is_clean 检查
            text = read(sk)
            self.assertNotIn("Samwang-afk", text, sk.name)
            self.assertNotIn("xiayuzizhuo", text, sk.name)
            self.assertNotIn("pa1nrui1", text, sk.name)


# ---------------------------------------------------------------- 判定器回归

class Case13JudgmentRegression(unittest.TestCase):
    """Judgment / 起草许可与交付链回归。"""

    def _deliberation(self, **overrides):
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

    def test_critical_unresolved_blocks(self):
        result = judge(self._deliberation())
        self.assertEqual(result["judgment"]["drafting_permission"], "BLOCKED")

    def test_pass_never_bypasses_delivery_chain(self):
        result = judge(
            {
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
        )
        self.assertTrue(result["judgment"]["do_not_bypass_delivery_gates"])
        self.assertIn("health_check", result["judgment"]["delivery_chain_required"])

    def test_reasoning_control_cli_smoke(self):
        proc = subprocess.run(
            [sys.executable, str(RC_SCRIPT), "classify", "-"],
            input=json.dumps({"task_type": "knowledge_question"}, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["mode"], "L0")


if __name__ == "__main__":
    unittest.main()
