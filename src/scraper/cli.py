#!/usr/bin/env python3
from __future__ import annotations

"""
Command line interface for the scraper package.

Usage examples:
  scraper harvest massive --output-dir ./harvest_output --max-content 200 --questions-per-content 5 --workers 8
  scraper harvest enhanced  # interactive
  scraper export quizmentor --db ./harvest_output/harvest.db --out ./out
"""

import argparse
from pathlib import Path

from .harvesters.massive import MassiveHarvester
from .harvesters.enhanced import EnhancedHarvester
from .exporters.quizmentor import QuizMentorExporter
from .importers.quizmentor import QuizMentorImporter
from .importers.airesearch import AIResearchImporter
from .validators import validate_quiz_dir, validate_harvest_db, validate_research_repo
from .orchestrator import ShipLocalOrchestrator


def cmd_harvest_massive(args) -> int:
    harvester = MassiveHarvester(output_dir=args.output_dir)
    if args.complete:
        harvester.run_complete_harvest(
            max_content=args.max_content,
            questions_per_content=args.questions_per_content,
            parallel_workers=args.workers,
        )
    else:
        content = harvester.harvest_all_sources(limit_per_source=args.max_content // 20)
        questions = harvester.generate_questions_from_content(content, args.questions_per_content)
        harvester.save_questions(questions)
        harvester.generate_csv_report()
        harvester.generate_statistics_report()
    return 0


def cmd_harvest_enhanced(args) -> int:
    harvester = EnhancedHarvester(output_dir=args.output_dir)
    harvester.run_interactive_harvest()
    return 0


def cmd_export_quizmentor(args) -> int:
    exporter = QuizMentorExporter(harvest_db=args.db)
    exporter.export(out=args.out)
    return 0


def cmd_import_quizmentor(args) -> int:
    importer = QuizMentorImporter(source_dir=args.src, target_dir=args.dst, mode=getattr(args, "mode", "copy"), verify=not args.no_verify)
    summary = importer.run()
    # Print a compact summary to stdout
    print(f"Imported {summary['copied']} quiz files → {summary['target_dir']} (issues: {len(summary['issues'])})")
    return 0


def cmd_import_airesearch(args) -> int:
    importer = AIResearchImporter(
        db_path=args.db,
        repo_path=args.repo,
        edition=args.edition,
        min_quality=args.min_quality,
        mapping_file=args.mapping,
        dry_run=args.dry_run,
        limit=args.limit,
        teach=args.teach,
    )
    summary = importer.run()
    print(
        "AI-Research import: created={} skipped={} repo={} dry_run={}".format(
            summary.get("created"), summary.get("skipped"), summary.get("repo"), summary.get("dry_run")
        )
    )
    return 0


def cmd_validate_quiz(args) -> int:
    res = validate_quiz_dir(args.src, strict=args.strict)
    print(json.dumps(res, indent=2))
    return 0 if res.get("ok", False) else 1


def cmd_validate_harvest(args) -> int:
    res = validate_harvest_db(args.db)
    print(json.dumps(res, indent=2))
    return 0 if res.get("ok", False) else 1


def cmd_validate_research(args) -> int:
    res = validate_research_repo(args.repo)
    print(json.dumps(res, indent=2))
    return 0 if res.get("ok", False) else 1


def cmd_ship_local(args) -> int:
    console = Console()
    orch = ShipLocalOrchestrator(console=console)
    result = orch.run(
        output_dir=args.output_dir,
        max_content=args.max_content,
        questions_per_content=args.questions_per_content,
        workers=args.workers,
        skip_harvest=args.skip_harvest,
        db=args.db,
        export_out=args.export_out,
        qm_quizzes_dir=args.qm_quizzes_dir,
        research_repo=args.research_repo,
        min_quality=args.min_quality,
        report_dir=args.report_dir,
        mode=args.mode,
        strict=args.strict,
        limit=args.limit,
    )
    print(json.dumps({k: v for k, v in result.items() if k in ("db", "export", "report")}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scraper", description="Modular scraping and question-generation engine")
    subparsers = parser.add_subparsers(dest="command")

    # harvest massive
    harvest_parser = subparsers.add_parser("harvest", help="Harvest content and generate questions")
    harvest_sub = harvest_parser.add_subparsers(dest="harvest_command")

    massive = harvest_sub.add_parser("massive", help="Run the massive harvester")
    massive.add_argument("--output-dir", default="./harvest_output")
    massive.add_argument("--max-content", type=int, default=500)
    massive.add_argument("--questions-per-content", type=int, default=5)
    massive.add_argument("--workers", type=int, default=10)
    massive.add_argument("--complete", action="store_true", help="Run end-to-end pipeline")
    massive.set_defaults(func=cmd_harvest_massive)

    enhanced = harvest_sub.add_parser("enhanced", help="Run the enhanced harvester (interactive)")
    enhanced.add_argument("--output-dir", default="./harvest_output")
    enhanced.set_defaults(func=cmd_harvest_enhanced)

    # export quizmentor
    export_parser = subparsers.add_parser("export", help="Export harvested data")
    export_sub = export_parser.add_subparsers(dest="export_command")

    qm = export_sub.add_parser("quizmentor", help="Export to QuizMentor quiz JSON format")
    qm.add_argument("--db", required=True, help="Path to harvest.db")
    qm.add_argument("--out", default="./out", help="Output directory")
    qm.set_defaults(func=cmd_export_quizmentor)

    # importers
    import_parser = subparsers.add_parser("import", help="Import artifacts into downstream repos")
    import_sub = import_parser.add_subparsers(dest="import_command")

    # import quizmentor
    iqm = import_sub.add_parser("quizmentor", help="Copy/link quiz JSON files into QuizMentor repo")
    iqm.add_argument("--from", dest="src", required=True, help="Directory containing quiz_*.json from exporter")
    iqm.add_argument("--to", dest="dst", required=True, help="Target quizzes directory (e.g., QuizMentor.ai/quizzes)")
    iqm.add_argument("--mode", choices=["copy", "link"], default="copy")
    iqm.add_argument("--no-verify", action="store_true", help="Skip basic schema validation")
    iqm.set_defaults(func=cmd_import_quizmentor)

    # import AI-Research
    iar = import_sub.add_parser("research", help="Write AI-Research markdown summaries + update index")
    iar.add_argument("--db", required=True, help="Path to harvest.db")
    iar.add_argument("--repo", required=True, help="Path to AI-Research repo root")
    iar.add_argument("--edition", choices=["PRO", "CE"], default="PRO")
    iar.add_argument("--min-quality", type=float, default=0.6)
    iar.add_argument("--mapping", help="Optional JSON tag→category mapping file", default=None)
    iar.add_argument("--dry-run", action="store_true")
    iar.add_argument("--limit", type=int, default=None)
    iar.set_defaults(func=cmd_import_airesearch)

    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate artifacts or repos")
    validate_sub = validate_parser.add_subparsers(dest="validate_command")

    vq = validate_sub.add_parser("quiz", help="Validate quiz export directory")
    vq.add_argument("--from", dest="src", required=True, help="Directory containing quiz_*.json")
    vq.add_argument("--strict", action="store_true")
    vq.set_defaults(func=cmd_validate_quiz)

    vh = validate_sub.add_parser("harvest", help="Validate harvest DB")
    vh.add_argument("--db", required=True)
    vh.set_defaults(func=cmd_validate_harvest)

    vr = validate_sub.add_parser("research", help="Validate AI-Research repo structure")
    vr.add_argument("--repo", required=True)
    vr.set_defaults(func=cmd_validate_research)

    # ship
    ship_parser = subparsers.add_parser("ship", help="One-shot local ship (harvest → export → validate → import → report)")
    ship_sub = ship_parser.add_subparsers(dest="ship_command")

    local = ship_sub.add_parser("local", help="Run the full local pipeline")
    local.add_argument("--output-dir", default="./harvest_output")
    local.add_argument("--max-content", type=int, default=200)
    local.add_argument("--questions-per-content", type=int, default=5)
    local.add_argument("--workers", type=int, default=8)
    local.add_argument("--skip-harvest", action="store_true")
    local.add_argument("--db", help="Existing harvest.db (required if --skip-harvest)")
    local.add_argument("--out", dest="export_out", default="./out", help="Export directory for quizzes")
    local.add_argument("--qm", dest="qm_quizzes_dir", required=True, help="Path to QuizMentor/quizzes directory")
    local.add_argument("--research", dest="research_repo", required=True, help="Path to AI-Research repo root")
    local.add_argument("--min-quality", type=float, default=0.6)
    local.add_argument("--report-dir", default="./reports")
    local.add_argument("--mode", choices=["copy", "link"], default="copy")
    local.add_argument("--strict", action="store_true")
    local.add_argument("--teach", action="store_true")
    local.add_argument("--limit", type=int, default=None)
    local.set_defaults(func=cmd_ship_local)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        return args.func(args)
    parser.print_help()
    return 1

