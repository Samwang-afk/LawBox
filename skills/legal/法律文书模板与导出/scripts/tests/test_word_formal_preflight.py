#!/usr/bin/env python3
"""Regression tests for formal Word preflight gates."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


from helpers import PREFLIGHT, make_workspace


class ClonePreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_tmp = tempfile.TemporaryDirectory()
        matter, system_record, _, env = make_workspace(Path(self.workspace_tmp.name))
        self.matter_path = str(matter)
        self.system_record_path = str(system_record)
        self.env = env

    def tearDown(self) -> None:
        self.workspace_tmp.cleanup()

    def write_clone_case(
        self,
        root: Path,
        *,
        omit_table_index: bool = False,
        matter_path: str | None = None,
        system_record_path: str | None = None,
        reading_review_text: str | None = None,
        source_boundary_text: str | None = None,
        legal_verification_text: str | None = None,
        known_gaps: list | None = None,
        omit_legal_verification_path: bool = False,
    ) -> dict[str, Path]:
        for name, text in {
            "reading_review.md": reading_review_text
            or "# 读取复查摘要\n文件名：合成测试\n存疑项：无\n",
            "source_boundary.md": source_boundary_text
            or "# 来源边界记录\n已核验：合成测试\n未核验：无\n缺口：无\n输出边界：仅用于测试\n",
            "legal_verification.md": legal_verification_text
            or "# 法规校验摘要\n已核验：不引用实体法条\n现行有效：不适用\n",
            "user_confirmation.md": "# 用户确认记录\n已确认：合成测试字段\n",
        }.items():
            (root / name).write_text(text, encoding="utf-8")

        complaint_data = {
            "template_id": "civil_complaint_private_lending_v1",
            "fields": {"plaintiff.natural.name": "张三"},
            "source_map": {"plaintiff.natural.name": "fixture"},
            "known_gaps": known_gaps or [],
        }
        target = {
            "table_index": 1,
            "row_index": 3,
            "cell_index": 2,
            "anchor_text": "姓名：",
        }
        if omit_table_index:
            target.pop("table_index")
        fill_plan = {
            "template_id": "civil_complaint_private_lending_v1",
            "fields": [
                {
                    "field_id": "plaintiff.natural.name",
                    "value": "张三",
                    "target": target,
                    "mode": "append_after_anchor",
                }
            ],
        }
        qc_meta = {
            "template_id": "civil_complaint_private_lending_v1",
            "source_skill": "诉讼文书起草",
            "doc_type": "民事起诉状",
            "case_cause": "民间借贷纠纷",
            "matter_path": matter_path or self.matter_path,
            "system_record_path": system_record_path or self.system_record_path,
            "legal_verification_required": True,
            "evidence": {
                "reading_review_path": str(root / "reading_review.md"),
                "source_boundary_path": str(root / "source_boundary.md"),
                "user_confirmation_source": str(root / "user_confirmation.md"),
            },
        }
        if not omit_legal_verification_path:
            qc_meta["evidence"]["legal_verification_path"] = str(root / "legal_verification.md")
        paths = {
            "complaint_data": root / "complaint-data.json",
            "fill_plan": root / "fill-plan.json",
            "qc_meta": root / "qc-meta.json",
            "report": root / "report.md",
        }
        paths["complaint_data"].write_text(json.dumps(complaint_data, ensure_ascii=False), encoding="utf-8")
        paths["fill_plan"].write_text(json.dumps(fill_plan, ensure_ascii=False), encoding="utf-8")
        paths["qc_meta"].write_text(json.dumps(qc_meta, ensure_ascii=False), encoding="utf-8")
        return paths

    def run_preflight(self, paths: dict[str, Path]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(PREFLIGHT),
                "--complaint-data",
                str(paths["complaint_data"]),
                "--fill-plan",
                str(paths["fill_plan"]),
                "--qc-meta",
                str(paths["qc_meta"]),
                "--report",
                str(paths["report"]),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            env=self.env,
        )

    def test_clone_preflight_accepts_complete_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_clone_case(Path(tmp))
            proc = self.run_preflight(paths)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("review_status: PASS", proc.stdout)

    def test_clone_preflight_blocks_missing_table_coordinate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_clone_case(Path(tmp), omit_table_index=True)
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_BUSINESS_REVISION", report)
            self.assertIn("缺少表格坐标：table_index", report)

    def test_clone_preflight_blocks_ocr_uncertain_reading_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_clone_case(
                Path(tmp),
                reading_review_text="# 读取复查摘要\n文件名：截图.png\n存疑项：[OCR待确认] OCR未识别到可用文字\n",
            )
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_MATERIAL", report)
            self.assertIn("OCR 存疑", report)

    def test_clone_preflight_blocks_incomplete_source_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_clone_case(
                Path(tmp),
                source_boundary_text="# 来源边界记录\n已核验：合成测试\n",
            )
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_BUSINESS_REVISION", report)
            self.assertIn("来源边界记录缺少必要栏目", report)

    def test_clone_preflight_blocks_missing_legal_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_clone_case(Path(tmp), omit_legal_verification_path=True)
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_MATERIAL", report)
            self.assertIn("缺少法规校验摘要路径", report)

    def test_clone_preflight_blocks_unverified_legal_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_clone_case(
                Path(tmp),
                legal_verification_text="# 法规校验摘要\n未完成核验：中华人民共和国民法典第六百七十五条\n",
            )
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_MATERIAL", report)
            self.assertIn("未完成核验", report)

    def test_clone_preflight_blocks_known_gaps_without_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_clone_case(
                Path(tmp),
                known_gaps=[{"field_id": "defendant.natural.phone", "reason": "材料缺失"}],
            )
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_USER_CONFIRMATION", report)
            self.assertIn("complaint-data.json 存在字段缺口", report)

    def test_clone_preflight_blocks_mismatched_matter_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            other_matter = Path(self.env["LEGAL_WORKSPACE"]) / "other_matter"
            other_matter.mkdir(parents=True)
            paths = self.write_clone_case(Path(tmp), matter_path=str(other_matter))
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_BUSINESS_REVISION", report)
            self.assertIn("当前事项.md 未匹配 matter_path", report)

    def test_clone_preflight_blocks_mismatched_system_record_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            other_system = Path(self.env["LEGAL_WORKSPACE"]) / "_系统记录" / "other_system"
            other_system.mkdir(parents=True)
            paths = self.write_clone_case(Path(tmp), system_record_path=str(other_system))
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_BUSINESS_REVISION", report)
            self.assertIn("当前事项.md 未匹配 system_record_path", report)


class HtmlPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_tmp = tempfile.TemporaryDirectory()
        matter, system_record, _, env = make_workspace(Path(self.workspace_tmp.name))
        self.matter_path = str(matter)
        self.system_record_path = str(system_record)
        self.env = env

    def tearDown(self) -> None:
        self.workspace_tmp.cleanup()

    def write_html_case(
        self,
        root: Path,
        *,
        matter_path: str | None = None,
        system_record_path: str | None = None,
        body: str | None = None,
        reading_review_text: str | None = None,
        source_boundary_text: str | None = None,
        legal_verification_text: str | None = None,
        required_confirmations: list[str] | None = None,
        user_confirmation_text: str | None = None,
        known_gaps: list | None = None,
        omit_reading_review_path: bool = False,
        omit_source_boundary_path: bool = False,
        omit_legal_verification_path: bool = False,
        omit_user_confirmation_path: bool = False,
    ) -> dict[str, Path]:
        for name, text in {
            "reading_review.md": reading_review_text or "# 读取复查摘要\n文件名：合成测试\n存疑项：无\n",
            "source_boundary.md": source_boundary_text
            or "# 来源边界记录\n已核验：合成测试\n未核验：无\n缺口：无\n输出边界：仅用于测试\n",
            "legal_verification.md": legal_verification_text or "# 法规校验摘要\n已核验：合成引用\n现行有效：是\n",
            "user_confirmation.md": user_confirmation_text or "# 用户确认记录\n已确认：合成测试事项\n",
        }.items():
            (root / name).write_text(text, encoding="utf-8")

        html = """<!doctype html>
<html>
<body>
<h1>合成测试法律文书</h1>
<p>{body}</p>
<p class="signature">示例律所 律师：【律师姓名】</p>
</body>
</html>
""".format(body=body or "本文书仅用于正式 Word 出稿前当前事项一致性门禁的自动化测试，事实均为合成数据。")
        evidence = {}
        if not omit_reading_review_path:
            evidence["reading_review_path"] = str(root / "reading_review.md")
        if not omit_source_boundary_path:
            evidence["source_boundary_path"] = str(root / "source_boundary.md")
        if not omit_legal_verification_path and legal_verification_text is not None:
            evidence["legal_verification_path"] = str(root / "legal_verification.md")
        if not omit_user_confirmation_path and required_confirmations:
            evidence["user_confirmation_source"] = str(root / "user_confirmation.md")
        meta = {
            "source_skill": "诉讼文书起草",
            "doc_type": "合成测试文书",
            "output_purpose": "正式交付",
            "profile": "litigation_standard",
            "matter_path": matter_path or self.matter_path,
            "system_record_path": system_record_path or self.system_record_path,
            "evidence": evidence,
            "required_confirmations": required_confirmations or [],
            "known_gaps": known_gaps or [],
        }
        paths = {
            "html": root / "draft.html",
            "meta": root / "preflight-meta.json",
            "output_html": root / "draft_checked.html",
            "report": root / "report.md",
        }
        paths["html"].write_text(html, encoding="utf-8")
        paths["meta"].write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        return paths

    def run_preflight(self, paths: dict[str, Path]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(PREFLIGHT),
                "--html",
                str(paths["html"]),
                "--meta",
                str(paths["meta"]),
                "--output-html",
                str(paths["output_html"]),
                "--report",
                str(paths["report"]),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            env=self.env,
        )

    def test_html_preflight_accepts_current_matter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_html_case(Path(tmp))
            proc = self.run_preflight(paths)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertRegex(proc.stdout, r"review_status: (PASS|FIXED_PASS)")

    def test_html_preflight_blocks_mismatched_matter_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            other_matter = Path(self.env["LEGAL_WORKSPACE"]) / "other_matter"
            other_matter.mkdir(parents=True)
            paths = self.write_html_case(Path(tmp), matter_path=str(other_matter))
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_BUSINESS_REVISION", report)
            self.assertIn("当前事项.md 未匹配 matter_path", report)

    def test_html_preflight_blocks_mismatched_system_record_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            other_system = Path(self.env["LEGAL_WORKSPACE"]) / "_系统记录" / "other_system"
            other_system.mkdir(parents=True)
            paths = self.write_html_case(Path(tmp), system_record_path=str(other_system))
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_BUSINESS_REVISION", report)
            self.assertIn("当前事项.md 未匹配 system_record_path", report)

    def test_html_preflight_blocks_cache_matter_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_matter = Path(self.env["LEGAL_WORKSPACE"]) / ".cache" / "matter"
            cache_matter.mkdir(parents=True)
            paths = self.write_html_case(Path(tmp), matter_path=str(cache_matter))
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_BUSINESS_REVISION", report)
            self.assertIn("matter_path 必须位于正式业务文件区", report)

    def test_html_preflight_blocks_cache_system_record_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_system = Path(self.env["LEGAL_WORKSPACE"]) / ".cache" / "system"
            cache_system.mkdir(parents=True)
            paths = self.write_html_case(Path(tmp), system_record_path=str(cache_system))
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_BUSINESS_REVISION", report)
            self.assertIn("system_record_path 必须位于正式系统记录区", report)

    def test_html_preflight_blocks_missing_reading_review_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_html_case(Path(tmp), omit_reading_review_path=True)
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_MATERIAL", report)
            self.assertIn("缺少读取复查摘要路径", report)

    def test_html_preflight_blocks_missing_source_boundary_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_html_case(Path(tmp), omit_source_boundary_path=True)
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_MATERIAL", report)
            self.assertIn("缺少来源边界记录路径", report)

    def test_html_preflight_blocks_ocr_uncertain_reading_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_html_case(
                Path(tmp),
                reading_review_text="# 读取复查摘要\n文件名：截图.png\n存疑项：[OCR待确认] 金额字段无法可靠识别\n",
            )
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_MATERIAL", report)
            self.assertIn("OCR 存疑", report)

    def test_html_preflight_blocks_incomplete_source_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_html_case(Path(tmp), source_boundary_text="# 来源边界记录\n已核验：合成测试\n")
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_BUSINESS_REVISION", report)
            self.assertIn("来源边界记录缺少必要栏目", report)

    def test_html_preflight_blocks_unverified_legal_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_html_case(
                Path(tmp),
                body="依据《民法典》第六百七十五条进行合成测试。",
                legal_verification_text="# 法规校验摘要\n未完成核验：中华人民共和国民法典第六百七十五条\n",
            )
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_MATERIAL", report)
            self.assertIn("未完成核验", report)

    def test_html_preflight_blocks_missing_required_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_html_case(
                Path(tmp),
                required_confirmations=["确认诉讼请求金额为10000元"],
                user_confirmation_text="# 用户确认记录\n已确认：其他事项\n",
            )
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_USER_CONFIRMATION", report)
            self.assertIn("缺少用户确认：确认诉讼请求金额为10000元", report)

    def test_html_preflight_allows_recorded_required_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_html_case(
                Path(tmp),
                required_confirmations=["确认诉讼请求金额为10000元"],
                user_confirmation_text="# 用户确认记录\n确认诉讼请求金额为10000元\n",
            )
            proc = self.run_preflight(paths)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertRegex(proc.stdout, r"review_status: (PASS|FIXED_PASS)")

    def test_html_preflight_blocks_known_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_html_case(Path(tmp), known_gaps=[{"field": "被告身份证号", "reason": "材料缺失"}])
            proc = self.run_preflight(paths)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = paths["report"].read_text(encoding="utf-8")
            self.assertIn("NEEDS_USER_CONFIRMATION", report)
            self.assertIn("存在 known_gaps", report)


if __name__ == "__main__":
    unittest.main()
