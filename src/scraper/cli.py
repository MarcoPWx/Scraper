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

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        return args.func(args)
    parser.print_help()
    return 1

