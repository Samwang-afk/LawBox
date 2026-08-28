#!/usr/bin/env python3
"""Apply a contract redline plan to a DOCX file.

This script is intentionally scoped to contract review redlines:
- copy the original DOCX to a new output path
- add real Word tracked changes and comments
- write an execution log for every finding

It does not create the formal legal opinion. Formal .docx opinions still go
through 法律文书出稿前审查 and 法律文书模板与导出.
"""

from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

W_NS = NS["w"]
R_NS = NS["r"]
CT_NS = NS["ct"]
REL_NS = NS["rel"]

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)


def write_xml_tree(path: Path, tree: ET.ElementTree, *, default_namespace: str | None = None) -> None:
    if default_namespace:
        ET.register_namespace("", default_namespace)
    else:
        ET.register_namespace("w", W_NS)
        ET.register_namespace("r", R_NS)
    tree.write(path, encoding="utf-8", xml_declaration=True)


SUPPORTED_ACTIONS = {
    "auto",
    "comment",
    "replace",
    "insert",
    "delete",
    "report-only",
    "report_only",
    "skip",
    "none",
}

REVISION_ACTIONS = {"replace", "insert", "delete"}

PLACEHOLDER_HINTS = (
    "待填写",
    "待补",
    "待补充",
    "留空",
    "空白",
    "未填写",
    "负责人",
    "联系方式",
    "邮箱",
    "附件缺失",
    "缺少附件",
    "未提供附件",
    "____",
    "【",
)

UNCONFIRMED_ROLE_VALUES = {
    "",
    "待确认",
    "待用户确认",
    "未确认",
    "未提及",
    "未提及/待补充",
    "待补充",
    "unknown",
    "none",
    "null",
}


def qn(tag: str) -> str:
    prefix, local = tag.split(":", 1)
    if prefix == "w":
        return f"{{{W_NS}}}{local}"
    if prefix == "r":
        return f"{{{R_NS}}}{local}"
    raise ValueError(f"Unsupported namespace prefix: {prefix}")


def load_plan(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("redline plan 顶层必须是对象")
    findings = payload.get("findings")
    if findings is None:
        payload["findings"] = []
    elif not isinstance(findings, list):
        raise ValueError("redline plan findings 必须是数组")
    return payload


def validate_party_role_gate(plan: dict[str, Any]) -> None:
    meta = plan.get("meta")
    if not isinstance(meta, dict):
        raise ValueError("审查立场未确认：redline plan 缺少 meta，必须先询问用户按哪一方立场审查")
    party_role = str(meta.get("party_role") or "").strip()
    source = str(meta.get("party_role_confirmation_source") or "").strip()
    if not boolean_field(meta, "party_role_confirmed"):
        raise ValueError("审查立场未确认：必须先询问用户按哪一方立场审查，并设置 meta.party_role_confirmed=true")
    if party_role.lower() in UNCONFIRMED_ROLE_VALUES:
        raise ValueError("审查立场未确认：meta.party_role 不能为空或待确认")
    if not source:
        raise ValueError("审查立场未确认：缺少 meta.party_role_confirmation_source")


def normalize_action(value: Any) -> str:
    raw = str(value or "auto").strip().lower()
    aliases = {
        "report_only": "report-only",
        "仅意见书": "report-only",
        "仅写入意见书": "report-only",
        "批注": "comment",
        "修订": "replace",
        "替换": "replace",
        "新增": "insert",
        "插入": "insert",
        "删除": "delete",
        "跳过": "skip",
    }
    return aliases.get(raw, raw)


def has_placeholder_hint(finding: dict[str, Any]) -> bool:
    haystack = " ".join(
        str(finding.get(key) or "")
        for key in (
            "issue",
            "risk",
            "legal_risk",
            "business_risk",
            "comment",
            "suggestion",
            "target_text",
            "original_text",
            "replacement_text",
            "insert_text",
        )
    )
    return any(hint in haystack for hint in PLACEHOLDER_HINTS)


def boolean_field(finding: dict[str, Any], *names: str) -> bool:
    for name in names:
        value = finding.get(name)
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lower() in {"true", "yes", "1", "是"}:
            return True
    return False


def resolve_action(finding: dict[str, Any]) -> str:
    requested = normalize_action(finding.get("action"))
    if requested not in SUPPORTED_ACTIONS:
        raise ValueError(f"不支持的 action: {finding.get('action')}")
    handling = str(finding.get("handling_advice") or "").strip()
    needs_confirmation = has_placeholder_hint(finding) or handling == "需客户确认"
    if requested != "auto":
        if requested == "report_only":
            return "report-only"
        if requested in REVISION_ACTIONS:
            if needs_confirmation and not boolean_field(finding, "allow_unconfirmed_revision"):
                return "comment"
            if handling == "可优化" and not boolean_field(finding, "allow_direct_revision"):
                return "report-only"
        return requested

    if needs_confirmation:
        return "comment"
    if handling == "可优化":
        return "report-only"
    if finding.get("replacement_text") is not None:
        return "replace"
    if finding.get("insert_text") is not None:
        return "insert"
    if finding.get("delete") is True:
        return "delete"
    return "comment"


def selector_value(finding: dict[str, Any], key: str) -> Any:
    selector = finding.get("selector")
    if isinstance(selector, dict):
        return selector.get(key)
    return None


def target_text_for(finding: dict[str, Any]) -> str:
    value = finding.get("target_text")
    if value is not None:
        return str(value)
    value = selector_value(finding, "contains")
    if value is not None:
        return str(value)
    value = finding.get("original_text")
    return str(value) if value is not None else ""


def looks_like_full_paragraph_change(target: str, paragraph_text: str) -> bool:
    target_clean = target.strip()
    paragraph_clean = paragraph_text.strip()
    if not target_clean or not paragraph_clean or len(target_clean) < 20:
        return False
    if target_clean == paragraph_clean:
        return True
    return len(target_clean) / len(paragraph_clean) >= 0.85


def get_text(element: ET.Element) -> str:
    parts: list[str] = []
    for node in element.iter():
        if node.tag in {qn("w:t"), qn("w:delText")} and node.text:
            parts.append(node.text)
    return "".join(parts)


def set_text_element(run: ET.Element, text: str, *, deleted: bool = False) -> None:
    text_tag = qn("w:delText") if deleted else qn("w:t")
    text_el = ET.SubElement(run, text_tag)
    text_el.text = text
    if text[:1].isspace() or text[-1:].isspace():
        text_el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def make_run(text: str, *, deleted: bool = False) -> ET.Element:
    run = ET.Element(qn("w:r"))
    set_text_element(run, text, deleted=deleted)
    return run


def make_ins(text: str, *, change_id: int, author: str, date: str) -> ET.Element:
    ins = ET.Element(qn("w:ins"))
    ins.set(qn("w:id"), str(change_id))
    ins.set(qn("w:author"), author)
    ins.set(qn("w:date"), date)
    ins.append(make_run(text))
    return ins


def make_del(text: str, *, change_id: int, author: str, date: str) -> ET.Element:
    deletion = ET.Element(qn("w:del"))
    deletion.set(qn("w:id"), str(change_id))
    deletion.set(qn("w:author"), author)
    deletion.set(qn("w:date"), date)
    deletion.append(make_run(text, deleted=True))
    return deletion


def local_date() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass
class Match:
    paragraph: ET.Element
    text: str
    index: int


@dataclass
class RevisionOp:
    result: dict[str, Any]
    finding: dict[str, Any]
    action: str
    paragraph: ET.Element
    index: int
    target: str
    replacement: str | None
    comment: str | None


@dataclass
class CommentOp:
    result: dict[str, Any]
    paragraph: ET.Element
    comment: str


@dataclass
class InsertOp:
    result: dict[str, Any]
    paragraph: ET.Element
    insert_text: str
    comment: str | None


class RedlineEditor:
    def __init__(self, unpacked_dir: Path, *, author: str, organization: str = ""):
        self.unpacked_dir = unpacked_dir
        self.author = author
        self.organization = organization
        self.document_path = unpacked_dir / "word" / "document.xml"
        self.settings_path = unpacked_dir / "word" / "settings.xml"
        self.rels_path = unpacked_dir / "word" / "_rels" / "document.xml.rels"
        self.content_types_path = unpacked_dir / "[Content_Types].xml"
        self.tree = ET.parse(self.document_path)
        self.root = self.tree.getroot()
        self.change_id = self._next_change_id()
        self.comment_id = self._next_comment_id()
        self._comments_tree: ET.ElementTree | None = None

    def save(self) -> None:
        self._ensure_track_revisions()
        self._remove_stale_ignorable_namespaces()
        write_xml_tree(self.document_path, self.tree)
        if self._comments_tree is not None:
            write_xml_tree(self.unpacked_dir / "word" / "comments.xml", self._comments_tree)

    def _remove_stale_ignorable_namespaces(self) -> None:
        for key in list(self.root.attrib):
            if key.endswith("}Ignorable") or key == "Ignorable":
                del self.root.attrib[key]

    def _next_change_id(self) -> int:
        max_id = -1
        for tag in (qn("w:ins"), qn("w:del")):
            for item in self.root.iter(tag):
                try:
                    max_id = max(max_id, int(item.get(qn("w:id"), "-1")))
                except ValueError:
                    pass
        return max_id + 1

    def _next_comment_id(self) -> int:
        path = self.unpacked_dir / "word" / "comments.xml"
        if not path.exists():
            return 0
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            return 0
        max_id = -1
        for item in root.iter(qn("w:comment")):
            try:
                max_id = max(max_id, int(item.get(qn("w:id"), "-1")))
            except ValueError:
                pass
        return max_id + 1

    def _take_change_id(self) -> int:
        value = self.change_id
        self.change_id += 1
        return value

    def _ensure_track_revisions(self) -> None:
        if self.settings_path.exists():
            tree = ET.parse(self.settings_path)
            root = tree.getroot()
        else:
            root = ET.Element(qn("w:settings"))
            tree = ET.ElementTree(root)
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        if root.find(qn("w:trackRevisions")) is None:
            root.append(ET.Element(qn("w:trackRevisions")))
        write_xml_tree(self.settings_path, tree)

    def _ensure_comments(self) -> ET.ElementTree:
        if self._comments_tree is not None:
            return self._comments_tree
        path = self.unpacked_dir / "word" / "comments.xml"
        if path.exists():
            self._comments_tree = ET.parse(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            root = ET.Element(qn("w:comments"))
            self._comments_tree = ET.ElementTree(root)
            self._ensure_comment_relationships()
            self._ensure_comment_content_types()
        return self._comments_tree

    def _ensure_comment_relationships(self) -> None:
        self.rels_path.parent.mkdir(parents=True, exist_ok=True)
        if self.rels_path.exists():
            tree = ET.parse(self.rels_path)
            root = tree.getroot()
        else:
            root = ET.Element(f"{{{REL_NS}}}Relationships")
            tree = ET.ElementTree(root)
        for rel in root.findall(f"{{{REL_NS}}}Relationship"):
            if rel.get("Target") == "comments.xml":
                write_xml_tree(self.rels_path, tree, default_namespace=REL_NS)
                return
        next_id = 1
        for rel in root.findall(f"{{{REL_NS}}}Relationship"):
            rid = rel.get("Id", "")
            if rid.startswith("rId"):
                try:
                    next_id = max(next_id, int(rid[3:]) + 1)
                except ValueError:
                    pass
        rel = ET.SubElement(root, f"{{{REL_NS}}}Relationship")
        rel.set("Id", f"rId{next_id}")
        rel.set(
            "Type",
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments",
        )
        rel.set("Target", "comments.xml")
        write_xml_tree(self.rels_path, tree, default_namespace=REL_NS)

    def _ensure_comment_content_types(self) -> None:
        if not self.content_types_path.exists():
            return
        tree = ET.parse(self.content_types_path)
        root = tree.getroot()
        for item in root.findall(f"{{{CT_NS}}}Override"):
            if item.get("PartName") == "/word/comments.xml":
                write_xml_tree(self.content_types_path, tree, default_namespace=CT_NS)
                return
        override = ET.SubElement(root, f"{{{CT_NS}}}Override")
        override.set("PartName", "/word/comments.xml")
        override.set(
            "ContentType",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml",
        )
        write_xml_tree(self.content_types_path, tree, default_namespace=CT_NS)

    def paragraph_matches(self, text: str) -> list[Match]:
        matches: list[Match] = []
        for paragraph in self.root.iter(qn("w:p")):
            paragraph_text = get_text(paragraph)
            start = 0
            while True:
                idx = paragraph_text.find(text, start)
                if idx < 0:
                    break
                matches.append(Match(paragraph=paragraph, text=paragraph_text, index=idx))
                start = idx + len(text)
        return matches

    def resolve_paragraph(
        self,
        finding: dict[str, Any],
        *,
        action: str,
    ) -> Match:
        selector = finding.get("selector")
        occurrence = int(finding.get("occurrence") or 0) or None
        target_text = target_text_for(finding)
        if not target_text:
            raise ValueError(f"action={action} 缺少 target_text/original_text/selector.contains")

        paragraph_index = selector.get("paragraph_index") if isinstance(selector, dict) else None
        if paragraph_index is not None:
            try:
                index = int(paragraph_index)
            except (TypeError, ValueError) as exc:
                raise ValueError("selector.paragraph_index 必须是从 1 开始的整数") from exc
            paragraphs = list(self.root.iter(qn("w:p")))
            if index < 1 or index > len(paragraphs):
                raise ValueError(f"selector.paragraph_index={index} 超出范围，实际段落 {len(paragraphs)} 个")
            paragraph = paragraphs[index - 1]
            paragraph_text = get_text(paragraph)
            found_at = paragraph_text.find(target_text)
            if found_at < 0:
                raise ValueError(f"第 {index} 段未找到目标文本: {target_text}")
            return Match(paragraph=paragraph, text=paragraph_text, index=found_at)

        matches = self.paragraph_matches(target_text)
        if not matches:
            raise ValueError(f"未找到目标文本: {target_text}")
        if occurrence is not None:
            if occurrence < 1 or occurrence > len(matches):
                raise ValueError(f"occurrence={occurrence} 超出范围，实际命中 {len(matches)} 处")
            return matches[occurrence - 1]
        if len(matches) > 1:
            raise ValueError(f"目标文本命中 {len(matches)} 处，请提供 occurrence 或 selector")
        return matches[0]

    def replace_text(self, finding: dict[str, Any], comment: str | None = None) -> str:
        replacement = finding.get("replacement_text")
        if replacement is None:
            raise ValueError("replace 缺少 replacement_text")
        match = self.resolve_paragraph(finding, action="replace")
        target = target_text_for(finding)
        if not target:
            raise ValueError("replace 缺少 target_text/original_text/selector.contains")
        if (
            looks_like_full_paragraph_change(target, match.text)
            and not boolean_field(finding, "allow_full_paragraph_replace")
        ):
            raise ValueError(
                "疑似整段替换：请将 target_text 拆成最小待修改文本，"
                "完整条款原文仅放 original_text；确需整段重写时设置 "
                "allow_full_paragraph_replace=true 并说明原因"
            )
        before = match.text[: match.index]
        after = match.text[match.index + len(target) :]
        self._rewrite_paragraph(
            match.paragraph,
            [
                ("equal", before),
                ("delete", target),
                ("insert", str(replacement)),
                ("equal", after),
            ],
        )
        if comment:
            self.add_comment(match.paragraph, comment)
        return "已替换目标文本"

    def delete_text(self, finding: dict[str, Any], comment: str | None = None) -> str:
        match = self.resolve_paragraph(finding, action="delete")
        target = target_text_for(finding)
        if not target:
            raise ValueError("delete 缺少 target_text/original_text/selector.contains")
        if (
            looks_like_full_paragraph_change(target, match.text)
            and not boolean_field(finding, "allow_full_paragraph_replace")
        ):
            raise ValueError(
                "疑似整段删除：请将 target_text 拆成最小待删除文本；"
                "确需整段删除时设置 allow_full_paragraph_replace=true 并说明原因"
            )
        before = match.text[: match.index]
        after = match.text[match.index + len(target) :]
        self._rewrite_paragraph(
            match.paragraph,
            [
                ("equal", before),
                ("delete", target),
                ("equal", after),
            ],
        )
        if comment:
            self.add_comment(match.paragraph, comment)
        return "已删除目标文本"

    def insert_text(self, finding: dict[str, Any], comment: str | None = None) -> str:
        insert_text = finding.get("insert_text") or finding.get("replacement_text")
        if not insert_text:
            raise ValueError("insert 缺少 insert_text/replacement_text")
        match = self.resolve_paragraph(finding, action="insert")
        self.insert_after_paragraph(match.paragraph, str(insert_text), comment=comment)
        return "已在目标段落后插入文本"

    def insert_after_paragraph(
        self,
        paragraph: ET.Element,
        insert_text: str,
        comment: str | None = None,
    ) -> None:
        parent = self._find_parent(self.root, paragraph)
        if parent is None:
            raise ValueError("未找到插入段落父节点")
        idx = list(parent).index(paragraph)
        para = ET.Element(qn("w:p"))
        para.append(
            make_ins(
                str(insert_text),
                change_id=self._take_change_id(),
                author=self.author_display,
                date=local_date(),
            )
        )
        parent.insert(idx + 1, para)
        if comment:
            self.add_comment(paragraph, comment)

    def add_comment_by_finding(self, finding: dict[str, Any], comment: str) -> str:
        match = self.resolve_paragraph(finding, action="comment")
        self.add_comment(match.paragraph, comment)
        return "已添加批注"

    @property
    def author_display(self) -> str:
        if self.organization:
            return f"{self.author}｜{self.organization}"
        return self.author

    def add_comment(self, paragraph: ET.Element, text: str) -> None:
        comments_tree = self._ensure_comments()
        comments_root = comments_tree.getroot()
        cid = self.comment_id
        self.comment_id += 1
        date = local_date()

        comment = ET.SubElement(comments_root, qn("w:comment"))
        comment.set(qn("w:id"), str(cid))
        comment.set(qn("w:author"), self.author_display)
        comment.set(qn("w:date"), date)
        comment_p = ET.SubElement(comment, qn("w:p"))
        comment_r = ET.SubElement(comment_p, qn("w:r"))
        comment_t = ET.SubElement(comment_r, qn("w:t"))
        comment_t.text = text

        start = ET.Element(qn("w:commentRangeStart"))
        start.set(qn("w:id"), str(cid))
        end = ET.Element(qn("w:commentRangeEnd"))
        end.set(qn("w:id"), str(cid))
        ref_run = ET.Element(qn("w:r"))
        ref = ET.SubElement(ref_run, qn("w:commentReference"))
        ref.set(qn("w:id"), str(cid))
        paragraph.insert(0, start)
        paragraph.append(end)
        paragraph.append(ref_run)

    def _rewrite_paragraph(self, paragraph: ET.Element, segments: list[tuple[str, str]]) -> None:
        ppr = None
        for child in list(paragraph):
            if child.tag == qn("w:pPr"):
                ppr = child
                break
        for child in list(paragraph):
            paragraph.remove(child)
        if ppr is not None:
            paragraph.append(ppr)
        date = local_date()
        for kind, text in segments:
            if not text:
                continue
            if kind == "equal":
                paragraph.append(make_run(text))
            elif kind == "delete":
                paragraph.append(
                    make_del(
                        text,
                        change_id=self._take_change_id(),
                        author=self.author_display,
                        date=date,
                    )
                )
            elif kind == "insert":
                paragraph.append(
                    make_ins(
                        text,
                        change_id=self._take_change_id(),
                        author=self.author_display,
                        date=date,
                    )
                )

    def _find_parent(self, current: ET.Element, target: ET.Element) -> ET.Element | None:
        for child in list(current):
            if child is target:
                return current
            found = self._find_parent(child, target)
            if found is not None:
                return found
        return None


def build_comment(finding: dict[str, Any]) -> str:
    explicit = str(finding.get("comment") or "").strip()
    if explicit:
        return explicit
    lines = []
    if finding.get("handling_advice"):
        lines.append(f"处理建议：{finding['handling_advice']}")
    if finding.get("clause"):
        lines.append(f"条款位置：{finding['clause']}")
    if finding.get("issue"):
        lines.append(f"问题：{finding['issue']}")
    if finding.get("legal_risk"):
        lines.append(f"法律风险：{finding['legal_risk']}")
    if finding.get("business_risk"):
        lines.append(f"业务风险：{finding['business_risk']}")
    if finding.get("replacement_text") and normalize_action(finding.get("action")) != "replace":
        lines.append(f"建议文本：{finding['replacement_text']}")
    if finding.get("source"):
        lines.append(f"来源：{finding['source']}")
    return "\n".join(lines) or "请复核该条款。"


def revision_comment(finding: dict[str, Any]) -> str | None:
    explicit = str(finding.get("comment") or "").strip()
    if explicit:
        return explicit
    if boolean_field(finding, "comment_required", "requires_comment"):
        return build_comment(finding)
    return None


def empty_result(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": finding.get("id"),
        "requested_action": normalize_action(finding.get("action")),
        "action": None,
        "status": "skipped",
        "message": "",
    }


def apply_finding(editor: RedlineEditor, finding: dict[str, Any]) -> dict[str, Any]:
    result = empty_result(finding)
    try:
        action = resolve_action(finding)
        result["action"] = action
        if action in {"skip", "none"}:
            result["message"] = "按计划跳过"
            return result
        if action == "report-only":
            result["status"] = "report_only"
            result["message"] = "仅写入审查意见书，不写入 Word 正文"
            return result
        if action == "comment":
            result["message"] = editor.add_comment_by_finding(finding, build_comment(finding))
        elif action == "replace":
            result["message"] = editor.replace_text(finding, comment=revision_comment(finding))
        elif action == "insert":
            result["message"] = editor.insert_text(finding, comment=revision_comment(finding))
        elif action == "delete":
            result["message"] = editor.delete_text(finding, comment=revision_comment(finding))
        else:
            raise ValueError(f"不支持的 action: {action}")
        result["status"] = "applied"
    except Exception as exc:  # Keep processing other findings.
        result["status"] = "failed"
        result["message"] = str(exc)
    return result


def collect_finding(
    editor: RedlineEditor,
    finding: dict[str, Any],
) -> tuple[dict[str, Any], RevisionOp | CommentOp | InsertOp | None]:
    result = empty_result(finding)
    try:
        action = resolve_action(finding)
        result["action"] = action
        if action in {"skip", "none"}:
            result["message"] = "按计划跳过"
            return result, None
        if action == "report-only":
            result["status"] = "report_only"
            result["message"] = "仅写入审查意见书，不写入 Word 正文"
            return result, None
        if action == "comment":
            match = editor.resolve_paragraph(finding, action="comment")
            return result, CommentOp(result, match.paragraph, build_comment(finding))
        if action == "insert":
            insert_text = finding.get("insert_text") or finding.get("replacement_text")
            if not insert_text:
                raise ValueError("insert 缺少 insert_text/replacement_text")
            match = editor.resolve_paragraph(finding, action="insert")
            return result, InsertOp(result, match.paragraph, str(insert_text), revision_comment(finding))
        if action in {"replace", "delete"}:
            target = target_text_for(finding)
            if not target:
                raise ValueError(f"{action} 缺少 target_text/original_text/selector.contains")
            if action == "replace" and finding.get("replacement_text") is None:
                raise ValueError("replace 缺少 replacement_text")
            match = editor.resolve_paragraph(finding, action=action)
            if (
                looks_like_full_paragraph_change(target, match.text)
                and not boolean_field(finding, "allow_full_paragraph_replace")
            ):
                verb = "替换" if action == "replace" else "删除"
                raise ValueError(
                    f"疑似整段{verb}：请将 target_text 拆成最小待修改文本，"
                    "完整条款原文仅放 original_text；确需整段处理时设置 "
                    "allow_full_paragraph_replace=true 并说明原因"
                )
            return result, RevisionOp(
                result=result,
                finding=finding,
                action=action,
                paragraph=match.paragraph,
                index=match.index,
                target=target,
                replacement=str(finding.get("replacement_text")) if action == "replace" else None,
                comment=revision_comment(finding),
            )
        raise ValueError(f"不支持的 action: {action}")
    except Exception as exc:
        result["status"] = "failed"
        result["message"] = str(exc)
        return result, None


def apply_revision_group(editor: RedlineEditor, paragraph: ET.Element, ops: list[RevisionOp]) -> None:
    paragraph_text = get_text(paragraph)
    ordered = sorted(ops, key=lambda item: (item.index, -(len(item.target))))
    cursor = 0
    segments: list[tuple[str, str]] = []
    for op in ordered:
        if op.index < cursor:
            raise ValueError(f"{op.result.get('id')} 与同段其他修订范围重叠，请拆分或合并")
        if paragraph_text[op.index : op.index + len(op.target)] != op.target:
            raise ValueError(f"{op.result.get('id')} 目标文本位置已变化，请重新定位")
        if op.index > cursor:
            segments.append(("equal", paragraph_text[cursor : op.index]))
        segments.append(("delete", op.target))
        if op.action == "replace" and op.replacement is not None:
            segments.append(("insert", op.replacement))
        cursor = op.index + len(op.target)
    if cursor < len(paragraph_text):
        segments.append(("equal", paragraph_text[cursor:]))
    editor._rewrite_paragraph(paragraph, segments)


def apply_findings(editor: RedlineEditor, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    revision_groups: dict[int, tuple[ET.Element, list[RevisionOp]]] = {}
    comments: list[CommentOp] = []
    inserts: list[InsertOp] = []

    for finding in findings:
        result, op = collect_finding(editor, finding)
        results.append(result)
        if isinstance(op, RevisionOp):
            key = id(op.paragraph)
            revision_groups.setdefault(key, (op.paragraph, []) )[1].append(op)
        elif isinstance(op, CommentOp):
            comments.append(op)
        elif isinstance(op, InsertOp):
            inserts.append(op)

    for paragraph, ops in revision_groups.values():
        try:
            apply_revision_group(editor, paragraph, ops)
            for op in ops:
                op.result["status"] = "applied"
                op.result["message"] = "已替换目标文本" if op.action == "replace" else "已删除目标文本"
                if op.comment:
                    editor.add_comment(paragraph, op.comment)
        except Exception as exc:
            for op in ops:
                op.result["status"] = "failed"
                op.result["message"] = str(exc)

    for op in comments:
        try:
            editor.add_comment(op.paragraph, op.comment)
            op.result["status"] = "applied"
            op.result["message"] = "已添加批注"
        except Exception as exc:
            op.result["status"] = "failed"
            op.result["message"] = str(exc)

    for op in inserts:
        try:
            editor.insert_after_paragraph(op.paragraph, op.insert_text, comment=op.comment)
            op.result["status"] = "applied"
            op.result["message"] = "已在目标段落后插入文本"
        except Exception as exc:
            op.result["status"] = "failed"
            op.result["message"] = str(exc)

    return results


def pack_docx(unpacked_dir: Path, output_docx: Path) -> None:
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_docx, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in unpacked_dir.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(unpacked_dir))


def build_summary(
    *,
    input_docx: Path,
    output_docx: Path,
    plan_path: Path,
    plan: dict[str, Any],
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    counts = {
        "applied": sum(1 for item in results if item["status"] == "applied"),
        "failed": sum(1 for item in results if item["status"] == "failed"),
        "skipped": sum(1 for item in results if item["status"] == "skipped"),
        "report_only": sum(1 for item in results if item["status"] == "report_only"),
    }
    return {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "input_docx": str(input_docx),
        "output_docx": str(output_docx),
        "plan_path": str(plan_path),
        "meta": plan.get("meta") if isinstance(plan.get("meta"), dict) else {},
        **counts,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="执行合同 redline-plan 并生成 Word 审核修订稿")
    parser.add_argument("--input", required=True, help="原 DOCX 路径")
    parser.add_argument("--plan", required=True, help="redline-plan.json 路径")
    parser.add_argument("--output", required=True, help="输出审核修订稿 DOCX 路径")
    parser.add_argument("--log", help="执行日志 JSON 路径")
    parser.add_argument("--author", default="【律师姓名】", help="批注/修订作者")
    parser.add_argument(
        "--organization",
        default="【律所名称】",
        help="批注/修订作者机构",
    )
    args = parser.parse_args()

    input_docx = Path(args.input).expanduser().resolve()
    plan_path = Path(args.plan).expanduser().resolve()
    output_docx = Path(args.output).expanduser().resolve()
    log_path = (
        Path(args.log).expanduser().resolve()
        if args.log
        else output_docx.with_name(f"{output_docx.stem}_redline-execution-log.json")
    )
    if not input_docx.exists():
        raise FileNotFoundError(f"原 DOCX 不存在: {input_docx}")
    if not plan_path.exists():
        raise FileNotFoundError(f"redline-plan 不存在: {plan_path}")

    plan = load_plan(plan_path)
    validate_party_role_gate(plan)
    with tempfile.TemporaryDirectory(prefix="contract-redline-") as tmp:
        unpacked_dir = Path(tmp) / "unpacked"
        with zipfile.ZipFile(input_docx) as zf:
            zf.extractall(unpacked_dir)
        editor = RedlineEditor(
            unpacked_dir,
            author=args.author,
            organization=args.organization,
        )
        results = apply_findings(
            editor,
            [finding for finding in plan.get("findings", []) if isinstance(finding, dict)],
        )
        editor.save()
        pack_docx(unpacked_dir, output_docx)

    summary = build_summary(
        input_docx=input_docx,
        output_docx=output_docx,
        plan_path=plan_path,
        plan=plan,
        results=results,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
