<div align="center">
  
  # Scraper
  
  ### Local‑First Knowledge Harvester & Compliance Packager
  
  <p align="center">
    <strong>Deterministic heuristics, zero LLMs, privacy‑first, fast.</strong>
  </p>
  
  <br/>
  
  ![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python)
  ![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite)
  ![Local Only](https://img.shields.io/badge/Local%20Only-True-blue?style=flat-square)
  [![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](./LICENSE)
  [![Documentation](https://img.shields.io/badge/Docs-Teaching%20First-success?style=flat-square)](./docs)
  
</div>

<br/>

---

## Overview
Scraper ingests curated technical sources and produces two kinds of artifacts without any LLMs:
- Quizzes for QuizMentor (JSON files)
- Markdown summaries + index updates for AI‑Research

It’s local‑only, deterministic, and idempotent by design. Great for privacy‑sensitive teams that still want strong explainability and fast iteration.

## Features
- Local‑first: no cloud calls, runs on your machine
- Deterministic heuristics: TF‑IDF, SimHash, Levenshtein, explicit quality gates
- Two adapters: QuizMentor (quizzes) and AI‑Research (markdown summaries + index)
- Teaching‑first: clear CLI, reports, and concepts explained
- Idempotent importers: safe to re‑run without duplicates

## Quick Start

```bash
# 1) Install (editable)
pip install -e .

# 2) Harvest content to SQLite (local‑only)
scraper harvest massive \
  --output-dir ./harvest_out \
  --max-content 200 \
  --questions-per-content 5 \
  --workers 8 \
  --complete

# 3a) Export quizzes for QuizMentor (local files)
scraper export quizmentor --db ./harvest_out/harvest.db --out ./out

# 3b) Import research summaries into AI‑Research (dry‑run first)
scraper import research \
  --db ./harvest_out/harvest.db \
  --repo /path/to/AI-Research \
  --edition PRO \
  --min-quality 0.75 \
  --dry-run --limit 10

# 3c) Dock quizzes into a local QuizMentor repo
scraper import quizmentor --from ./out --to /path/to/QuizMentor.ai/quizzes --mode copy
```

## CLI Essentials
- Harvest (broad):
  - `scraper harvest massive --output-dir ./harvest_out --max-content 200 --questions-per-content 5 --workers 8 --complete`
- Harvest (quality‑focused):
  - `scraper harvest enhanced --output-dir ./harvest_out`
- Export (quizzes):
  - `scraper export quizmentor --db ./harvest_out/harvest.db --out ./out`
- Import (QuizMentor):
  - `scraper import quizmentor --from ./out --to /path/to/QuizMentor.ai/quizzes --mode copy`
- Import (AI‑Research):
  - `scraper import research --db ./harvest_out/harvest.db --repo /path/to/AI-Research --edition PRO --min-quality 0.75`

## Architecture
```
Sources -> Harvesters -> SQLite (harvest.db) -> Export (quizzes) OR Import (research)
```
- Export produces: `quizzes/quiz_<category>_harvested.json`, `harvest_index.json`
- Import (research) produces: `docs/research/summaries/<slug>.md` and updates `docs/research/index.md`

## Project Structure
- `src/scraper/harvesters` – harvesting engines (massive/enhanced)
- `src/scraper/exporters` – output formatters and pipelines
- `src/scraper/importers` – adapters (QuizMentor, AI‑Research)
- `src/scraper/cli.py` – CLI entry point (`scraper`)

## Contributing
PRs welcome! Please keep flows local‑first and add a brief rationale for any new gates/thresholds. Consider adding a small sample DB and a CLI flag to reproduce.

## License
MIT

---

### Meeting Mode (fast lookup)
- A curated hub of one‑pagers and cheatsheets designed for speed, not depth.
- Each page has a TL;DR, a single diagram, 7–10 talking points, 3–5 tradeoffs, pitfalls, and copy/paste snippets.
- Search‑first: press `/` to focus search, type a keyword (RAG, SSE, contracts, prompts), hit enter.
- Where: Home quick links; /lookup/ (one‑pagers); /cheatsheets/ (copy‑ready); /architecture/GALLERY (diagrams).

Masterclass path (00–12)
- Lessons with narrative + Mermaid diagram + mini‑lab + Grok check + mastery checklist (localStorage)
- Continue button deep‑links to your last Masterclass lesson
- See /syllabus

Quick Start (local‑only)
```bash
# Install (editable)
pip install -e /Users/betolbook/Documents/github/Scraper

# Harvest → Export (quiz) → Import (local)
scraper harvest massive --output-dir /tmp/harvest --max-content 200 --questions-per-content 5 --workers 8 --complete
scraper export quizmentor --db /tmp/harvest/harvest.db --out ./out
scraper import quizmentor --from ./out --to /Users/betolbook/Documents/github/QuizMentor.ai/quizzes --mode copy

# Research (dry‑run first)
scraper import research --db /tmp/harvest/harvest.db --repo /Users/betolbook/Documents/github/AI-Research --edition PRO --min-quality 0.75 --dry-run --limit 10
```
Product: Local Knowledge Harvester & Compliance Packager
- Tagline: Privacy‑first harvesting and packaging with legal guardrails, previews, and teaching‑first explainability.
- Who it serves: content/learning teams, platform/QA, legal/compliance, PMs.
- Differentiators: local‑only, deterministic heuristics, TDD‑gated pipelines, teach logs that map to docs, configurable exporters/importers, and a desktop UI (Tauri).

A modular educational content harvester and question-generation engine (extracted from QuizMentor.ai) with built-in exporters and importers for two targets:
- QuizMentor (quizzes JSON) — local-only by default
- AI-Research (markdown summaries + index updates) — local-only by default

This README is an onboarding manual. It teaches you what the system does, how to run it, the math/algorithms behind it, and all the concepts/abbreviations used. Everything here runs locally without any LLM or cloud services.

Who is this for?
- Engineers who want to harvest dev/tech sources and turn them into multiple-choice questions (MCQs).
- Editors who want to convert high-quality sources into consistent markdown entries (AI-Research) with deterministic, inspectable heuristics.


At a glance (local-only flows)

+-----------+     +------------+     +----------------------+     +-------------------+      +----------------------+
| Sources   | --> | Harvesters | --> | SQLite (harvest.db)  | --> | Exporters (quiz)  |  or  | Importers (research) |
+-----------+     +------------+     +----------------------+     +-------------------+      +----------------------+
                                                                 | quizzes/*.json    |      | summaries/*.md       |
                                                                 | harvest_index.json|      | index.md updated     |
                                                                 +-------------------+      +----------------------+

Docking bays (adapters)
- QuizMentor docking: local file drop-in to QuizMentor/quizzes/ (staging). No DB required.
- AI-Research docking: writes docs/research/summaries/*.md and appends to docs/research/index.md. No LLM required.


Quick start (5 minutes, local-only)

Prereqs: Python 3.10+, pip, internet access.

1) Install (editable)
   pip install -e /Users/betolbook/Documents/github/Scraper
   # or
   pip install -e /path/to/Scraper

2) Harvest (fast path)
   scraper harvest massive --output-dir /tmp/harvest --max-content 200 --questions-per-content 5 --workers 8 --complete

3a) Export quizzes for QuizMentor (local files)
   scraper export quizmentor --db /tmp/harvest/harvest.db --out ./out

3b) Import summaries into AI-Research (no LLM needed)
   scraper import research --db /tmp/harvest/harvest.db --repo /Users/betolbook/Documents/github/AI-Research --edition PRO --min-quality 0.75 --dry-run --limit 10
   # remove --dry-run to write docs/research/summaries/*.md and update docs/research/index.md

3c) Import quizzes into QuizMentor repo (local file drop)
   scraper import quizmentor --from ./out --to /Users/betolbook/Documents/github/QuizMentor.ai/quizzes --mode copy


Folder structure
- src/scraper/harvesters: harvesting engines (massive/enhanced)
- src/scraper/exporters: output formatters and pipelines
- src/scraper/importers: local adapters (QuizMentor, AI-Research)
- src/scraper/cli.py: command line interface (entry point: `scraper`)


Commands (cheat sheet)
- Harvest (broad):
  scraper harvest massive --output-dir ./harvest_output --max-content 200 --questions-per-content 5 --workers 8 --complete
- Harvest (interactive, quality-focused):
  scraper harvest enhanced --output-dir ./harvest_output
- Export quizzes (JSON grouped by category):
  scraper export quizmentor --db ./harvest_output/harvest.db --out ./out
- Import quizzes to QuizMentor repo (local-only):
  scraper import quizmentor --from ./out --to /path/to/QuizMentor.ai/quizzes --mode copy
- Import entries to AI-Research repo (markdown + index, local-only):
  scraper import research --db ./harvest_output/harvest.db --repo /path/to/AI-Research --edition PRO --min-quality 0.75

- Ship (one-shot, teach + preview):
  scraper ship local \
    --qm /path/to/QuizMentor.ai/quizzes \
    --research /path/to/AI-Research \
    --report-dir ./reports \
    --teach --preview --strict \
    --max-content 200 --questions-per-content 5


Core concepts & glossary (plain English)
- Idempotent: An operation you can run multiple times and get the same final state. Here, re-running the importer won’t duplicate summaries or index rows.
- Normalization (vector): Scaling a vector so its length (L2 norm) is 1. Used so cosine similarity compares direction only, not magnitude.
- Centroid (text/category): The “center” vector of a group (e.g., all entries in a category), computed by averaging (then normalizing) their TF‑IDF vectors.
- Metadata enrichment: Fetching extra attributes from a page (e.g., <meta name="author">, og:site_name, published time). Optional and rate-limited; disabled by default.
- TF‑IDF: Term Frequency – Inverse Document Frequency. Scores each token higher if it’s frequent in a document but rare across documents.
- Cosine similarity: Similarity between two vectors in [-1, 1]; with normalized TF‑IDF, it’s in [0, 1]. 1 means identical direction.
- Levenshtein distance/ratio: Edit distance between strings. Ratio in [0, 1] (or 0–100%) for similarity.
- SimHash: A fast locality-sensitive hashing; similar texts produce similar 64-bit hashes. Hamming distance counts differing bits.
- Flesch‑Kincaid readability: Estimates how easy a text is to read from sentence length and syllables (we approximate by length heuristics).
- Sigmoid: A squashing function σ(x)=1/(1+e^(−x)) mapping any real number into (0,1). Useful for scoring into a probability-like value.
- MCQ: Multiple-choice question.
- Heuristic: A rule-of-thumb algorithm that is deterministic and fast, not a trained ML model.


How it works (high level)

1) Harvesters collect content from:
   - Vendor docs (AWS/Azure/GCP/Kubernetes/Docker/etc.)
   - StackOverflow (popular questions by tag)
   - GitHub (README extraction for curated repos/lists)

2) Question generation converts content → MCQs:
   - Extract key concepts
   - Generate question text from templates
   - Find a plausible correct answer (from context) and craft distractors
   - Score difficulty and confidence; keep only unique questions

3) Exporters format the data for downstream systems
   - QuizMentor exporter → per-category quizzes/*.json + harvest_index.json

4) Importers (adapters) deliver artifacts to target repos (local-only)
   - QuizMentor importer → copies/links quiz files into QuizMentor/quizzes
   - AI-Research importer → writes markdown summaries and updates docs/research/index.md


Heuristics & algorithms (no LLM required)

A) MassiveHarvester (MCQ generation)

- Concept extraction
  - Patterns: ProperCase words, ALLCAPS tokens, `code spans`, **bold**, markdown headings
  - Clean and de‑dup; take top N (default 20)

- Question templates
  - Definition: "What is X?" / "Which best describes X?"
  - Purpose: "What is the primary purpose of X?"
  - Comparison/Implementation variants

- Correct answer extraction (definitional scoring)
  - sentences = split(context)
  - relevant = sentences containing concept (case-insensitive)
  - score(sentence) = w0 + w1*[has(" is ", " are ", " refers to ")] + w2*proximity(concept, verb) − w3*length_penalty
  - best = argmax score; clamp to 80–180 characters; normalize leading article

- Distractors (category-informed)
  - Start from curated wrong-but-plausible siblings per domain (e.g., AWS, K8s, DB)
  - Apply contrast rules (negations, antonyms) and length balancing (±50%)
  - Filter by similarity 0.2–0.8 (Levenshtein ratio); ensure uniqueness
  - Distractor quality q ∈ [0,1]: start 1.0; subtract for length skew, near-duplicates, ultra-low/high similarity

- Difficulty
  - features: question_length>15 (+1), contains [explain/compare/analyze/evaluate] (+1), avg_option_len>50 (+1), option_similarity>0.6 (+1)
  - difficulty = clamp(1, 5, 1 + sum(features))

- Uniqueness
  - textual similarity: Levenshtein ratio < 0.85 to existing
  - fingerprint = md5(question + sorted(options)) for quick dedupe

ASCII (MCQ pipeline)

[content] -> [extract_concepts] -> [template] -> [definitional_scoring]
       -> [generate_distractors] -> [difficulty] -> [uniqueness]
       -> [save]


B) EnhancedHarvester (quality-focused generation)

- Semantic uniqueness
  - Build TF‑IDF vectors for previous questions
  - unique if max cosine < 0.85 (fallback: Levenshtein ratio < 0.85)

- Answer position balance
  - Keep counts for A/B/C/D; if imbalance > 20, place the correct answer in least-used slot

- Distractor quality q
  - Length variance penalty; duplicate penalty; similarity band penalty; generic-term penalty

- Confidence (explicit formula)
  - confidence = σ(β0 + β1*q + β2*(1 − max_cosine) + β3*content_quality + β4*pattern_score)
  - Defaults: β0=0, β1=1.2, β2=0.8, β3=0.5, β4=0.5 (documented below)

- Difficulty (heuristic)
  - base 1..3 from concept shape; +1 if long context; +1 if q>0.8; clamp 1..5

ASCII (enhanced)

[content] -> [concepts] -> [question]
          -> [distractors]-> [quality q]
          -> [balance A/B/C/D] -> [confidence σ(...)]
          -> [save if unique]


C) QuizMentor exporter (structure & filters)

- Source: generated_questions in harvest.db
- Filter: confidence ≥ 0.75
- Group by category; write quizzes/quiz_<category>_harvested.json and harvest_index.json


D) AI-Research importer (markdown + index, idempotent)

- Source: harvested_content where quality_score ≥ --min-quality
- For each item:
  - slug = slugify(domain + title)
  - bullets = 5 informative sentences (prefer 50–200 chars)
  - quotes = 2 longer lines (≥80 chars)
  - concepts = top tokens (patterns above)
  - tags_final = (harvest tags) ∪ {edition:PRO|CE}
  - category = tag→category map (user-overrideable) else Drafts
  - write docs/research/summaries/<slug>.md from template fields
  - append one row to docs/research/index.md under the category (skip if slug already present)

Idempotency explained
- Re-running import won’t create duplicates: existing slug.md is skipped; index row is only added if slug not found.

ASCII (category decision)

[tags_final] --count matches--> {Category: score}
        pick max score; if none, use Drafts

Note: Future (optional): centroid-based suggestions = cosine similarity to per-category TF‑IDF centroids, blended with tag rules. Still local and heuristic-only.


Adapters (local docking)

- QuizMentor adapter (local files)
  - Input: ./out/quizzes/quiz_*.json from exporter
  - Action: copy/link files into /path/to/QuizMentor.ai/quizzes/
  - Optional: verify minimal schema (questions[], options[], correct_answer:int)

- AI-Research adapter (local markdown)
  - Input: harvest.db
  - Action: write summaries/*.md and update index.md (idempotent)


Adapter interface specs (copy-paste friendly)

1) QuizMentor adapter (file drop-in)

Directory docking
- Source: <export_dir>/quizzes/quiz_*.json and <export_dir>/harvest_index.json
- Target: <quizmentor_repo>/quizzes/

File naming
- quiz_<category>_harvested.json (category lowercased, spaces replaced with underscores)

Per-file JSON schema (producer side: Scraper → consumer side: QuizMentor staging)
{
  "quiz_id": "harvest_<category>",
  "title": "<Category> Quiz (Harvested)",
  "description": "Auto-generated quiz from harvested <category> content",
  "category": "<category>",                // string, lowercase category key
  "difficulty": "mixed",                    // string: "mixed"
  "time_limit": 30,                          // number (seconds)
  "passing_score": 70,                       // number (percent)
  "questions": [
    {
      "id": "harvest_<row_id>",            // string; stable per DB row
      "question": "...",                    // string
      "options": ["A", "B", "C", "D"],     // array<string> length 4 preferred
      "correct_answer": 0,                   // integer index into options (0..3)
      "explanation": "...",                  // string (<= 500 chars)
      "difficulty": 1,                       // integer 1..5
      "tags": ["<category>", "<subcategory?>"] // array<string>
    }
  ],
  "metadata": {
    "source": "automated_harvest",
    "question_count": 42,                    // integer count
    "difficulty_distribution": {"1": 10, "2": 20, ...} // object of counts
  }
}

Optional flat dev/mock file (if you want to support mock fixtures directly)
- Path: <quizmentor_repo>/__mocks__/mocks/fixtures/questions.json
- Schema:
{
  "questions": [
    {
      "id": "q_001",
      "category": "science",
      "difficulty": "easy",               // "easy" | "medium" | "hard"
      "type": "multiple",                  // "multiple" | "true_false"
      "question": "...",
      "correctAnswer": "Mars",
      "incorrectAnswers": ["Venus", "Jupiter", "Saturn"],
      "explanation": "...",
      "points": 10,
      "timeLimit": 30
    }
  ],
  "quizSets": [
    {
      "id": "quiz_001",
      "title": "Science Basics",
      "description": "...",
      "category": "science",
      "questionIds": ["q_001", "q_002"],
      "difficulty": "mixed",
      "totalPoints": 60,
      "estimatedTime": 80
    }
  ]
}

Mapping from Scraper quiz to dev/mock
- options + correct_answer (index) → correctAnswer (text) + incorrectAnswers (other options)
- difficulty int 1..5 → string: 1–2 "easy", 3 "medium", 4–5 "hard"
- tags → category string (choose primary); subcategory may be embedded in question metadata (optional)

ASCII flow (QuizMentor adapter)

+------------------+     +-----------------+     +--------------------------+
| harvest.db       | --> | Export quizzes  | --> | <export_dir>/quizzes/*.json |
+------------------+     +-----------------+     +-------------+------------+
                                                  |
                                                  v
                                         <quizmentor_repo>/quizzes/


2) AI-Research adapter (markdown + index)

Directory docking
- Target repo root: <ai_research_repo>
- Summary files: <ai_research_repo>/docs/research/summaries/<slug>.md
- Index file: <ai_research_repo>/docs/research/index.md
- Template (reference): <ai_research_repo>/docs/research/templates/ENTRY_TEMPLATE.md

Slug rules
- slug = slugify("<domain>-<title>")
- slugify: lowercase; replace non [a-z0-9] with dashes; collapse dashes; trim

Summary markdown layout (frontmatter-like section)
---
# Generated by Scraper AI-Research Importer
title: <title>
source: <url>
authors: []
published_at: unknown
publisher: <domain>
source_type: article|post|paper|site|spec|book  # heuristic
license:
edition: PRO|CE
tags: [tag1, tag2, edition:PRO]
concepts: [concept1, concept2]
related: []
status: todo
date_added: YYYY-MM-DD
---

summary:
- bullet 1 (<=200 chars)
- bullet 2
- bullet 3
- bullet 4
- bullet 5

key_quotes:
- "A longer quote (>=80 chars)"
- "Another informative quote"

ideas_to_try:
- 
- 

links:
- url: <url>
  note: source

Index row format (append under category header)
- <Title> | <URL> | [tag1, tag2, edition:PRO] | PRO | todo | <slug> | YYYY-MM-DD

ASCII flow (AI-Research adapter)

+------------------+     +-------------------------+     +----------------------------------+
| harvest.db       | --> | Import research (local) | --> | summaries/<slug>.md + index.md    |
+------------------+     +-------------------------+     +------------------+---------------+
                                                           |                 |
                                                           |(idempotent)     |
                                                           +-----------------+


Adapter invariants
- QuizMentor
  - quiz_*.json must contain an array questions[] with options[] and correct_answer index
  - File names are deterministic per category; safe to overwrite; consumers may curate later
- AI-Research
  - A slug.md is created once; re-runs skip existing slugs (idempotent)
  - Index row is inserted once; no duplicates on re-run


More diagrams (stage-by-stage)

Harvest (Massive) breakdown

[seed URLs] -> [fetch HTML/API] -> [parse] -> [content blocks]
        -> [extract concepts] -> [questions] -> [save to SQLite]

Harvest (Enhanced) breakdown

[content blocks] -> [concepts] -> [question templates]
                -> [correct + distractors] -> [quality q]
                -> [balance A/B/C/D] -> [confidence σ(...)]
                -> [persist enhanced_harvest.db]

Export (QuizMentor)

[generated_questions] --(filter confidence>=0.75)--> [group by category]
                    -> [write quizzes/quiz_<cat>_harvested.json]
                    -> [write harvest_index.json]

Import (AI-Research)

[harvested_content] --(quality>=min)--> [slugify]
                   -> [summaries/<slug>.md]
                   -> [append index.md under category]


Parameters & defaults (tweak in code or future config)
- Export filter: min_confidence_export = 0.75
- MassiveHarvester
  - max_concepts = 20
  - uniqueness_threshold (Levenshtein ratio) = 0.85
  - difficulty feature thresholds: length>15, option_len>50, option_sim>0.6
- EnhancedHarvester
  - semantic_uniqueness: max_cosine < 0.85
  - balance_imabalance_threshold = 20
  - confidence β-weights: β0=0, β1=1.2, β2=0.8, β3=0.5, β4=0.5
- AI-Research importer
  - min_quality = 0.6 (CLI flag --min-quality)
  - category map: built-in + optional JSON overrides


End-to-end examples (local-only)

1) Quick harvest + quiz export + local import to QuizMentor
   scraper harvest massive --output-dir /tmp/harvest --max-content 100 --questions-per-content 5 --workers 8 --complete
   scraper export quizmentor --db /tmp/harvest/harvest.db --out ./out
   scraper import quizmentor --from ./out --to /Users/betolbook/Documents/github/QuizMentor.ai/quizzes --mode copy

2) Quick research import (dry-run first)
   scraper import research --db /tmp/harvest/harvest.db --repo /Users/betolbook/Documents/github/AI-Research --edition PRO --min-quality 0.75 --dry-run --limit 10
   scraper import research --db /tmp/harvest/harvest.db --repo /Users/betolbook/Documents/github/AI-Research --edition PRO --min-quality 0.75 --limit 10


Troubleshooting
- “No quiz files found”: ensure you ran the exporter and that ./out contains quiz_*.json
- “Index.md not updated”: confirm /docs/research/index.md exists and has category headers. The importer inserts a row right after the matching category header (falls back to Drafts if none found).
- “Duplicate slugs skipped”: expected; idempotency prevents duplicates. Delete the existing file to re-import, or request an --update-existing feature.


Security & compliance
- Respect robots.txt and source ToS
- Rate-limit requests (built-in sleeps in harvesters)
- Preserve attribution in AI-Research entries (source URL, publisher/domain)


FAQ
- Do I need a local LLM (Ollama)? No. Everything runs with deterministic heuristics. An optional LLM enhancer can be added later.
- What is “idempotent”? Running an import twice yields the same result—no duplicate files or index rows.
- What are “centroids” and “normalization”? A centroid is the average vector of items in a group. Normalization scales vectors to length 1 so cosine similarity compares direction only.
- What is “metadata enrichment”? Optionally fetching <meta> tags (author, publisher) or dates from pages to fill extra fields. Off by default.


Roadmap (local-first)
- Optional: flat questions.json export matching app mock schema (dev fixtures)
- Importer reports (JSON/CSV) and --update-existing flag
- Optional centroid-based category suggestions blended with tags
- Optional metadata enrichment with strict rate limits and clear toggles


License
MIT


Appendix A — Big-picture architecture (numbered) and zoom-ins

[1]           [2]            [3]                       [4]                      [5]                      [6]
+---------+   +----------+   +---------------------+   +--------------------+   +--------------------+   +---------------------+
| Sources |-->| Harvest  |-->| SQLite (harvest.db) |-->| Export (quizzes)  |-->| Validate (manifest)|-->| Import QuizMentor   |
| (docs,  |   | (massive |   | + enhanced.db (opt) |   | + manifest.json   |   | + schema + sanity  |   |   quizzes/*.json    |
|  SO,    |   |  /enh)   |   +---------------------+   +--------------------+   +--------------------+   +---------------------+
|  github)|   +----------+                                               |                               
+---------+                                                              | [7]
                                                                          v
                                                                      +---------------------+     [8]
                                                                      | Import AI-Research  |----->+----------------------+
                                                                      |  summaries/*.md     |      | HTML Report (static) |
                                                                      |  index.md append    |      |  totals, warnings,   |
                                                                      +---------------------+      |  diffs, previews     |
                                                                                                     +----------------------+

Notes
1) Sources: curated vendor docs, StackOverflow, GitHub READMEs (local HTTP fetch)
2) Harvest: MassiveHarvester (broad) and EnhancedHarvester (quality-focused)
3) Storage: SQLite database at output_dir/harvest.db (plus enhanced_harvest.db for enhanced)
4) Export (quizzes): write quizzes/quiz_<category>_harvested.json + harvest_index.json + manifest.json
5) Validate: quick gates (manifest checksums, minimal schema, sanity stats)
6) Import QuizMentor: copy/link files into QuizMentor/quizzes (staging)
7) Import AI-Research: create summaries/<slug>.md and append docs/research/index.md (idempotent)
8) HTML Report: single static page summarizing counts, categories, warnings, and previews


Appendix B — User journeys (step-by-step)

1) Quiz Engineer (local staging)
- Goal: Land fresh quizzes into QuizMentor/quizzes
- Journey:
  1. scraper harvest massive --output-dir /tmp/harvest --complete
  2. scraper export quizmentor --db /tmp/harvest/harvest.db --out /tmp/harvest_out
  3. scraper validate quiz --from /tmp/harvest_out   # optional gate
  4. scraper import quizmentor --from /tmp/harvest_out --to /path/to/QuizMentor.ai/quizzes --mode copy
  5. Open /path/to/QuizMentor.ai/quizzes and sample open quiz_* files
- Success signals: quiz files present, counts match manifest, app/mocks can read
- Failure states: no quiz files (rerun export), schema errors (fix), counts mismatch (investigate manifest)

2) Research Editor (markdown, no LLM)
- Goal: Create canonical markdown summaries and index entries
- Journey:
  1. scraper harvest massive --output-dir /tmp/harvest --complete (or reuse DB)
  2. scraper validate harvest --db /tmp/harvest/harvest.db  # optional
  3. scraper import research --db /tmp/harvest/harvest.db --repo /path/to/AI-Research --edition PRO --min-quality 0.75 --dry-run --limit 20
  4. Remove --dry-run and run again to write files
- Success signals: new summaries/<slug>.md files, new rows in index.md under correct categories
- Failure states: missing index.md (create it), unknown tags (warn), duplicate slug (skipped)

3) MLE (quality & rules tuning)
- Goal: Adjust tags map and thresholds, rerun safely
- Journey:
  1. Create tags_map.json (synonyms + enforce)
  2. Rerun research import with --mapping tags_map.json
  3. Compare report and diffs; iterate

4) PM (visibility)
- Goal: See what shipped this run
- Journey:
  1. Open reports/ship-report.html
  2. Check totals, warnings, previews, and diffs


Appendix C — S2S stories (system-to-system)

1) Scraper → QuizMentor staging
- Contract: quiz_*.json per category; harvest_index.json; optional manifest.json
- Behavior: overwrite-safe; verify-only and dock modes supported; optional symlinks

2) Scraper → AI-Research repo
- Contract: summaries/<slug>.md and an appended row in docs/research/index.md
- Behavior: idempotent writes; tag normalization to canonical list; Drafts fallback

3) Scraper internal
- Contract: harvest.db tables (generated_questions, harvested_content)
- Behavior: thresholds (min_quality, min_confidence), dedupe guards, deterministic scoring


Appendix D — Artifacts & logs (what you’ll see)

After a ship run, a typical tree looks like:

/tmp/harvest
├─ harvest.db
└─ quiz_harvest_20250903_215500.csv             # optional CSV report

/tmp/harvest_out
├─ manifest.json                                # checksums + counts
├─ harvest_index.json
└─ quizzes/
   ├─ quiz_kubernetes_harvested.json
   ├─ quiz_aws_harvested.json
   └─ ...

/path/to/QuizMentor.ai/quizzes
├─ quiz_kubernetes_harvested.json
├─ quiz_aws_harvested.json
└─ harvest_index.json

/path/to/AI-Research/docs/research
├─ summaries/
│  ├─ kubernetes-intro-kubernetes-io.md
│  └─ ...
├─ index.md
└─ TAGS.md

./reports
└─ ship-report.html                              # human-friendly HTML report


Appendix E — Validation gates & reports (details)

Gates
- Manifest: sha256/size/questions stable per file; totals match
- Minimal schema (quizzes): questions[], options[], correct_answer in range, difficulty 1..5, metadata
- Sanity stats: generated_questions > 0; avg_confidence ≥ min; duplicate ratio acceptable
- Repo checks: AI-Research docs/research paths & template exist; categories discoverable in index.md

Report (HTML)
- Cards: Totals, Quiz Files, Research Entries, Warnings/Errors
- Tables: per-quiz breakdown and per-summary listing
- Previews: sample 1–2 Qs per category; first summary bullet per entry
- Footer: run parameters (db path, output dir, thresholds), timestamps


Appendix F — Deep-dive notes (manifest, schema, symlink, sentinel, SimHash)

- Manifest: a JSON inventory of produced files (name, sha256, size, counts). Used to verify integrity before import.
- Minimal schema: just enough structure to prove the file is usable (not a full registry). Faster than JSON Schema, good for gates.
- Symlink vs copy: symlink saves space/time by pointing to source files; copy duplicates bytes. Use copy by default; if symlink fails, fallback to copy.
- Sentinel file: optional export_complete.json used as a "done" marker. Redundant if you validate manifest + schema; keep it optional.
- SimHash dedupe: compute 64-bit hash from character trigrams, compare Hamming distance to detect near-duplicates (skip if < 8–10).

Pseudocode (SimHash)
- shards = trigrams(text)
- h = simhash64(shards)
- if any hamdist(h, h_prev) < threshold: skip


Appendix G — Operations runbook (checklists)

Harvest:
- Ensure internet; pick output_dir; choose max-content and workers per bandwidth
- Watch for transient HTTP errors; re-run is safe

Export:
- Ensure DB path; pick out dir; confirm categories expected

Validate (optional but recommended):
- Run scraper validate quiz --from <out> and check for OK
- On strict failures: inspect manifest or bad file and re-export

Import:
- QuizMentor: copy into quizzes; re-run safe (overwrites staging)
- AI-Research: re-run safe (idempotent; existing slugs skipped; index no-dupe)

Report:
- Store reports/ship-report.html with the commit/PR; review warnings with editors


Appendix H — Examples & scripts

QuizMentor repo utility (verify/dock): scripts/harvest-dock.js
- Verify only: node scripts/harvest-dock.js --verify-only --from /tmp/harvest_out/quizzes
- Dock: node scripts/harvest-dock.js --from /tmp/harvest_out/quizzes --to ./quizzes --mode copy

Scraper planned commands
- scraper validate harvest|quiz|research  # run gates without importing
- scraper ship local --output ... --repos.quizmentor ... --repos.research ... --report-dir ./reports --strict


Appendix I — Extended glossary (quick refs)
- Canonical list: the official, source-of-truth list of allowed values (e.g., TAGS.md)
- Idempotent: re-running yields same end state (no duplicate files/rows)
- Normalization: making values consistent (vectors: length 1; tags: lowercase-hyphen-synonyms)
- Centroid: average vector of a category; for similarity-based suggestions
- Cosine similarity: [0..1] similarity on normalized vectors
- TF‑IDF: token weighting by frequency and rarity
- SimHash: near-duplicate detection via Hamming distance
- Manifest: JSON describing outputs (hashes, sizes, counts)
- Minimal schema: minimum fields/types to accept a file
- Sentinel: optional "done" marker; not required
- Symlink: filesystem pointer to source file; fallback to copy


Appendix J — Mega architecture diagram (teaching edition)

                               ┌─────────────────────────── Sources (curated) ────────────────────────────┐
                               │  - Vendor Docs  - StackOverflow  - GitHub READMEs  - Tutorials (opt)   │
                               └──────────────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
                                     ┌───────────────────────────────┐
                                     │ [2] Harvesters (local HTTP)  │
                                     │  Massive + Enhanced          │
                                     │  • parse HTML, extract text  │
                                     │  • extract concepts          │
                                     │  • generate MCQs             │
                                     └──────────────┬────────────────┘
                                                    │ questions + content
                                                    ▼
                                    ┌───────────────────────────────────────┐
                                    │ [3] SQLite (harvest.db / enhanced.db)│
                                    │  harvested_content, generated_questions│
                                    └──────────────┬────────────────────────┘
                                                   │
                                                   ▼
                               ┌───────────────────────────────┐     ┌─────────────────────────────────┐
                               │ [4] Export (quizzes JSON)     │     │  (optional) Export complete     │
                               │  • quizzes/quiz_<cat>.json    │     │  • manifest.json + sentinel     │
                               │  • harvest_index.json         │     └─────────────────────────────────┘
                               └──────────────┬────────────────┘
                                              │
                                              ▼
                               ┌───────────────────────────────┐
                               │ [5] Validate (local gates)    │
                               │  • manifest checksums         │
                               │  • minimal schema             │
                               │  • sanity stats               │
                               └──────────────┬────────────────┘
                                              │ ok
                                              ├───────────────────────────────────────────┐
                                              │                                           │
                                              ▼                                           ▼
             ┌─────────────────────────────────────────────┐               ┌─────────────────────────────────────────┐
             │ [6] Import to QuizMentor (staging files)    │               │ [7] Import to AI-Research (markdown)   │
             │  • copy/link quiz_*.json → quizzes/         │               │  • summaries/<slug>.md from template  │
             │  • overwrite-safe                            │               │  • index.md row under category        │
             └──────────────────────────┬────────────────────┘               └──────────────────────────┬────────────┘
                                        │                                             │
                                        │                                             │ idempotent
                                        ▼                                             ▼
                                 ┌─────────────────┐                         ┌──────────────────────────┐
                                 │  Staging files │                         │   Markdown knowledge    │
                                 │  for curation  │                         │   base (private)        │
                                 └─────────────────┘                         └──────────────────────────┘
                                              
                                              ▼
                               ┌───────────────────────────────┐
                               │  [8] HTML Report (static)     │
                               │  • totals, warnings, previews │
                               │  • parameters + timestamps    │
                               └───────────────────────────────┘

Legend
- Solid arrows = data flow; dotted/optional blocks = optional components (manifest, sentinel, HTML)
- Idempotent steps do not duplicate on re-runs


Appendix K — Sequence diagram (text) for one-shot ship

User -> Scraper: ship local (paths..., thresholds..., report-dir)
Scraper -> Harvesters: run massive (or enhanced)
Harvesters -> SQLite: write harvested_content, generated_questions
Scraper -> Export: read SQLite, write quizzes/*.json + index + manifest
Scraper -> Validate: check manifest, schema, sanity
Validate --> Scraper: OK (or warnings)
Scraper -> Import QM: copy/link files into QuizMentor/quizzes
Scraper -> Import Research: write summaries/*.md + index append
Scraper -> Report: render ship-report.html
Report --> User: Open reports/ship-report.html


Appendix L — Sample logs (annotated)

- Harvest
  [INFO] Starting Massive Harvest... (max_content=200, workers=8)
  [INFO] Harvested 136 content items; Generated 512 questions (avg_conf=0.82)

- Export (quiz)
  [INFO] Writing quizzes: 11 categories → /tmp/harvest_out/quizzes
  [INFO] Wrote manifest.json (totals.questions=1107)

- Validate
  [OK] 11/11 quiz files pass minimal schema
  [OK] Checksums match manifest; totals OK
  [WARN] 2 files have explanations > 500 chars (trimmed)

- Import QM
  [OK] Docked 11/11 quiz files to QuizMentor/quizzes (mode=copy)

- Import Research
  [OK] Created 18 summaries; Skipped 2 existing slugs; Appended 18 index rows

- Report
  [OK] Wrote reports/ship-report.html


Appendix M — Common pitfalls & quick fixes
- No quiz files found → Re-run export; check path /tmp/harvest_out/quizzes
- Schema error (correct_answer out of range) → Inspect file, regenerate with fixed generator
- Unknown tag → Add to tags_map.json or keep as warning (editor can fix later)
- Duplicate slugs → Expected on re-run; importer skips them
- Symlink failure → Switch to --mode copy (Windows or restricted FS)


Appendix N — Teach me like I’m new (clarifications)
- Canonical list: the official “allowed values” list maintained by a project (e.g., AI-Research TAGS.md). We normalize to it for consistency.
- Minimal schema: “Do we have the minimum fields the app needs?” Fast yes/no without full schema registry.
- Sentinel file: an optional “done” marker; not necessary when we validate manifest and schema.
- SimHash: a fast fingerprint for text; if two fingerprints differ by only a few bits (Hamming distance), the texts are near-duplicates.
- Idempotent: safe to run again; nothing breaks or duplicates.


Appendix O — Teach & Preview mode quickstart

Teach mode (verbose learning logs)
- Use --teach on ship or harvest/import commands to see labeled decisions:
  - [teach §E. Validate] Levenshtein ratio > 0.85 → reject near-duplicate wording
  - [teach §F. SimHash] Hamming distance < 8 → skip near-duplicate question by fingerprint
  - [teach §B. Heuristics] EnhancedHarvester TF‑IDF cosine max < 0.85 → unique
- These labels map to sections in this README so you can jump between logs and docs.

Preview mode (fast sampling)
- Use --preview on ship to include previews in the HTML report:
  - Quizzes: two sample questions per category
  - Research: the first bullet of each new summary

One-shot with teach+preview
  scraper ship local \
    --qm /path/to/QuizMentor.ai/quizzes \
    --research /path/to/AI-Research \
    --report-dir ./reports \
    --teach --preview --strict \
    --max-content 200 --questions-per-content 5

Heuristics thresholds (cheat sheet)
- Uniqueness (text): Levenshtein ratio < 0.85
- Uniqueness (semantic, enhanced): TF‑IDF cosine max < 0.85
- Near-duplicate fingerprint (SimHash): Hamming distance < 8 → skip


Appendix P — Productization & Tauri UI (proposal)

This project can stand alone as a desktop product: local-only harvesting, previews, and teaching-first logs.
- See docs/TAURI.md for a proposed Tauri UI (Rust + WebView) in the style of AI-OS-PRO
- See docs/EPICS.md for epics, phases, and acceptance criteria (Frontend, Learning Center, Gating, Reports)
- See docs/JOURNEYS.md for 20 user journeys and 20 system-to-system journeys used as acceptance scenarios
- See docs/SYSTEM_STATUS.md for an at-a-glance status snapshot

End of appendices.


Appendix Q — Legal guardrails & policy (overview)
- See docs/LEGAL_GUARDRAILS.md for the design and gates
- Use docs/POLICY_TEMPLATE.yaml to create a project policy.yaml
- Ship Report shows a Legal Summary card (placeholder until gates are implemented)
