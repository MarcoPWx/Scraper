# Dev Log – Scraper

Date: 2025-09-03

Scope: Local-first harvesting → quizzes (QuizMentor) and research markdown (AI-Research) with deterministic heuristics. No LLMs, no remote DBs.

What shipped today
- Importers (local docking)
  - QuizMentor importer: copies/links quiz_*.json into <quizmentor_repo>/quizzes/
  - AI-Research importer: writes docs/research/summaries/<slug>.md and appends docs/research/index.md (idempotent)
- CLI additions
  - scraper import quizmentor --from <export_dir> --to <quizmentor_repo>/quizzes --mode copy|link [--no-verify]
  - scraper import research --db <harvest.db> --repo <ai_research_repo> --edition PRO|CE --min-quality <float> [--mapping path] [--dry-run] [--limit N]
- README rewrite (onboarding manual)
  - Glossary and definitions (idempotent, normalization, centroids, metadata enrichment)
  - Detailed algorithms (extraction, distractors, difficulty, confidence, uniqueness)
  - ASCII diagrams per stage and adapter interface specs for both repos

Design decisions
- Local-only by default: keep all workflows runnable without Supabase/Ollama/cloud
- Idempotent importers: re-runs skip existing slugs/files and avoid duplicate index rows
- Deterministic heuristics: transparent rules, documented formulas, tunable constants

Heuristics (current)
- MassiveHarvester
  - Concepts: regex patterns for ProperCase/ALLCAPS/code/bold/headings; de-dup, top N
  - Answer: pick longest relevant sentence for concept (definition mode clamps length)
  - Distractors: category-informed + length balancing + similarity banding
  - Difficulty: +length +keywords +option_length +option_similarity → 1..5
  - Uniqueness: Levenshtein ratio threshold (0.85), plus md5 fingerprint
- EnhancedHarvester
  - Semantic uniqueness: TF‑IDF cosine < 0.85 (fallback to string ratio)
  - Answer position balance: keep A/B/C/D counts; correct goes to least-used if imbalance > 20
  - Distractor quality q ∈ [0,1], confidence σ(β0 + β1*q + β2*(1−cos) + …)

Adapters (today)
- QuizMentor staging
  - Source: <export_dir>/quizzes/quiz_*.json, harvest_index.json
  - Target: <quizmentor_repo>/quizzes/
  - Schema: questions[], options[], correct_answer (index), explanation, difficulty(1..5)
- AI-Research staging
  - Writes: docs/research/summaries/<slug>.md and docs/research/index.md
  - Slugify: lowercase, non-alnum → dash, collapse, trim

Verification checklist
- QuizMentor: quizzes/ contains quiz_*.json; sample file has questions[] with options[4] and correct_answer
- AI-Research: summaries/<slug>.md created; index.md appended exactly one row under category; re-run shows skipped

Next up (short-term)
- Importer reports
  - --report-dir <path> to emit JSON/CSV of {created, skipped, issues}; include category decisions and reasons
- Answer extraction upgrades
  - Definitional scoring with pattern verbs ("is", "refers to") and proximity weight; context window for continuity
- Uniqueness+ speed
  - SimHash trigram fingerprints with Hamming threshold; maintain LRU for fast recent dedupe
- Category placement (research)
  - Optional centroid-based suggestion blended with tag→category; thresholds documented; still local-only
- Flat questions export (optional)
  - --format questions produces a single questions.json matching dev/mock schema (correctAnswer + incorrectAnswers)

Future (deferred)
- Optional metadata enrichment (author/publisher/date) behind a --enrich-meta flag, with rate limits
- Optional Supabase adapter for QuizMentor (schema push) when DB is available

Notes
- All new behavior is documented in README with examples and ASCII flows
- Keep imports idempotent; add --update-existing later only when there’s a reviewer workflow

---

Date: 2025-09-03 (Teach + Preview upgrade)

What changed
- Ship command: added --teach and --preview flags to scraper ship local
- HTML report: added Previews cards (2 sample questions per category; first bullet for each new summary)
- Teach logs: labeled decisions for learning
  - [teach §E. Validate] Levenshtein > 0.85 → reject
  - [teach §F. SimHash] Hamming < 8 → skip near-duplicate question
  - [teach §B. Heuristics] Enhanced TF‑IDF cosine max < 0.85 → unique
- Orchestrator: fixed signature and CLI wiring; pass teach/preview through to harvesters/importers
- Import (research): supports --teach to print category decision scoring

Why
- Improve explainability while running (teaching-first)
- Provide fast visual sampling before full review (previews)

How to use
  scraper ship local \
    --qm /path/to/QuizMentor.ai/quizzes \
    --research /path/to/AI-Research \
    --report-dir ./reports \
    --teach --preview --strict \
    --max-content 200 --questions-per-content 5

Follow-ups
- Strict gates (fail-fast) toggles for manifest/schema/tag mismatches
- SimHash dedupe report section listing skipped questions with distances
- Inline README anchors in teach logs like [teach §F. SimHash]
