#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.markdown import Markdown

from .harvesters.massive import MassiveHarvester
from .exporters.quizmentor import QuizMentorExporter
from .importers.quizmentor import QuizMentorImporter
from .importers.airesearch import AIResearchImporter
from .validators import validate_quiz_dir, validate_harvest_db, validate_research_repo, sha256_file
from .html_report import write_ship_report


class ShipLocalOrchestrator:
    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def _log_step(self, title: str) -> None:
        self.console.rule(f"[bold cyan]{title}")

    def run(self,
            output_dir: str,
            max_content: int,
            questions_per_content: int,
            workers: int,
            skip_harvest: bool,
            db: str | None,
            export_out: str,
            qm_quizzes_dir: str,
            research_repo: str,
            min_quality: float,
            report_dir: str,
            mode: str = "copy",
            strict: bool = False,
            limit: int | None = None,
            ) -> Dict[str, Any]:
        ctx: Dict[str, Any] = {"steps": [], "warnings": []}

        # 1) Harvest (optional)
        if skip_harvest:
            if not db:
                raise ValueError("--db required when --skip-harvest is set")
            db_path = Path(db)
            self._log_step("Using existing harvest DB")
            self.console.print(f"[green]DB:[/green] {db_path}")
        else:
            self._log_step("Harvest (massive)")
            harvester = MassiveHarvester(output_dir=output_dir)
            summary = harvester.run_complete_harvest(
                max_content=max_content,
                questions_per_content=questions_per_content,
                parallel_workers=workers,
            )
            db_path = Path(summary.get("database", harvester.db_path))
            self.console.print(f"[green]DB:[/green] {db_path}")
            ctx["steps"].append({"harvest": summary})

        # Optional: quick DB validate
        vdb = validate_harvest_db(str(db_path))
        if not vdb.get("ok", False):
            ctx["warnings"].append({"harvest_db": vdb})
        self.console.print(f"Questions in DB: {vdb.get('stats',{}).get('generated_questions', 0)}")

        # 2) Export quizzes
        self._log_step("Export (QuizMentor)")
        export_dir = Path(export_out)
        export_dir.mkdir(parents=True, exist_ok=True)
        exporter = QuizMentorExporter(harvest_db=str(db_path))
        quiz_summary = exporter.export(out=str(export_dir))
        self.console.print(f"[green]Exported[/green] {len(quiz_summary)} category file(s) to {export_dir}")

        # 3) Build manifest
        self._log_step("Manifest")
        files_info: List[Dict[str, Any]] = []
        total_questions = 0
        for cat in quiz_summary:
            file_path = Path(cat["file"]) if Path(cat["file"]).is_absolute() else export_dir / Path(cat["file"]).name
            try:
                data = json.loads(file_path.read_text())
                qcount = len(data.get("questions", []))
            except Exception:
                qcount = cat.get("questions", 0)
            files_info.append({
                "file": str(file_path),
                "category": cat.get("category"),
                "sha256": sha256_file(file_path),
                "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
                "question_count": qcount,
            })
            total_questions += qcount
        manifest = {
            "version": "1.0",
            "created_at": None,
            "generator": "scraper#ship-local",
            "database": {"path": str(db_path), "generated_questions": vdb.get("stats",{}).get("generated_questions", 0), "avg_confidence": vdb.get("stats",{}).get("avg_confidence")},
            "quizzes": files_info,
            "totals": {"quiz_files": len(files_info), "questions": total_questions},
        }
        (export_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        self.console.print(f"[green]Wrote[/green] manifest.json")

        # 4) Validate (quizzes)
        self._log_step("Validate (quizzes)")
        vq = validate_quiz_dir(str(export_dir), strict=strict)
        if not vq.get("ok", False):
            self.console.print("[yellow]Warnings during quiz validation[/yellow]")
            ctx["warnings"].append({"quiz_validate": vq})
        else:
            self.console.print(f"[green]OK[/green] quiz validation; files={len(vq.get('files',[]))} questions≈{vq.get('total_questions',0)}")

        # 5) Import QuizMentor
        self._log_step("Import → QuizMentor (staging)")
        qm_importer = QuizMentorImporter(source_dir=str(export_dir), target_dir=str(qm_quizzes_dir), mode=mode, verify=not strict)
        qm_res = qm_importer.run()
        self.console.print(f"Docked {qm_res.get('copied',0)}/{qm_res.get('files',0)} files to {qm_res.get('target_dir')}")

        # 6) Import AI-Research
        self._log_step("Import → AI-Research (markdown)")
        rr_check = validate_research_repo(research_repo)
        if not rr_check.get("ok", False):
            self.console.print("[yellow]AI-Research repo checks produced warnings[/yellow]")
            ctx["warnings"].append({"research_repo": rr_check})
        rimp = AIResearchImporter(db_path=str(db_path), repo_path=str(research_repo), edition="PRO", min_quality=min_quality, mapping_file=None, dry_run=False, limit=limit)
        rres = rimp.run()
        self.console.print(f"Created={rres.get('created',0)} Skipped={rres.get('skipped',0)} in {rres.get('repo')}")

        # 7) HTML report
        self._log_step("HTML report")
        quizzes_for_report = []
        for fi in files_info:
            quizzes_for_report.append({
                "category": Path(fi["file"]).stem.replace("quiz_",""),
                "file": fi["file"],
                "question_count": fi["question_count"],
                "sha256": fi["sha256"],
            })
        research_for_report = rres.get("items", [])
        totals = {
            "quiz_files": len(files_info),
            "quiz_questions": total_questions,
            "research_created": rres.get("created", 0),
            "research_skipped": rres.get("skipped", 0),
        }
        params = {
            "output_dir": output_dir,
            "db": str(db_path),
            "export_out": str(export_dir),
            "qm_quizzes_dir": str(qm_quizzes_dir),
            "research_repo": str(research_repo),
            "min_quality": min_quality,
            "max_content": max_content,
            "questions_per_content": questions_per_content,
            "workers": workers,
            "strict": strict,
            "mode": mode,
        }
        report_path = Path(report_dir) / "ship-report.html"
        write_ship_report(str(report_path), {
            "totals": totals,
            "quizzes": quizzes_for_report,
            "research": research_for_report,
            "warnings": ctx.get("warnings", []),
            "params": params,
        })
        self.console.print(f"[green]Report:[/green] {report_path}")

        return {
            "db": str(db_path),
            "export": str(export_dir),
            "quizmentor": qm_res,
            "research": rres,
            "report": str(report_path),
            "warnings": ctx.get("warnings", []),
        }
