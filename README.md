# Scraper

A modular educational content scraping and question-generation engine extracted from QuizMentor.ai.

Features:
- HTTP scraping via requests + BeautifulSoup and RSS via feedparser
- Massive harvest pipeline (MassiveHarvester) with SQLite storage, CSV exports, stats
- Enhanced harvest pipeline (EnhancedHarvester) with semantic uniqueness and distractor quality
- Pluggable exporters (QuizMentor format included) for generating downstream artifacts
- Simple CLI: `scraper harvest ...` and `scraper export ...`

Quick start

1) Install (editable):
pip install -e /Users/betolbook/Documents/github/Scraper

2) Harvest content (massive pipeline):
   scraper harvest massive --output-dir /tmp/harvest --max-content 200 --questions-per-content 5 --workers 8

3) Export to QuizMentor format:
   scraper export quizmentor --db /tmp/harvest/harvest.db --out ./out

Folder structure
- src/scraper/harvesters: harvesting engines
- src/scraper/exporters: output formatters and pipelines
- src/scraper/cli.py: command line interface

License: MIT


Importers (run here)

- QuizMentor importer
  - Copies/links quiz_*.json produced by exporter into your QuizMentor repo
  - Command:
    - scraper import quizmentor --from ./out --to /Users/betolbook/Documents/github/QuizMentor.ai/quizzes --mode copy

- AI-Research importer (no LLM required)
  - Reads harvested_content in SQLite (harvest.db)
  - Writes docs/research/summaries/<slug>.md and appends a row to docs/research/index.md
  - Category decision uses tag→category rules with fallback to Drafts; you can supply a JSON mapping file
  - Command examples:
    - scraper import research --db /tmp/harvest/harvest.db --repo /Users/betolbook/Documents/github/AI-Research --edition PRO --min-quality 0.75
    - scraper import research --db ./harvest_output/harvest.db --repo /Users/betolbook/Documents/github/AI-Research --mapping ./tag_category_map.json --limit 50

ASCII: end-to-end flow

+-----------+     +------------+     +----------------------+     +-------------------+      +-------------------+
| Sources   | --> | Harvesters | --> | SQLite (harvest.db)  | --> | Exporters (quiz)  |  or  | Importers (research)|
+-----------+     +------------+     +----------------------+     +-------------------+      +-------------------+
                                                                  | quizzes/*.json    |      | summaries/*.md    |
                                                                  | harvest_index.json|      | index.md updated  |
                                                                  +-------------------+      +-------------------+

User stories
- As a Quiz Engineer, I can import generated quizzes directly into QuizMentor/quizzes with a single command.
- As a Research Editor, I can generate correctly structured markdown entries in AI-Research without a local LLM.
- As an MLE, I can tune tag→category mapping without code changes via a JSON file.

S2S stories
- Scraper (import research) reads SQLite → writes AI-Research summaries and updates index.md idempotently.
- Scraper (import quizmentor) copies quiz JSON artifacts → QuizMentor repo for downstream consumption.

LLM note
- No local LLM is required. If desired later, we can add optional summarization/category refinement via a local Ollama or API, gated by an environment flag.
