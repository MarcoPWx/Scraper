#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def write_ship_report(path: str, context: Dict[str, Any]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    totals = context.get("totals", {})
    quizzes = context.get("quizzes", [])
    research = context.get("research", [])
    previews_quiz = context.get("previews_quiz", [])
    previews_research = context.get("previews_research", [])
    warnings = context.get("warnings", [])
    params = context.get("params", {})
    legal = context.get("legal", {})

    def esc(s: str) -> str:
        return (
            str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    quizzes_rows = "".join(
        f"<tr><td>{esc(q.get('category',''))}</td><td>{esc(q.get('file',''))}</td><td>{q.get('question_count',0)}</td><td><code>{esc(q.get('sha256','')[:12])}</code></td></tr>"
        for q in quizzes
    )
    research_rows = "".join(
        f"<tr><td>{esc(r.get('slug',''))}</td><td>{esc(r.get('category',''))}</td><td>{esc(r.get('file',''))}</td></tr>"
        for r in research
    )
    warn_list = "".join(f"<li>{esc(json.dumps(w))}</li>" for w in warnings)
    preview_quiz_list = "".join(
        f"<li><b>{esc(p.get('category',''))}</b>: {esc(p.get('q1',''))} | {esc(p.get('q2',''))}</li>" for p in previews_quiz
    )
    preview_research_list = "".join(
        f"<li><b>{esc(p.get('slug',''))}</b>: {esc(p.get('first_bullet',''))}</li>" for p in previews_research
    )
    legal_rows = "".join(
        f"<tr><td>{esc(k)}</td><td>{esc(str(v))}</td></tr>" for k, v in legal.items()
    )

    html = f"""<!doctype html>
<html>
<head>
<meta charset=\"utf-8\" />
<title>Scraper Ship Report</title>
<style>
body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
.card {{ border: 1px solid #eee; border-radius: 8px; padding: 12px; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ border-bottom: 1px solid #eee; padding: 6px 8px; text-align: left; }}
code {{ background: #f7f7f7; padding: 1px 4px; border-radius: 4px; }}
</style>
</head>
<body>
<h1>Scraper Ship Report</h1>
<div class=\"grid\">
  <div class=\"card\"><h2>Totals</h2>
    <ul>
      <li>Quiz files: {totals.get('quiz_files',0)}</li>
      <li>Quiz questions: {totals.get('quiz_questions',0)}</li>
      <li>Research created: {totals.get('research_created',0)}</li>
      <li>Research skipped: {totals.get('research_skipped',0)}</li>
    </ul>
  </div>
  <div class=\"card\"><h2>Parameters</h2>
    <pre>{esc(json.dumps(params, indent=2))}</pre>
  </div>
</div>

<div class=\"card\">
  <h2>Quizzes</h2>
  <table>
    <thead><tr><th>Category</th><th>File</th><th>Questions</th><th>sha256</th></tr></thead>
    <tbody>{quizzes_rows}</tbody>
  </table>
</div>

<div class=\"card\">
  <h2>Research</h2>
  <table>
    <thead><tr><th>Slug</th><th>Category</th><th>File</th></tr></thead>
    <tbody>{research_rows}</tbody>
  </table>
</div>

<div class=\"card\">
  <h2>Warnings</h2>
  <ul>{warn_list or '<li>None</li>'}</ul>
</div>

<div class=\"card\">
  <h2>Previews (Quiz)</h2>
  <ul>{preview_quiz_list or '<li>None</li>'}</ul>
</div>

<div class=\"card\">
  <h2>Previews (Research)</h2>
  <ul>{preview_research_list or '<li>None</li>'}</ul>
</div>

<div class=\"card\">
  <h2>Legal Summary</h2>
  <table>
    <thead><tr><th>Gate</th><th>Status/Counts</th></tr></thead>
    <tbody>{legal_rows or '<tr><td colspan=2><i>No legal data</i></td></tr>'}</tbody>
  </table>
  <p style=\"font-size: 12px; color: #888\">See Legal Guardrails doc and policy.yaml for configuration. [teach §Legal]</p>
</div>

</body>
</html>"""
    out.write_text(html)
    return out
