#!/usr/bin/env python3
from __future__ import annotations

"""
QuizMentor importer
- Copies or links quiz JSON artifacts (produced by the exporter) into a target
  quizzes directory (e.g., QuizMentor.ai/quizzes)
- Optionally verifies a minimal schema for quiz files
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

from .base import BaseImporter


class QuizMentorImporter(BaseImporter):
    def __init__(self, source_dir: str, target_dir: str, mode: str = "copy", verify: bool = True) -> None:
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.mode = mode  # copy | link
        self.verify = verify
        self.target_dir.mkdir(parents=True, exist_ok=True)

    def _iter_quiz_files(self) -> List[Path]:
        quiz_files = sorted(self.source_dir.glob("quiz_*.json"))
        return quiz_files

    def _verify_quiz_file(self, path: Path) -> List[str]:
        problems: List[str] = []
        try:
            with open(path, "r") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                problems.append("root is not an object")
                return problems
            if "quiz_id" not in data or "questions" not in data:
                problems.append("missing quiz_id or questions")
            if not isinstance(data.get("questions", []), list):
                problems.append("questions is not a list")
            else:
                for idx, q in enumerate(data["questions"][:5]):  # spot check first 5
                    if not all(k in q for k in ["question", "options", "correct_answer"]):
                        problems.append(f"q[{idx}] missing required fields")
                        break
                    if not isinstance(q["options"], list) or not isinstance(q["correct_answer"], int):
                        problems.append(f"q[{idx}] invalid options/correct_answer types")
                        break
        except Exception as e:
            problems.append(f"json error: {e}")
        return problems

    def _transfer(self, src: Path, dst: Path) -> None:
        if self.mode == "link":
            try:
                if dst.exists():
                    dst.unlink()
                dst.symlink_to(src)
                return
            except Exception:
                # fallback to copy if symlink not allowed
                pass
        shutil.copy2(src, dst)

    def run(self, **kwargs) -> Dict[str, Any]:
        quiz_files = self._iter_quiz_files()
        copied, skipped, issues = 0, 0, []
        for qf in quiz_files:
            if self.verify:
                problems = self._verify_quiz_file(qf)
                if problems:
                    issues.append({"file": str(qf), "problems": problems})
                    # still copy, but mark issues
            target = self.target_dir / qf.name
            self._transfer(qf, target)
            copied += 1
        index_src = self.source_dir / "harvest_index.json"
        if index_src.exists():
            self._transfer(index_src, self.target_dir / index_src.name)
        summary = {
            "source_dir": str(self.source_dir),
            "target_dir": str(self.target_dir),
            "files": len(quiz_files),
            "copied": copied,
            "skipped": skipped,
            "issues": issues,
        }
        return summary
