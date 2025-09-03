#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_quiz_dir(src_dir: str, strict: bool = False) -> Dict[str, Any]:
    base = Path(src_dir)
    if not base.exists() or not base.is_dir():
        return {"ok": False, "issues": [{"dir": str(base), "error": "not_found"}], "files": []}

    files = sorted([p for p in base.glob("quiz_*_harvested.json") if p.is_file()])
    if not files:
        return {"ok": False, "issues": [{"dir": str(base), "error": "no_quiz_files"}], "files": []}

    issues: List[Dict[str, Any]] = []
    files_info: List[Dict[str, Any]] = []
    total_questions = 0
    for fp in files:
        try:
            data = json.loads(fp.read_text())
        except Exception as e:
            issues.append({"file": str(fp), "problems": [f"json parse error: {e}"]})
            continue
        problems: List[str] = []
        if not isinstance(data, dict):
            problems.append("root not object")
        questions = data.get("questions")
        if not isinstance(questions, list):
            problems.append("questions not array")
        else:
            # spot check first few
            for i, q in enumerate(questions[:5]):
                if not isinstance(q, dict):
                    problems.append(f"q[{i}] not object")
                    break
                if not isinstance(q.get("question"), str) or not q.get("question", "").strip():
                    problems.append(f"q[{i}].question missing")
                if not isinstance(q.get("options"), list) or len(q.get("options", [])) < 2:
                    problems.append(f"q[{i}].options invalid")
                ca = q.get("correct_answer")
                if not isinstance(ca, int):
                    problems.append(f"q[{i}].correct_answer not int")
                else:
                    if ca < 0 or ca >= len(q.get("options", [])):
                        problems.append(f"q[{i}].correct_answer out of range")
                diff = q.get("difficulty")
                if not isinstance(diff, int) or not (1 <= diff <= 5):
                    problems.append(f"q[{i}].difficulty not 1..5")
        meta = data.get("metadata")
        if not isinstance(meta, dict):
            problems.append("metadata not object")
        if problems:
            issues.append({"file": str(fp), "problems": problems})
        q_count = len(questions) if isinstance(questions, list) else 0
        files_info.append({
            "file": str(fp),
            "sha256": sha256_file(fp),
            "size_bytes": fp.stat().st_size,
            "question_count": q_count,
        })
        total_questions += q_count

    ok = len(issues) == 0 if strict else True
    return {"ok": ok, "issues": issues, "files": files_info, "total_questions": total_questions}


def validate_harvest_db(db_path: str) -> Dict[str, Any]:
    p = Path(db_path)
    if not p.exists():
        return {"ok": False, "issues": [{"db": str(p), "error": "db_not_found"}]}
    issues: List[Dict[str, Any]] = []
    stats: Dict[str, Any] = {}
    try:
        conn = sqlite3.connect(str(p))
        cur = conn.cursor()
        # Tables exist?
        try:
            cur.execute("SELECT COUNT(*) FROM generated_questions")
            stats["generated_questions"] = cur.fetchone()[0]
        except Exception as e:
            issues.append({"db": str(p), "error": f"missing_table_generated_questions: {e}"})
        try:
            cur.execute("SELECT COUNT(*) FROM harvested_content")
            stats["harvested_content"] = cur.fetchone()[0]
        except Exception as e:
            issues.append({"db": str(p), "error": f"missing_table_harvested_content: {e}"})
        # Avg confidence
        try:
            cur.execute("SELECT AVG(confidence) FROM generated_questions")
            stats["avg_confidence"] = cur.fetchone()[0]
        except Exception:
            pass
        conn.close()
    except Exception as e:
        issues.append({"db": str(p), "error": f"db_error: {e}"})
    ok = (stats.get("generated_questions", 0) > 0) and (len(issues) == 0)
    return {"ok": ok, "issues": issues, "stats": stats}


def validate_research_repo(repo_path: str) -> Dict[str, Any]:
    base = Path(repo_path)
    docs = base / "docs" / "research"
    summaries = docs / "summaries"
    index_md = docs / "index.md"
    template = docs / "templates" / "ENTRY_TEMPLATE.md"
    issues: List[Dict[str, Any]] = []
    if not docs.exists():
        issues.append({"repo": str(base), "error": "missing_docs_research"})
    if not summaries.exists():
        issues.append({"repo": str(base), "error": "missing_summaries_dir"})
    if not index_md.exists():
        issues.append({"repo": str(base), "error": "missing_index_md"})
    if not template.exists():
        issues.append({"repo": str(base), "error": "missing_entry_template"})
    return {"ok": len(issues) == 0, "issues": issues}
