# scraper

A modular educational content scraping and question-generation engine extracted from QuizMentor.ai.

Features:
- HTTP scraping via requests + BeautifulSoup and RSS via feedparser
- Massive harvest pipeline (MassiveHarvester) with SQLite storage, CSV exports, stats
- Enhanced harvest pipeline (EnhancedHarvester) with semantic uniqueness and distractor quality
- Pluggable exporters (QuizMentor format included) for generating downstream artifacts
- Simple CLI: `scraper harvest ...` and `scraper export ...`

Quick start

1) Install (editable):
   pip install -e /Users/betolbook/Documents/github/scraper

2) Harvest content (massive pipeline):
   scraper harvest massive --output-dir /tmp/harvest --max-content 200 --questions-per-content 5 --workers 8

3) Export to QuizMentor format:
   scraper export quizmentor --db /tmp/harvest/harvest.db --out ./out

Folder structure
- src/scraper/harvesters: harvesting engines
- src/scraper/exporters: output formatters and pipelines
- src/scraper/cli.py: command line interface

License: MIT
