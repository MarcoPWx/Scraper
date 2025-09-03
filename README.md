# Scraper

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
