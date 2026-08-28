#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backup all source files referenced by the template/export manifest."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
LEGAL_DIR = SKILL_DIR.parent
MANIFEST_PATH = SKILL_DIR / "assets" / "template-manifest.json"
BACKUP_ROOT = LEGAL_DIR / "_backups"


def main() -> int:
    parser = argparse.ArgumentParser(description="Backup format source files before migration.")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = args.output_dir or (BACKUP_ROOT / f"法律文书模板与导出迁移_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)

    sources: list[str] = []
    for item in manifest.get("format_candidates", []):
        sources.append(item["source"])
    for item in manifest.get("technical_plan_assessments", []):
        sources.append(item["source"])

    copied: list[str] = []
    missing: list[str] = []
    for rel in sorted(set(sources)):
        src = LEGAL_DIR / rel
        if not src.exists():
            missing.append(rel)
            continue
        dst = backup_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)

    report = {
        "backup_dir": str(backup_dir),
        "copied_count": len(copied),
        "missing_count": len(missing),
        "copied": copied,
        "missing": missing,
    }
    report_path = backup_dir / "backup-manifest.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"backup_dir: {backup_dir}")
    print(f"copied_count: {len(copied)}")
    print(f"missing_count: {len(missing)}")
    if missing:
        for rel in missing:
            print(f"missing: {rel}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
