#!/usr/bin/env python3
"""
Validate minimal quiz schema in a directory.

Usage:
  python3 scripts/validate_quiz_dir.py --from ./out/quizzes

Checks:
- File name pattern quiz_*.json
- questions[] array exists and non-empty
- Each question has: question (str), options (list of 2..), correct_answer (int) within range
- Difficulty in 1..5 if present

Exit code: 0 on success, non-zero if any file fails.
"""
import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List

QUIZ_PATTERN = re.compile(r"^quiz_.*\.json$")


def validate_quiz_file(path: str) -> List[str]:
    errors: List[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        errors.append(f"{path}: not valid JSON ({e})")
        return errors

    questions = data.get("questions")
    if not isinstance(questions, list) or not questions:
        errors.append(f"{path}: questions[] missing or empty")
        return errors

    for idx, q in enumerate(questions):
        prefix = f"{path} [q#{idx}]"
        if not isinstance(q, dict):
            errors.append(f"{prefix}: not an object")
            continue
        question = q.get("question")
        options = q.get("options")
        ca = q.get("correct_answer")
        if not isinstance(question, str) or not question.strip():
            errors.append(f"{prefix}: question missing/empty")
        if not isinstance(options, list) or len(options) < 2:
            errors.append(f"{prefix}: options must be an array with >=2 entries")
        else:
            if not all(isinstance(o, str) and o.strip() for o in options):
                errors.append(f"{prefix}: options must be non-empty strings")
        if not isinstance(ca, int):
            errors.append(f"{prefix}: correct_answer must be an integer index")
        else:
            if not (0 <= ca < (len(options) if isinstance(options, list) else 0)):
                errors.append(f"{prefix}: correct_answer index out of range")
        diff = q.get("difficulty")
        if diff is not None:
            if not isinstance(diff, int) or not (1 <= diff <= 5):
                errors.append(f"{prefix}: difficulty must be int in 1..5 if present")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True, help="Directory containing quiz_*.json")
    args = ap.parse_args()

    src = os.path.abspath(args.src)
    if not os.path.isdir(src):
        print(f"ERR: not a directory: {src}", file=sys.stderr)
        return 2

    files = [f for f in os.listdir(src) if QUIZ_PATTERN.match(f)]
    if not files:
        print(f"WARN: no quiz_*.json found in {src}")
        return 1

    total_errors = 0
    for name in sorted(files):
        path = os.path.join(src, name)
        errs = validate_quiz_file(path)
        if errs:
            total_errors += len(errs)
            for e in errs:
                print(f"FAIL: {e}")
        else:
            print(f"OK: {path}")

    if total_errors:
        print(f"SUMMARY: {total_errors} validation errors found", file=sys.stderr)
        return 1
    print("SUMMARY: all quizzes passed minimal schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())

