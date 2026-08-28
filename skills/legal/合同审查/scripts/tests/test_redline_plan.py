from __future__ import annotations

import json
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


SKILL_ROOT = Path(__file__).resolve().parents[2]
APPLY = SKILL_ROOT / "scripts" / "redline" / "apply_redline_plan.py"
QA = SKILL_ROOT / "scripts" / "redline" / "qa_redline.py"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


def confirmed_meta(role: str = "甲方") -> dict:
    return {
        "party_role": role,
        "party_role_confirmed": True,
        "party_role_confirmation_source": "用户确认：测试用例",
    }


def write_minimal_docx(path: Path, body_xml: str | None = None) -> None:
    files = {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/settings.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>"
        ),
        "word/_rels/document.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            "</Relationships>"
        ),
        "word/settings.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "</w:settings>"
        ),
        "word/document.xml": body_xml
        or (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body>"
            "<w:p><w:r><w:t>甲方验收合格后支付尾款。</w:t></w:r></w:p>"
            "<w:p><w:r><w:t>合同联系人：____。</w:t></w:r></w:p>"
            "</w:body>"
            "</w:document>"
        ),
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)


class RedlinePlanTests(unittest.TestCase):
    def test_party_role_confirmation_is_required_before_redline(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_docx = root / "input.docx"
            output_docx = root / "output.docx"
            plan_path = root / "redline-plan.json"
            log_path = root / "redline-log.json"
            write_minimal_docx(input_docx)

            plan_path.write_text(
                json.dumps(
                    {
                        "meta": {"party_role": "甲方"},
                        "findings": [
                            {
                                "id": "Q001",
                                "action": "replace",
                                "target_text": "甲方验收合格后支付尾款。",
                                "replacement_text": "甲方应在验收合格后5个工作日内支付尾款。",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(APPLY),
                    "--input",
                    str(input_docx),
                    "--plan",
                    str(plan_path),
                    "--output",
                    str(output_docx),
                    "--log",
                    str(log_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("审查立场未确认", result.stderr)
            self.assertFalse(output_docx.exists())
            self.assertFalse(log_path.exists())

    def test_apply_redline_plan_writes_revisions_comments_and_log(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_docx = root / "input.docx"
            output_docx = root / "output.docx"
            plan_path = root / "redline-plan.json"
            log_path = root / "redline-log.json"
            write_minimal_docx(input_docx)

            plan = {
                "meta": {
                    "contract_id": "测试-合同-01",
                    "client_name": "测试客户",
                    **confirmed_meta("甲方"),
                },
                "findings": [
                    {
                        "id": "Q001",
                        "handling_advice": "必须修改",
                        "clause": "第1条",
                        "issue": "验收标准不明确",
                        "action": "replace",
                        "target_text": "甲方验收合格后支付尾款。",
                        "replacement_text": "甲方应在验收合格后5个工作日内支付尾款。",
                        "comment": "建议补充验收期限和付款触发条件。",
                    },
                    {
                        "id": "Q002",
                        "handling_advice": "需客户确认",
                        "clause": "联系人",
                        "issue": "联系人留空",
                        "action": "auto",
                        "target_text": "合同联系人：____。",
                        "comment": "联系人为空，需客户补充。",
                    },
                    {
                        "id": "Q003",
                        "handling_advice": "可优化",
                        "action": "auto",
                        "target_text": "不存在的文本",
                        "comment": "仅意见书提示。",
                    },
                ],
            }
            plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(APPLY),
                    "--input",
                    str(input_docx),
                    "--plan",
                    str(plan_path),
                    "--output",
                    str(output_docx),
                    "--log",
                    str(log_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_docx.exists())
            self.assertTrue(log_path.exists())

            with zipfile.ZipFile(output_docx) as zf:
                document = ET.fromstring(zf.read("word/document.xml"))
                settings = ET.fromstring(zf.read("word/settings.xml"))
                comments = ET.fromstring(zf.read("word/comments.xml"))
                rels = zf.read("word/_rels/document.xml.rels").decode("utf-8")
                content_types = zf.read("[Content_Types].xml").decode("utf-8")
            self.assertIsNotNone(settings.find("w:trackRevisions", NS))
            self.assertEqual(len(document.findall(".//w:ins", NS)), 1)
            self.assertEqual(len(document.findall(".//w:del", NS)), 1)
            self.assertEqual(len(comments.findall(".//w:comment", NS)), 2)
            self.assertIn("comments.xml", rels)
            self.assertNotIn("ns0:", rels)
            self.assertNotIn("ns0:", content_types)

            log = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(log["applied"], 2)
            self.assertEqual(log["report_only"], 1)
            self.assertEqual(log["failed"], 0)

            qa = subprocess.run(
                [
                    sys.executable,
                    str(QA),
                    "--docx",
                    str(output_docx),
                    "--expect-ins",
                    "1",
                    "--expect-del",
                    "1",
                    "--expect-comments",
                    "2",
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(qa.returncode, 0, qa.stdout + qa.stderr)

    def test_duplicate_target_requires_occurrence(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_docx = root / "input.docx"
            output_docx = root / "output.docx"
            plan_path = root / "redline-plan.json"
            log_path = root / "redline-log.json"
            write_minimal_docx(
                input_docx,
                body_xml=(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    "<w:body>"
                    "<w:p><w:r><w:t>重复文本</w:t></w:r></w:p>"
                    "<w:p><w:r><w:t>重复文本</w:t></w:r></w:p>"
                    "</w:body>"
                    "</w:document>"
                ),
            )

            plan_path.write_text(
                json.dumps(
                    {
                        "meta": confirmed_meta("甲方"),
                        "findings": [
                            {
                                "id": "Q001",
                                "action": "comment",
                                "target_text": "重复文本",
                                "comment": "重复命中时应失败。",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPLY),
                    "--input",
                    str(input_docx),
                    "--plan",
                    str(plan_path),
                    "--output",
                    str(output_docx),
                    "--log",
                    str(log_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            log = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(log["failed"], 1)
            self.assertIn("命中 2 处", log["results"][0]["message"])

    def test_occurrence_and_comment_required_control_revision_comments(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_docx = root / "input.docx"
            output_docx = root / "output.docx"
            plan_path = root / "redline-plan.json"
            log_path = root / "redline-log.json"
            write_minimal_docx(
                input_docx,
                body_xml=(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    "<w:body>"
                    "<w:p><w:r><w:t>付款期限为5日。</w:t></w:r></w:p>"
                    "<w:p><w:r><w:t>付款期限为5日。</w:t></w:r></w:p>"
                    "<w:p><w:r><w:t>乙方承担全部责任。</w:t></w:r></w:p>"
                    "</w:body>"
                    "</w:document>"
                ),
            )

            plan_path.write_text(
                json.dumps(
                    {
                        "meta": confirmed_meta("乙方"),
                        "findings": [
                            {
                                "id": "Q001",
                                "action": "replace",
                                "target_text": "付款期限为5日。",
                                "occurrence": 2,
                                "replacement_text": "付款期限为7日。",
                            },
                            {
                                "id": "Q002",
                                "action": "replace",
                                "selector": {"contains": "乙方承担全部责任。"},
                                "replacement_text": "乙方就其违约行为依法承担相应责任。",
                                "handling_advice": "必须修改",
                                "issue": "责任范围明显失衡",
                                "comment_required": True,
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(APPLY),
                    "--input",
                    str(input_docx),
                    "--plan",
                    str(plan_path),
                    "--output",
                    str(output_docx),
                    "--log",
                    str(log_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            with zipfile.ZipFile(output_docx) as zf:
                document = ET.fromstring(zf.read("word/document.xml"))
                comments = ET.fromstring(zf.read("word/comments.xml"))
            paragraph_texts = ["".join(node.itertext()) for node in document.findall(".//w:p", NS)]
            self.assertIn("付款期限为5日。", paragraph_texts[0])
            self.assertIn("付款期限为5日。付款期限为7日。", paragraph_texts[1])
            self.assertEqual(len(document.findall(".//w:ins", NS)), 2)
            self.assertEqual(len(document.findall(".//w:del", NS)), 2)
            self.assertEqual(len(comments.findall(".//w:comment", NS)), 1)

    def test_full_paragraph_replace_is_blocked_without_explicit_override(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_docx = root / "input.docx"
            output_docx = root / "output.docx"
            plan_path = root / "redline-plan.json"
            log_path = root / "redline-log.json"
            paragraph = "第三条 乙方应勤勉尽职完成委托事项，并保证按时出庭。"
            write_minimal_docx(
                input_docx,
                body_xml=(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    "<w:body>"
                    f"<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>"
                    "</w:body>"
                    "</w:document>"
                ),
            )

            plan_path.write_text(
                json.dumps(
                    {
                        "meta": confirmed_meta("乙方"),
                        "findings": [
                            {
                                "id": "Q001",
                                "action": "replace",
                                "target_text": paragraph,
                                "replacement_text": "第三条 乙方应勤勉尽责完成委托事项。",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(APPLY),
                    "--input",
                    str(input_docx),
                    "--plan",
                    str(plan_path),
                    "--output",
                    str(output_docx),
                    "--log",
                    str(log_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            log = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(log["failed"], 1)
            self.assertIn("疑似整段替换", log["results"][0]["message"])

    def test_manual_replace_is_downgraded_for_optional_and_unconfirmed_items(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_docx = root / "input.docx"
            output_docx = root / "output.docx"
            plan_path = root / "redline-plan.json"
            log_path = root / "redline-log.json"
            write_minimal_docx(
                input_docx,
                body_xml=(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    "<w:body>"
                    "<w:p><w:r><w:t>甲方不存在歧义。</w:t></w:r></w:p>"
                    "<w:p><w:r><w:t>当事人：[ 徐峰 ]与[ ]；</w:t></w:r></w:p>"
                    "</w:body>"
                    "</w:document>"
                ),
            )

            plan_path.write_text(
                json.dumps(
                    {
                        "meta": confirmed_meta("甲方"),
                        "findings": [
                            {
                                "id": "Q001",
                                "handling_advice": "可优化",
                                "action": "replace",
                                "target_text": "甲方不存在歧义。",
                                "replacement_text": "甲方已阅读并理解本合同。",
                            },
                            {
                                "id": "Q002",
                                "handling_advice": "必须修改",
                                "action": "replace",
                                "target_text": "当事人：[ 徐峰 ]与[ ]；",
                                "replacement_text": "当事人：[ 徐峰之父【姓名待补】 ]与[ 对方待补 ]；",
                                "comment": "需补齐当事人信息。",
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(APPLY),
                    "--input",
                    str(input_docx),
                    "--plan",
                    str(plan_path),
                    "--output",
                    str(output_docx),
                    "--log",
                    str(log_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            log = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(log["report_only"], 1)
            self.assertEqual(log["applied"], 1)
            self.assertEqual(log["results"][0]["action"], "report-only")
            self.assertEqual(log["results"][1]["action"], "comment")

            with zipfile.ZipFile(output_docx) as zf:
                document = ET.fromstring(zf.read("word/document.xml"))
                comments = ET.fromstring(zf.read("word/comments.xml"))
            self.assertEqual(len(document.findall(".//w:ins", NS)), 0)
            self.assertEqual(len(document.findall(".//w:del", NS)), 0)
            self.assertEqual(len(comments.findall(".//w:comment", NS)), 1)

    def test_attachment_reference_can_be_a_deterministic_revision(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_docx = root / "input.docx"
            output_docx = root / "output.docx"
            plan_path = root / "redline-plan.json"
            log_path = root / "redline-log.json"
            write_minimal_docx(
                input_docx,
                body_xml=(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    "<w:body>"
                    "<w:p><w:r><w:t>具体服务成果以附件一为准。</w:t></w:r></w:p>"
                    "</w:body>"
                    "</w:document>"
                ),
            )

            plan_path.write_text(
                json.dumps(
                    {
                        "meta": confirmed_meta("甲方"),
                        "findings": [
                            {
                                "id": "Q001",
                                "handling_advice": "必须修改",
                                "action": "replace",
                                "target_text": "具体服务成果以附件一为准",
                                "replacement_text": "具体服务成果以本合同附件一《服务成果清单》为准",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(APPLY),
                    "--input",
                    str(input_docx),
                    "--plan",
                    str(plan_path),
                    "--output",
                    str(output_docx),
                    "--log",
                    str(log_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            log = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(log["applied"], 1)
            self.assertEqual(log["results"][0]["action"], "replace")

            with zipfile.ZipFile(output_docx) as zf:
                document = ET.fromstring(zf.read("word/document.xml"))
            self.assertEqual(len(document.findall(".//w:ins", NS)), 1)
            self.assertEqual(len(document.findall(".//w:del", NS)), 1)


if __name__ == "__main__":
    unittest.main()
