#!/usr/bin/env python3
"""Regression tests for reasoning evidence chain in preflight review (L2/L3 drafting gate)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


from helpers import PREFLIGHT, make_workspace


def write_checked_html(path: Path, with_conditional_markers: bool = False) -> None:
    markers = "<p>【假设】按用户主张暂以借贷构建</p><p>【待确认】款项性质</p>" if with_conditional_markers else ""
    path.write_text(
        f"""<!doctype html>
<html>
<body>
<h1>合成起诉状</h1>
<p>原告主张被告向其借款 20 万元。</p>
{markers}
<p class="signature">【律所名称】</p>
<p class="signature">律师：【律师姓名】</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_reading_review(path: Path) -> None:
    path.write_text("# 读取复查摘要\n\n已完整读取材料，关键数据无存疑项。\n", encoding="utf-8")


def write_source_boundary(path: Path) -> None:
    path.write_text("# 来源边界记录\n\n已核验、未核验、缺口、输出边界。\n", encoding="utf-8")


def write_judgment(path: Path, permission: str) -> None:
    path.write_text(
        f"""# Judgment 记录

issue: 借款返还请求权
status: supported
confidence:
  level: high
drafting_permission: {permission}
""",
        encoding="utf-8",
    )


def base_meta(matter: Path, system_record: Path) -> dict:
    return {
        "source_skill": "诉讼文书起草",
        "doc_type": "民事起诉状",
        "output_purpose": "正式交付",
        "profile": "litigation_standard",
        "matter_path": str(matter),
        "system_record_path": str(system_record),
        "evidence": {
            "reading_review_path": str(system_record / "读取复查摘要.md"),
            "source_boundary_path": str(system_record / "来源边界记录.md"),
        },
    }


class ReasoningEvidencePreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_tmp = tempfile.TemporaryDirectory()
        matter, system_record, _, env = make_workspace(Path(self.workspace_tmp.name))
        self.matter = matter
        self.system_record = system_record
        self.env = env

    def tearDown(self) -> None:
        self.workspace_tmp.cleanup()

    def run_preflight(self, root: Path, meta: dict) -> subprocess.CompletedProcess[str]:
        import json

        meta_path = root / "preflight-meta.json"
        meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(PREFLIGHT), "--html", str(root / "draft.html"), "--meta", str(meta_path),
             "--output-html", str(root / "draft_checked.html"), "--report", str(root / "report.md")],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            env=self.env,
        )

    def report_text(self, root: Path) -> str:
        return (root / "report.md").read_text(encoding="utf-8")

    def test_l2_blocked_permission_hard_blocks(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.matter) as tmp:
            root = Path(tmp)
            write_checked_html(root / "draft.html")
            write_reading_review(self.system_record / "读取复查摘要.md")
            write_source_boundary(self.system_record / "来源边界记录.md")
            write_judgment(self.system_record / "judgment.md", "BLOCKED")
            meta = base_meta(self.matter, self.system_record)
            meta["reasoning"] = {
                "level": "L2",
                "judgment_path": str(self.system_record / "judgment.md"),
                "drafting_permission": "BLOCKED",
            }
            proc = self.run_preflight(root, meta)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("HARD_BLOCK", self.report_text(root))

    def test_l2_pass_with_judgment_passes(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.matter) as tmp:
            root = Path(tmp)
            write_checked_html(root / "draft.html")
            write_reading_review(self.system_record / "读取复查摘要.md")
            write_source_boundary(self.system_record / "来源边界记录.md")
            write_judgment(self.system_record / "judgment.md", "PASS")
            meta = base_meta(self.matter, self.system_record)
            meta["reasoning"] = {
                "level": "L2",
                "judgment_path": str(self.system_record / "judgment.md"),
                "drafting_permission": "PASS",
            }
            proc = self.run_preflight(root, meta)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("PASS", self.report_text(root))

    def test_l2_missing_judgment_path_needs_material(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.matter) as tmp:
            root = Path(tmp)
            write_checked_html(root / "draft.html")
            write_reading_review(self.system_record / "读取复查摘要.md")
            write_source_boundary(self.system_record / "来源边界记录.md")
            meta = base_meta(self.matter, self.system_record)
            meta["reasoning"] = {"level": "L2", "drafting_permission": "PASS"}
            proc = self.run_preflight(root, meta)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("NEEDS_MATERIAL", self.report_text(root))

    def test_l2_missing_judgment_file_needs_material(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.matter) as tmp:
            root = Path(tmp)
            write_checked_html(root / "draft.html")
            write_reading_review(self.system_record / "读取复查摘要.md")
            write_source_boundary(self.system_record / "来源边界记录.md")
            meta = base_meta(self.matter, self.system_record)
            meta["reasoning"] = {
                "level": "L2",
                "judgment_path": str(self.system_record / "judgment.md"),
                "drafting_permission": "PASS",
            }
            proc = self.run_preflight(root, meta)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("NEEDS_MATERIAL", self.report_text(root))

    def test_conditional_without_markers_needs_revision(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.matter) as tmp:
            root = Path(tmp)
            write_checked_html(root / "draft.html", with_conditional_markers=False)
            write_reading_review(self.system_record / "读取复查摘要.md")
            write_source_boundary(self.system_record / "来源边界记录.md")
            write_judgment(self.system_record / "judgment.md", "CONDITIONAL")
            meta = base_meta(self.matter, self.system_record)
            meta["reasoning"] = {
                "level": "L3",
                "judgment_path": str(self.system_record / "judgment.md"),
                "drafting_permission": "CONDITIONAL",
            }
            proc = self.run_preflight(root, meta)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            report = self.report_text(root)
            self.assertIn("NEEDS_BUSINESS_REVISION", report)
            self.assertIn("CONDITIONAL", report)

    def test_conditional_with_markers_passes(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.matter) as tmp:
            root = Path(tmp)
            write_checked_html(root / "draft.html", with_conditional_markers=True)
            write_reading_review(self.system_record / "读取复查摘要.md")
            write_source_boundary(self.system_record / "来源边界记录.md")
            write_judgment(self.system_record / "judgment.md", "CONDITIONAL")
            meta = base_meta(self.matter, self.system_record)
            meta["reasoning"] = {
                "level": "L3",
                "judgment_path": str(self.system_record / "judgment.md"),
                "drafting_permission": "CONDITIONAL",
            }
            proc = self.run_preflight(root, meta)
            self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_l1_without_reasoning_unaffected(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.matter) as tmp:
            root = Path(tmp)
            write_checked_html(root / "draft.html")
            write_reading_review(self.system_record / "读取复查摘要.md")
            write_source_boundary(self.system_record / "来源边界记录.md")
            meta = base_meta(self.matter, self.system_record)
            proc = self.run_preflight(root, meta)
            self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_reasoning_level_l1_ignored(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.matter) as tmp:
            root = Path(tmp)
            write_checked_html(root / "draft.html")
            write_reading_review(self.system_record / "读取复查摘要.md")
            write_source_boundary(self.system_record / "来源边界记录.md")
            meta = base_meta(self.matter, self.system_record)
            meta["reasoning"] = {"level": "L1", "drafting_permission": "PASS"}
            proc = self.run_preflight(root, meta)
            self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_clone_qc_meta_blocked_hard_blocks(self) -> None:
        import json

        with tempfile.TemporaryDirectory(dir=self.matter) as tmp:
            root = Path(tmp)
            (root / "complaint-data.json").write_text(json.dumps({}, ensure_ascii=False), encoding="utf-8")
            (root / "fill-plan.json").write_text(json.dumps({}, ensure_ascii=False), encoding="utf-8")
            write_judgment(self.system_record / "judgment.md", "BLOCKED")
            qc_meta = base_meta(self.matter, self.system_record)
            qc_meta["reasoning"] = {
                "level": "L2",
                "judgment_path": str(self.system_record / "judgment.md"),
                "drafting_permission": "BLOCKED",
            }
            (root / "qc-meta.json").write_text(json.dumps(qc_meta, ensure_ascii=False), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(PREFLIGHT),
                 "--complaint-data", str(root / "complaint-data.json"),
                 "--fill-plan", str(root / "fill-plan.json"),
                 "--qc-meta", str(root / "qc-meta.json"),
                 "--report", str(root / "report.md")],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                env=self.env,
            )
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("HARD_BLOCK", (root / "report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
