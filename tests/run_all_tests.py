#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the root benchmark suite and every retained upstream skill test file.

Usage:
    py -3 tests/run_all_tests.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable


def child_env() -> dict:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def find_skill_tests():
    tests = []
    for p in (REPO / "skills" / "legal").rglob("test_*.py"):
        if "fixtures" in p.parts:
            continue
        tests.append(p)
    return sorted(tests)


# 依赖外部 PDF/OCR 工具的测试：缺少工具时按环境跳过（与上游行为一致）。
# 仅当失败输出命中下列环境签名时才视为 ENV_SKIP；其他失败仍计为 FAIL。
ENV_DEPENDENT = {
    "test_files_to_material_packet.py",
}

ENV_FAIL_SIGNATURES = [
    "WinError 2",
    "OCR",
    "pdftotext",
    "pdf2text",
    "系统找不到指定的文件",
]


def run_skill_test_file(path: Path):
    proc = subprocess.run(
        [PY, "-X", "utf8", str(path)],
        cwd=str(path.parent),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=child_env(),
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    print("=== 1. Root behavioral benchmark ===")
    suite = unittest.defaultTestLoader.discover(str(REPO / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print("benchmark: ran=%d failures=%d errors=%d" % (result.testsRun, len(result.failures), len(result.errors)))

    print("=== 2. Retained skill regression tests ===")
    files = find_skill_tests()
    total_failed = 0
    env_skipped = 0
    for f in files:
        code, output = run_skill_test_file(f)
        rel = f.relative_to(REPO).as_posix()
        if code != 0 and f.name in ENV_DEPENDENT and any(sig in output for sig in ENV_FAIL_SIGNATURES):
            env_skipped += 1
            print(f"  {rel} -> ENV_SKIP (external PDF/OCR tool unavailable; same behavior as upstream on this platform)")
            continue
        status = "PASS" if code == 0 else f"FAIL({code})"
        if code != 0:
            total_failed += 1
            tail = "\n".join(output.strip().splitlines()[-25:])
            print(f"  {rel} -> {status}\n{tail}\n")
        else:
            print(f"  {rel} -> {status}")
    print("skill test files: %d, failed: %d, env_skipped: %d" % (len(files), total_failed, env_skipped))

    ok = result.wasSuccessful() and total_failed == 0
    print("=== OVERALL:", "PASS" if ok else "FAIL", "===")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
